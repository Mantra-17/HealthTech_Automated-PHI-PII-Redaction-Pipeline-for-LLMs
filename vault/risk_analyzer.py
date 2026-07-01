import re
import logging
from typing import Dict,Any

logger = logging.getLogger(__name__)

class RiskAnalyzer:
    """
    Automated checks to verify statistical safety of pseudonymized output (Day 20).
    Verifies absence of standard explicit PHI patterns in the redacted text.
    """

    # Basic regex patterns for HIPAA Safe Harbor explicit identifiers
    PATTERNS = {
        "SSN": r"\b\d{3}-\d{2}-\d{4}\b",
        "EMAIL": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        "PHONE": r"\b\d{3}[-.\s]??\d{3}[-.\s]??\d{4}\b",
        # Matches any date format looking like MM/DD/YYYY, MM-DD-YYYY
        "DATE": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        "AADHAAR": r"\b\d{4}\s\d{4}\s\d{4}\b",
    }

    @classmethod
    def calculate_risk(cls, original_text: str, redacted_text: str) -> Dict[str, Any]:
        """
        Analyzes the redacted text for leaked PHI.
        Returns a dictionary with 'is_safe' boolean and 'leakages' list.
        """
        leakages = []

        for phi_type, pattern in cls.PATTERNS.items():
            matches = re.findall(pattern, redacted_text)
            if matches:
                # To prevent leakage in logs, we only log the type and count, not the match
                logger.error(f"Potential PHI Leakage detected! Type: {phi_type}, Count: {len(matches)}")
                leakages.extend([{"type": phi_type, "count": len(matches)}])

        is_safe = len(leakages) == 0

        if is_safe:
            logger.info("Risk Analysis passed. No explicit PHI patterns detected in redacted text.")

        return {
            "is_safe": is_safe,
            "leakages": leakages
        }
