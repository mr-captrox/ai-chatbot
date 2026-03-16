"""
LLM instantiation using Groq provider.
Provides the model instance for agent execution.
"""

from langchain_groq import ChatGroq

from chatbot.core.config import settings


def get_groq_llm() -> ChatGroq:
    """
    Initialize and return Groq LLM instance.

    Uses configuration from environment variables:
    - GROQ_API_KEY: Groq API key
    - LLM_MODEL_NAME: Model name (default: llama-3.1-70b-versatile)
    - LLM_TEMPERATURE: Temperature for sampling (default: 0.7)
    - LLM_MAX_TOKENS: Max tokens in response (default: 1024)

    Returns:
        ChatGroq: Configured LLM instance

    Raises:
        ValueError: If GROQ_API_KEY not provided
    """
    if not settings.groq_api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")

    llm = ChatGroq(
        model=settings.llm_model_name,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.groq_api_key,
    )

    return llm


# Lazy-loaded LLM instance
_llm_instance = None


def get_llm() -> ChatGroq:
    """
    Get or create LLM instance (singleton pattern).

    Returns:
        ChatGroq: LLM instance
    """
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_groq_llm()
    return _llm_instance
