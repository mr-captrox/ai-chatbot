
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add current dir to path for imports
sys.path.append(os.getcwd())

# Force load from .env in parent dir (backend root)
env_path = Path('../.env')
print(f"Loading env from: {env_path.absolute()}")
load_dotenv(dotenv_path=env_path)

from chatbot.core.config import settings

print(f"\n--- Environment Check ---")
print(f"GROQ_API_KEY set: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"GOOGLE_API_KEY set: {bool(os.getenv('GOOGLE_API_KEY'))}")
print(f"GOOGLE_GEMINI_API_KEY set: {bool(os.getenv('GOOGLE_GEMINI_API_KEY'))}")

print(f"\n--- Settings Check ---")
print(f"Settings GROQ key length: {len(settings.groq_api_key) if settings.groq_api_key else 0}")
print(f"Settings GOOGLE key length: {len(settings.google_api_key) if settings.google_api_key else 0}")
print(f"Settings GEMINI key length: {len(settings.google_gemini_api_key) if settings.google_gemini_api_key else 0}")
