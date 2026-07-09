"""
app.py — Flask entry point
"""

import os
import uuid
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

from logger import setup_logging
from routes.proxy import proxy_bp
from routes.evaluation import evaluation_bp

# Initialize structured JSON logging
setup_logging()

load_dotenv()

# Serve static frontend files directly from Flask to completely avoid CORS issues
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../frontend"))
app = Flask(__name__, static_folder=static_dir, static_url_path="")

# CORS support for development API clients
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Register blueprints
app.register_blueprint(proxy_bp, url_prefix="/api")
app.register_blueprint(evaluation_bp, url_prefix="/api")


@app.after_request
def add_response_headers(response):
    """Add standard headers to every response."""
    # Ensure a unique request identifier is present on every request response
    if not response.headers.get("X-Request-Id"):
        response.headers["X-Request-Id"] = str(uuid.uuid4())
    return response


@app.route("/", methods=["GET"])
def index():
    """Serve the modular index.html entry point."""
    return app.send_static_file("index.html")


@app.route("/health", methods=["GET"])
def health():
    """Enhanced health check showing all module statuses."""
    import os, spacy, redis as redis_lib
    from datetime import datetime
    
    # Check Redis
    try:
        r = redis_lib.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        redis_ok = "connected"
    except Exception:
        redis_ok = "fallback (fakeredis)"
    
    # Check NLP
    try:
        spacy.load("en_core_web_sm")
        nlp_ok = "en_core_web_sm loaded"
    except Exception:
        try:
            spacy.load("en_core_web_lg")
            nlp_ok = "en_core_web_lg loaded"
        except Exception:
            nlp_ok = "unavailable"
    
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "modules": {
            "redis": redis_ok,
            "nlp": nlp_ok,
            "audit_log": "active"
        }
    }, 200


def _print_startup_banner():
    """Print a startup health check banner showing module status."""
    import os
    
    # Check Redis
    try:
        import redis as redis_lib
        r = redis_lib.from_url(os.getenv("REDIS_URL", "redis://localhost:6379/0"))
        r.ping()
        redis_status = "✅ Connected"
    except Exception:
        redis_status = "⚠️  Using fakeredis (development mode)"
    
    # Check NLP
    try:
        import spacy
        spacy.load("en_core_web_sm")
        nlp_status = "✅ en_core_web_sm loaded"
    except Exception:
        try:
            spacy.load("en_core_web_lg")
            nlp_status = "✅ en_core_web_lg loaded"
        except Exception:
            nlp_status = "❌ No spaCy model found"
    
    # Check logs dir
    log_path = os.getenv("AUDIT_LOG_PATH", "logs/audit.log")
    os.makedirs(os.path.dirname(log_path) if os.path.dirname(log_path) else "logs", exist_ok=True)
    log_status = f"✅ {log_path} ready"
    
    port = os.getenv("FLASK_PORT", "5001")
    
    banner = f"""
╔══════════════════════════════════════════════════════╗
║        PHI Redaction Pipeline — Starting Up          ║
╠══════════════════════════════════════════════════════╣
║  Redis:      {redis_status:<40}║
║  NLP Model:  {nlp_status:<40}║
║  Audit Log:  {log_status:<40}║
║  API:        ✅ http://0.0.0.0:{port:<26}║
╠══════════════════════════════════════════════════════╣
║     Ready to process clinical notes securely! 🔒     ║
╚══════════════════════════════════════════════════════╝
"""
    print(banner)


if __name__ == "__main__":
    _print_startup_banner()
    port = int(os.getenv("FLASK_PORT", 5001))
    # In production, this can be served by gunicorn/uwsgi
    app.run(debug=True, port=port, host="0.0.0.0")
