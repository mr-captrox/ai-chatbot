import sys
from pathlib import Path

# Add back-end to path
sys.path.append(str(Path(__file__).parent))

try:
    import fastapi
    print("FastAPI is installed")
except ImportError:
    print("FastAPI is MISSING")

try:
    from chatbot.core.config import settings
    print("chatbot.core.config is working")
except ImportError as e:
    print(f"chatbot.core.config is MISSING: {e}")
