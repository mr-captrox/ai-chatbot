"""
OCR (Optical Character Recognition) service using EasyOCR.
Extracts text from images for the Image Analysis Agent.
"""

from io import BytesIO
from typing import List, Optional, Tuple

import easyocr
from PIL import Image


class OCRService:
    """
    OCR service using EasyOCR for text extraction from images.
    Supports multiple languages and provides confidence scores.
    """

    def __init__(self, languages: List[str] = None, gpu: bool = False):
        """
        Initialize OCR service.

        Args:
            languages: List of language codes (default: ['en'])
            gpu: Whether to use GPU acceleration (default: False)
        """
        self.languages = languages or ["en"]
        self.gpu = gpu
        self.reader = None
        # Removed _initialize_reader from __init__ to improve startup time

    def _initialize_reader(self) -> None:
        """Initialize EasyOCR reader (lazy loading)."""
        if self.reader is None:
            self.reader = easyocr.Reader(
                self.languages,
                gpu=self.gpu
            )

    def extract_text_from_image(
        self,
        image_input: Image.Image | str | bytes
    ) -> Tuple[str, List[dict]]:
        """
        Extract text from image.

        Args:
            image_input: PIL Image, file path, or image bytes

        Returns:
            Tuple of (extracted_text, raw_results)
            where raw_results contains detailed OCR data with positions and confidence

        Raises:
            ValueError: If image cannot be loaded
        """
        try:
            # Ensure reader is initialized
            self._initialize_reader()
            
            # Load image if needed
            if isinstance(image_input, str):
                image = Image.open(image_input)
            elif isinstance(image_input, bytes):
                image = Image.open(BytesIO(image_input))
            elif isinstance(image_input, Image.Image):
                image = image_input
            else:
                raise ValueError("Invalid image input type")

            # Convert PIL Image to RGB if needed
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Run OCR
            results = self.reader.readtext(image)

            # Format results
            extracted_text = "\n".join([text[1] for text in results])
            raw_results = [
                {
                    "text": text[1],
                    "confidence": float(text[2]),
                    "bbox": text[0],
                }
                for text in results
            ]

            return extracted_text, raw_results

        except Exception as e:
            raise ValueError(f"Failed to extract text from image: {str(e)}")

    def extract_text_with_layout(
        self,
        image_input: Image.Image | str | bytes
    ) -> dict:
        """
        Extract text with layout information (position, size, confidence).

        Args:
            image_input: PIL Image, file path, or image bytes

        Returns:
            Dictionary with extracted text and layout information
        """
        extracted_text, raw_results = self.extract_text_from_image(image_input)

        # Get image dimensions
        if isinstance(image_input, str):
            image = Image.open(image_input)
        elif isinstance(image_input, bytes):
            image = Image.open(BytesIO(image_input))
        else:
            image = image_input

        return {
            "extracted_text": extracted_text,
            "image_size": image.size,
            "detections": raw_results,
            "total_detections": len(raw_results),
            "average_confidence": sum(r["confidence"] for r in raw_results) / len(raw_results) if raw_results else 0,
        }

    def add_language(self, language_code: str) -> None:
        """
        Add support for additional language.

        Args:
            language_code: ISO 639-1 language code (e.g., 'es', 'fr', 'de')
        """
        if language_code not in self.languages:
            self.languages.append(language_code)
            self.reader = None  # Reset reader to include new language
            self._initialize_reader()

    def get_supported_languages(self) -> List[str]:
        """
        Get list of currently supported languages.

        Returns:
            List of supported language codes
        """
        return self.languages.copy()
