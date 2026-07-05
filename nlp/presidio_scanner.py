"""
NLP-based PHI/PII scanner and redactor using Microsoft Presidio and spaCy.

This module detects and redacts Protected Health Information (PHI)
and Personally Identifiable Information (PII) using natural language
processing (NLP) models, making it context-aware (especially for names,
organizations, and locations).
"""

from __future__ import annotations

import os
import re
import time
import logging
from typing import TypedDict
from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

# ---------------------------------------------------------------------------
# Shared types (matching the regex_redact.py structure for integration)
# ---------------------------------------------------------------------------

class MatchFinding(TypedDict):
    """A single PHI/PII match found in text."""
    type: str
    original_value: str
    start: int
    end: int

class ScanResult(TypedDict):
    """Full output returned by :func:`scan_and_redact`."""
    redacted_text: str
    findings: list[MatchFinding]
    total_phi_found: int
    redaction_summary: dict[str, int]
    nlp_duration_ms: float


# ---------------------------------------------------------------------------
# Clinical Header & Eponym Filter (Precision Improvement)
# ---------------------------------------------------------------------------

# Common clinical eponyms that shouldn't be flagged as PERSON names
EPONYMS = {
    "parkinson", "alzheimer", "crohn", "hodgkin", "huntington", 
    "down", "grave", "tourette", "asperger", "meniere", "wilson"
}

# Clinical metadata headers that frequently cause NER false positives (e.g. classified as ORG or PERSON)
HEADERS_TO_EXCLUDE = {
    "dob", "mrn", "ssn", "ip", "email", "aadhaar", "phone", 
    "address", "cell", "name", "contact", "portal", "residence",
    "backup", "mobile", "physician", "doctor", "patient", "license",
    "hospital", "clinic", "ward", "date", "status", "chief", "complaint",
    "history", "treatment", "discharged", "admitted", "review", "clinical", "note",
    "us", "er", "ent"
}

# Pre-compiled regular expressions for performance optimization
PUNCT_STRIP_RE = re.compile(r'^[^a-z0-9]+|[^a-z0-9]+$')
PERSON_INVALID_CHARS_RE = re.compile(r'[\d+@/\\:#_\[\]=]')
EPONYMS_RE = re.compile(r'|'.join(EPONYMS))

def is_false_positive(word: str, entity_type: str) -> bool:
    """
    Checks if a detected word is a false positive based on clinical context and clean name rules.
    """
    word_clean = word.strip().lower()
    
    # Strip common non-alphanumeric punctuation from borders (e.g. "SSN:" -> "ssn")
    word_alphanumeric = PUNCT_STRIP_RE.sub('', word_clean)
    
    # Rule 1: Exclude common clinical headers/meta-terms from PERSON, ORGANIZATION, and LOCATION
    if entity_type in ("PERSON", "ORGANIZATION", "LOCATION"):
        if word_alphanumeric in HEADERS_TO_EXCLUDE or word_clean in HEADERS_TO_EXCLUDE:
            return True
            
    # Rule 2: Specific validation for PERSON names
    if entity_type == "PERSON":
        # Person names should not contain numbers or clinical symbols
        if PERSON_INVALID_CHARS_RE.search(word):
            return True
        # Person names should not contain known disease eponyms (e.g. "Parkinson's disease")
        if EPONYMS_RE.search(word_clean):
            return True
        # Person names are usually longer than a single character
        if len(word_alphanumeric) <= 1:
            return True
            
    return False


# ---------------------------------------------------------------------------
# NLP Redaction Engine Class
# ---------------------------------------------------------------------------

class PresidioScanner:
    def __init__(self):
        # Configure Presidio to use the small, fast en_core_web_sm model
        # instead of trying to download the large en_core_web_lg model.
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        
        configuration = {
            "nlp_engine_name": "spacy",
            "models": [{"model_name": "en_core_web_sm", "lang_code": "en"}],
        }
        provider = NlpEngineProvider(nlp_configuration=configuration)
        nlp_engine = provider.create_engine()
        
        # Initialize the Analyzer and Anonymizer engines
        self.analyzer = AnalyzerEngine(nlp_engine=nlp_engine)
        self.anonymizer = AnonymizerEngine()

        # Add custom recognizer for Insurance IDs
        insurance_pattern = Pattern(
            name="insurance_id_pattern",
            regex=r"\bINS-\d+-[A-Za-z0-9]+\b",
            score=0.95
        )
        insurance_recognizer = PatternRecognizer(
            supported_entity="INSURANCE_ID",
            patterns=[insurance_pattern],
            context=["insurance", "policy", "plan", "subscriber"]
        )
        self.analyzer.registry.add_recognizer(insurance_recognizer)

        # Add custom recognizer for Professional/Medical/State License numbers
        license_pattern = Pattern(
            name="license_number_pattern",
            regex=r"\b[A-Za-z]{2,3}-\d{4}-\d{3,8}\b",
            score=0.95
        )
        license_recognizer = PatternRecognizer(
            supported_entity="LICENSE_NUMBER",
            patterns=[license_pattern],
            context=["license", "licence", "registration", "cert", "doctor", "physician"]
        )
        self.analyzer.registry.add_recognizer(license_recognizer)
        
        # Mapping Presidio entities to our standard label formats
        self.redaction_labels = {
            "PERSON": "[PERSON_REDACTED]",
            "PHONE_NUMBER": "[PHONE_REDACTED]",
            "EMAIL_ADDRESS": "[EMAIL_REDACTED]",
            "DATE_TIME": "[DATE_REDACTED]",
            "IP_ADDRESS": "[IP_REDACTED]",
            "URL": "[URL_REDACTED]",
            "LOCATION": "[LOCATION_REDACTED]",
            "US_SSN": "[SSN_REDACTED]",
            "ORGANIZATION": "[ORGANIZATION_REDACTED]",
            "US_DRIVER_LICENSE": "[LICENSE_REDACTED]",
            "MEDICAL_LICENSE": "[LICENSE_REDACTED]",
            "INSURANCE_ID": "[INSURANCE_REDACTED]",
            "LICENSE_NUMBER": "[LICENSE_REDACTED]",
        }
        
        # Precompute supported entity list to avoid rebuilding it on every scan
        self.supported_entities = list(self.redaction_labels.keys())

        # Pre-build OperatorConfig objects to avoid repeatedly initializing them on every scan
        self.operators = {
            entity_name: OperatorConfig("replace", {"new_value": label})
            for entity_name, label in self.redaction_labels.items()
        }

    def scan_and_redact(self, text: str) -> ScanResult:
        """
        Scan text for PII/PHI using Presidio (with spaCy NER) and redact it.
        """
        start_time = time.perf_counter()
        
        # 1. Analyze text to find PII entities (restricted to supported entities for optimization)
        raw_results = self.analyzer.analyze(
            text=text,
            language="en",
            entities=self.supported_entities
        )
        
        # Filter analyzer results to only include those we explicitly support and are not false positives
        analyzer_results = [
            r for r in raw_results 
            if r.entity_type in self.redaction_labels
            and not is_false_positive(text[r.start:r.end], r.entity_type)
        ]
        
        # 2. Extract findings matching the standard structure
        findings: list[MatchFinding] = []
        summary: dict[str, int] = {}
        
        for result in analyzer_results:
            ent_type = result.entity_type
            orig_val = text[result.start:result.end]
            type_lower = ent_type.lower()
            
            findings.append({
                "type": type_lower,
                "original_value": orig_val,
                "start": result.start,
                "end": result.end
            })
            summary[type_lower] = summary.get(type_lower, 0) + 1

        # 3. Anonymize the text using the AnonymizerEngine using pre-configured operators
        anonymized_result = self.anonymizer.anonymize(
            text=text,
            analyzer_results=analyzer_results,
            operators=self.operators
        )
        
        duration_ms = (time.perf_counter() - start_time) * 1000
        logger = logging.getLogger(__name__)
        logger.info(f"NLP Presidio scan completed in {duration_ms:.2f} ms")
        
        return {
            "redacted_text": anonymized_result.text,
            "findings": sorted(findings, key=lambda f: f["start"]),
            "total_phi_found": len(findings),
            "redaction_summary": summary,
            "nlp_duration_ms": duration_ms
        }


# ---------------------------------------------------------------------------
# Demo execution
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    scanner = PresidioScanner()
    
    # Path to sample notes
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    notes_path = os.path.join(base_dir, "nlp", "sample_notes.txt")
    
    if os.path.exists(notes_path):
        print(f"Reading sample notes from {notes_path}...")
        with open(notes_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split notes by blank lines / NOTE headers
        notes = [note.strip() for note in content.split("NOTE ") if note.strip()]
        
        for idx, note_body in enumerate(notes, 1):
            # Reconstruct the header since we split by it
            full_note = f"NOTE {note_body}"
            
            print("\n" + "="*80)
            print(f"PROCESSING NOTE {idx}:")
            print("-" * 40)
            print("ORIGINAL NOTE:")
            print(full_note)
            print("-" * 40)
            
            result = scanner.scan_and_redact(full_note)
            
            print("REDACTED NOTE:")
            print(result["redacted_text"])
            print("-" * 40)
            print(f"TOTAL PHI FOUND: {result['total_phi_found']}")
            
            breakdown_parts = [
                f"{category}: {count}"
                for category, count in sorted(result["redaction_summary"].items())
            ]
            print(f"FINDINGS BREAKDOWN: {', '.join(breakdown_parts)}")
            print("="*80)
    else:
        print(f"Error: Could not find sample notes file at: {notes_path}")
