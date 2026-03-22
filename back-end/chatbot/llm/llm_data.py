import os
from groq import Groq
from langsmith import wrappers
from chatbot.core.config import settings

def get_groq_llm():
    """Initialize Wrapped Groq LLM."""
    api_key = settings.groq_api_key
    if not api_key:
        return None
    
    # Initialize native client
    groq_client = Groq(api_key=api_key)
    
    # Wrap with LangSmith tracing (Groq is OpenAI-compatible)
    wrapped_client = wrappers.wrap_openai(
        groq_client,
        tracing_extra={
            "tags": ["groq", "llama", "python"],
            "metadata": {
                "integration": "groq-native",
                "project": settings.langsmith_project_name
            },
        },
    )
    return wrapped_client


# Lazy-loaded LLM instance
_llm_instance = None


def get_llm():
    """Get or create the wrapped Groq client."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_groq_llm()
            
        if _llm_instance is None:
            raise ValueError("No Groq API key provided")
            
    return _llm_instance
