#!/usr/bin/env python3
"""
Batch-scan all notes in ``sample_notes.txt`` and print a redaction report.

This tool acts as a CLI client to verify and benchmark rules-based PHI/PII redaction
across synthetic clinical note corpora, checking HIPAA Safe Harbor alignment.

Usage:
    python regex_pipeline/batch_scan.py
    python regex_pipeline/batch_scan.py --verbose
    python regex_pipeline/batch_scan.py --detect-only
    python regex_pipeline/batch_scan.py --stats
    python regex_pipeline/batch_scan.py --note NOTE_007
    python regex_pipeline/batch_scan.py --output results.json
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as ``python regex/batch_scan.py`` from project root.
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from regex_pipeline.note_loader import load_sample_notes
from regex_pipeline.regex_redact import REDACTION_LABELS, scan_and_redact

MEDICAL_TERMS = (
    "Parkinson's disease",
    "Alzheimer's disease",
)


def _check_medical_terms_preserved(original: str, redacted: str) -> list[str]:
    """Return disease names that were incorrectly removed from the text."""
    violations: list[str] = []
    for term in MEDICAL_TERMS:
        if term in original and term not in redacted:
            violations.append(term)
    return violations


def run_batch(
    notes_path: Path,
    verbose: bool = False,
    as_json: bool = False,
    detect_only: bool = False,
    stats: bool = False,
    output_path: Path | None = None,
    note_id_filter: str | None = None,
    redaction_labels: bool = False,
) -> int:
    """
    Scan clinical notes, execute the redaction pipeline, and report findings.

    Args:
        notes_path: Path to the note corpus file.
        verbose: Print original and redacted note snippets side-by-side.
        as_json: Output stdout results in machine-readable JSON format.
        detect_only: Run detection only without actual redaction.
        stats: Show aggregate metrics across all processed notes.
        output_path: Save evaluation output to a target file.
        note_id_filter: Target a specific Note ID (e.g. NOTE_007) for parsing.
        redaction_labels: Show mapping of original substrings to redaction labels.

    Returns:
        Integer count of notes containing medical term preservation issues.
    """
    notes = load_sample_notes(notes_path)
    if not notes:
        print(f"No notes found in {notes_path}", file=sys.stderr)
        return 1

    # Filter notes dictionary by a specific note ID if requested
    if note_id_filter:
        if note_id_filter not in notes:
            print(f"Error: Note ID '{note_id_filter}' not found in {notes_path}", file=sys.stderr)
            return 1
        notes = {note_id_filter: notes[note_id_filter]}

    issues = 0
    report: dict[str, object] = {"notes": {}, "total_notes": len(notes)}
    batch_results = []
    note_results = {}
    printed_lines: list[str] = []

    def log(msg: str = "") -> None:
        print(msg)
        printed_lines.append(msg)

    for note_id, body in sorted(notes.items()):
        result = scan_and_redact(body)
        preserved_violations = _check_medical_terms_preserved(body, result["redacted_text"])
        if preserved_violations:
            issues += 1

        note_results[note_id] = {
            "total_phi_found": result["total_phi_found"],
            "redaction_summary": result["redaction_summary"],
            "medical_term_violations": preserved_violations,
            "findings": result["findings"],
            "redacted_text": result["redacted_text"],
        }
        batch_results.append(result)

        if not as_json:
            if detect_only:
                summary_str = ", ".join(
                    f"{k}:{v}" for k, v in sorted(result["redaction_summary"].items())
                )
                log(f"{note_id}: would redact {result['total_phi_found']} items [{summary_str}]")
            else:
                summary_str = ", ".join(
                    f"{k}: {v}" for k, v in sorted(result["redaction_summary"].items())
                )
                log(f"{note_id}: {result['total_phi_found']} PHI items ({summary_str})")
                if preserved_violations:
                    log(f"  WARNING: medical terms altered: {', '.join(preserved_violations)}")
                if verbose:
                    log(f"  ORIGINAL:  {body[:120]}{'...' if len(body) > 120 else ''}")
                    log(f"  REDACTED:  {result['redacted_text'][:120]}{'...' if len(result['redacted_text']) > 120 else ''}")
                    log()

            if redaction_labels:
                for finding in result["findings"]:
                    orig = finding["original_value"]
                    label = REDACTION_LABELS.get(
                        finding["type"], f"[{finding['type'].upper()}_REDACTED]"
                    )
                    log(f'  "{orig}" → "{label}"')

    # Output aggregate metrics if requested
    if stats and not as_json:
        total_notes = len(notes)
        total_phi = sum(r["total_phi_found"] for r in batch_results)

        cat_totals = {}
        for r in batch_results:
            for cat, count in r["redaction_summary"].items():
                cat_totals[cat] = cat_totals.get(cat, 0) + count

        if cat_totals:
            most_common_type = max(cat_totals, key=cat_totals.get)
            most_common_count = cat_totals[most_common_type]
            most_common_str = f"{most_common_type} ({most_common_count} occurrences)"
        else:
            most_common_str = "None (0 occurrences)"

        avg_phi = total_phi / total_notes if total_notes > 0 else 0.0
        zero_phi_notes = sum(1 for r in batch_results if r["total_phi_found"] == 0)

        log()
        log("========================================")
        log("AGGREGATE STATISTICS")
        log("========================================")
        log(f"Total notes: {total_notes}")
        log(f"Total PHI items: {total_phi}")
        log(f"Most common type: {most_common_str}")
        log(f"Average PHI per note: {avg_phi:.1f}")
        log(f"Notes with zero PHI: {zero_phi_notes}")
        log("========================================")

    # Standard JSON report building
    for note_id, entry_data in note_results.items():
        report["notes"][note_id] = {
            "total_phi_found": entry_data["total_phi_found"],
            "redaction_summary": entry_data["redaction_summary"],
            "medical_term_violations": entry_data["medical_term_violations"],
        }

    if as_json:
        json_output = json.dumps(report, indent=2)
        print(json_output)
        printed_lines.append(json_output)
    else:
        log("-" * 60)
        log(f"Scanned {len(notes)} notes. Issues: {issues}")

    # Handle output file persistence
    if output_path:
        ext = output_path.suffix.lower()
        if ext == ".json":
            output_data = {
                "total_notes": len(notes),
                "issues": issues,
                "notes": {},
            }
            if stats:
                cat_totals = {}
                for r in batch_results:
                    for cat, count in r["redaction_summary"].items():
                        cat_totals[cat] = cat_totals.get(cat, 0) + count
                most_common_type = max(cat_totals, key=cat_totals.get) if cat_totals else None
                most_common_count = cat_totals[most_common_type] if cat_totals else 0
                avg_phi = sum(r["total_phi_found"] for r in batch_results) / len(notes) if notes else 0.0
                zero_phi_notes = sum(1 for r in batch_results if r["total_phi_found"] == 0)
                output_data["stats"] = {
                    "total_notes": len(notes),
                    "total_phi_items": sum(r["total_phi_found"] for r in batch_results),
                    "most_common_type": most_common_type,
                    "most_common_occurrences": most_common_count,
                    "average_phi_per_note": round(avg_phi, 1),
                    "notes_with_zero_phi": zero_phi_notes,
                }
            for note_id, res in note_results.items():
                output_data["notes"][note_id] = {
                    "total_phi_found": res["total_phi_found"],
                    "redaction_summary": res["redaction_summary"],
                    "medical_term_violations": res["medical_term_violations"],
                    "findings": res["findings"],
                    "redacted_text": res["redacted_text"],
                }
            output_path.write_text(json.dumps(output_data, indent=2), encoding="utf-8")
        else:
            output_path.write_text("\n".join(printed_lines), encoding="utf-8")

    return issues


def main() -> None:
    """Command line entry point for parsing and processing CLI arguments."""
    parser = argparse.ArgumentParser(description="Batch-scan clinical notes for PHI/PII.")
    parser.add_argument(
        "--notes",
        type=Path,
        default=Path(__file__).resolve().parent / "sample_notes.txt",
        help="Path to numbered sample notes file",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print original and redacted note snippets side-by-side",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print execution report in machine-readable JSON format to stdout",
    )
    parser.add_argument(
        "--detect-only",
        action="store_true",
        help="Perform detection only without redacting, printing the findings summary per note",
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show aggregate statistics across all processed clinical notes",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Save results to a file. Auto-detects format (.json or .txt) from file extension",
    )
    parser.add_argument(
        "--note",
        type=str,
        help="Scan a specific note by ID (e.g. NOTE_007)",
    )
    parser.add_argument(
        "--redaction-labels",
        action="store_true",
        help="Show a detailed mapping of what each detected item was replaced with",
    )

    args = parser.parse_args()

    exit_code = (
        1
        if run_batch(
            notes_path=args.notes,
            verbose=args.verbose,
            as_json=args.json,
            detect_only=args.detect_only,
            stats=args.stats,
            output_path=args.output,
            note_id_filter=args.note,
            redaction_labels=args.redaction_labels,
        )
        else 0
    )

    raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
