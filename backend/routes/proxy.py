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
from collections import defaultdict
import time as _time

# Add project root to sys.path to enable imports from sibling directories
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from vault.vault import Vault as RealVault
from vault.redis_client import RedisClient
from nlp.presidio_scanner import PresidioScanner
from regex_pipeline.regex_redact import scan_and_redact as regex_scan
from logger import FileAuditLogger
import fakeredis

logger = logging.getLogger(__name__)
proxy_bp = Blueprint("proxy", __name__)

# Initialize rate limit configurations
_rate_limit_store: dict = defaultdict(list)
RATE_LIMIT_MAX = 20        # requests
RATE_LIMIT_WINDOW = 60     # seconds

def _is_rate_limited(ip: str) -> tuple[bool, int]:
    """Returns (is_limited, retry_after_seconds)"""
    now = _time.time()
    window_start = now - RATE_LIMIT_WINDOW
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if t > window_start]
    if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX:
        oldest = min(_rate_limit_store[ip])
        retry_after = int(RATE_LIMIT_WINDOW - (now - oldest)) + 1
        return True, retry_after
    _rate_limit_store[ip].append(now)
    return False, 0

# Initialize file-based compliance auditor
audit_logger = FileAuditLogger()


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
    # Rate limiter
    client_ip = request.remote_addr or "unknown"
    limited, retry_after = _is_rate_limited(client_ip)
    if limited:
        response = jsonify({
            "error": "Too many requests. Please slow down.",
            "code": "RATE_LIMITED",
            "retry_after_seconds": retry_after
        })
        response.headers["Retry-After"] = str(retry_after)
        return response, 429

    data = request.get_json(force=True)
    text = data.get("text", "").strip()

    # Input validations
    if not text:
        return jsonify({"error": "Text cannot be empty", "code": "EMPTY_INPUT"}), 400

    if len(text) > 10000:
        return jsonify({
            "error": "Text too long. Maximum 10000 characters allowed",
            "code": "INPUT_TOO_LONG",
            "length": len(text),
            "max_length": 10000
        }), 413

    session_id = str(uuid.uuid4())
    all_findings = []
    
    start_time = _time.perf_counter()

    # 1. Run Regex Scanner
    t_reg_start = _time.perf_counter()
    regex_result = None
    try:
        regex_result = regex_scan(text)
        all_findings.extend(regex_result.get("findings", []))
    except Exception as e:
        logger.error(f"Regex scan error: {e}")
    regex_scan_ms = (_time.perf_counter() - t_reg_start) * 1000.0

    # 2. Run NLP Presidio Scanner
    t_nlp_start = _time.perf_counter()
    nlp_result = None
    nlp_duration_ms = None
    if nlp_scanner:
        try:
            nlp_result = nlp_scanner.scan_and_redact(text)
            nlp_duration_ms = nlp_result.get("nlp_duration_ms")
            all_findings.extend(nlp_result.get("findings", []))
        except Exception as e:
            logger.error(f"NLP scan error: {e}")
    nlp_scan_ms = (_time.perf_counter() - t_nlp_start) * 1000.0

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
    t_vault_start = _time.perf_counter()
    try:
        clean_text, processed_entities = real_vault.redact_note(
            session_id, 
            text, 
            entities_to_process, 
            confidence_threshold=0.7
        )
    except Exception as e:
        logger.exception("Redaction failed")
        audit_logger.log_error(request_id=session_id, error_message=str(e))
        return jsonify({"error": f"Redaction failed: {str(e)}"}), 500
    vault_redact_ms = (_time.perf_counter() - t_vault_start) * 1000.0

    total_ms = (_time.perf_counter() - start_time) * 1000.0

    # Build token_map for UI representation (pseudonym -> original)
    token_map = {}
    for e in processed_entities:
        token_map[e["token"]] = e["text"]

    # Log redaction metadata (HIPAA safe)
    audit_logger.log_redaction(
        request_id=session_id,
        session_id=session_id,
        phi_types=list(set(f["type"] for f in resolved_findings)),
        phi_count=len(resolved_findings),
        text_length=len(text),
        processing_time_ms=total_ms,
        regex_found=len(regex_result.get("findings", [])) if regex_result else 0,
        nlp_found=len(nlp_result.get("findings", [])) if nlp_result else 0,
        duplicates_removed=len(all_findings) - len(resolved_findings)
    )

    return jsonify({
        "session_id":      session_id,
        "clean_text":      clean_text,
        "token_map":       token_map,
        "entities_found":  len(token_map),
        "entities":        [
            {"original": e["text"], "category": e["type"]}
            for e in processed_entities
        ],
        "nlp_duration_ms": nlp_duration_ms,
        "performance": {
            "regex_scan_ms": round(regex_scan_ms, 1),
            "nlp_scan_ms": round(nlp_scan_ms, 1),
            "vault_redact_ms": round(vault_redact_ms, 1),
            "total_ms": round(total_ms, 1)
        }
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

    # 3. Fallback summary response if no API keys are configured (Dynamic Mock Generator)
    import re
    tokens = re.findall(r"\b[A-Za-z\d_]+_\d+\b", clean_text)
    
    person_tokens = [t for t in tokens if t.startswith("PERSON") or t.startswith("PATIENT")]
    date_tokens = [t for t in tokens if t.startswith("DATE")]
    mrn_tokens = [t for t in tokens if t.upper().startswith("MRN")]
    
    patient = person_tokens[0] if person_tokens else "the patient"
    doctor_str = ""
    if len(person_tokens) > 1:
        doctor_str = f" under the care of {person_tokens[1]}"
        
    text_lower = clean_text.lower()
    
    if "gastroenteritis" in text_lower or "gastro" in text_lower or "amit" in text_lower:
        diagnosis = "Acute Gastroenteritis"
        explanation = "an acute inflammation of the mucous membrane lining the stomach and the intestines, likely viral or bacterial in origin, leading to fluid loss."
        complications = "severe clinical dehydration, electrolyte imbalance, and metabolic acidosis."
        treatment_plan = "Initiation of oral rehydration therapy (ORT) or IV fluids depending on clinical tolerance. Short course of antiemetics (e.g., Ondansetron) if vomiting is persistent. Antibiotics (e.g., Azithromycin) only if bacterial origin is confirmed via stool culture."
        dietary_advice = "Follow clear liquid diet transitioning to bland foods (banana, rice, applesauce, toast - BRAT diet). Avoid dairy, caffeine, and fatty foods for 48 hours."
        diagnostics = "Complete Blood Count (CBC) to screen for active infection, serum electrolytes to check hydration status, and stool culture if symptoms do not improve within 72 hours."
        warning_signs = "Inability to keep liquids down for 24 hours, high-grade fever above 102 F, blood in stool, or signs of severe dehydration (extreme dizziness, dry mouth, little to no urination)."
    elif "migraine" in text_lower or "headache" in text_lower or "jessica" in text_lower:
        diagnosis = "Chronic Migraine Episodes"
        explanation = "a neurological disorder characterized by recurring moderate-to-severe headache attacks, often accompanied by sensory disturbances (aura), nausea, photophobia, and phonophobia."
        complications = "status migrainosus, medication overuse headaches, and disruption of daily activities."
        treatment_plan = "Take PRN abortive rescue medications (e.g., Triptans or NSAIDs) at the first sign of aura or onset. Initiate a migraine diary to track attacks. Consider daily prophylactic therapy (e.g., Beta-blockers, Amitriptyline) if frequency exceeds 4 episodes per month."
        dietary_advice = "Maintain regular sleep and hydration schedules. Eat meals at consistent times. Identify and avoid triggers such as aged cheeses, MSG, artificial sweeteners, and alcohol."
        diagnostics = "Detailed cranial nerve and neurological exam. Consider brain MRI/CT if headache characteristics change, become progressive, or if focal neurological deficits occur."
        warning_signs = "Sudden 'thunderclap' headache (reaching maximum intensity within seconds), or headaches accompanied by a stiff neck, high fever, confusion, seizures, or double vision."
    elif "chest" in text_lower or "congestion" in text_lower or "priyah" in text_lower or "cough" in text_lower:
        diagnosis = "Chest Congestion & Acute Respiratory Symptoms"
        explanation = "congestion of the bronchial passages, possibly representing acute bronchitis, reactive airway flare, or a lower respiratory tract infection."
        complications = "secondary bacterial pneumonia, chronic bronchitis progression, or acute respiratory distress."
        treatment_plan = "Supportive respiratory care. Prescribe expectorants (e.g., Guaifenesin) to thin mucus. Warm water saline gurgling. Bronchodilator inhaler (e.g., Albuterol) if wheezing or airway restriction is present."
        dietary_advice = "Increase warm fluid intake (herbal teas, broths, water) to help liquefy secretions. Rest in a well-humidified room. Avoid exposure to smoke, dust, and other airborne irritants."
        diagnostics = "Chest X-ray to rule out lung consolidation or pneumonia. Pulse oximetry to check resting oxygen saturation levels. Sputum culture if cough is productive of purulent phlegm."
        warning_signs = "Shortness of breath at rest, difficulty speaking in full sentences, chest pain, bluish tint on lips or fingertips, or resting oxygen saturation dropping below 94%."
    else:
        diagnosis = "Acute Clinical Symptoms"
        explanation = "unspecified acute symptoms requiring clinical investigation and supportive care."
        complications = "worsening of the underlying disease process."
        treatment_plan = "Symptom-based therapy. Follow the prescribed medication course precisely as instructed."
        dietary_advice = "Ensure adequate rest, balanced nutrition, and hydration. Avoid any known allergens."
        diagnostics = "Routine metabolic panels and follow-up clinical examination in 1-2 weeks."
        warning_signs = "New or rapidly worsening symptoms, severe pain, or high fever."

    date_str = f" on {date_tokens[0]}" if date_tokens else ""
    mrn_str = f" (MRN: {mrn_tokens[0]})" if mrn_tokens else ""
    
    return (
        f"CLINICAL SUMMARY & ACTION PLAN\n\n"
        f"1. ASSESSMENT:\n"
        f"Patient {patient}{mrn_str} was evaluated{date_str} for {diagnosis}{doctor_str}.\n\n"
        f"2. DISCUSSION OF PROBLEM:\n"
        f"The patient's presentation suggests {explanation} Early intervention is key to prevent complications like {complications}\n\n"
        f"3. MEDICAL RECOMMENDATIONS:\n"
        f"- Treatment Plan: {treatment_plan}\n"
        f"- Dietary & Activity Advice: {dietary_advice}\n"
        f"- Recommended Diagnostics: {diagnostics}\n\n"
        f"4. PATIENT EDUCATION & WARNING SIGNS:\n"
        f"Seek immediate emergency medical attention if you experience red flag symptoms including: {warning_signs}"
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
        audit_logger.log_session_cleared(session_id)
        return jsonify({"deleted": True, "session_id": session_id}), 200
    except Exception as e:
        logger.exception("Failed to delete session")
        return jsonify({"error": str(e)}), 500


# ─────────────────────────────────────────────
# GET /api/audit-log
# ─────────────────────────────────────────────
@proxy_bp.route("/audit-log", methods=["GET"])
def get_audit_log():
    """
    Returns recent audit log entries for compliance officer review.
    Query params:
      ?limit=50    (default 50, max 100)
      ?status=error (filter by status)
    HIPAA SAFE: Only returns metadata, never PHI content.
    """
    limit = request.args.get("limit", 50, type=int)
    if limit > 100:
        limit = 100
    status = request.args.get("status")

    entries = audit_logger.get_recent_logs(limit)
    if status:
        entries = [e for e in entries if e.get("status") == status]

    return jsonify({
        "total_returned": len(entries),
        "entries": entries
    }), 200


# ─────────────────────────────────────────────
# GET /api/stats
# ─────────────────────────────────────────────
@proxy_bp.route("/stats", methods=["GET"])
def get_pipeline_stats():
    """
    Returns aggregate pipeline statistics computed from audit log.
    Useful for management dashboard and compliance reporting.
    """
    stats_data = audit_logger.get_aggregate_stats()
    if stats_data.get("total_requests", 0) == 0:
        return jsonify({"message": "No requests processed yet", "total_requests": 0}), 200
    return jsonify(stats_data), 200


# ─────────────────────────────────────────────
# POST /api/validate — lightweight stateless pre-check
# ─────────────────────────────────────────────
@proxy_bp.route("/validate", methods=["POST"])
def validate_text():
    """
    Lightweight PHI pre-check using regex ONLY (no NLP, no Vault).
    ~12ms response time vs ~300ms for full /api/redact.
    Use this to show live PHI warnings in the UI before full redaction.
    Does NOT store anything in Redis. Stateless.
    """
    data = request.get_json(force=True)
    text = data.get("text", "").strip()

    # Input validations (same empty/too-long checks as /api/redact)
    if not text:
        return jsonify({"error": "Text cannot be empty", "code": "EMPTY_INPUT"}), 400

    if len(text) > 10000:
        return jsonify({
            "error": "Text too long. Maximum 10000 characters allowed",
            "code": "INPUT_TOO_LONG",
            "length": len(text),
            "max_length": 10000
        }), 413

    start_time = _time.perf_counter()
    regex_res = regex_scan(text)
    findings = regex_res.get("findings", [])
    total_detected = len(findings)
    contains_phi = total_detected > 0

    # Build types mapping
    by_type = {}
    for f in findings:
        t = f["type"]
        by_type[t] = by_type.get(t, 0) + 1

    # Compute risk level
    # "LOW" if total_detected <= 1
    # "MEDIUM" if total_detected 2-4
    # "HIGH" if total_detected >= 5 OR "person" in types found
    has_person = "person" in by_type
    if total_detected >= 5 or has_person:
        risk_level = "HIGH"
        risk_reason = f"{total_detected} PHI items detected including contact and identification details"
    elif 2 <= total_detected <= 4:
        risk_level = "MEDIUM"
        risk_reason = f"{total_detected} PHI items detected. Caution is recommended."
    else:
        risk_level = "LOW"
        risk_reason = f"{total_detected} PHI item detected. Minimal risk." if total_detected == 1 else "No PHI items detected. Safe for external services."

    duration_ms = (_time.perf_counter() - start_time) * 1000.0

    return jsonify({
        "request_id": str(uuid.uuid4()),
        "contains_phi": contains_phi,
        "phi_summary": {
            "total_detected": total_detected,
            "by_type": by_type
        },
        "risk_level": risk_level,
        "risk_reason": risk_reason,
        "safe_to_send_to_ai": not contains_phi,
        "recommendation": "Run full /api/redact before sending to any external AI service" if contains_phi else "Text is clean and safe to send to AI",
        "processing_time_ms": round(duration_ms, 2)
    }), 200
