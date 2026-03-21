from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from chatbot.core.config import settings


def get_google_llm() -> Optional[ChatGoogleGenerativeAI]:
    """Initialize Google Gemini LLM."""
    api_key = settings.google_gemini_api_key or settings.google_api_key
    if not api_key:
        return None
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_tokens,
        max_retries=2,
    )


# Lazy-loaded LLM instance
_llm_instance = None


def get_llm():
    """Get or create LLM instance (Gemini Flash as per user request)."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = get_google_llm()
            
        if _llm_instance is None:
            raise ValueError("No Gemini API key provided")
            
    return _llm_instance
