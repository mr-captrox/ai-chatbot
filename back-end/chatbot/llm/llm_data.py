import os
from google import genai
from langsmith import wrappers
from chatbot.core.config import settings

def get_google_llm():
    """Initialize Wrapped Native Google Gemini LLM."""
    api_key = settings.google_gemini_api_key or settings.google_api_key
    if not api_key:
        return None
    
    # Initialize native client
    gemini_client = genai.Client(api_key=api_key)
    
    # Wrap with LangSmith tracing
    wrapped_client = wrappers.wrap_gemini(
        gemini_client,
        tracing_extra={
            "tags": ["gemini", "native", "python"],
            "metadata": {
                "integration": "google-genai-native",
                "project": settings.langsmith_project_name
            },
        },
    )
    return wrapped_client


# Lazy-loaded LLM instance
_llm_instance = None


def get_llm():
    """Get or create the wrapped Gemini client."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_google_llm()
            
        if _llm_instance is None:
            raise ValueError("No Gemini API key provided")
            
    return _llm_instance
