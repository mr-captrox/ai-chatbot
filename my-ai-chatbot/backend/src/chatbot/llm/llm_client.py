"""
LLM (Language Model) client initialization and management.

This module provides a singleton instance of ChatGoogleGenerativeAI configured
with Google's Gemini 1.5 Flash model. All other modules should import this
singleton instance rather than creating their own LLM clients.
"""

from langchain_google_genai import ChatGoogleGenerativeAI

from ..core.config import settings


def _initialize_llm() -> ChatGoogleGenerativeAI:
    """
    Initialize and return a configured ChatGoogleGenerativeAI instance.
    
    This factory function creates a singleton LLM client with:
    - Model: gemini-1.5-flash (fast, cost-effective)
    - Temperature: 0 (deterministic output)
    - API Key from environment configuration
    
    Returns:
        ChatGoogleGenerativeAI: Configured LLM instance ready for use.
        
    Raises:
        ValueError: If GOOGLE_API_KEY is not set in environment.
    """
    if not settings.GOOGLE_API_KEY:
        raise ValueError("GOOGLE_API_KEY environment variable is not set")

    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY,
        convert_system_message_to_human=True,
    )


# Singleton instance - import this in other modules
llm = _initialize_llm()
