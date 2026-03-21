"""
Pydantic schemas for request/response validation and type hints.
Used throughout the application for data validation.
"""

from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    """Available agent types."""
    RESEARCH = "research"
    RAG = "rag"
    IMAGE_ANALYSIS = "image_analysis"


class Source(BaseModel):
    """Source reference for retrieved information."""
    title: str = Field(..., description="Title of the source")
    url: Optional[str] = Field(None, description="URL if available")
    author: Optional[str] = Field(None, description="Author name if available")
    relevance_score: float = Field(..., description="Relevance score 0-1")
    excerpt: Optional[str] = Field(None, description="Excerpt from source")


class AgentResponse(BaseModel):
    """Response from an agent."""
    agent_type: AgentType = Field(..., description="Type of agent that processed query")
    answer: str = Field(..., description="The agent's response")
    confidence: float = Field(default=0.5, description="Confidence score 0-1")
    sources: List[Source] = Field(default_factory=list, description="Sources used")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    trace_id: Optional[str] = Field(None, description="LangSmith trace ID")


class ChatMessage(BaseModel):
    """A single chat message."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[float] = Field(None, description="Unix timestamp")


class ChatRequest(BaseModel):
    """Request to chat with the chatbot."""
    message: str = Field(..., description="User message")
    context: Optional[List[ChatMessage]] = Field(
        default_factory=list,
        description="Previous conversation context"
    )
    agent_types: List[AgentType] = Field(
        default_factory=lambda: [AgentType.RESEARCH, AgentType.RAG],
        description="Which agents to use"
    )
    use_image: bool = Field(default=False, description="Whether to use image analysis")
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    thread_id: Optional[str] = Field(None, description="LangSmith thread ID for grouping traces")


class ChatResponse(BaseModel):
    """Response to a chat request."""
    message: str = Field(..., description="The chatbot's response")
    agent_responses: List[AgentResponse] = Field(
        default_factory=list,
        description="Responses from individual agents"
    )
    trace_id: Optional[str] = Field(None, description="Main trace ID for this request")


class DocumentUploadRequest(BaseModel):
    """Request to upload documents to knowledge base."""
    document_name: str = Field(..., description="Name/title of document")
    document_type: str = Field(
        default="pdf",
        description="Type: 'pdf', 'txt', 'url', 'markdown'"
    )
    content: Optional[str] = Field(None, description="Document content (for text uploads)")
    url: Optional[str] = Field(None, description="URL (for URL uploads)")
    tags: List[str] = Field(default_factory=list, description="Document tags/categories")


class DocumentUploadResponse(BaseModel):
    """Response to document upload."""
    success: bool = Field(..., description="Whether upload succeeded")
    document_id: Optional[str] = Field(None, description="ID of uploaded document")
    chunks_created: int = Field(0, description="Number of chunks created")
    message: str = Field(..., description="Status message")


class TraceInfo(BaseModel):
    """Information about a LangSmith trace."""
    trace_id: str = Field(..., description="Trace ID")
    agent_type: Optional[str] = Field(None, description="Agent type")
    start_time: float = Field(..., description="Start time unix timestamp")
    end_time: Optional[float] = Field(None, description="End time unix timestamp")
    status: str = Field(..., description="Status: 'running', 'success', 'error'")
    tool_calls: List[dict] = Field(default_factory=list, description="Tool calls made")
    error: Optional[str] = Field(None, description="Error message if failed")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Status: 'healthy', 'degraded', 'down'")
    version: str = Field(..., description="API version")
    timestamp: float = Field(..., description="Response time")
    services: dict[str, str] = Field(
        default_factory=dict,
        description="Status of each service"
    )


class QuotaResponse(BaseModel):
    """Rate limit status."""
    remaining: int = Field(..., description="Remaining requests in period")
    limit: int = Field(..., description="Max requests allowed per period")
    period_seconds: int = Field(..., description="Rate limit period in seconds")
    wait_time: int = Field(..., description="Seconds to wait if limit exceeded")
