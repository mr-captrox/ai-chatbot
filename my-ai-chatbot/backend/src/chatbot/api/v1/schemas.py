"""
API request and response schemas for FastAPI endpoints.

These Pydantic models define the contract for API requests and responses,
providing automatic validation and serialization/deserialization of JSON.
"""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request schema for the /chat endpoint."""

    message: str = Field(..., description="User message or query", min_length=1)
    session_id: str = Field(..., description="Unique session identifier for conversation history")
    collection_name: str = Field(
        "default",
        description="ChromaDB collection name for RAG queries",
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "message": "What is in the uploaded document?",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
                "collection_name": "default",
            }
        }


class ChatResponse(BaseModel):
    """Response schema for the /chat endpoint."""

    response: str = Field(..., description="Assistant's response message")
    session_id: str = Field(..., description="Session identifier matching the request")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "response": "Based on the uploaded document, ...",
                "session_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }


class IngestResponse(BaseModel):
    """Response schema for the /ingest/* endpoints."""

    status: str = Field(..., description="Status of ingestion (success/error)")
    message: str = Field(..., description="Detailed message about ingestion result")
    collection_name: str = Field(
        ..., description="Collection name where document was stored"
    )

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "status": "success",
                "message": "Successfully ingested document.pdf: stored 5 chunks",
                "collection_name": "default",
            }
        }


class HealthResponse(BaseModel):
    """Response schema for the /health endpoint."""

    status: str = Field(..., description="Health status of the API")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {"example": {"status": "ok"}}
