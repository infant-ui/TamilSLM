# services/retrieval-service/app/ingestion/chunk_validator.py
import re
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger("ingestion.chunk_validator")

class ChunkValidator:
    def __init__(self, min_chars: int = 50, max_chars: int = 4000):
        self.min_chars = min_chars
        self.max_chars = max_chars

    def validate_chunk(self, text: str, metadata: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validates chunk quality. Returns (is_valid, reason).
        """
        if not text:
            return False, "Empty text"
            
        clean_text = text.strip()
        length = len(clean_text)
        
        # 1. Size constraints
        if length < self.min_chars:
            return False, f"Chunk text is too short ({length} chars, min threshold is {self.min_chars})"
            
        if length > self.max_chars:
            return False, f"Chunk text is too long ({length} chars, max threshold is {self.max_chars})"

        # 2. Math Formula Syntax Check
        # Check matching brackets for standard LaTeX math blocks
        dollar_count = clean_text.count("$")
        if dollar_count % 2 != 0:
            return False, "Unbalanced LaTeX math blocks ($ count is odd)"

        bracket_pairs = [("{", "}"), ("[", "]"), ("(", ")")]
        for open_b, close_b in bracket_pairs:
            # Count inside math blocks if present
            if open_b in clean_text or close_b in clean_text:
                if clean_text.count(open_b) != clean_text.count(close_b):
                    # Log as warning rather than rejection, as text equations might have normal unmatched parentheses
                    logger.debug(f"Warning: Unbalanced parentheses count for '{open_b}' and '{close_b}' in chunk.")

        # 3. Metadata Verification
        required_metadata = ["class_level", "medium", "subject", "filename"]
        for key in required_metadata:
            if key not in metadata or metadata[key] is None:
                return False, f"Missing required metadata field: '{key}'"

        # 4. Unicode Character Validity
        # Check for excessive consecutive non-spaced character sequences (indicator of OCR gluing failures)
        words = clean_text.split()
        if words:
            longest_word = max(len(w) for w in words)
            # In English and Tamil, words are rarely longer than 35 characters
            if longest_word > 45:
                return False, f"Contains extremely long word ({longest_word} characters) which points to OCR character gluing error"

        return True, "Valid"
