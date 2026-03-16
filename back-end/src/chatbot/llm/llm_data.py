from typing import Optional
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

from chatbot.core.config import settings


def get_google_llm() -> Optional[ChatGoogleGenerativeAI]:
    """Initialize Google Gemini LLM."""
    api_key = settings.google_gemini_api_key or settings.google_api_key
    if not api_key:
        return None
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=settings.llm_temperature,
        max_output_tokens=settings.llm_max_tokens,
        max_retries=2,
    )


def get_groq_llm() -> Optional[ChatGroq]:
    """Initialize Groq LLM."""
    if not settings.groq_api_key:
        return None

    return ChatGroq(
        model=settings.llm_model_name,
        temperature=settings.llm_temperature,
        max_tokens=settings.llm_max_tokens,
        api_key=settings.groq_api_key,
    )


# Lazy-loaded LLM instance
_llm_instance = None


def get_llm():
    """Get or create LLM instance (Gemini preferred)."""
    global _llm_instance
    if _llm_instance is None:
        # Prefer Gemini if key is provided
        _llm_instance = get_google_llm()
        
        # Fallback to Groq
        if _llm_instance is None:
            _llm_instance = get_groq_llm()
            
        if _llm_instance is None:
            raise ValueError("No LLM API keys provided (Google/Gemini or Groq)")
            
    return _llm_instance
