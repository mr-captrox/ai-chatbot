"""
Internet search service using Google Custom Search.

This service wraps Google Custom Search API to provide internet search
functionality as a LangChain Tool for the ReAct agent.
"""

from langchain.tools import Tool
from langchain_community.utilities import GoogleSearchAPIWrapper

from ..core.config import settings


def _initialize_search() -> GoogleSearchAPIWrapper:
    """
    Initialize Google Custom Search wrapper with API credentials.
    
    Returns:
        GoogleSearchAPIWrapper: Configured search client.
        
    Raises:
        ValueError: If required API credentials are not set.
    """
    if not settings.GOOGLE_CSE_ID or not settings.GOOGLE_CSE_API_KEY:
        raise ValueError(
            "Google Custom Search credentials not configured. "
            "Set GOOGLE_CSE_ID and GOOGLE_CSE_API_KEY in .env"
        )

    return GoogleSearchAPIWrapper(
        google_api_key=settings.GOOGLE_CSE_API_KEY,
        google_cse_id=settings.GOOGLE_CSE_ID,
    )


def search(query: str, num_results: int = 3) -> str:
    """
    Perform an internet search using Google Custom Search.
    
    Args:
        query: Search query string.
        num_results: Number of results to return (default: 3).
        
    Returns:
        Formatted search results as a string.
        
    Example:
        >>> results = search("Python programming 2024")
        >>> print(results)
    """
    try:
        search_client = _initialize_search()

        # Use run() method which returns results as a formatted string
        results = search_client.run(query)
        return results
    except Exception as e:
        return f"Error performing search: {str(e)}"


# Create the Search Tool for LangChain/LangGraph
def create_search_tool() -> Tool:
    """
    Create a LangChain Tool wrapper for internet search functionality.
    
    Returns:
        Tool: Configured LangChain Tool ready for use in agent workflows.
    """
    return Tool(
        name="internet_search",
        func=search,
        description="Search the internet for current information, news, and recent events. Use this when you need up-to-date information not available in your training data.",
    )
