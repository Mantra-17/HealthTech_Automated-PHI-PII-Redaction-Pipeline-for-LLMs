#!/usr/bin/env python3
"""
pattern_validator.py
Validates all 13 PHI regex patterns with targeted assertions.
Run: python -m regex_pipeline.pattern_validator
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from regex_pipeline.regex_redact import scan_and_redact


def run_all_validations() -> bool:
    """
    Execute 30 targeted pattern validation assertions on the regex redaction engine.

    Returns:
        True if all 30 assertions pass, False otherwise.
    """
    assertions = [
        # PHONES
        {
            "desc": '"9876543210" IS detected as phone',
            "run": lambda: any(f["type"] == "phone" for f in scan_and_redact("9876543210")["findings"]),
        },
        {
            "desc": '"+91-98765-43210" IS detected as phone',
            "run": lambda: any(f["type"] == "phone" for f in scan_and_redact("+91-98765-43210")["findings"]),
        },
        {
            "desc": '"(555) 123-4567" IS detected as phone',
            "run": lambda: any(f["type"] == "phone" for f in scan_and_redact("(555) 123-4567")["findings"]),
        },
        {
            "desc": '"12345" is NOT detected as phone',
            "run": lambda: not any(f["type"] == "phone" for f in scan_and_redact("12345")["findings"]),
        },
        # DATES
        {
            "desc": '"14/02/1985" IS detected as date',
            "run": lambda: any(f["type"] == "date" for f in scan_and_redact("14/02/1985")["findings"]),
        },
        {
            "desc": '"June 12 2026" IS detected as date',
            "run": lambda: any(f["type"] == "date" for f in scan_and_redact("June 12 2026")["findings"]),
        },
        {
            "desc": '"2026-07-01" IS detected as date',
            "run": lambda: any(f["type"] == "date" for f in scan_and_redact("2026-07-01")["findings"]),
        },
        {
            "desc": '"hello world" is NOT detected as date',
            "run": lambda: not any(f["type"] == "date" for f in scan_and_redact("hello world")["findings"]),
        },
        # EMAILS
        {
            "desc": '"rahul@gmail.com" IS detected as email',
            "run": lambda: any(f["type"] == "email" for f in scan_and_redact("rahul@gmail.com")["findings"]),
        },
        {
            "desc": '"user+tag@hospital.co.uk" IS detected as email',
            "run": lambda: any(f["type"] == "email" for f in scan_and_redact("user+tag@hospital.co.uk")["findings"]),
        },
        # SSN
        {
            "desc": '"123-45-6789" IS detected as ssn',
            "run": lambda: any(f["type"] == "ssn" for f in scan_and_redact("123-45-6789")["findings"]),
        },
        {
            "desc": '"12-345-6789" is NOT detected as ssn (wrong format)',
            "run": lambda: not any(f["type"] == "ssn" for f in scan_and_redact("12-345-6789")["findings"]),
        },
        # AADHAAR
        {
            "desc": '"1234 5678 9012" IS detected as aadhaar (spaced)',
            "run": lambda: any(f["type"] == "aadhaar" for f in scan_and_redact("1234 5678 9012")["findings"]),
        },
        {
            "desc": '"123456789012" IS detected as aadhaar (unspaced)',
            "run": lambda: any(f["type"] == "aadhaar" for f in scan_and_redact("123456789012")["findings"]),
        },
        # MRN
        {
            "desc": '"MRN-00234" IS detected as mrn',
            "run": lambda: any(f["type"] == "mrn" for f in scan_and_redact("MRN-00234")["findings"]),
        },
        {
            "desc": '"MRN00234" is NOT detected (no dash)',
            "run": lambda: not any(f["type"] == "mrn" for f in scan_and_redact("MRN00234")["findings"]),
        },
        # IP
        {
            "desc": '"192.168.1.1" IS detected as ip',
            "run": lambda: any(f["type"] == "ip" for f in scan_and_redact("192.168.1.1")["findings"]),
        },
        {
            "desc": '"999.999.999.999" is NOT detected (invalid octets)',
            "run": lambda: not any(f["type"] == "ip" for f in scan_and_redact("999.999.999.999")["findings"]),
        },
        # URL
        {
            "desc": '"www.hospital.com" IS detected as url',
            "run": lambda: any(f["type"] == "url" for f in scan_and_redact("www.hospital.com")["findings"]),
        },
        {
            "desc": '"https://portal.health.gov" IS detected as url',
            "run": lambda: any(f["type"] == "url" for f in scan_and_redact("https://portal.health.gov")["findings"]),
        },
        # INDIAN PIN
        {
            "desc": '"400001" IS detected as pin',
            "run": lambda: any(f["type"] == "pin" for f in scan_and_redact("400001")["findings"]),
        },
        {
            "desc": '"000001" is NOT detected (starts with 0)',
            "run": lambda: not any(f["type"] == "pin" for f in scan_and_redact("000001")["findings"]),
        },
        # US ZIP
        {
            "desc": '"90210" IS detected as zip',
            "run": lambda: any(f["type"] == "zip" for f in scan_and_redact("90210")["findings"]),
        },
        {
            "desc": '"90210-1234" IS detected as zip (ZIP+4)',
            "run": lambda: any(f["type"] == "zip" for f in scan_and_redact("90210-1234")["findings"]),
        },
        # INSURANCE
        {
            "desc": '"INS-789012-A" IS detected as insurance',
            "run": lambda: any(f["type"] == "insurance" for f in scan_and_redact("INS-789012-A")["findings"]),
        },
        {
            "desc": '"INS-789012" is NOT detected as insurance (no suffix)',
            "run": lambda: not any(f["type"] == "insurance" for f in scan_and_redact("INS-789012")["findings"]),
        },
        # LICENSE
        {
            "desc": '"MH-2024-7890" IS detected as license',
            "run": lambda: any(f["type"] == "license" for f in scan_and_redact("MH-2024-7890")["findings"]),
        },
        {
            "desc": '"MH-202-7890" is NOT detected as license (wrong year format)',
            "run": lambda: not any(f["type"] == "license" for f in scan_and_redact("MH-202-7890")["findings"]),
        },
        # OVERLAP
        {
            "desc": "URL containing digits is not double-redacted as PIN",
            "run": lambda: [
                f["type"] for f in scan_and_redact("Visit https://portal.health.gov/400001")["findings"]
            ]
            == ["url"],
        },
        {
            "desc": "Email not double-redacted as containing phone digits",
            "run": lambda: [
                f["type"] for f in scan_and_redact("Send to rahul9876543210@gmail.com")["findings"]
            ]
            == ["email"],
        },
    ]

    passed_count = 0
    failed_assertions = []

    for assertion in assertions:
        try:
            if assertion["run"]():
                print(f"✅ PASS: {assertion['desc']}")
                passed_count += 1
            else:
                print(f"❌ FAIL: {assertion['desc']}")
                failed_assertions.append(assertion["desc"])
        except Exception as e:
            print(f"❌ FAIL (EXCEPTION): {assertion['desc']} ({e})")
            failed_assertions.append(f"{assertion['desc']} (Exception: {e})")

    total = len(assertions)
    print()
    if passed_count == total:
        print("============================================")
        print("PATTERN VALIDATION RESULTS")
        print(f"{passed_count}/{total} assertions passed ✅")
        print("============================================")
        return True
    else:
        print("============================================")
        print("PATTERN VALIDATION RESULTS")
        print(f"❌ {total - passed_count}/{total} assertions failed")
        for fail in failed_assertions:
            print(f" - {fail}")
        print("============================================")
        return False


if __name__ == "__main__":
    success = run_all_validations()
    sys.exit(0 if success else 1)
