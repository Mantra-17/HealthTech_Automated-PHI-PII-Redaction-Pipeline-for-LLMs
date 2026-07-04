import time
import logging
import functools
from typing import Optional, List, Dict, Any, Tuple
import redis

from .token_store import TokenStore
from .nlp_adapter import NLPAdapter
from .text_engine import TextEngine
from .exceptions import VaultError

logger = logging.getLogger(__name__)

def track_latency(func):
    """Decorator to measure execution time of Vault operations for latency tracking."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(f"Vault.{func.__name__} completed in {elapsed_ms:.2f} ms")
    return wrapper

class Vault:
    """
    High-level Vault Engine facade integrating Token Storage, NLP processing, and Text Redaction.
    Provides session-scoped, secure pseudonymization for clinical notes.
    """

    def __init__(self, redis_client: redis.Redis, ttl_seconds: Optional[int] = None):
        self.redis = redis_client
        self.token_store = TokenStore(redis_client, ttl_seconds)
        self.nlp_adapter = NLPAdapter(self.token_store)

    @track_latency
    def redact_note(self, session_id: str, text: str, nlp_entities: List[Dict[str, Any]], confidence_threshold: float = 0.7) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Redact sensitive entities in *text* and store the token map in Redis.

        Processing steps:
            1. Filter *nlp_entities* by *confidence_threshold* via :class:`NLPAdapter`.
            2. For each qualifying entity, retrieve an existing token or create a new
               one via :class:`TokenStore` (idempotent — same name → same token).
            3. Replace every occurrence of each entity text in *text* with its token.

        Args:
            session_id:           UUID that scopes all tokens to this clinical session.
            text:                 The raw clinical note containing PHI/PII.
            nlp_entities:         List of detected entities from the regex + NLP scanners.
                                  Each dict must contain ``text`` (str), ``type`` (str),
                                  and optionally ``confidence`` (float, defaults to 1.0).
            confidence_threshold: Minimum confidence score required to redact an entity.
                                  Entities below this threshold are silently skipped.

        Returns:
            A tuple of:
                redacted_text (str)        — the note with PHI replaced by tokens
                processed_entities (list)  — each dict contains ``text``, ``token``,
                                             and ``type`` for every entity that was
                                             actually redacted

        Raises:
            VaultError: If the underlying token store or text engine raises.
        """
        try:
            # 1. Process NLP entities to generate or retrieve tokens
            processed_entities = self.nlp_adapter.process_entities(session_id, nlp_entities, threshold=confidence_threshold)
            
            # 2. Perform text replacement
            redacted_text = TextEngine.redact(text, processed_entities)
            
            return redacted_text, processed_entities
        except Exception as e:
            logger.exception(f"Redaction failed for session {session_id}: {e}")
            raise VaultError(f"Failed to redact note: {str(e)}") from e

    @track_latency
    def restore_note(self, session_id: str, redacted_text: str) -> str:
        """
        Restore a redacted note back to its original form using the session token map.

        All pseudonym tokens present in *redacted_text* (matching the pattern
        ``[A-Z]+_\d+``) are looked up in Redis under the given *session_id*,
        decrypted, and substituted back into the text.

        Args:
            session_id:    UUID of the session whose token map should be used.
            redacted_text: Text containing pseudonym tokens to replace.

        Returns:
            The restored text with original PHI values reinstated.  Tokens that
            cannot be found in the session are left unchanged and a warning is
            logged for each one.

        Raises:
            VaultError: If the underlying token store or text engine raises.
        """
        try:
            restored_text = TextEngine.restore(session_id, redacted_text, self.token_store)
            return restored_text
        except Exception as e:
            logger.exception(f"Restoration failed for session {session_id}: {e}")
            raise VaultError(f"Failed to restore note: {str(e)}") from e

    def clear_session(self, session_id: str) -> int:
        """
        Delete all Vault keys for a session from Redis.

        Removes all three key types (NAME, TOKEN, COUNTER) that belong to
        *session_id* in a single ``DEL`` command.

        Args:
            session_id: UUID of the session to purge.

        Returns:
            The number of Redis keys that were deleted (0 if the session did
            not exist or had already expired).

        Raises:
            VaultError: If the Redis ``DEL`` operation fails.
        """
        pattern = f"{session_id}:*"
        try:
            keys = self.redis.keys(pattern)
            if keys:
                return self.redis.delete(*keys)
            return 0
        except redis.RedisError as e:
            logger.exception("Failed to clear session %s: %s", session_id, e)
            raise VaultError(f"Failed to clear session: {str(e)}") from e
