"""
Core configuration module for the chatbot application.
Loads environment variables and provides centralized settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Automatically loads from .env file using python-dotenv integration.
    """

    # API Configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000

    # LLM Configuration
    llm_model_name: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1024

    # LangSmith Configuration
    langsmith_api_key: str = ""
    langsmith_tracing: bool = True
    langsmith_endpoint: str = "https://api.smith.langchain.com"
    langsmith_project_name: str = "chatbotv2"

    # Groq Configuration
    groq_api_key: str = ""

    # Tavily API Configuration (for web search)
    tavily_api_key: str = ""

    # Vector Database Configuration
    vector_db_path: Path = Path("./data/vector_store")

    # Streamlit Configuration
    streamlit_api_url: str = "http://localhost:8000"

    class Config:
        """Pydantic config for environment variable loading."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings singleton.
    Caches settings after first load to avoid repeated file I/O.

    Returns:
        Settings: Application configuration object

    Raises:
        ValueError: If required environment variables are missing
    """
    return Settings()


# Expose settings for easy import
settings = get_settings()
