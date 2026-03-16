from chatbot.core.config import settings

print(f"GROQ Key loaded: {bool(settings.groq_api_key)}")
print(f"GROQ Key starts with: {settings.groq_api_key[:10] if settings.groq_api_key else 'NONE'}")
print(f"GROQ Key length: {len(settings.groq_api_key) if settings.groq_api_key else 0}")
print(f"Tavily Key loaded: {bool(settings.tavily_api_key)}")
print(f"LangSmith Key loaded: {bool(settings.langsmith_api_key)}")
