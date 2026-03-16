"""
ChromaDB client initialization and collection management.

This module initializes a persistent ChromaDB client that stores vector
embeddings on disk (not in-memory). It provides helper functions to create
and retrieve collections for storing and searching documents.
"""

import os
from pathlib import Path

import chromadb

from ..core.config import settings


def _initialize_client() -> chromadb.PersistentClient:
    """
    Initialize and return a persistent ChromaDB client.
    
    The client uses the directory specified in settings.CHROMA_PERSIST_DIR
    to store all vector data persistently on disk. This allows the database
    to survive application restarts.
    
    Returns:
        chromadb.PersistentClient: Initialized ChromaDB client.
    """
    persist_dir = settings.CHROMA_PERSIST_DIR

    # Create directory if it doesn't exist
    Path(persist_dir).mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(path=persist_dir)


# Singleton ChromaDB client instance
client = _initialize_client()


def get_or_create_collection(name: str, metadata: dict = None) -> chromadb.Collection:
    """
    Get an existing ChromaDB collection or create it if it doesn't exist.
    
    Collections are named storage units within ChromaDB that hold embeddings
    and metadata for a specific set of documents. This helper ensures a
    consistent interface for accessing collections regardless of whether
    they already exist.
    
    Args:
        name: Collection name (alphanumeric, underscores allowed)
        metadata: Optional metadata dict to store with the collection
        
    Returns:
        chromadb.Collection: The collection object ready for use.
        
    Example:
        >>> collection = get_or_create_collection("documents")
        >>> collection.add(ids=["doc1"], embeddings=[[...]], documents=["..."])
    """
    if metadata is None:
        metadata = {"description": f"Collection '{name}'"}

    # ChromaDB automatically creates or retrieves collections
    return client.get_or_create_collection(
        name=name,
        metadata=metadata,
        # Use cosine similarity for nearest neighbor search
        distance_config=chromadb.config.CollectionConfig(metric="cosine"),
    )


def delete_collection(name: str) -> None:
    """
    Delete a ChromaDB collection by name.
    
    Use this to clean up collections that are no longer needed.
    
    Args:
        name: Name of the collection to delete.
    """
    client.delete_collection(name=name)


def list_collections() -> list[str]:
    """
    List all collection names in the ChromaDB database.
    
    Returns:
        List of collection names.
    """
    return [col.name for col in client.list_collections()]
