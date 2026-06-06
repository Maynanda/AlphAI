"""
Local text embeddings generator using sentence-transformers.
"""

import logging
from typing import List

logger = logging.getLogger(__name__)

# Lazy imports to save load time at startup
class LocalEmbedding:
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.model = None
        self.is_loaded = False

    def load_model(self) -> bool:
        """Loads the sentence transformer embedding model."""
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            self.is_loaded = True
            logger.info("Embedding model loaded successfully.")
            return True
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.is_loaded = False
            return False

    def embed_query(self, text: str) -> List[float]:
        """Embed a single query text."""
        if not self.is_loaded or self.model is None:
            self.load_model()
        
        # Safe fallback check
        if self.model is None:
            raise RuntimeError("SentenceTransformer model could not be loaded.")

        embedding = self.model.encode(text, normalize_embeddings=True)
        return embedding.tolist()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a batch of document texts."""
        if not self.is_loaded or self.model is None:
            self.load_model()

        if self.model is None:
            raise RuntimeError("SentenceTransformer model could not be loaded.")

        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()
