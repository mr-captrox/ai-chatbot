import sys
import os
from pathlib import Path

# Add backend/src to path
sys.path.append(str(Path(__file__).parent / "backend"))
sys.path.append(str(Path(__file__).parent / "backend" / "src"))

from chatbot.llm.workflow import invoke_agent
import dotenv

# Load .env
dotenv.load_dotenv(Path(__file__).parent / "backend" / ".env")

def test_agent_search():
    print("Testing agent with web search...")
    messages = [{"role": "user", "content": "What is the current stock price of Google (Alphabet Inc.)?"}]
    try:
        response = invoke_agent(messages)
        print(f"Agent Response: {response}")
    except Exception:
        import traceback
        traceback.print_exc()

def test_agent_general():
    print("\nTesting agent with general knowledge...")
    messages = [{"role": "user", "content": "Tell me a short joke."}]
    try:
        response = invoke_agent(messages)
        print(f"Agent Response: {response}")
    except Exception:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import time
    test_agent_general()
    print("Waiting 10 seconds for quota...")
    time.sleep(10)
    test_agent_search()
