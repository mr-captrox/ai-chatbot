"""
Embeddings initialization and management.

This module provides a singleton instance of GoogleGenerativeAIEmbeddings.
The embeddings model is used to convert text and documents into vector
representations for semantic search and RAG (Retrieval-Augmented Generation).
"""

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from ..core.config import settings


def _initialize_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    Initialize and return a configured GoogleGenerativeAIEmbeddings instance.
    
    This factory function creates a singleton embeddings client with:
    - Model: models/embedding-001 (Google's embedding model)
    - API Key from environment configuration
    
    Returns:
        GoogleGenerativeAIEmbeddings: Configured embeddings instance ready for use.
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment.
    """
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")

    return GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=settings.GOOGLE_API_KEY,
    )


# Singleton instance - import this in other modules
embeddings = _initialize_embeddings()
