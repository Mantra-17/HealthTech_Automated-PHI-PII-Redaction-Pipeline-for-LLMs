"""
Risk Analyzer module to evaluate re-identification risk and ensure safety of redacted outputs.
"""

import re
from typing import Dict, Any, List

class RiskAnalyzer:
    """
    Analyzes re-identification risk and checks if sensitive patterns (like SSNs,
    emails, phone numbers, or Aadhaar numbers) remain unredacted in the processed text.
    """

    PATTERNS = {
        "ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
        "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
        "phone": re.compile(r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3,5}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}\b"),
        "aadhaar": re.compile(r"\b\d{4}\s\d{4}\s\d{4}\b"),
    }

    @staticmethod
    def calculate_risk(original_text: str, redacted_text: str) -> Dict[str, Any]:
        """
        Scans redacted_text to determine if any unredacted sensitive patterns exist.
        Returns a dictionary with 'is_safe' (bool) and 'leakages' (list).
        """
        leakages = []

        for pattern_name, regex in RiskAnalyzer.PATTERNS.items():
            matches = regex.findall(redacted_text)
            for match in matches:
                leakages.append({
                    "type": pattern_name,
                    "value": match
                })

        return {
            "is_safe": len(leakages) == 0,
            "leakages": leakages
        }
