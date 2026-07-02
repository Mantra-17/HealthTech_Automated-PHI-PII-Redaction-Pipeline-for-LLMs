"""
routes/proxy.py
---------------
Integrated production de-identification proxy API endpoints.
Connects Regex baseline detection, Presidio NLP, and the session-scoped Redis Vault.
"""

import os
import sys
import requests
import uuid
import logging
from flask import Blueprint, request, jsonify
from pathlib import Path

# Add project root to sys.path to enable imports from sibling directories
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from vault.vault import Vault as RealVault
from vault.redis_client import RedisClient
from nlp.presidio_scanner import PresidioScanner
from regex_pipeline.regex_redact import scan_and_redact as regex_scan
import fakeredis

logger = logging.getLogger(__name__)
proxy_bp = Blueprint("proxy", __name__)

# Initialize connection to Redis, falling back to fakeredis if unavailable
try:
    redis_client = RedisClient().get_client()
    redis_client.ping()
    print("[SUCCESS] Vault Proxy: connected to real Redis")
except Exception as e:
    print(f"[WARNING] Vault Proxy: Redis unavailable ({e}), falling back to fakeredis")
    redis_client = fakeredis.FakeStrictRedis(decode_responses=True)

# Initialize Vault facade and Presidio NLP scanner
real_vault = RealVault(redis_client, ttl_seconds=1800)

try:
    nlp_scanner = PresidioScanner()
    print("[SUCCESS] Vault Proxy: Presidio NLP scanner initialized successfully")
except Exception as e:
    print(f"[WARNING] Vault Proxy: Failed to initialize Presidio NLP scanner ({e})")
    nlp_scanner = None


def resolve_all_overlaps(findings):
    """
    Remove overlapping matches across Regex and NLP scanners,
    keeping the longest span or the highest priority match type.
    """
    if not findings:
        return []

    priority = {
        "url": 100,
        "url_address": 100,
        "email": 90,
        "email_address": 90,
        "ip": 85,
        "ip_address": 85,
        "aadhaar": 80,
        "ssn": 75,
        "us_ssn": 75,
        "insurance": 74,
        "insurance_id": 74,
        "license": 72,
        "us_driver_license": 72,
        "medical_license": 72,
        "license_number": 72,
        "mrn": 70,
        "phone": 65,
        "phone_number": 65,
        "date": 60,
        "date_time": 60,
        "person": 55,
        "zip": 50,
        "location": 45,
        "pin": 40,
        "organization": 35,
    }

    # Sort by start position, then by span length (longest first), then priority.
    ranked = sorted(
        findings,
        key=lambda f: (
            f["start"],
            -(f["end"] - f["start"]),
            -priority.get(f["type"].lower(), 0),
        ),
    )

    accepted = []
    for candidate in ranked:
        overlaps = any(
            not (candidate["end"] <= kept["start"] or candidate["start"] >= kept["end"])
            for kept in accepted
        )
        if not overlaps:
            accepted.append(candidate)

    return sorted(accepted, key=lambda f: f["start"])


# ─────────────────────────────────────────────
# POST /api/redact
# ─────────────────────────────────────────────
@proxy_bp.route("/redact", methods=["POST"])
def redact_note():
    data = request.get_json(force=True)
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No text provided"}), 400

    session_id = str(uuid.uuid4())
    all_findings = []

    # 1. Run Regex Scanner
    try:
        regex_result = regex_scan(text)
        all_findings.extend(regex_result.get("findings", []))
    except Exception as e:
        logger.error(f"Regex scan error: {e}")

    # 2. Run NLP Presidio Scanner
    nlp_duration_ms = None
    if nlp_scanner:
        try:
            nlp_result = nlp_scanner.scan_and_redact(text)
            nlp_duration_ms = nlp_result.get("nlp_duration_ms")
            all_findings.extend(nlp_result.get("findings", []))
        except Exception as e:
            logger.error(f"NLP scan error: {e}")

    # Resolve overlaps between Regex and NLP outputs
    resolved_findings = resolve_all_overlaps(all_findings)
    entities_to_process = []
    seen = set()
    for f in resolved_findings:
        key = (f["original_value"].strip().lower(), f["type"].upper())
        if key not in seen:
            seen.add(key)
            entities_to_process.append({
                "text": f["original_value"],
                "type": f["type"].upper(),
                "confidence": 1.0
            })

    # 3. Call real Vault facade to generate tokens and redact the note
    try:
        clean_text, processed_entities = real_vault.redact_note(
            session_id, 
            text, 
            entities_to_process, 
            confidence_threshold=0.7
        )
    except Exception as e:
        logger.exception("Redaction failed")
        return jsonify({"error": f"Redaction failed: {str(e)}"}), 500

    # Build token_map for UI representation (pseudonym -> original)
    token_map = {}
    for e in processed_entities:
        token_map[e["token"]] = e["text"]

    return jsonify({
        "session_id":      session_id,
        "clean_text":      clean_text,
        "token_map":       token_map,
        "entities_found":  len(token_map),
        "entities":        [
            {"original": e["text"], "category": e["type"]}
            for e in processed_entities
        ],
        "nlp_duration_ms": nlp_duration_ms
    }), 200


# ─────────────────────────────────────────────
# POST /api/ask — send clean text to external AI
# ─────────────────────────────────────────────
@proxy_bp.route("/ask", methods=["POST"])
def ask_ai():
    data       = request.get_json(force=True)
    session_id = data.get("session_id", "")
    clean_text = data.get("clean_text", "").strip()

    if not clean_text or not session_id:
        return jsonify({"error": "session_id and clean_text are required"}), 400

    # Call external AI (Claude or OpenAI)
    api_key  = os.getenv("ANTHROPIC_API_KEY") or os.getenv("OPENAI_API_KEY")
    provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"

    ai_response_raw = _call_ai(clean_text, api_key, provider)

    # Restore identities in AI response using Jash's real Vault
    try:
        ai_response_restored = real_vault.restore_note(session_id, ai_response_raw)
    except Exception as e:
        logger.exception("Restoration failed")
        return jsonify({"error": f"Restoration failed: {str(e)}"}), 500

    return jsonify({
        "session_id":           session_id,
        "ai_response_raw":      ai_response_raw,
        "ai_response_restored": ai_response_restored
    }), 200


def _call_ai(clean_text, api_key, provider):
    """Send pseudonymised text to external AI and return its response."""
    # 1. Try Google Gemini API (Free Tier) first if configured
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json={
                    "contents": [{
                        "parts": [{
                            "text": (
                                "You are a clinical decision support assistant. "
                                "Summarise the following de-identified clinical note "
                                "and suggest next steps. Use the placeholder names "
                                "exactly as given — do NOT invent real names.\n\n"
                                + clean_text
                            )
                        }]
                    }]
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")

    # 2. Try Anthropic/OpenAI if keys are configured
    if api_key:
        if provider == "anthropic":
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key":         api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type":      "application/json",
                },
                json={
                    "model":      "claude-sonnet-4-6",
                    "max_tokens": 512,
                    "messages": [
                        {
                            "role":    "user",
                            "content": (
                                "You are a clinical decision support assistant. "
                                "Summarise the following de-identified clinical note "
                                "and suggest next steps. Use the placeholder names "
                                "exactly as given — do NOT invent real names.\n\n"
                                + clean_text
                            )
                        }
                    ]
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["content"][0]["text"]

        else:  # openai
            resp = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type":  "application/json",
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are a clinical decision support assistant. Use placeholder names exactly as given."},
                        {"role": "user",   "content": clean_text}
                    ]
                },
                timeout=30
            )
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"]

    # 3. Fallback summary response if no API keys are configured
    return (
        "Summary: The patient presents with respiratory symptoms consistent with "
        "a mild lower respiratory tract infection. Recommend completing the "
        "prescribed antibiotic course, repeating imaging if symptoms persist, "
        "and scheduling a follow-up."
    )


# ─────────────────────────────────────────────
# POST /api/restore — manually restore a text
# ─────────────────────────────────────────────
@proxy_bp.route("/restore", methods=["POST"])
def restore_text():
    data       = request.get_json(force=True)
    session_id = data.get("session_id", "")
    text       = data.get("text", "")

    try:
        restored_text = real_vault.restore_note(session_id, text)
    except Exception as e:
        logger.exception("Restoration failed")
        return jsonify({"error": f"Restoration failed: {str(e)}"}), 500

    return jsonify({"restored_text": restored_text}), 200


# ─────────────────────────────────────────────
# GET /api/sessions
# ─────────────────────────────────────────────
@proxy_bp.route("/sessions", methods=["GET"])
def list_sessions():
    try:
        keys = redis_client.keys("*:*")
        session_ids = set()
        for k in keys:
            k_str = k.decode("utf-8") if isinstance(k, bytes) else k
            parts = k_str.split(":")
            if parts:
                session_ids.add(parts[0])
                
        sessions_detailed = []
        for s_id in session_ids:
            if not s_id:
                continue
            # Count tokens matching s_id:TOKEN:*
            token_keys = redis_client.keys(f"{s_id}:TOKEN:*")
            token_count = len(token_keys)
            
            # Since TTL is refreshed on read/write, let's get the max TTL of these keys
            ttl = 1800
            if token_keys:
                first_key = token_keys[0]
                key_ttl = redis_client.ttl(first_key)
                if key_ttl and key_ttl > 0:
                    ttl = key_ttl
                    
            sessions_detailed.append({
                "id": s_id,
                "token_count": token_count,
                "expires_in_mins": int(ttl / 60)
            })
            
        return jsonify({"sessions": sessions_detailed}), 200
    except Exception as e:
        logger.exception("Failed to list sessions")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# DELETE /api/sessions/<session_id>
# ─────────────────────────────────────────────
@proxy_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    try:
        real_vault.clear_session(session_id)
        return jsonify({"deleted": True, "session_id": session_id}), 200
    except Exception as e:
        logger.exception("Failed to delete session")
        return jsonify({"error": str(e)}), 500
