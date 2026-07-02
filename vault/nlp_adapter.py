import logging
from typing import Any, Dict, List, Optional
from .token_store import TokenStore

logger = logging.getLogger(__name__)

class NLPAdapter:
    """
    Adapter that connects NLP extraction outputs with the Vault engine.
    Filters entities by confidence and maps them to tokens.
    """
    
    def __init__(self, token_store: TokenStore, default_confidence_threshold: float = 0.7):
        self.token_store = token_store
        self.default_threshold = default_confidence_threshold

    def process_entities(self, session_id: str, nlp_results: List[Dict[str, Any]], threshold: Optional[float] = None) -> List[Dict[str, Any]]:
        """
        Takes raw NLP results and returns tokenized entities.
        
        Expected input format:
        [
            {"text": "John Smith", "type": "PERSON", "confidence": 0.95},
            {"text": "Dr Adams", "type": "DOCTOR", "confidence": 0.88}
        ]
        
        Returns:
        [
            {"text": "John Smith", "token": "PERSON_001", "type": "PERSON"},
            {"text": "Dr Adams", "token": "DOCTOR_001", "type": "DOCTOR"}
        ]
        """
        min_confidence = threshold if threshold is not None else self.default_threshold
        processed_entities = []

        for entity in nlp_results:
            text = entity.get("text")
            entity_type = entity.get("type", "UNKNOWN")
            confidence = entity.get("confidence", 1.0) # Default to 1.0 if not provided

            if not text:
                logger.warning("Skipping entity without text.")
                continue

            if confidence < min_confidence:
                logger.debug(f"Skipping entity '{text}' due to low confidence ({confidence} < {min_confidence}).")
                continue

            try:
                token = self.token_store.get_or_create_token(session_id, entity_type, text)
                processed_entities.append({
                    "text": text,
                    "token": token,
                    "type": entity_type
                })
            except Exception as e:
                logger.error("Failed to process entity '%s': %s", text, e)
                # Skip this entity rather than aborting the entire batch.
                # A single tokenisation failure should not block the rest of
                # the redaction pass; the entity will simply remain unredacted.
                continue
                
        return processed_entities
