import json
import logging
from datetime import datetime
from pathlib import Path

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Include extra attributes if they are present in the log record
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        if hasattr(record, "event_type"):
            log_data["event_type"] = record.event_type
        if hasattr(record, "latency_ms"):
            log_data["latency_ms"] = record.latency_ms
            
        # Include details on exceptions if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)

def setup_logging():
    # Setup root logger to output structured JSON to stdout
    root = logging.getLogger()
    
    # Remove existing handlers to avoid duplicate output formatting
    for handler in root.handlers[:]:
        root.removeHandler(handler)
        
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    
    # Silence noisy dependencies while keeping core events
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("spacy").setLevel(logging.WARNING)


class FileAuditLogger:
    """
    Writes HIPAA-safe structured audit logs to logs/audit.log.

    CRITICAL: This logger must NEVER log:
    - original_text or any part of patient note
    - redacted_text
    - token values or mappings
    - patient names, identifiers, or any PHI

    Only safe metadata is logged: counts, types, timing, session IDs.
    """

    def __init__(self, log_path: str = "logs/audit.log") -> None:
        """Initialize the logger and ensure log directory exists."""
        self.log_path = Path(log_path)
        # Create directory recursively
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._rotate_if_needed()

    def _rotate_if_needed(self) -> None:
        """Rotate audit.log if size exceeds 1MB limit (1,048,576 bytes)."""
        if self.log_path.exists() and self.log_path.stat().st_size > 1048576:
            rotated_path = self.log_path.with_name("audit.log.1")
            try:
                # Rename/rollover file, overwriting existing rotated file
                self.log_path.replace(rotated_path)
            except Exception:
                pass

    def _write_log(self, data: dict) -> None:
        """Helper to rotate if needed, and write a single JSON line to the log."""
        self._rotate_if_needed()
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data) + "\n")

    def log_redaction(
        self,
        request_id: str,
        session_id: str,
        phi_types: list[str],
        phi_count: int,
        text_length: int,
        processing_time_ms: float,
        regex_found: int,
        nlp_found: int,
        duplicates_removed: int,
        status: str = "success",
    ) -> None:
        """
        Record a secure de-identification request log.

        Never records actual clinical text or identifiers to ensure HIPAA compliance.
        """
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id,
            "event": "redaction_completed",
            "session_id": session_id,
            "phi_types_found": phi_types,
            "phi_count": phi_count,
            "text_length_chars": text_length,
            "processing_time_ms": round(processing_time_ms, 1),
            "regex_found": regex_found,
            "nlp_found": nlp_found,
            "duplicates_removed": duplicates_removed,
            "status": status,
        }
        self._write_log(log_data)

    def log_error(self, request_id: str, error_message: str) -> None:
        """Record an operation failure event log."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "request_id": request_id,
            "event": "redaction_error",
            "error": error_message,
            "status": "error",
        }
        self._write_log(log_data)

    def log_session_cleared(self, session_id: str) -> None:
        """Record a session token vault clearance event log."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": "session_cleared",
            "session_id": session_id,
        }
        self._write_log(log_data)

    def get_recent_logs(self, n: int = 50) -> list[dict]:
        """Read and parse the last n lines from audit.log."""
        if not self.log_path.exists():
            return []

        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            recent_lines = lines[-n:]
            parsed_logs = []
            for line in recent_lines:
                line_str = line.strip()
                if line_str:
                    try:
                        parsed_logs.append(json.loads(line_str))
                    except Exception:
                        pass
            return parsed_logs
        except Exception:
            return []

    def get_aggregate_stats(self) -> dict:
        """Compute aggregate statistics from all audit.log events."""
        if not self.log_path.exists():
            return {
                "total_requests": 0,
                "total_phi_redacted": 0,
                "avg_phi_per_request": 0.0,
                "avg_processing_time_ms": 0.0,
                "phi_type_breakdown": {},
                "error_count": 0,
                "error_rate_percent": 0.0,
                "most_common_phi_type": "None",
                "log_file_size_kb": 0.0,
            }

        try:
            with open(self.log_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception:
            lines = []

        completed_requests = 0
        error_count = 0
        total_phi_redacted = 0
        total_processing_time = 0.0
        phi_type_breakdown: dict[str, int] = {}

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue
            try:
                log_data = json.loads(line_str)
                event = log_data.get("event")
                if event == "redaction_completed":
                    completed_requests += 1
                    total_phi_redacted += log_data.get("phi_count", 0)
                    total_processing_time += log_data.get("processing_time_ms", 0.0)

                    # Build counts breakdown
                    for t in log_data.get("phi_types_found", []):
                        phi_type_breakdown[t] = phi_type_breakdown.get(t, 0) + 1
                elif event == "redaction_error":
                    error_count += 1
            except Exception:
                pass

        total_requests = completed_requests + error_count
        avg_phi = (
            (total_phi_redacted / completed_requests) if completed_requests > 0 else 0.0
        )
        avg_time = (
            (total_processing_time / completed_requests) if completed_requests > 0 else 0.0
        )
        error_pct = (error_count / total_requests * 100.0) if total_requests > 0 else 0.0

        most_common = "None"
        if phi_type_breakdown:
            most_common = max(phi_type_breakdown, key=phi_type_breakdown.get)

        try:
            file_size_kb = self.log_path.stat().st_size / 1024.0
        except Exception:
            file_size_kb = 0.0

        return {
            "total_requests": total_requests,
            "total_phi_redacted": total_phi_redacted,
            "avg_phi_per_request": round(avg_phi, 1),
            "avg_processing_time_ms": round(avg_time, 1),
            "phi_type_breakdown": phi_type_breakdown,
            "error_count": error_count,
            "error_rate_percent": round(error_pct, 1),
            "most_common_phi_type": most_common,
            "log_file_size_kb": round(file_size_kb, 2),
        }

