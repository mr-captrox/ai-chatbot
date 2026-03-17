"""
Tavily API search service for web search.
"""

import requests
from typing import List, Tuple
from tavily import TavilyClient

from chatbot.llm.schemas import Source
from chatbot.core.config import settings


class GoogleSearchService:
    """
    Search service using Google Custom Search Engine (CSE) API.
    """

    def __init__(self):
        """Initialize Google CSE options."""
        self.api_key = settings.google_cse_api_key or settings.google_api_key
        self.cse_id = settings.google_cse_id

        if not self.api_key:
            raise ValueError("Google API Key not set. Provide GOOGLE_CSE_API_KEY or GOOGLE_API_KEY.")
        if not self.cse_id:
            raise ValueError("GOOGLE_CSE_ID not set. Get it from https://programmablesearchengine.google.com/")

    def search(self, query: str, num_results: int = 3) -> List[Source]:
        """
        Search the web using Google CSE API.
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "q": query,
                "key": self.api_key,
                "cx": self.cse_id,
                "num": num_results
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            sources = []
            if "items" in data:
                for item in data["items"]:
                    sources.append(Source(
                        title=item.get("title", "Unknown"),
                        url=item.get("link", ""),
                        relevance_score=0.9,  # Default score for Google results
                        excerpt=item.get("snippet", "No excerpt available")
                    ))
            
            return sources

        except Exception as e:
            raise ValueError(f"Google Search failed: {str(e)}")


class TavilySearchService:
    """
    Search service using Tavily API for web search.
    Tavily is optimized for AI agents and has generous free tier limits.
    """

    def __init__(self):
        """Initialize Tavily API client."""
        if not settings.tavily_api_key:
            raise ValueError(
                "TAVILY_API_KEY environment variable not set. "
                "Get it for free from https://tavily.com/"
            )

        self.client = TavilyClient(api_key=settings.tavily_api_key)

    def search(self, query: str, num_results: int = 3) -> List[Source]:
        """
        Search the web using Tavily API.

        Args:
            query: Search query
            num_results: Number of results to return

        Returns:
            List of Source objects with search results
        """
        try:
            # Search using Tavily
            response = self.client.search(
                query=query,
                max_results=num_results,
                include_answer=True,
                search_depth="advanced"
            )

            sources = []

            # Extract sources from results
            if "results" in response:
                for result in response["results"][:num_results]:
                    source = Source(
                        title=result.get("title", "Unknown"),
                        url=result.get("url", ""),
                        author=None,
                        relevance_score=result.get("score", 0.8),
                        excerpt=result.get("content", "No excerpt available")
                    )
                    sources.append(source)

            return sources

        except Exception as e:
            raise ValueError(f"Search failed: {str(e)}")

    def search_and_format(self, query: str, num_results: int = 5) -> Tuple[str, List[Source]]:
        """
        Search and format results as readable string with sources.

        Args:
            query: Search query
            num_results: Number of results

        Returns:
            Tuple of (formatted_string, sources_list)
        """
        try:
            sources = self.search(query, num_results)

            # Format results
            if sources:
                formatted = f"**Search Results for: {query}**\n\n"
                formatted += f"Found {len(sources)} relevant sources:\n\n"

                for i, source in enumerate(sources, 1):
                    formatted += f"{i}. **{source.title}**\n"
                    formatted += f"   URL: {source.url}\n"
                    formatted += f"   Relevance: {source.relevance_score:.0%}\n"
                    formatted += f"   {source.excerpt}\n\n"
            else:
                formatted = f"No results found for: {query}"

            return formatted, sources[:num_results]

        except Exception as e:
            raise ValueError(f"Search formatting failed: {str(e)}")
