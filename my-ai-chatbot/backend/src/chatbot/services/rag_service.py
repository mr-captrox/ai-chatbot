"""
RAG (Retrieval-Augmented Generation) service for document ingestion and retrieval.

This service handles:
1. Ingesting documents (PDF, TXT) into ChromaDB with embeddings
2. Querying documents to retrieve relevant context
3. Wrapping RAG functionality as a LangChain Tool
"""

from typing import Optional

from langchain.tools import Tool
from langchain.text_splitter import RecursiveCharacterTextSplitter

from ..database.chromadb_client import get_or_create_collection
from ..llm.embeddings import embeddings
from ..utils.file_utils import read_pdf_bytes, read_txt_bytes


def ingest_document(
    file_bytes: bytes, filename: str, collection_name: str = "default"
) -> str:
    """
    Ingest a document (PDF or TXT) into the RAG system.
    
    Process:
    1. Read the file based on its extension
    2. Split text into chunks (1000 chars, 200 overlap)
    3. Generate embeddings for each chunk
    4. Store in ChromaDB collection
    
    Args:
        file_bytes: Raw file content as bytes.
        filename: Filename (must end with .pdf or .txt).
        collection_name: Name of the ChromaDB collection to store in.
        
    Returns:
        Success message with document count.
        
    Raises:
        ValueError: If file format is unsupported.
        
    Example:
        >>> with open("document.pdf", "rb") as f:
        ...     result = ingest_document(f.read(), "document.pdf", "my_docs")
        ...     print(result)
        "Successfully ingested document.pdf: stored 5 chunks"
    """
    # Determine file type and read content
    if filename.lower().endswith(".pdf"):
        text_content = read_pdf_bytes(file_bytes)
    elif filename.lower().endswith(".txt"):
        text_content = read_txt_bytes(file_bytes)
    else:
        raise ValueError(
            f"Unsupported file format: {filename}. Only PDF and TXT are supported."
        )

    # Split text into chunks with overlap for better context
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_text(text_content)

    if not chunks:
        return f"Warning: No text content found in {filename}"

    # Get or create collection
    collection = get_or_create_collection(collection_name)

    # Generate embeddings and store in ChromaDB
    try:
        # Create unique IDs for each chunk
        doc_ids = [f"{filename}_{i}" for i in range(len(chunks))]

        # Embed the chunks
        chunk_embeddings = embeddings.embed_documents(chunks)

        # Add to collection with metadata
        collection.add(
            ids=doc_ids,
            documents=chunks,
            embeddings=chunk_embeddings,
            metadatas=[{"source": filename, "chunk_index": i} for i in range(len(chunks))],
        )

        return f"Successfully ingested {filename}: stored {len(chunks)} chunks in collection '{collection_name}'"
    except Exception as e:
        raise ValueError(f"Failed to ingest document: {str(e)}")


def query_rag(
    question: str, collection_name: str = "default", k: int = 4
) -> str:
    """
    Query the RAG system to retrieve relevant document chunks.
    
    Process:
    1. Embed the question
    2. Search ChromaDB for top-k similar chunks
    3. Return concatenated context
    
    Args:
        question: User's question/query.
        collection_name: Collection to search in.
        k: Number of top results to retrieve.
        
    Returns:
        Concatenated context from relevant documents, or message if no results.
        
    Example:
        >>> context = query_rag("What is the capital of France?", "my_docs")
        >>> print(context)
    """
    try:
        # Get collection
        collection = get_or_create_collection(collection_name)

        # Embed the question
        question_embedding = embeddings.embed_query(question)

        # Query ChromaDB for similar chunks
        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=k,
            include=["documents", "metadatas", "distances"],
        )

        # Format results
        if not results["documents"] or not results["documents"][0]:
            return f"No relevant documents found in collection '{collection_name}' for your query."

        # Concatenate retrieved documents
        context_parts = []
        for i, doc in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else 0

            source = metadata.get("source", "Unknown")
            context_parts.append(f"[Source: {source}]\n{doc}")

        context = "\n\n---\n\n".join(context_parts)
        return context
    except Exception as e:
        return f"Error querying RAG system: {str(e)}"


# Create the RAG Tool for LangChain/LangGraph
def create_rag_tool(collection_name: str = "default") -> Tool:
    """
    Create a LangChain Tool wrapper for the RAG query functionality.
    
    Args:
        collection_name: The ChromaDB collection to search in.
        
    Returns:
        Tool: Configured LangChain Tool ready for use in agent workflows.
    """

    def rag_query_wrapper(question: str) -> str:
        """Wrapper that calls query_rag with specified collection."""
        return query_rag(question, collection_name=collection_name, k=4)

    return Tool(
        name="rag_search",
        func=rag_query_wrapper,
        description="Search through the uploaded documents to find relevant information. Use this to answer questions about the specific files the user has uploaded.",
    )
