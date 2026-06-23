# HIPAA Alignment Report

This document outlines how the HealthTech Vault Engine specifically aligns with the Health Insurance Portability and Accountability Act (HIPAA) Privacy Rule, focusing on the protection of electronic Protected Health Information (ePHI).

## Technical Safeguards

1. **Access Control**: The Vault engine isolates PHI using `session_id`. Tokens generated for one session cannot be reverse-mapped using another session's context.
2. **Data Integrity**: Redis pipelines ensure atomic operations. Tokens and mappings are never left in a partial state.
3. **Audit Controls**: All Vault operations are logged (without exposing PHI). Latency and mapping counts are tracked.
4. **Person or Entity Authentication**: (Handled by the FastAPI layer upstream, but Vault strictly requires explicit session tokens).
5. **Transmission Security**: The Redis client supports TLS (`REDIS_TLS=true`), encrypting data-in-transit between the application and the Redis datastore.

## Data Minimization & Retention

The Vault enforces a strict TTL (Time To Live) on all stored mappings. By default, mappings expire after 30 minutes, ensuring that ePHI does not persist in the temporary cache longer than necessary for the LLM proxy round-trip.

## De-identification Standard

The Vault facilitates compliance with the HIPAA Safe Harbor method by programmatically replacing sensitive identifiers with reversible pseudonyms (e.g., `PATIENT_001`) before data leaves the secure boundary.

See [Safe Harbor Mapping Document](safe_harbor_mapping.md) for detailed identifier mappings.
