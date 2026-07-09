#!/usr/bin/env python3
"""
accuracy_scorer.py
Measures PHI detection accuracy of the regex pipeline.
Imports scan_and_redact from regex_pipeline.regex_redact
and load_sample_notes from regex_pipeline.note_loader
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path to enable imports from sibling directories
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from regex_pipeline.note_loader import load_sample_notes
from regex_pipeline.regex_redact import REDACTION_LABELS, scan_and_redact


class AccuracyScorer:
    """Measures PHI detection metrics across clinical notes."""

    def __init__(self) -> None:
        """Initialize the scorer by loading the sample notes."""
        self.notes: dict[str, str] = load_sample_notes()

    def score_note(self, original_text: str, redacted_text: str) -> dict:
        """
        Calculate redaction metrics for a single note.

        Args:
            original_text: The original unredacted text.
            redacted_text: The redacted output text.

        Returns:
            A dictionary containing evaluation metrics for the note.
        """
        # Count total occurrence of redaction labels
        phi_found = sum(redacted_text.count(label) for label in REDACTION_LABELS.values())

        # Determine which labels were actually used
        redaction_labels_used = [
            label for label in REDACTION_LABELS.values() if redacted_text.count(label) > 0
        ]

        # Calculate percentage of text redacted based on matched spans in original text
        res = scan_and_redact(original_text)
        findings = res.get("findings", [])
        chars_changed = sum(len(f["original_value"]) for f in findings)
        total_chars = len(original_text)

        redaction_percentage = (
            (chars_changed / total_chars * 100.0) if total_chars > 0 else 0.0
        )

        return {
            "phi_found": phi_found,
            "redaction_labels_used": redaction_labels_used,
            "redaction_percentage": round(redaction_percentage, 2),
        }

    def score_batch(self, notes_path: str | Path | None = None) -> dict:
        """
        Evaluate redaction metrics across all loaded clinical notes.

        Args:
            notes_path: Optional custom path to the notes file.

        Returns:
            A dictionary containing aggregated evaluation metrics.
        """
        notes = load_sample_notes(notes_path) if notes_path else self.notes
        if not notes:
            return {
                "total_notes": 0,
                "total_phi_found": 0,
                "avg_phi_per_note": 0.0,
                "best_note": "N/A",
                "worst_note": "N/A",
                "patterns_breakdown": {k: 0 for k in REDACTION_LABELS.keys()},
            }

        total_notes = len(notes)
        total_phi_found = 0
        per_note_counts: dict[str, int] = {}
        patterns_breakdown = {k: 0 for k in REDACTION_LABELS.keys()}

        for note_id, text in notes.items():
            res = scan_and_redact(text)
            redacted_text = res["redacted_text"]

            # Score the note
            score = self.score_note(text, redacted_text)
            note_phi = score["phi_found"]
            total_phi_found += note_phi
            per_note_counts[note_id] = note_phi

            # Aggregate pattern counts
            for cat, count in res.get("redaction_summary", {}).items():
                if cat in patterns_breakdown:
                    patterns_breakdown[cat] += count

        avg_phi_per_note = total_phi_found / total_notes if total_notes > 0 else 0.0

        best_note = max(per_note_counts, key=per_note_counts.get) if per_note_counts else "N/A"
        worst_note = min(per_note_counts, key=per_note_counts.get) if per_note_counts else "N/A"

        return {
            "total_notes": total_notes,
            "total_phi_found": total_phi_found,
            "avg_phi_per_note": round(avg_phi_per_note, 1),
            "best_note": best_note,
            "worst_note": worst_note,
            "patterns_breakdown": patterns_breakdown,
        }

    def generate_report(self, batch_result: dict) -> str:
        """
        Print and return a formatted text report of the accuracy results.

        Args:
            batch_result: The batch scoring dictionary.

        Returns:
            The formatted string report.
        """
        lines = [
            "============================================",
            "PHI DETECTION ACCURACY REPORT",
            "============================================",
            f"Total notes scanned: {batch_result['total_notes']}",
            f"Total PHI items found: {batch_result['total_phi_found']}",
            f"Average PHI per note: {batch_result['avg_phi_per_note']}",
            "",
            "Pattern breakdown:",
        ]

        # Scaled to maximum category count using 12 characters bar width
        breakdown = batch_result["patterns_breakdown"]
        max_val = max(breakdown.values()) if breakdown.values() else 1

        for pat in REDACTION_LABELS.keys():
            count = breakdown.get(pat, 0)
            filled = int(round((count / max_val) * 12)) if max_val > 0 else 0
            bar = "█" * filled + "░" * (12 - filled)
            lines.append(f"{pat:<9}{bar} {count:>2} items")

        lines.append("============================================")
        report_text = "\n".join(lines)

        # Print report to console
        print(report_text)

        # Write to accuracy_report.txt
        report_path = Path(__file__).resolve().parent / "accuracy_report.txt"
        report_path.write_text(report_text, encoding="utf-8")

        return report_text


if __name__ == "__main__":
    scorer = AccuracyScorer()
    res = scorer.score_batch()
    scorer.generate_report(res)
