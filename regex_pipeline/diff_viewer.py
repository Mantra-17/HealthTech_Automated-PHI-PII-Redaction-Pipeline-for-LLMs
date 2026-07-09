#!/usr/bin/env python3
"""
diff_viewer.py
Shows character-level diff between original and redacted clinical notes.
Useful for compliance officers to audit exactly what was removed.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TypedDict

# Add project root to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from regex_pipeline.note_loader import load_sample_notes
from regex_pipeline.regex_redact import REDACTION_LABELS, scan_and_redact


class Change(TypedDict):
    """Represents a single character-level change in the redacted text."""

    position_start: int
    position_end: int
    original_value: str
    redacted_label: str
    phi_type: str


class DiffReport(TypedDict):
    """Full difference summary report between original and redacted texts."""

    changes: list[Change]
    total_chars: int
    changed_chars: int
    unchanged_chars: int
    redaction_percentage: float


class DiffViewer:
    """Computes and displays character-level differences in text redaction."""

    def generate_diff(
        self, original: str, redacted: str, findings: list[dict]
    ) -> DiffReport:
        """
        Build a DiffReport from the original text and its scanner findings.

        Args:
            original: The original unredacted text.
            redacted: The redacted text.
            findings: The list of findings from the scan_and_redact run.

        Returns:
            A structured DiffReport dictionary.
        """
        changes: list[Change] = []
        changed_chars = 0

        # Sort findings to match sequential order of appearance
        for f in sorted(findings, key=lambda x: x["start"]):
            start = f["start"]
            end = f["end"]
            orig = f["original_value"]
            label = REDACTION_LABELS.get(f["type"], f"[{f['type'].upper()}_REDACTED]")

            changes.append(
                {
                    "position_start": start,
                    "position_end": end,
                    "original_value": orig,
                    "redacted_label": label,
                    "phi_type": f["type"],
                }
            )
            changed_chars += len(orig)

        total_chars = len(original)
        unchanged_chars = total_chars - changed_chars
        redaction_percentage = (
            (changed_chars / total_chars * 100.0) if total_chars > 0 else 0.0
        )

        return {
            "changes": changes,
            "total_chars": total_chars,
            "changed_chars": changed_chars,
            "unchanged_chars": unchanged_chars,
            "redaction_percentage": round(redaction_percentage, 1),
        }

    def print_inline_diff(self, original: str, redacted: str, findings: list[dict]) -> None:
        """
        Print a clear terminal comparison detailing positions and values replaced.

        Args:
            original: The original unredacted text.
            redacted: The redacted text.
            findings: The list of findings.
        """
        diff_report = self.generate_diff(original, redacted, findings)

        print("ORIGINAL:")
        print(original)
        print()
        print("REDACTED:")
        print(redacted)
        print()
        print("CHANGES MADE:")
        for change in diff_report["changes"]:
            start = change["position_start"]
            end = change["position_end"]
            orig = change["original_value"]
            label = change["redacted_label"]
            phi_type = change["phi_type"]
            print(f'  Position {start}-{end}: "{orig}"  →  {label}   (type: {phi_type})')

        print()
        total_items = len(diff_report["changes"])
        unchanged_pct = round(100.0 - diff_report["redaction_percentage"], 1)
        print(f"SUMMARY: {total_items} items redacted | {unchanged_pct}% of text unchanged")

    def generate_html_diff(self, original: str, redacted: str, findings: list[dict]) -> str:
        """
        Return an HTML string representation of the text redaction differences.

        Args:
            original: The original unredacted text.
            redacted: The redacted text.
            findings: The list of findings.

        Returns:
            A string containing self-contained HTML/CSS code.
        """
        diff_report = self.generate_diff(original, redacted, findings)
        redaction_percentage = diff_report["redaction_percentage"]

        html_parts: list[str] = []
        curr = 0

        # Build inline formatted markers
        for change in diff_report["changes"]:
            start = change["position_start"]
            end = change["position_end"]
            orig = change["original_value"]
            label = change["redacted_label"]

            # Append unchanged preceding block
            html_parts.append(original[curr:start])

            # Append red strikethrough for original, followed by bold green for replaced label
            html_parts.append(
                f'<span style="background-color: #ffeef0; text-decoration: line-through; color: #d73a49;">{orig}</span>'
                f'<span style="background-color: #e6ffed; color: #22863a; font-weight: bold; margin-left: 4px; padding: 0 2px; border-radius: 2px;">{label}</span>'
            )
            curr = end

        html_parts.append(original[curr:])
        body_content = "".join(html_parts)

        # Wrap in a clean browser-ready page layout
        html_document = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>PHI Redaction Audit Diff</title>
  <style>
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.6;
      margin: 40px auto;
      max-width: 900px;
      color: #24292e;
      background-color: #fafbfc;
    }}
    .container {{
      background: #ffffff;
      padding: 30px;
      border: 1px solid #e1e4e8;
      border-radius: 6px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }}
    .header {{
      border-bottom: 2px solid #e1e4e8;
      padding-bottom: 15px;
      margin-bottom: 20px;
    }}
    h1 {{
      margin: 0 0 10px 0;
      font-size: 24px;
      color: #0366d6;
    }}
    .summary {{
      font-size: 14px;
      color: #586069;
    }}
    .metric {{
      display: inline-block;
      margin-right: 20px;
      font-weight: 500;
    }}
    pre {{
      background: #f6f8fa;
      padding: 20px;
      border: 1px solid #e1e4e8;
      border-radius: 6px;
      white-space: pre-wrap;
      word-break: break-word;
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      font-size: 14px;
      line-height: 1.8;
    }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>PHI Redaction Audit Diff</h1>
      <div class="summary">
        <span class="metric">🎯 <strong>Items Redacted:</strong> {len(findings)}</span>
        <span class="metric">🔒 <strong>Text Unchanged:</strong> {100.0 - redaction_percentage:.1f}%</span>
      </div>
    </div>
    <h3>Visual Audit Log</h3>
    <pre>{body_content}</pre>
  </div>
</body>
</html>
"""
        return html_document


if __name__ == "__main__":
    # Load first sample note
    notes = load_sample_notes()
    note_id = "NOTE_001"
    original_text = notes[note_id]

    # Process redaction
    result = scan_and_redact(original_text)
    redacted_text = result["redacted_text"]
    findings = result["findings"]

    viewer = DiffViewer()
    print(f"=== {note_id} INLINE DIFF ===")
    viewer.print_inline_diff(original_text, redacted_text, findings)
    print()

    # Generate HTML representation
    html_output = viewer.generate_html_diff(original_text, redacted_text, findings)
    output_path = Path(__file__).resolve().parent / "diff_output.html"
    output_path.write_text(html_output, encoding="utf-8")
    print(f"Diff saved to {output_path}")
