"""
FastAPI application entry point.
Initializes the server, mounts routers, and configures middleware.
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load environment variables FIRST, before any other imports
env_file = Path(__file__).parent / ".env"
load_dotenv(env_file, override=True)

from chatbot.api.v1 import endpoints
from chatbot.core.config import settings
from chatbot.utils.logging_config import logger, setup_logging

# Initialize LangSmith if API key is provided
if settings.langsmith_api_key:
    os.environ["LANGSMITH_TRACING"] = str(settings.langsmith_tracing).lower()
    os.environ["LANGCHAIN_TRACING_V2"] = str(settings.langsmith_tracing).lower()
    os.environ["LANGSMITH_ENDPOINT"] = settings.langsmith_endpoint
    os.environ["LANGSMITH_API_KEY"] = settings.langsmith_api_key
    os.environ["LANGSMITH_PROJECT"] = settings.langsmith_project_name

# Log key lengths (not values) to verify env loading
logger.info(f"Loaded Groq AI key length: {len(settings.groq_api_key) if settings.groq_api_key else 0}")
logger.info(f"Loaded Tavily key length: {len(settings.tavily_api_key) if settings.tavily_api_key else 0}")

# Setup logging
setup_logging(log_level="INFO")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan context manager.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Chatbot application starting...")
    logger.info(f"LLM Model: {settings.llm_model_name}")
    logger.info(f"Vector DB: {settings.vector_db_path}")

    yield

    # Shutdown
    logger.info("Chatbot application shutting down...")


# Create FastAPI app
app = FastAPI(
    title="Chatbot API",
    description="AI Chatbot with Research, RAG, and Image Analysis Agents",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(endpoints.router)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Chatbot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
    )
