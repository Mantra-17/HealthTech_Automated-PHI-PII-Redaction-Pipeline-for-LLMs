# PHI Redaction Proxy — Frontend

A standalone HTML/CSS/JS dashboard demonstrating the HealthTech Automated PHI/PII Redaction Pipeline.

## Structure
```
frontend/
├── index.html        # App shell: sidebar nav + 5 views
├── css/
│   └── styles.css     # Theme + layout
└── js/
    ├── redaction.js   # Detection rules + redact()/restore() (mirrors backend redaction_engine.py)
    └── app.js          # UI wiring, vault table, audit log, simulated AI call
```

## Views
1. **New note** — paste a clinical note, run redaction, see the token map, simulate sending to an AI and getting a restored response.
2. **Pipeline** — visual walkthrough of the 6-step proxy flow.
3. **Vault sessions** — table of active token-map sessions (in-memory for this demo).
4. **Audit log** — running log of redaction/restore events.
5. **Settings** — detection categories and vault config (illustrative).

## Running locally
Just open `index.html` in a browser, or serve it:
```bash
cd frontend
python -m http.server 8080
```

## Notes
- `redaction.js` is a client-side mirror of `backend/redaction_engine.py`'s regex + name-detection rules, so the two stay structurally aligned if/when a real backend is wired in.
- The "Send to AI assistant" button currently simulates a response — swap `buildMockAIResponse()` in `app.js` for a real fetch to your proxy API.
