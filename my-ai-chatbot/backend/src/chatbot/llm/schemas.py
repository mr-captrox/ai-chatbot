"""
Type schemas for LLM inputs and outputs.

This module defines Pydantic models for type-safe handling of LLM-related
data structures, including messages, tool inputs, and agent state.
"""

from typing import Any, Optional

from pydantic import BaseModel, Field


class MessageSchema(BaseModel):
    """Schema for a single message in conversation history."""

    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")


class ToolInputSchema(BaseModel):
    """Schema for tool input parameters."""

    tool_name: str = Field(..., description="Name of the tool to invoke")
    tool_input: dict[str, Any] = Field(..., description="Input parameters for the tool")


class AgentStateSchema(BaseModel):
    """Schema for the agent's internal state."""

    messages: list[MessageSchema] = Field(
        default_factory=list, description="Conversation message history"
    )
    uploaded_file: Optional[bytes] = Field(
        None, description="Uploaded file content (PDF/TXT)"
    )
    uploaded_image: Optional[bytes] = Field(None, description="Uploaded image content")
