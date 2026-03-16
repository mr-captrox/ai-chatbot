"""
File utilities for document processing and image handling.

This module provides utility functions for:
- Reading PDF files and extracting text
- Reading text files
- Converting images to base64 for transmission to vision models
"""

import base64
from io import BytesIO

from PIL import Image
from pypdf import PdfReader


def read_pdf_bytes(file_bytes: bytes) -> str:
    """
    Read and extract text from a PDF file given as bytes.
    
    Extracts text from all pages of the PDF. If a page has no text
    (e.g., scanned image), returns empty string for that page.
    
    Args:
        file_bytes: PDF file content as bytes.
        
    Returns:
        Extracted text from all PDF pages concatenated together.
        
    Raises:
        ValueError: If PDF is corrupted or cannot be read.
        
    Example:
        >>> with open("document.pdf", "rb") as f:
        ...     text = read_pdf_bytes(f.read())
        ...     print(text[:100])
    """
    try:
        pdf_file = BytesIO(file_bytes)
        pdf_reader = PdfReader(pdf_file)

        text = ""
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            except Exception as e:
                text += f"\n--- Page {page_num + 1} (Error) ---\nCould not extract text: {str(e)}"

        return text
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {str(e)}")


def read_txt_bytes(file_bytes: bytes) -> str:
    """
    Read and decode a text file from bytes.
    
    Attempts to decode as UTF-8 first, then falls back to other encodings
    if that fails.
    
    Args:
        file_bytes: Text file content as bytes.
        
    Returns:
        Decoded text content.
        
    Raises:
        ValueError: If file cannot be decoded as text.
        
    Example:
        >>> with open("document.txt", "rb") as f:
        ...     text = read_txt_bytes(f.read())
    """
    try:
        return file_bytes.decode("utf-8")
    except UnicodeDecodeError:
        # Try other common encodings
        for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
            try:
                return file_bytes.decode(encoding)
            except UnicodeDecodeError:
                continue

        raise ValueError(
            "Could not decode text file - tried UTF-8, Latin-1, CP1252, ISO-8859-1"
        )


def image_to_base64(image_bytes: bytes) -> str:
    """
    Convert image bytes to base64-encoded string.
    
    This is used for sending images to vision models (like Gemini Vision)
    which expect base64-encoded image data.
    
    Args:
        image_bytes: Raw image file content as bytes.
        
    Returns:
        Base64-encoded string representation of the image.
        
    Raises:
        ValueError: If image is corrupted or unsupported format.
        
    Example:
        >>> with open("photo.jpg", "rb") as f:
        ...     b64 = image_to_base64(f.read())
        ...     print(b64[:50] + "...")  # "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEA..."
    """
    try:
        # Validate that it's actually an image by loading it
        image_file = BytesIO(image_bytes)
        Image.open(image_file).verify()

        # Re-open since verify() closes it
        image_file = BytesIO(image_bytes)
        img = Image.open(image_file)

        # Get format
        image_format = img.format or "JPEG"

        # Encode to base64
        base64_str = base64.b64encode(image_bytes).decode("utf-8")

        # Return with MIME type prefix for easier usage
        mime_type = f"image/{image_format.lower()}"
        return f"data:{mime_type};base64,{base64_str}"
    except Exception as e:
        raise ValueError(f"Failed to convert image to base64: {str(e)}")


def get_image_mime_type(image_bytes: bytes) -> str:
    """
    Detect and return the MIME type of an image.
    
    Args:
        image_bytes: Raw image file content as bytes.
        
    Returns:
        MIME type string (e.g., "image/jpeg", "image/png").
        
    Raises:
        ValueError: If image cannot be detected.
    """
    try:
        img = Image.open(BytesIO(image_bytes))
        format_name = img.format or "JPEG"
        return f"image/{format_name.lower()}"
    except Exception as e:
        raise ValueError(f"Failed to detect image format: {str(e)}")
