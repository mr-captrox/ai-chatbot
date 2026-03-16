"""
Core configuration management using pydantic-settings.

This module loads all environment variables from a .env file and exposes them
as a Settings object that can be imported throughout the application.
All configuration is centralized here to follow the twelve-factor app methodology.
"""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables (.env file).
    
    Attributes:
        GOOGLE_API_KEY: API key for Google Generative AI (Gemini)
        GOOGLE_CSE_ID: Google Custom Search Engine ID
        GOOGLE_CSE_API_KEY: Google Custom Search API key
        LANGCHAIN_API_KEY: LangSmith API key for tracing
        LANGCHAIN_TRACING_V2: Enable LangChain tracing v2 (should be "true")
        LANGCHAIN_PROJECT: LangSmith project name (default: "final-chatbot")
        CHROMA_PERSIST_DIR: Directory path for ChromaDB persistence (default: "./chroma_db")
    """

    # Google API Configuration
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_CSE_ID: Optional[str] = None
    GOOGLE_CSE_API_KEY: Optional[str] = None

    # LangSmith Configuration
    # We support both LANGCHAIN_ and LANGSMITH_ prefixes for better compatibility
    LANGCHAIN_API_KEY: Optional[str] = None
    LANGCHAIN_TRACING_V2: str = "true"
    LANGCHAIN_PROJECT: str = "final-chatbot"

    # Legacy mappings (used in some .env files)
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_TRACING: Optional[str] = None
    LANGSMITH_ENDPOINT: Optional[str] = None
    LANGSMITH_PROJECT: Optional[str] = None

    # ChromaDB Configuration
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    model_config = SettingsConfigDict(
        # Try root .env first, then backend .env if not found
        env_file=(
            Path(__file__).parent.parent.parent.parent.parent / ".env",
            Path(__file__).parent.parent.parent.parent / ".env",
        ),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",  # Ignore extra fields from .env file
    )

    def model_post_init(self, __context):
        """Handle legacy env var mappings after initialization."""
        if not self.LANGCHAIN_API_KEY and self.LANGSMITH_API_KEY:
            self.LANGCHAIN_API_KEY = self.LANGSMITH_API_KEY
        
        if self.LANGSMITH_PROJECT and self.LANGCHAIN_PROJECT == "final-chatbot":
            self.LANGCHAIN_PROJECT = self.LANGSMITH_PROJECT
        
        if self.LANGSMITH_TRACING and self.LANGSMITH_TRACING.lower() == "true":
            self.LANGCHAIN_TRACING_V2 = "true"


# Singleton instance - import this in other modules
settings = Settings()
