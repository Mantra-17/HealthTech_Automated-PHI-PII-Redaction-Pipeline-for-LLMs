# Report Evidence Summary

This document summarizes the mapping between key chapters in the report and the actual implementation files in the repository.

| Chapter | Subsection | Code File Path | Implementation Feature / Line Numbers |
| :--- | :--- | :--- | :--- |
| **Chapter 4** | 4.3 Database Design | `vault/token_store.py` | Redis key scopes, counters, and Fernet encryption/decryption hooks. |
| **Chapter 5** | 5.2 Backend Routing | `backend/routes/proxy.py` | Flask endpoints, route blueprints, and dynamic fallback. |
| **Chapter 5** | 5.3 Token Storage | `vault/token_store.py` | Fernet ciphers AES-128 data encryptions. |
| **Chapter 5** | 5.4 NLP Engine | `nlp/presidio_scanner.py` | Microsoft Presidio wrapper with custom clinical anonymizers. |
| **Chapter 6** | 6.2 Regex Scans | `regex_pipeline/regex_redact.py` | 13 pattern definitions and overlap matrix priorities. |
| **Chapter 6** | 6.5 File Auditor | `backend/logger.py` | File-rotating JSON log writers. |
| **Chapter 7** | 7.3 Pytest Suite | `tests/` | 65 automated assertion validations. |
| **Chapter 9** | 9.4 Rate Limiter | `backend/routes/proxy.py` | IP track list sliding windows rate-limit filter. |
