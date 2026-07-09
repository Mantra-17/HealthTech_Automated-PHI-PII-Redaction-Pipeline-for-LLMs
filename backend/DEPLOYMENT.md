# Deployment Guide — PHI Redaction Pipeline

## Quick Start (Local)

### Prerequisites
- Python 3.11+
- Redis (running on localhost:6379)
- spaCy model installed

### Step 1: Clone and setup
```bash
git clone https://github.com/Mantra-17/HealthTech_Automated-PHI-PII-Redaction-Pipeline-for-LLMs.git
cd HealthTech_Automated-PHI-PII-Redaction-Pipeline-for-LLMs
```

### Step 2: Create virtual environment
```bash
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
# OR
.venv\Scripts\activate     # Windows
```

### Step 3: Install dependencies
```bash
pip install -r backend/requirements.txt
python -m spacy download en_core_web_sm
```

### Step 4: Setup environment
```bash
cp backend/env.example backend/.env
# Edit .env and add your AI API key
```

### Step 5: Start Redis
```bash
# Mac (homebrew)
brew services start redis

# Linux
sudo systemctl start redis

# Windows (WSL)
sudo service redis-server start
```

### Step 6: Run the server
```bash
cd backend
python app.py
```

Server starts at: http://localhost:5001

---

## Testing All Endpoints

### Health check
```bash
curl http://localhost:5001/health
```

### Validate text (fast pre-check)
```bash
curl -X POST http://localhost:5001/api/validate \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient John Smith, DOB: 14/02/1985, Phone: 9876543210"}'
```

### Full redaction
```bash
curl -X POST http://localhost:5001/api/redact \
  -H "Content-Type: application/json" \
  -d '{"text": "Patient John Smith, DOB: 14/02/1985, Phone: 9876543210, Email: john@gmail.com"}'
```

### View audit log
```bash
curl http://localhost:5001/api/audit-log?limit=10
```

### View statistics
```bash
curl http://localhost:5001/api/stats
```

### Ask AI (after redaction)
```bash
curl -X POST http://localhost:5001/api/ask \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "clean_text": "PATIENT_001 has chest pain"}'
```

---

## Troubleshooting

### Redis not connecting
The app automatically falls back to fakeredis (in-memory) if Redis is unavailable.
You'll see: `[WARNING] Vault Proxy: Redis unavailable, falling back to fakeredis`
This is fine for development. Install Redis for production.

### NLP model missing
```bash
python -m spacy download en_core_web_sm
```

### Port already in use
Change FLASK_PORT in .env file.

### Import errors
Make sure you're running from the backend/ directory:
```bash
cd backend && python app.py
```
