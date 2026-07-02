
# 🏥 HealthTech — Automated PHI/PII Redaction Pipeline for LLMs

A secure, privacy-first proxy dashboard and API pipeline that enables healthcare professionals to safely use external Large Language Models (like Gemini, Claude, or GPT) without violating HIPAA or leaking protected patient data.

---

## 🚨 The Core Problem
Healthcare professionals spend hours typing clinical notes and summarizing records. Naturally, they want to leverage AI tools (like ChatGPT or Gemini) to write patient discharge summaries or structure medical records. 

However, **copying and pasting raw clinical notes into external AI APIs is a direct HIPAA violation.** Once a patient's Name, Date of Birth, Aadhaar/SSN, or Phone Number leaves the hospital's network boundary, that data is exposed and cannot be recalled. 

Because of this risk, hospitals are forced to block access to modern generative AI, hurting clinical productivity.

---

## ✅ Our Solution
Our application acts as a secure **privacy proxy** between the clinician and the external AI API:
1. **Intercepts:** The doctor pastes a note into our dashboard.
2. **Redacts:** Our backend scans the text, identifies all Protected Health Information (PHI) and Personally Identifiable Information (PII), and swaps them with secure, reversible placeholders (e.g., `Rahul Sharma` ➔ `[Patient A]`).
3. **Stores:** The mapping of placeholders to original values is stored in a temporary, memory-based vault.
4. **Queries AI:** The cleaned, safe note is forwarded to the LLM (e.g., Gemini).
5. **Restores:** The LLM's response comes back using the placeholder tokens. The proxy automatically swaps the real details back in.
6. **Returns:** The doctor sees a completed summary containing the patient's real information, but **the external AI never saw a single piece of sensitive data.**

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURE HOSPITAL BOUNDARY                     │
│                                                                 │
│  1. Doctor submits note                                         │
│         ↓                                                       │
│  2. Redaction Engine  ──→  Regex rules + NLP entity detection   │
│         ↓                                                       │
│  3. Token Vault  ──→  stores  "Patient A" ↔ "Rahul Sharma"      │
│         ↓                                                       │
│  4. Clean note sent  ──────────────────────────────────────►   │  External AI
│                                                           ◄───  │  (Gemini API)
│  5. AI responds with placeholders only                          │
│         ↓                                                       │
│  6. Vault restores details ──→ Doctor sees final summary        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technical Approach & How it Works

### 1. Hybrid Scanner (Regex + NLP)
To achieve high accuracy and catch all 18 HIPAA-defined identifiers, we combine two engines:
*   **Regex Engine (Rules-based):** Highly optimized patterns designed to catch structured identifiers with 100% precision. This includes Indian Aadhaar numbers, US Social Security Numbers (SSNs), phone numbers (multiple US and Indian formats), email addresses, Medical Record Numbers (MRNs), postal PIN/ZIP codes, IP addresses, URLs, insurance plan codes, and medical licenses.
*   **NLP Engine (Presidio + spaCy):** Uses Named Entity Recognition (NER) to understand sentence context and identify unstructured values (like patient names, clinic names, and geographical locations) that cannot be parsed by regex alone.

### 2. Overlap & Conflict Resolution
Because we run two scanners in parallel, they will sometimes target the same words (e.g., a phone number detected by regex might also be flagged as an organization by the NLP). We built a priority-based overlap resolver that ranks findings by specificity and span length. It discards conflicting matches and applies the most accurate tag, avoiding messy double-redactions.

### 3. Secure Ephemeral Vault (Redis + TTL)
The proxy needs to store the token mappings (e.g., `Patient A` = `Rahul Sharma`) so it can restore them later. 
*   To ensure security, these mappings are stored in a **Redis** instance.
*   Every mapping key is configured with a **30-minute Time-To-Live (TTL)**. After 30 minutes, the mapping keys expire automatically and are permanently wiped from memory.
*   **Failover/Availability:** If Redis is down or unavailable, the backend automatically switches to an in-memory `fakeredis` database so clinical workflows are never disrupted.

---

## 📂 Project Structure

```
HealthTech_Automated-PHI-PII-Redaction-Pipeline-for-LLMs/
│
├── backend/                # Flask web server and routing API
│   ├── routes/
│   │   └── proxy.py        # Core API endpoints (/redact, /ask, /restore, /sessions)
│   ├── app.py              # Application entry point (serves API & static frontend)
│   └── requirements.txt    # Python backend package dependencies
│
├── frontend/               # Single-page clinical dashboard
│   ├── index.html          # HTML app layout
│   ├── css/styles.css      # Dark-mode dashboard theme
│   └── js/
│       ├── app.js          # App lifecycle & state management
│       ├── redaction.js    # Client-side validation mirror
│       └── ui.js           # View swapping & event handlers
│
├── regex_pipeline/         # Core rules-based redaction engine
│   ├── regex_redact.py     # Main pattern matching logic
│   ├── batch_scan.py       # Batch scanner for testing notes
│   └── sample_notes.txt    # 15 synthetic clinical test records
│
├── nlp/                    # Context-aware NLP engine
│   └── presidio_scanner.py # Microsoft Presidio + spaCy NER handler
│
├── vault/                  # Pseudonymization vault client
│   └── vault.py            # Redis mapping client with TTL management
│
└── tests/                  # 56 automated unit tests
```

---

## 🚀 How to Run the Project

### Option A: Run via Docker Compose (Recommended)
This compiles and starts the Flask server, downloads the spaCy NLP models, and boots up a local Redis container automatically.
```bash
# 1. Start the services
docker-compose up --build -d

# 2. View server logs
docker-compose logs -f backend

# 3. Open your browser to:
http://localhost:5001
```

### Option B: Run Natively (Local Virtual Environment)
If you want to run it directly inside your local python directory without Docker:
```bash
# 1. Start a Redis container for the Vault storage (or start a local Redis service)
docker run -d --name healthtech-redis -p 6379:6379 redis:7-alpine

# 2. Activate the virtual environment
source .venv/bin/activate

# 3. Install packages and download the NLP spaCy model
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm

# 4. Start the Flask application
python backend/app.py

# 5. Open your browser to:
http://localhost:5001
```
*(Note: If the Redis database is not running, the application will automatically fall back to an in-memory `fakeredis` database without crashing).*

---

## 🧪 Testing & Code Verification

We wrote a complete test suite to verify regex rules, NLP detection accuracy, overlap resolution, and session-clearing behaviors.

```bash
# Activate your virtual environment
source .venv/bin/activate

# Run all 56 automated unit tests
pytest tests/ -v
```

### Terminal CLI Verification
If you want to test and show the pipeline's performance directly inside your terminal shell instead of using the frontend dashboard:

*   **Test the Regex Engine Standalone:**
    ```bash
    python regex_pipeline/regex_redact.py
    ```
*   **Batch-Scan 15 clinical records with side-by-side comparisons:**
    ```bash
    python regex_pipeline/batch_scan.py --verbose
    ```
*   **Test the Presidio NLP entity recognizer:**
    ```bash
    python nlp/presidio_scanner.py
    ```

---

## 👥 Intern Team & Roles
This project was designed and built during our 30-day Cybersecurity & Healthcare AI internship:

*   **Mantra (Team Lead):** Core Regex Redaction Engine & Overlap Resolution client (`regex_pipeline/`)
*   **Tirth:** Presidio + spaCy NLP NER Pipeline client (`nlp/`)
*   **Jash:** Pseudonymization client & TTL Redis Vault client (`vault/`)
*   **Rohit:** Flask API routes, logging infrastructure, and frontend UI Integration (`backend/` & `frontend/`)
