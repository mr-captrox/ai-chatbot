"""
Simple agent workflow using LLM with tool binding.

This module builds an agent with:
1. 3 tools: RAG, Internet Search, and OCR
2. Google Gemini 1.5 Flash LLM with tool binding
3. LangGraph ReAct agent for autonomous tool execution
"""

from typing import Any, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent

from ..llm.llm_client import llm
from ..llm.prompts import SYSTEM_PROMPT
from ..services.ocr_service import create_ocr_tool
from ..services.rag_service import create_rag_tool
from ..services.search_service import create_search_tool


def build_agent(
    uploaded_file_bytes: Optional[bytes] = None,
    uploaded_image_bytes: Optional[bytes] = None,
    collection_name: str = "default",
):
    """
    Build and return a functional ReAct agent.
    
    The agent:
    - Binds 3 tools to an LLM
    - Uses LangGraph to manage the reasoning-action loop
    """
    # Create all tools with session-specific context
    rag_tool = create_rag_tool(collection_name=collection_name)
    search_tool = create_search_tool()
    ocr_tool = create_ocr_tool(image_bytes=uploaded_image_bytes)

    tools = [rag_tool, search_tool, ocr_tool]

    # Create the ReAct agent
    # We use the system prompt to guide tool selection and behavior
    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=SYSTEM_PROMPT
    )
    
    return agent


def invoke_agent(
    messages: list[dict[str, str]],
    uploaded_file_bytes: Optional[bytes] = None,
    uploaded_image_bytes: Optional[bytes] = None,
    collection_name: str = "default",
) -> str:
    """
    Invoke the agent with user messages and optional file/image context.
    """
    # Build the agent for this specific invocation (to inject dynamic tool context)
    agent = build_agent(
        uploaded_file_bytes=uploaded_file_bytes,
        uploaded_image_bytes=uploaded_image_bytes,
        collection_name=collection_name
    )
    
    # Convert message history to LangChain format
    langchain_messages = []
    for msg in messages:
        role = msg.get("role", "user").lower()
        content = msg.get("content", "")
        if role == "user":
            langchain_messages.append(HumanMessage(content=content))
        elif role == "assistant":
            from langchain_core.messages import AIMessage
            langchain_messages.append(AIMessage(content=content))

    # Run the agent
    # The agent returns the full state; we want the last message
    result = agent.invoke({"messages": langchain_messages})
    
    # Extract the last message content
    last_message = result["messages"][-1]
    
    if hasattr(last_message, "content"):
        return last_message.content
    return str(last_message)
