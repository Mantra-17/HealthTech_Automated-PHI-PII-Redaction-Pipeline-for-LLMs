"""
routes/evaluation.py
---------------------
Flask API endpoints for NLP precision, recall, and F1-score evaluation.
Provides endpoints to run custom evaluations and pre-compiled clinical note evaluations.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from flask import Blueprint, request, jsonify

# Add project root to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from nlp.evaluator import NLPEvaluator
from regex_pipeline.note_loader import load_sample_notes
from regex_pipeline.regex_redact import scan_and_redact as regex_scan

evaluation_bp = Blueprint("evaluation", __name__)

# Static ground truth definitions matching accuracy_test.py
MISSES_15 = {
    "NOTE_003": [
        {"text": "9 Lake View Road", "type": "location"},
        {"text": "Bengaluru", "type": "location"}
    ],
    "NOTE_004": [
        {"text": "75 Brook Lane", "type": "location"}
    ],
    "NOTE_005": [
        {"text": "12 Residency Road", "type": "location"},
        {"text": "Jaipur", "type": "location"}
    ],
    "NOTE_006": [
        {"text": "230 King St", "type": "location"}
    ],
    "NOTE_007": [
        {"text": "4 Riverfront Apartments", "type": "location"},
        {"text": "Ahmedabad", "type": "location"}
    ],
    "NOTE_008": [
        {"text": "890 Maple Drive", "type": "location"},
        {"text": "DC", "type": "location"}
    ],
    "NOTE_010": [
        {"text": "NY", "type": "location"}
    ],
    "NOTE_011": [
        {"text": "17 Civil Lines", "type": "location"},
        {"text": "Lucknow", "type": "location"}
    ],
    "NOTE_012": [
        {"text": "OR", "type": "location"}
    ],
    "NOTE_013": [
        {"text": "55 Sector 17", "type": "location"},
        {"text": "Chandigarh", "type": "location"}
    ],
    "NOTE_014": [
        {"text": "GA", "type": "location"}
    ]
}

GROUND_TRUTH_16_20 = {
    "NOTE_016": [
        {"text": "John Smith", "type": "person"},
        {"text": "14/02/1985", "type": "date"},
        {"text": "05/06/2026", "type": "date"},
        {"text": "(555) 019-2834", "type": "phone"},
        {"text": "666-29-9012", "type": "ssn"},
        {"text": "42 MG Road", "type": "location"},
        {"text": "Mumbai", "type": "location"},
        {"text": "Maharashtra", "type": "location"},
        {"text": "400001", "type": "pin"},
        {"text": "Emily Carter", "type": "person"},
        {"text": "Sunrise Hospital", "type": "organization"}
    ],
    "NOTE_017": [
        {"text": "Rahul Verma", "type": "person"},
        {"text": "MRN-998822", "type": "mrn"},
        {"text": "01/06/2026", "type": "date"},
        {"text": "rahul.verma@outlook.com", "type": "email"},
        {"text": "91-98765-43210", "type": "phone"},
        {"text": "Anil Mehta", "type": "person"},
        {"text": "Metro Care Center", "type": "organization"}
    ],
    "NOTE_018": [
        {"text": "Sarah Johnson", "type": "person"},
        {"text": "INS-789012-A", "type": "insurance"},
        {"text": "15 Park Street", "type": "location"},
        {"text": "Delhi", "type": "location"},
        {"text": "110001", "type": "pin"},
        {"text": "Mike Johnson", "type": "person"},
        {"text": "9123456780", "type": "phone"},
        {"text": "Priya Nair", "type": "person"},
        {"text": "MH-2024-7890", "type": "license"}
    ],
    "NOTE_019": [
        {"text": "June 12, 2026", "type": "date"},
        {"text": "Robert 'Bob' Taylor", "type": "person"},
        {"text": "09-18-1972", "type": "date"},
        {"text": "192.168.1.104", "type": "ip"},
        {"text": "rtaylor72@yahoo.com", "type": "email"},
        {"text": "Sarah Jenkins", "type": "person"}
    ],
    "NOTE_020": [
        {"text": "Alice Green", "type": "person"},
        {"text": "03/15/2026", "type": "date"},
        {"text": "https://clinical-portal.local/records/g-89211", "type": "url"},
        {"text": "James Andrews", "type": "person"}
    ]
}


def get_spans_for_entity(text: str, entity_text: str, category: str) -> list[dict]:
    spans = []
    start_idx = 0
    while True:
        idx = text.find(entity_text, start_idx)
        if idx == -1:
            break
        spans.append({
            "text": entity_text,
            "type": category,
            "start": idx,
            "end": idx + len(entity_text)
        })
        start_idx = idx + 1
    return spans


def parse_detection_report(report_path: Path) -> dict[str, list[dict]]:
    findings = {}
    if not report_path.exists():
        return findings
    with open(report_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line.startswith("|"):
                continue
            cols = [c.strip() for c in line.split("|")]
            if len(cols) < 5:
                continue
            note_id = cols[1]
            if not re.match(r'^NOTE_\d{3}$', note_id):
                continue
            category = cols[2].replace("**", "").strip().lower()
            text = cols[3].replace("`", "").strip()
            span = cols[4].strip()
            m_span = re.match(r'^(\d+)-(\d+)$', span)
            if m_span:
                start = int(m_span.group(1))
                end = int(m_span.group(2))
                if note_id not in findings:
                    findings[note_id] = []
                findings[note_id].append({
                    "text": text,
                    "type": category,
                    "start": start,
                    "end": end
                })
    return findings


def load_all_notes() -> dict[str, str]:
    notes = load_sample_notes(_PROJECT_ROOT / "regex_pipeline" / "sample_notes.txt")
    nlp_path = _PROJECT_ROOT / "nlp" / "sample_notes.txt"
    if nlp_path.exists():
        with open(nlp_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        parts = re.split(r"\n(?=NOTE \d+:)", content)
        for part in parts:
            part = part.strip()
            if not part:
                continue
            lines = part.splitlines()
            header = lines[0].strip()
            m = re.search(r"\d+", header)
            if m:
                note_num = int(m.group(0))
                note_id = f"NOTE_{note_num+15:03d}"
                body = "\n".join(lines[1:]).strip()
                notes[note_id] = body
    return notes


def compile_ground_truth(notes: dict[str, str]) -> dict[str, list[dict]]:
    ground_truth = {}
    report_path = _PROJECT_ROOT / "detection_report.md"
    extracted_detections = parse_detection_report(report_path)

    for note_id in [f"NOTE_{i:03d}" for i in range(1, 16)]:
        if note_id not in notes:
            continue
        body = notes[note_id]
        gt_list = []
        if note_id in extracted_detections:
            for d in extracted_detections[note_id]:
                gt_list.append({"text": d["text"], "type": d["type"], "start": d["start"], "end": d["end"]})
        if note_id in MISSES_15:
            for m in MISSES_15[note_id]:
                spans = get_spans_for_entity(body, m["text"], m["type"])
                gt_list.extend(spans)
        
        # Dedup
        seen = set()
        deduped = []
        for gt in gt_list:
            key = (gt["start"], gt["end"])
            if key not in seen:
                seen.add(key)
                deduped.append(gt)
        ground_truth[note_id] = sorted(deduped, key=lambda x: x["start"])

    for note_id in [f"NOTE_{i:03d}" for i in range(16, 21)]:
        if note_id not in notes:
            continue
        body = notes[note_id]
        gt_list = []
        if note_id in GROUND_TRUTH_16_20:
            for item in GROUND_TRUTH_16_20[note_id]:
                spans = get_spans_for_entity(body, item["text"], item["type"])
                gt_list.extend(spans)
        
        # Dedup
        seen = set()
        deduped = []
        for gt in gt_list:
            key = (gt["start"], gt["end"])
            if key not in seen:
                seen.add(key)
                deduped.append(gt)
        ground_truth[note_id] = sorted(deduped, key=lambda x: x["start"])

    return ground_truth


@evaluation_bp.route("/evaluate", methods=["POST"])
def evaluate_custom():
    """
    Evaluates arbitrary ground truth and predictions lists/dicts.
    """
    data = request.json or {}
    gt = data.get("ground_truth")
    pred = data.get("predictions")
    mode = data.get("mode", "exact")
    strict_type = data.get("strict_type", True)
    aggregation = data.get("aggregation", "micro")

    if gt is None or pred is None:
        return jsonify({"error": "Missing ground_truth or predictions in request body"}), 400

    try:
        evaluator = NLPEvaluator(mode=mode, strict_type=strict_type, aggregation=aggregation)
        report = evaluator.evaluate(gt, pred)
        return jsonify(report), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@evaluation_bp.route("/evaluate/sample-notes", methods=["GET"])
def get_sample_notes_evaluation():
    """
    Loads all 20 clinical notes, runs predictions using the combined active pipeline (Regex + Presidio NLP),
    compiles ground truth, and returns note bodies, ground truths, predictions, and calculated metrics.
    """
    try:
        # Import active components from proxy route to run pipeline
        from routes.proxy import resolve_all_overlaps, nlp_scanner

        notes = load_all_notes()
        ground_truth = compile_ground_truth(notes)
        
        # Generate predictions for all notes using combined pipeline
        predictions = {}
        for note_id, text in notes.items():
            regex_res = regex_scan(text)
            nlp_res = nlp_scanner.scan_and_redact(text) if nlp_scanner else {"findings": []}
            
            # Map NLP findings keys to match evaluator expectations
            nlp_findings = []
            for f in nlp_res.get("findings", []):
                nlp_findings.append({
                    "start": f["start"],
                    "end": f["end"],
                    "type": f["type"],
                    "text": f["original_value"]
                })

            regex_findings = []
            for f in regex_res.get("findings", []):
                regex_findings.append({
                    "start": f["start"],
                    "end": f["end"],
                    "type": f["type"],
                    "text": f["text"]
                })

            combined = regex_findings + nlp_findings
            resolved = resolve_all_overlaps(combined)
            predictions[note_id] = resolved

        # Prepare payload for UI rendering
        notes_data = {}
        for note_id in sorted(notes.keys()):
            notes_data[note_id] = {
                "body": notes[note_id],
                "ground_truth": ground_truth.get(note_id, []),
                "predictions": predictions.get(note_id, [])
            }

        return jsonify({
            "notes": notes_data
        }), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
