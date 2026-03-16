"""
RAG (Retrieval Augmented Generation) service.
Handles document loading, chunking, and semantic retrieval.
"""

from pathlib import Path
from typing import List, Optional, Tuple

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from chatbot.database.vector_store import FAISSVectorStore
from chatbot.llm.embeddings import get_embeddings
from chatbot.llm.schemas import Source
from chatbot.utils.document_loader import load_documents


class RAGService:
    """
    Handles Retrieval Augmented Generation operations.
    Loads documents, creates embeddings, and performs semantic search.
    """

    def __init__(self, vector_store_path: Optional[str] = None):
        """
        Initialize RAG service.

        Args:
            vector_store_path: Path to store FAISS index
        """
        self.embeddings = get_embeddings()
        embedding_dim = self.embeddings.get_embedding_dimension()
        self.vector_store = FAISSVectorStore(
            embedding_dim=embedding_dim,
            store_path=vector_store_path
        )
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=100,
            separators=["\n\n", "\n", " ", ""],
        )

    def add_documents_from_files(
        self,
        file_paths: List[str | Path]
    ) -> int:
        """
        Load documents from files and add to vector store.

        Args:
            file_paths: List of file paths to load

        Returns:
            Number of chunks created

        Raises:
            ValueError: If files not found or cannot be loaded
        """
        documents = []
        for file_path in file_paths:
            loaded_docs = load_documents(str(file_path))
            documents.extend(loaded_docs)

        return self._process_documents(documents)

    def add_documents_from_urls(
        self,
        urls: List[str]
    ) -> int:
        """
        Load documents from URLs and add to vector store.

        Args:
            urls: List of URLs to scrape

        Returns:
            Number of chunks created
        """
        documents = []
        for url in urls:
            try:
                loaded_docs = load_documents(url)
                documents.extend(loaded_docs)
            except Exception as e:
                print(f"Failed to load URL {url}: {str(e)}")

        return self._process_documents(documents)

    def add_documents_from_text(
        self,
        texts: List[str],
        metadata: List[dict] = None
    ) -> int:
        """
        Add text documents directly to vector store.

        Args:
            texts: List of text strings
            metadata: List of metadata dicts for each text

        Returns:
            Number of chunks created
        """
        documents = [
            Document(page_content=text, metadata=metadata[i] if metadata else {})
            for i, text in enumerate(texts)
        ]
        return self._process_documents(documents)

    def _process_documents(self, documents: List[Document]) -> int:
        """
        Process documents: split into chunks and add to vector store.

        Args:
            documents: List of Document objects

        Returns:
            Number of chunks created
        """
        # Split documents into chunks
        chunks = self.text_splitter.split_documents(documents)

        if not chunks:
            return 0

        # Get embeddings for chunks
        chunk_texts = [chunk.page_content for chunk in chunks]
        embeddings = self.embeddings.embed_documents(chunk_texts)

        # Add to vector store
        self.vector_store.add_documents(chunks, embeddings)

        return len(chunks)

    def search(
        self,
        query: str,
        k: int = 5
    ) -> List[Tuple[Document, float]]:
        """
        Search for relevant documents using semantic similarity.

        Args:
            query: Search query
            k: Number of results to return

        Returns:
            List of (Document, similarity_score) tuples
        """
        # Embed query
        query_embedding = self.embeddings.embed_query(query)

        # Search vector store
        results = self.vector_store.search(query_embedding.reshape(1, -1), k=k)

        return results

    def search_and_format(
        self,
        query: str,
        k: int = 5
    ) -> Tuple[str, List[Source]]:
        """
        Search and return formatted context and sources.

        Args:
            query: Search query
            k: Number of results

        Returns:
            Tuple of (context_text, sources)
        """
        results = self.search(query, k=k)

        if not results:
            return "No relevant documents found.", []

        context_text = ""
        sources = []

        for doc, similarity in results:
            context_text += f"---\n{doc.page_content}\n"

            source = Source(
                title=doc.metadata.get("source", "Unknown"),
                url=doc.metadata.get("url"),
                author=doc.metadata.get("author"),
                relevance_score=similarity,
                excerpt=doc.page_content[:200] + "..."
            )
            sources.append(source)

        return context_text, sources

    def save(self) -> None:
        """Save vector store to disk."""
        self.vector_store.save()

    def load(self) -> None:
        """Load vector store from disk."""
        try:
            self.vector_store.load()
        except FileNotFoundError:
            print("Vector store not found. Starting with empty store.")

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        self.vector_store.clear()

    def get_store_size(self) -> int:
        """Get number of chunks in vector store."""
        return self.vector_store.get_size()
