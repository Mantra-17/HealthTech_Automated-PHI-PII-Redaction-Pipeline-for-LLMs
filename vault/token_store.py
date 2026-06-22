import redis
import logging
from typing import Optional
from .token_generator import TokenGenerator

logger = logging.getLogger(__name__)

class TokenStore:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.generator = TokenGenerator(redis_client)

    def get_or_create_token(self, entity_type: str, entity_name: str) -> str:
        """
        Checks if an entity already has a token. If not, generates one and stores the bidirectional mapping.
        """
        name_key = f"NAME:{entity_type.upper()}:{entity_name.upper()}"
        
        try:
            # 1. Check if token already exists for this name
            existing_token = self.redis.get(name_key)
            if existing_token:
                logger.info(f"Token found for {entity_name}: {existing_token}")
                return existing_token

            # 2. If not found, generate a new token
            new_token = self.generator.generate_token(entity_type)
            token_key = f"TOKEN:{new_token}"

            # 3. Store the bidirectional mapping
            # We use a pipeline to ensure both keys are set atomically
            pipeline = self.redis.pipeline()
            pipeline.set(name_key, new_token)
            pipeline.set(token_key, entity_name)
            pipeline.execute()

            logger.info(f"Generated and stored new token for {entity_name}: {new_token}")
            return new_token

        except redis.RedisError as e:
            logger.error(f"Redis error during token operation for {entity_name}: {e}")
            raise

    def get_name_from_token(self, token: str) -> Optional[str]:
        """
        Retrieves the original entity name from a given token. Used for reversing pseudonymization.
        """
        token_key = f"TOKEN:{token.upper()}"
        try:
            name = self.redis.get(token_key)
            if not name:
                logger.warning(f"No name found for token: {token}")
            return name
        except redis.RedisError as e:
            logger.error(f"Redis error retrieving name for token {token}: {e}")
            raise
