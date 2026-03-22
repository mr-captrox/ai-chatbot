# AI Chatbot - Groq Llama 3 Edition

## Overview
A powerful multi-agent AI chatbot featuring **Research (Web Search)**, **RAG (Document Chat)**, and **Image Analysis (OCR)** capabilities. Built with **FastAPI**, **Streamlit**, and **LangChain**, and fully instrumented with **LangSmith Threads** for advanced conversation tracing.

## Tech Stack
- **Frontend**: Streamlit (Reactive UI with Session Memory)
- **Backend**: FastAPI (Async high-performance API)
- **LLM**: Meta Llama 3 via Groq (Optimized for speed and intelligence)
- **Search Engine**: Tavily AI (Designed specifically for AI-agent retrieval)
- **Vector Database**: FAISS (Fast Approximate Nearest Neighbor Search)
- **OCR Engine**: EasyOCR + Layout preservation
- **Monitoring**: LangSmith (Real-time tracing and Thread grouping)
- **Orchestration**: LangChain + Pydantic

## Key Features
- **3 Specialized Agents**:
    - 🔍 **Research Agent**: Deep web analysis via Tavily, providing cited sources.
    - 📚 **RAG Agent**: Indices PDFs, TXT, and MD files into a FAISS vector store for contextual answering.
    - 🖼️ **OCR Agent**: Processes uploaded images, extracts text with layout logic, and interprets content via LLM.
- **LangSmith Threads**: Conversations are automatically grouped into threads, allowing for history tracking and cost analysis across multiple turns.
- **Smart Rate Limiting**: Built-in "Request Sho-down" system limiting users to 10 requests per minute to prevent quota exhaustion.
- **Live Knowledge Base Status**: Real-time feedback on how many document segments are currently indexed.

## Project Structure
```text
chatbot/
├── back-end/
│   ├── .env.example            # Template for your secrets
│   ├── chatbot/
│   │   ├── api/                # FastAPI Routers & Pydantic Schemas
│   │   ├── core/               # Configuration management (Pydantic-Settings)
│   │   ├── database/           # FAISS Vector Store implementation
│   │   ├── llm/                # Gemini Prompt Templates & Model Config
│   │   ├── services/           # Research (Tavily), RAG, and OCR logic
│   │   └── utils/              # Rate Limiting & Document Loaders
│   └── main.py                 # Backend Entry Point
│
├── front-end/
│   └── app.py                  # Streamlit Dashboard & Chat UI
│
├── .gitignore                  # Standard Python & IDE ignores
└── README.md                   # You are here
```

## Setup Instructions

### 1. Prerequisites
- Python 3.10 or higher
- [Google AI Studio API Key](https://aistudio.google.com/)
- [Tavily API Key](https://tavily.com/)
- [LangSmith API Key](https://smith.langchain.com/)

### 2. Backend Initialization
```bash
cd back-end
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # Fill in your API keys
python main.py
```

### 3. Frontend Initialization
```bash
cd front-end
# In a new terminal
pip install requests streamlit python-dotenv
streamlit run app.py
```

## LangSmith Tracing
All interactions are traced to the **`chatbotv2`** project.
- **Conversation Grouping**: Uses `thread_id` metadata to link turns.
- **Model Usage**: Models used are `gemini-2.5-flash` for all reasoning tasks.

## Troubleshooting
- **API Offline**: Ensure the `main.py` is running on port 8000.
- **Document Indexing**: After uploading a file, you **must** click the blue "Add to Knowledge Base" button.
- **Rate Limit**: If the "Request Sho-down" reaches 0, wait 60 seconds before sending a new message.

## Author
**mr_captrox**
*Built for Advanced Agentic Coding - Google DeepMind*

## License
MIT
