"""
OCR (Optical Character Recognition) service using Gemini Vision.

This service uses Google's Gemini Vision model to analyze images and extract
text, as well as provide detailed explanations of image content.
"""

from typing import Optional
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI

from ..core.config import settings
from ..utils.file_utils import get_image_mime_type, image_to_base64


def _initialize_vision_llm() -> ChatGoogleGenerativeAI:
    """
    Initialize a ChatGoogleGenerativeAI instance for vision tasks.
    
    Uses the same Gemini model as the main LLM but configured for image analysis.
    
    Returns:
        ChatGoogleGenerativeAI: Vision-capable LLM instance.
    """
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        google_api_key=settings.GOOGLE_API_KEY,
        convert_system_message_to_human=True,
    )


def analyze_image(
    image_bytes: bytes,
    prompt: str = "Extract and explain all text and content from this image",
) -> str:
    """
    Analyze an image to extract text and provide content explanation.
    
    Uses Gemini Vision to:
    1. Extract all text from the image
    2. Describe visual content
    3. Provide context and explanations
    
    Args:
        image_bytes: Raw image file content as bytes.
        prompt: Custom analysis prompt (default: extract and explain).
               Override to ask specific questions about the image.
        
    Returns:
        Textual analysis and extracted content from the image.
        
    Raises:
        ValueError: If image is invalid or analysis fails.
        
    Example:
        >>> with open("screenshot.png", "rb") as f:
        ...     result = analyze_image(f.read(), "What text appears in this image?")
        ...     print(result)
    """
    try:
        # Initialize vision LLM
        vision_llm = _initialize_vision_llm()

        # Validate image and get MIME type
        mime_type = get_image_mime_type(image_bytes)

        # Convert image to base64 for API transmission
        # Note: We use the raw bytes for LangChain's image handling
        
        # Prepare the message with image content
        from langchain_core.messages import HumanMessage
        
        message = HumanMessage(
            content=[
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{__convert_to_b64(image_bytes)}",
                    },
                },
                {
                    "type": "text",
                    "text": prompt,
                },
            ],
        )

        # Call the vision model
        response = vision_llm.invoke([message])

        return response.content
    except Exception as e:
        raise ValueError(f"Failed to analyze image: {str(e)}")


def __convert_to_b64(image_bytes: bytes) -> str:
    """Helper: Convert image bytes to base64 string (without MIME prefix)."""
    import base64
    return base64.b64encode(image_bytes).decode("utf-8")


# Create the OCR Tool for LangChain/LangGraph
def create_ocr_tool(image_bytes: Optional[bytes] = None) -> Tool:
    """
    Create a LangChain Tool wrapper for OCR/image analysis functionality.
    
    Args:
        image_bytes: Optional image bytes to analyze.
        
    Returns:
        Tool: Configured LangChain Tool ready for use in agent workflows.
    """

    def ocr_wrapper(image_prompt: str) -> str:
        """
        Wrapper for OCR tool that uses provided image bytes.
        """
        if not image_bytes:
            return "No image has been uploaded for this session. Please upload an image first."
        
        try:
            return analyze_image(image_bytes, image_prompt)
        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    return Tool(
        name="ocr_analyze",
        func=ocr_wrapper,
        description="Extract and analyze text from the CURRENTLY UPLOADED image. Use this when you need to understand or extract text from the image the user just shared. Input should be a specific question or instruction about the image.",
    )
