"""
Logging configuration for the chatbot application.
"""

import logging
import sys
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_file: str = "logs/chatbot.log"
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file

    Returns:
        Configured logger instance
    """
    log_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create logger
    logger = logging.getLogger("chatbot")
    logger.setLevel(log_level)

    # Remove existing handlers
    logger.handlers = []

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    try:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")

    return logger


# Module-level logger instance
logger = setup_logging()
