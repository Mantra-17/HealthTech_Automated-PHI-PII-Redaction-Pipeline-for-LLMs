"""
vault/text_engine.py
--------------------
Stateless text substitution helpers for the forward (redact) and reverse
(restore) passes of the pseudonymisation pipeline.

Both operations are exposed as static methods on :class:`TextEngine` so they
can be called without constructing an instance — keeping the Vault facade code
flat and easy to trace.
"""

import re
import logging
from typing import List, Dict
from .token_store import TokenStore

logger = logging.getLogger(__name__)

class TextEngine:
    """
    Handles safe string substitution for forward redaction and reverse restoration.
    """
    
    @staticmethod
    def redact(text: str, entities: List[Dict[str, str]]) -> str:
        """
        Replaces identified entities with their tokens in the text.
        Handles duplicates and collisions by sequentially mapping multiple occurrences.
        Sorts entities by length (descending) to avoid partial replacement of overlapping entities.
        """
        if not text or not entities:
            return text
            
        redacted_text = text
        
        # Sort by length descending to replace "John Smith" before "John"
        sorted_entities = sorted(entities, key=lambda x: len(x.get("text", "")), reverse=True)
        
        # Group tokens by their entity text to maintain order of occurrence
        text_to_tokens = {}
        for entity in sorted_entities:
            entity_text = entity.get("text")
            token = entity.get("token")
            if not entity_text or not token:
                continue
            if entity_text not in text_to_tokens:
                text_to_tokens[entity_text] = []
            text_to_tokens[entity_text].append(token)

        # Replace each occurrence with its corresponding token in order
        for entity_text, tokens in text_to_tokens.items():
            escaped_text = re.escape(entity_text)
            
            if entity_text[0].isalnum() and entity_text[-1].isalnum():
                pattern = r'\b' + escaped_text + r'\b'
            else:
                pattern = escaped_text
                
            match_index = 0

            # ``replace_match`` is a closure over ``tokens`` and ``match_index``.
            # ``re.sub`` calls it once per regex match, left-to-right.  Using
            # ``nonlocal match_index`` lets us advance through the token list so
            # each successive occurrence of the same entity text gets the next
            # token in sequence (relevant when the same name appears multiple
            # times and was assigned different tokens by the scanner).
            def replace_match(match):
                nonlocal match_index
                if match_index < len(tokens):
                    tok = tokens[match_index]
                else:
                    # More occurrences than tokens — reuse the last token.
                    tok = tokens[-1]
                match_index += 1
                return tok

            try:
                redacted_text = re.sub(pattern, replace_match, redacted_text)
            except re.error as e:
                logger.error("Regex error for '%s': %s", entity_text, e)
                # Fallback: plain string replacement when the regex cannot compile
                # (e.g. special characters in the entity text).  Unlike the regex
                # path this does not distinguish between occurrences, so every
                # occurrence receives the first available token.
                for tok in tokens:
                    redacted_text = redacted_text.replace(entity_text, tok, 1)
                
        return redacted_text

    @staticmethod
    def restore(session_id: str, redacted_text: str, token_store: TokenStore) -> str:
        """
        Reconstructs the original text by finding all tokens and replacing them with original values.
        """
        if not redacted_text:
            return redacted_text
            
        restored_text = redacted_text
        
        # Find all potential tokens in the text (e.g., PATIENT_001, DOCTOR_001)
        # Matches uppercase letters followed by underscore and digits
        token_pattern = r'\b[A-Z]+_\d+\b'
        found_tokens = list(set(re.findall(token_pattern, redacted_text)))
        
        # Sort tokens by length descending, just in case (though format is standard)
        found_tokens.sort(key=len, reverse=True)
        
        for token in found_tokens:
            original_value = token_store.get_name_from_token(session_id, token)
            if original_value:
                # Replace all occurrences of the token
                restored_text = re.sub(r'\b' + re.escape(token) + r'\b', original_value, restored_text)
            else:
                logger.warning(f"Could not restore token {token} in session {session_id}")
                
        return restored_text
