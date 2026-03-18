"""
Document loading utilities for multiple formats.
Supports PDF, TXT, URLs, and Markdown.
"""

from pathlib import Path
from typing import List
from urllib.parse import urlparse

import requests
from langchain_core.documents import Document


def load_documents(source: str) -> List[Document]:
    """
    Load documents from various sources.

    Args:
        source: File path, URL, or text content

    Returns:
        List of Document objects

    Raises:
        ValueError: If source type cannot be determined or fails to load
    """
    source = source.strip()

    # Check if it's a URL
    if source.startswith("http://") or source.startswith("https://"):
        return _load_from_url(source)

    # Check if it's a file path
    file_path = Path(source)
    if file_path.exists():
        if file_path.suffix.lower() == ".pdf":
            return _load_from_pdf(str(file_path))
        elif file_path.suffix.lower() in [".txt", ".md"]:
            return _load_from_text(str(file_path))
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

    # Otherwise treat as raw text
    return _load_from_text_content(source)


def _load_from_pdf(file_path: str) -> List[Document]:
    """
    Load documents from PDF file.

    Args:
        file_path: Path to PDF file

    Returns:
        List of Document objects

    Raises:
        ImportError: If PyPDF2 not installed
    """
    try:
        import PyPDF2
    except ImportError:
        raise ImportError("PyPDF2 required for PDF loading. Install with: pip install PyPDF2")

    documents = []

    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)

            for page_num, page in enumerate(pdf_reader.pages):
                text = page.extract_text()

                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": Path(file_path).name,
                            "page": page_num + 1,
                            "type": "pdf",
                        }
                    )
                    documents.append(doc)

        return documents

    except Exception as e:
        raise ValueError(f"Failed to load PDF {file_path}: {str(e)}")


def _load_from_text(file_path: str) -> List[Document]:
    """
    Load documents from text file.

    Args:
        file_path: Path to text/markdown file

    Returns:
        List of Document objects
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        file_ext = Path(file_path).suffix.lower()

        doc = Document(
            page_content=content,
            metadata={
                "source": Path(file_path).name,
                "type": "text" if file_ext == ".txt" else "markdown",
            }
        )

        return [doc]

    except Exception as e:
        raise ValueError(f"Failed to load text file {file_path}: {str(e)}")


def _load_from_url(url: str) -> List[Document]:
    """
    Load documents from URL (scrape text content).

    Args:
        url: URL to scrape

    Returns:
        List of Document objects

    Raises:
        ValueError: If URL cannot be fetched
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Extract title from URL or HTML
        domain = urlparse(url).netloc

        # Simple HTML stripping (in production, use BeautifulSoup)
        import re
        html = response.text
        # Remove script and style tags
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
        # Remove HTML tags
        text = re.sub(r"<[^>]+>", "", html)
        # Clean up whitespace
        text = re.sub(r"\s+", " ", text).strip()

        if not text:
            raise ValueError("No text content found at URL")

        doc = Document(
            page_content=text,
            metadata={
                "source": domain,
                "url": url,
                "type": "web",
            }
        )

        return [doc]

    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL {url}: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to process URL {url}: {str(e)}")


def _load_from_text_content(text: str) -> List[Document]:
    """
    Load from raw text content string.

    Args:
        text: Raw text content

    Returns:
        List with single Document object
    """
    if not text.strip():
        return []

    doc = Document(
        page_content=text,
        metadata={
            "source": "user_text",
            "type": "raw_text",
        }
    )

    return [doc]
