"""
FAISS Vector Store wrapper for semantic search and RAG functionality.
Handles document embeddings, storage, and similarity search.
"""

import os
from pathlib import Path
from typing import List, Optional, Tuple

import faiss
import numpy as np
from langchain_core.documents import Document


class FAISSVectorStore:
    """
    FAISS-based vector store for efficient similarity search.
    Stores embeddings and document metadata for RAG operations.
    """

    def __init__(self, embedding_dim: int = 384, store_path: Optional[str] = None):
        """
        Initialize FAISS vector store.

        Args:
            embedding_dim: Dimension of embeddings (default 384 for sentence-transformers)
            store_path: Path to save/load FAISS index (optional)
        """
        self.embedding_dim = embedding_dim
        self.store_path = Path(store_path) if store_path else None
        self.index = faiss.IndexFlatL2(embedding_dim)
        self.documents: List[Document] = []
        self.embedding_to_doc_id = {}  # Map embedding index to document ID

    def add_documents(
        self,
        documents: List[Document],
        embeddings: np.ndarray
    ) -> None:
        """
        Add documents and their embeddings to the vector store.

        Args:
            documents: List of Document objects with content and metadata
            embeddings: NumPy array of shape (num_docs, embedding_dim)

        Raises:
            ValueError: If embeddings dimension doesn't match store dimension
            ValueError: If embeddings and documents count mismatch
        """
        if embeddings.shape[1] != self.embedding_dim:
            raise ValueError(
                f"Embedding dimension {embeddings.shape[1]} "
                f"doesn't match store dimension {self.embedding_dim}"
            )

        if len(embeddings) != len(documents):
            raise ValueError(
                f"Number of embeddings ({len(embeddings)}) "
                f"doesn't match number of documents ({len(documents)})"
            )

        # Add to FAISS index
        embeddings_float32 = embeddings.astype(np.float32)
        self.index.add(embeddings_float32)

        # Store documents and create mapping
        current_size = len(self.documents)
        for i, doc in enumerate(documents):
            doc_id = f"doc_{current_size + i}"
            self.documents.append(doc)
            self.embedding_to_doc_id[current_size + i] = doc_id

    def search(
        self,
        query_embedding: np.ndarray,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Search for similar documents using embedding similarity.

        Args:
            query_embedding: Embedding of the query (shape: (1, embedding_dim))
            k: Number of results to return

        Returns:
            List of (Document, similarity_score) tuples sorted by relevance
        """
        if query_embedding.shape[0] != 1:
            query_embedding = query_embedding.reshape(1, -1)

        query_embedding_float32 = query_embedding.astype(np.float32)

        # FAISS search (returns distances and indices)
        distances, indices = self.index.search(query_embedding_float32, k)

        results = []
        for distance, idx in zip(distances[0], indices[0]):
            if idx == -1:  # Invalid result
                continue

            if idx < len(self.documents):
                doc = self.documents[idx]
                # L2 distance -> similarity (inverse relationship)
                similarity = 1 / (1 + distance)
                results.append((doc, float(similarity)))

        return results

    def save(self) -> None:
        """
        Save vector store to disk.

        Raises:
            ValueError: If store_path not set
        """
        if not self.store_path:
            raise ValueError("store_path not set. Cannot save vector store.")

        self.store_path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, str(self.store_path / "index.faiss"))

        # Save documents and metadata as pickle for now (can use JSON later)
        import pickle

        metadata = {
            "documents": self.documents,
            "embedding_to_doc_id": self.embedding_to_doc_id,
            "embedding_dim": self.embedding_dim,
        }
        with open(self.store_path / "metadata.pkl", "wb") as f:
            pickle.dump(metadata, f)

    def load(self) -> None:
        """
        Load vector store from disk.

        Raises:
            ValueError: If store_path not set
            FileNotFoundError: If stored files not found
        """
        if not self.store_path:
            raise ValueError("store_path not set. Cannot load vector store.")

        if not self.store_path.exists():
            raise FileNotFoundError(f"Vector store not found at {self.store_path}")

        # Load FAISS index
        self.index = faiss.read_index(str(self.store_path / "index.faiss"))

        # Load metadata
        import pickle

        with open(self.store_path / "metadata.pkl", "rb") as f:
            metadata = pickle.load(f)
            self.documents = metadata["documents"]
            self.embedding_to_doc_id = metadata["embedding_to_doc_id"]
            self.embedding_dim = metadata["embedding_dim"]

    def get_size(self) -> int:
        """
        Get number of documents stored in vector store.

        Returns:
            Number of documents
        """
        return len(self.documents)

    def clear(self) -> None:
        """Clear all documents and embeddings from the vector store."""
        self.index = faiss.IndexFlatL2(self.embedding_dim)
        self.documents = []
        self.embedding_to_doc_id = {}
