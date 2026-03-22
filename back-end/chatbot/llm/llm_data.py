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
    from chatbot.utils.logging_config import logger
    logger.info(f"Initializing Groq client with key ending in: ...{api_key[-4:] if api_key else 'None'}")
    groq_client = Groq(api_key=api_key)
    return groq_client


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
