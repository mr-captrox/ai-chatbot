
import os
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv("back-end/.env")

groq_key = os.getenv("GROQ_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

print(f"Testing Groq Key: {groq_key[:10]}...")
try:
    client = Groq(api_key=groq_key)
    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": "hi"}],
        model="llama-3.1-8b-instant",
    )
    print("✅ Groq Success!")
except Exception as e:
    print(f"❌ Groq Failed: {str(e)}")

print(f"\nTesting Tavily Key: {tavily_key[:10]}...")
try:
    t_client = TavilyClient(api_key=tavily_key)
    response = t_client.search(query="hi")
    print("✅ Tavily Success!")
except Exception as e:
    print(f"❌ Tavily Failed: {str(e)}")
