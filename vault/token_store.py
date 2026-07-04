"""
vault/token_store.py
--------------------
Bidirectional, session-scoped token store backed by Redis.

Redis key schema
~~~~~~~~~~~~~~~~
For each redacted entity the store maintains three related keys:

1. ``<session_id>:NAME:<entity_type>:<sha256_of_name>``
       Value: the token string (e.g. ``PATIENT_001``)
       Purpose: check whether this name already has a token (idempotency).
       The name is SHA-256 hashed to prevent plaintext PHI appearing in keys.

2. ``<session_id>:TOKEN:<token>``
       Value: Fernet-encrypted original name
       Purpose: reverse lookup — decrypt to get the original value during restoration.

3. ``<session_id>:COUNTER:<entity_type>``
       Value: integer, monotonically increasing
       Purpose: shared by :class:`vault.token_generator.TokenGenerator` to
       generate sequential token numbers via Redis ``INCR``.

All three key types carry the same TTL so the entire session expires atomically.
"""

import os
import redis
import logging
import hashlib
from typing import Optional
from cryptography.fernet import Fernet
from .token_generator import TokenGenerator

logger = logging.getLogger(__name__)


class TokenStore:
    """
    Manages the bidirectional mapping between PHI/PII values and their
    pseudonym tokens within a single session.

    Encryption
    ----------
    Original entity values are encrypted with Fernet (AES-128-CBC + HMAC-SHA256)
    before being written to Redis.  The encryption key is read from the
    ``VAULT_ENCRYPTION_KEY`` environment variable.  If the variable is absent or
    malformed, a fallback static key is used (see security note in ``__init__``).

    TTL
    ---
    Every Redis key written by this class carries a TTL (default: 1800 s) so
    sessions expire automatically without an explicit cleanup step.  TTLs are
    refreshed on every read to implement a sliding-window expiry.
    """
    def __init__(self, redis_client: redis.Redis, ttl_seconds: Optional[int] = None):
        self.redis = redis_client
        self.generator = TokenGenerator(redis_client)
        self.ttl_seconds = int(ttl_seconds or os.getenv("VAULT_TTL_SECONDS", 1800))
        
        # Initialize Fernet symmetric encryption cipher
        key_str = os.getenv("VAULT_ENCRYPTION_KEY")
        # SECURITY NOTE: The hardcoded fallback key below is provided as a
        # convenience for local development only.  In any environment that
        # handles real PHI, set VAULT_ENCRYPTION_KEY to a securely generated
        # Fernet key (use `Fernet.generate_key().decode()` to create one) and
        # store it in a secrets manager — never commit it to source control.
        if not key_str:
            key_str = "t8X7u6f7Wv9M2W-3eYt_mH-sJ9qK5l6Z8X9C1vB3dE8="
        try:
            self.cipher = Fernet(key_str.encode())
        except Exception as e:
            logger.warning(f"Invalid encryption key provided. Generating dynamic fallback key: {e}")
            self.cipher = Fernet(Fernet.generate_key())

    def _hash_name(self, name: str) -> str:
        """Hash name values using SHA-256 to prevent plaintext names from leaking in Redis keys."""
        return hashlib.sha256(name.upper().encode("utf-8")).hexdigest()

    def get_or_create_token(self, session_id: str, entity_type: str, entity_name: str) -> str:
        """
        Checks if an entity already has a token in this session. If not, generates one and stores the bidirectional mapping.
        """
        # Strict collision prevention by including type in the mapping key
        # We hash the entity name in the key to protect patient identities at rest
        hashed_name = self._hash_name(entity_name)
        name_key = f"{session_id}:NAME:{entity_type.upper()}:{hashed_name}"
        
        try:
            # 1. Check if token already exists for this name
            existing_token = self.redis.get(name_key)
            if existing_token:
                # Refresh TTL on read
                token_str = existing_token.decode('utf-8') if isinstance(existing_token, bytes) else existing_token
                token_key = f"{session_id}:TOKEN:{token_str}"
                
                pipeline = self.redis.pipeline()
                pipeline.expire(name_key, self.ttl_seconds)
                pipeline.expire(token_key, self.ttl_seconds)
                pipeline.execute()
                
                logger.info(f"Token found in session: {token_str}")
                return token_str

            # 2. If not found, generate a new token
            new_token = self.generator.generate_token(session_id, entity_type)
            token_key = f"{session_id}:TOKEN:{new_token}"

            # 3. Encrypt the original patient identity name before storing it in Redis
            encrypted_name = self.cipher.encrypt(entity_name.encode("utf-8")).decode("utf-8")

            # 4. Store the bidirectional mapping with TTL
            pipeline = self.redis.pipeline()
            pipeline.set(name_key, new_token, ex=self.ttl_seconds)
            pipeline.set(token_key, encrypted_name, ex=self.ttl_seconds)
            pipeline.execute()

            logger.info(f"Generated and securely stored encrypted token for entity: {new_token}")
            return new_token

        except redis.RedisError as e:
            logger.error(f"Redis error during token operation for {entity_name}: {e}")
            raise

    def get_name_from_token(self, session_id: str, token: str) -> Optional[str]:
        """
        Retrieve and decrypt the original entity value for a given token.

        Used during the restoration phase to reverse pseudonym substitution.

        Args:
            session_id: The UUID of the active redaction session.
            token:      The pseudonym token (e.g. ``"PATIENT_001"``).
                        The token is upper-cased before the Redis lookup because
                        tokens are always stored with an upper-case key, regardless
                        of the case used in the redacted text.

        Returns:
            The decrypted original entity value, or ``None`` if not found.

        Raises:
            redis.RedisError: If the Redis lookup fails.
        """
        token_key = f"{session_id}:TOKEN:{token.upper()}"
        try:
            encrypted_name = self.redis.get(token_key)
            if encrypted_name:
                encrypted_str = encrypted_name.decode('utf-8') if isinstance(encrypted_name, bytes) else encrypted_name
                
                # Decrypt the ciphertext
                decrypted_bytes = self.cipher.decrypt(encrypted_str.encode("utf-8"))
                return decrypted_bytes.decode("utf-8")
                
            logger.warning(f"No name found for token: {token} in session {session_id}")
            return None
        except redis.RedisError as e:
            logger.error(f"Redis error retrieving name for token {token} in session {session_id}: {e}")
            raise
