import os
import sys
import re
from pathlib import Path

# Add project root to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from regex_pipeline.note_loader import load_sample_notes
from regex_pipeline.regex_redact import scan_and_redact as regex_scan
from nlp.presidio_scanner import PresidioScanner
from scratch.accuracy_test import load_all_20_notes, parse_detection_report, MISSES_15, GROUND_TRUTH_16_20, overlaps, get_spans_for_entity, resolve_all_overlaps

def to_canonical(t):
    t = t.lower().strip()
    if t in ("person", "names"):
        return "PERSON"
    if t in ("date", "date_time", "time"):
        return "DATE"
    if t in ("phone", "phone_number"):
        return "PHONE"
    if t in ("email", "email_address"):
        return "EMAIL"
    if t in ("ssn", "us_ssn"):
        return "SSN"
    if t in ("mrn",):
        return "MRN"
    if t in ("insurance", "insurance_id"):
        return "INSURANCE"
    if t in ("license", "us_driver_license", "license_number", "medical_license"):
        return "LICENSE"
    if t in ("location", "zip", "pin"):
        return "LOCATION"
    if t in ("organization", "org"):
        return "ORGANIZATION"
    if t in ("url", "web_url"):
        return "URL"
    if t in ("ip", "ip_address"):
        return "IP"
    if t in ("aadhaar",):
        return "AADHAAR"
    return t.upper()

CANONICAL_CATEGORIES = [
    "PERSON", "DATE", "LOCATION", "PHONE", "EMAIL",
    "SSN", "MRN", "INSURANCE", "LICENSE", "URL", "IP",
    "ORGANIZATION", "AADHAAR"
]

def evaluate_per_entity(notes, ground_truth, run_fn):
    metrics = {cat: {"tp": 0, "fp": 0, "fn": 0} for cat in CANONICAL_CATEGORIES}
    
    for note_id, body in sorted(notes.items()):
        gt_findings = ground_truth[note_id]
        detected = run_fn(body)
        
        gt_by_cat = {cat: [] for cat in CANONICAL_CATEGORIES}
        for gt in gt_findings:
            cat = to_canonical(gt["type"])
            if cat in gt_by_cat:
                gt_by_cat[cat].append(gt)
            else:
                print(f"Warning: Unknown GT category {gt['type']} ({cat})")
                
        det_by_cat = {cat: [] for cat in CANONICAL_CATEGORIES}
        for det in detected:
            cat = to_canonical(det["type"])
            if cat in det_by_cat:
                det_by_cat[cat].append(det)
            else:
                # Add check for unrecognized categories, default to LOCATION or PERSON or warning
                print(f"Warning: Unknown Detected category {det['type']} ({cat})")
                
        for cat in CANONICAL_CATEGORIES:
            gts = gt_by_cat[cat]
            dets = det_by_cat[cat]
            
            matched_gt = set()
            matched_detected = set()
            
            for gt_idx, gt in enumerate(gts):
                for det_idx, det in enumerate(dets):
                    det_span = {"start": det["start"], "end": det["end"]}
                    if overlaps(gt, det_span):
                        matched_gt.add(gt_idx)
                        matched_detected.add(det_idx)
                        
            metrics[cat]["tp"] += len(matched_gt)
            metrics[cat]["fn"] += len(gts) - len(matched_gt)
            metrics[cat]["fp"] += len(dets) - len(matched_detected)
            
    results = {}
    for cat in CANONICAL_CATEGORIES:
        tp = metrics[cat]["tp"]
        fp = metrics[cat]["fp"]
        fn = metrics[cat]["fn"]
        
        precision = (tp / (tp + fp)) if (tp + fp) > 0 else (1.0 if fn == 0 else 0.0)
        recall = (tp / (tp + fn)) if (tp + fn) > 0 else 1.0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
        
        results[cat] = {
            "tp": tp,
            "fp": fp,
            "fn": fn,
            "precision": precision,
            "recall": recall,
            "f1": f1
        }
    return results

def make_markdown_table(results):
    lines = [
        "| Entity Category | True Positives (TP) | False Positives (FP) | False Negatives (FN) | Precision | Recall | F1-Score |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: |"
    ]
    for cat in CANONICAL_CATEGORIES:
        r = results[cat]
        # Format values
        p_str = f"{r['precision']:.2%}" if r['precision'] is not None else "N/A"
        r_str = f"{r['recall']:.2%}" if r['recall'] is not None else "N/A"
        f_str = f"{r['f1']:.2%}" if r['f1'] is not None else "N/A"
        lines.append(f"| **{cat}** | {r['tp']} | {r['fp']} | {r['fn']} | {p_str} | {r_str} | {f_str} |")
    return "\n".join(lines)

def main():
    scanner = PresidioScanner()
    notes = load_all_20_notes()
    
    report_path = _PROJECT_ROOT / "detection_report.md"
    extracted_detections = parse_detection_report(report_path)
    
    # Compile ground truth
    ground_truth = {}
    for note_id in [f"NOTE_{i:03d}" for i in range(1, 16)]:
        body = notes[note_id]
        gt_list = []
        if note_id in extracted_detections:
            for d in extracted_detections[note_id]:
                gt_list.append({"text": d["text"], "type": d["type"], "start": d["start"], "end": d["end"]})
        if note_id in MISSES_15:
            for m in MISSES_15[note_id]:
                spans = get_spans_for_entity(body, m["text"], m["type"])
                gt_list.extend(spans)
        seen = set()
        deduped_gt = []
        for gt in gt_list:
            key = (gt["start"], gt["end"])
            if key not in seen:
                seen.add(key)
                deduped_gt.append(gt)
        ground_truth[note_id] = sorted(deduped_gt, key=lambda x: x["start"])
        
    for note_id in [f"NOTE_{i:03d}" for i in range(16, 21)]:
        body = notes[note_id]
        gt_list = []
        for item in GROUND_TRUTH_16_20[note_id]:
            spans = get_spans_for_entity(body, item["text"], item["type"])
            gt_list.extend(spans)
        seen = set()
        deduped_gt = []
        for gt in gt_list:
            key = (gt["start"], gt["end"])
            if key not in seen:
                seen.add(key)
                deduped_gt.append(gt)
        ground_truth[note_id] = sorted(deduped_gt, key=lambda x: x["start"])
        
    # Evaluate Regex-Baseline
    print("Evaluating Regex-Baseline per entity...")
    run_regex = lambda body: regex_scan(body)["findings"]
    results_regex = evaluate_per_entity(notes, ground_truth, run_regex)
    
    # Evaluate Presidio-NLP
    print("Evaluating Presidio-NLP per entity...")
    run_nlp = lambda body: scanner.scan_and_redact(body)["findings"]
    results_nlp = evaluate_per_entity(notes, ground_truth, run_nlp)
    
    # Evaluate Combined-Proxy (Combined Pipeline)
    print("Evaluating Combined-Proxy per entity...")
    run_combined = lambda body: resolve_all_overlaps(regex_scan(body)["findings"] + scanner.scan_and_redact(body)["findings"])
    results_combined = evaluate_per_entity(notes, ground_truth, run_combined)
    
    print("\n--- REGEX BASELINE ---")
    print(make_markdown_table(results_regex))
    print("\n--- PRESIDIO NLP ---")
    print(make_markdown_table(results_nlp))
    print("\n--- COMBINED PROXY ---")
    print(make_markdown_table(results_combined))

if __name__ == "__main__":
    main()
