"""
Embedding generation using HuggingFace models.
No API key required - uses local models.
"""

import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings


class EmbeddingProvider:
    """
    Wrapper for HuggingFace embeddings.
    Uses free, no-API-key-required sentence transformer models.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embeddings provider.

        Args:
            model_name: HuggingFace model identifier.
                Default "all-MiniLM-L6-v2" produces 384-dim embeddings.
                Other options:
                - "all-mpnet-base-v2": 768-dim, better quality
                - "paraphrase-MiniLM-L6-v2": 384-dim, faster
        """
        self.embeddings = HuggingFaceEmbeddings(model_name=model_name)

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query string.

        Args:
            query: Query text to embed

        Returns:
            NumPy array of shape (embedding_dim,)
        """
        return np.array(self.embeddings.embed_query(query))

    def embed_documents(self, documents: list[str]) -> np.ndarray:
        """
        Embed multiple documents.

        Args:
            documents: List of document texts

        Returns:
            NumPy array of shape (num_docs, embedding_dim)
        """
        return np.array(self.embeddings.embed_documents(documents))

    def get_embedding_dimension(self) -> int:
        """
        Get embedding dimension.

        Returns:
            Dimension of embeddings produced by this model
        """
        # Embed a dummy string to get dimension
        dummy_embedding = self.embed_query("dummy")
        return len(dummy_embedding)


# Lazy-loaded embeddings instance
_embeddings_instance = None


def get_embeddings() -> EmbeddingProvider:
    """
    Get or create embeddings provider (singleton pattern).

    Returns:
        EmbeddingProvider: Embeddings provider instance
    """
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = EmbeddingProvider()
    return _embeddings_instance
