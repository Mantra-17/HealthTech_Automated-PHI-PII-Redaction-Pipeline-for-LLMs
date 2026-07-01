# Safe Harbor Mapping Document

The HIPAA Safe Harbor method requires the removal of 18 specific types of identifiers. Our automated NLP and Regex pipeline identifies these, and the Vault engine handles their pseudonymization.

## Identifier Redaction Strategy

1. **Names**: Mapped to `PATIENT_xxx`, `DOCTOR_xxx`, `RELATIVE_xxx`.
2. **Geographic subdivisions smaller than a state**: Mapped to `LOCATION_xxx`, `HOSPITAL_xxx`.
3. **Dates (except year)**: Mapped to `DATE_xxx`.
4. **Phone numbers**: Mapped to `PHONE_xxx`.
5. **Vehicle identifiers/Serial numbers**: Mapped to `VEHICLE_xxx`.
6. **Fax numbers**: Mapped to `FAX_xxx`.
7. **Device identifiers and serial numbers**: Mapped to `DEVICE_xxx`.
8. **Email addresses**: Mapped to `EMAIL_xxx`.
9. **Web Universal Resource Locators (URLs)**: Mapped to `URL_xxx`.
10. **Social Security numbers**: Mapped to `SSN_xxx`.
11. **Internet Protocol (IP) addresses**: Mapped to `IP_xxx`.
12. **Medical record numbers**: Mapped to `MRN_xxx`.
13. **Biometric identifiers**: Mapped to `BIOMETRIC_xxx`.
14. **Health plan beneficiary numbers**: Mapped to `PLAN_xxx`.
15. **Full-face photographs**: N/A (Text-based proxy only).
16. **Account numbers**: Mapped to `ACCOUNT_xxx`.
17. **Any other unique identifying number**: Mapped to `ID_xxx`.
18. **Certificate/license numbers**: Mapped to `LICENSE_xxx`.

## Vault Consistency

The Vault guarantees that the same Safe Harbor identifier appearing multiple times in the same session receives the exact same token, preserving the structural integrity of the clinical note for the LLM while achieving 100% anonymization of explicit identifiers.
