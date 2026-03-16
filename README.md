# Chatbot Application - Final Project

## Overview
A full-stack AI chatbot application with specialized agents (Research, RAG, Image Analysis), integrated with LangSmith for tracing and monitoring, and powered by Groq LLM.

## Tech Stack
- **Frontend**: Streamlit
- **Backend**: FastAPI + Python
- **LLM**: Groq (Mixtral 8x7b)
- **Vector Database**: FAISS
- **OCR**: EasyOCR
- **Search**: Google Custom Search Engine (CSE) API
- **Tracing**: LangSmith
- **Orchestration**: LangGraph

## Project Structure

```
chatbot/
├── back-end/
│   ├── .venv/                          # Virtual environment (created locally)
│   ├── src/
│   │   ├── chatbot/
│   │   │   ├── api/
│   │   │   │   ├── v1/
│   │   │   │   │   ├── __init__.py
│   │   │   │   │   ├── endpoints.py    # Chat, upload, trace endpoints
│   │   │   │   │   └── schemas.py      # Request/response models
│   │   │   ├── core/
│   │   │   │   ├── __init__.py
│   │   │   │   └── config.py           # Configuration & env vars
│   │   │   ├── database/
│   │   │   │   ├── __init__.py
│   │   │   │   └── vector_store.py     # FAISS wrapper
│   │   │   ├── llm/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── embeddings.py       # Embedding logic
│   │   │   │   ├── llm_data.py         # Groq LLM instantiation
│   │   │   │   ├── prompts.py          # Prompt templates
│   │   │   │   ├── schemas.py          # Pydantic models
│   │   │   │   └── workflow.py         # LangGraph agents
│   │   │   ├── services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── search_service.py   # Google Search wrapper
│   │   │   │   ├── ocr_service.py      # EasyOCR wrapper
│   │   │   │   ├── rag_service.py      # RAG & retrieval
│   │   │   │   └── agent_service.py    # Agent execution
│   │   │   └── utils/
│   │   │       ├── __init__.py
│   │   │       ├── document_loader.py  # PDF, URL, text loading
│   │   │       └── logging_config.py   # Logging setup
│   │   └── __init__.py
│   ├── main.py                          # FastAPI app entry point
│   ├── requirements.txt                # Python dependencies
│   └── .env                            # Environment variables (DO NOT COMMIT)
│
├── front-end/
│   ├── app.py                          # Streamlit interface
│   ├── config.py                       # Frontend settings
│   ├── requirements.txt                # Streamlit dependencies
│   └── .env                            # Frontend env (optional)
│
├── .gitignore                          # Git ignore rules
└── README.md                           # Project documentation

```

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd back-end
   ```

2. **Create and activate virtual environment**
   ```bash
   # Create venv
   python -m venv .venv
   
   # Activate (Windows)
   .venv\Scripts\activate
   
   # Activate (macOS/Linux)
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy `.env` template and fill in API keys:
     - [Google API Key / Gemini API Key](https://aistudio.google.com/app/apikey)
     - [Google Custom Search ID (CSE_ID)](https://programmablesearchengine.google.com/)
     - [LangSmith API Key](https://smith.langchain.com/)

5. **Run FastAPI server**
   ```bash
   python src/main.py
   ```
   Server runs at `http://127.0.0.1:8000`

### Frontend Setup

1. **In a new terminal, navigate to frontend directory**
   ```bash
   cd front-end
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run Streamlit app**
   ```bash
   streamlit run app.py
   ```
   App opens at `http://localhost:8501`

## API Endpoints

- `POST /chat` — Send a message to the chatbot
- `POST /upload-document` — Upload PDF/documents for RAG
- `GET /trace/{trace_id}` — Retrieve LangSmith trace
- `GET /health` — Health check

## Features

### 3 Specialized Agents

1. **Research Agent**: Searches the internet using Google Search API, returns web sources
2. **RAG Agent**: Retrieves from FAISS vector store, generates answers from uploaded documents
3. **Image Analysis Agent**: Extracts text from images using EasyOCR, analyzes content

### LangSmith Integration
- All agent executions traced
- Tool calls logged
- Chain steps visible in dashboard
- [LangSmith Dashboard](https://smith.langchain.com/)

## Architecture

The chatbot follows a modular architecture:
- **Config** → Environment management & settings
- **LLM** → Groq integration, prompts, schemas
- **Database** → FAISS vector store
- **Services** → Search, OCR, RAG, agent execution
- **API** → FastAPI endpoints
- **Frontend** → Streamlit UI

## Submission Components

1. **Project Structure** ✓ (above)
2. **GitHub Repository** — Push complete source code
3. **LangSmith Traces** — Screenshots showing agent execution, tool usage, and workflow tracing

## LangSmith Setup

1. Create account at [smith.langchain.com](https://smith.langchain.com/)
2. Create new project
3. Copy API key to `.env` → `LANGSMITH_API_KEY`
4. Run chatbot and verify traces appear in dashboard

## Troubleshooting

- **Import errors**: Ensure venv is activated and all dependencies installed
- **API key errors**: Check `.env` file has valid API keys
- **FAISS errors**: Rebuild with `pip install faiss-cpu --upgrade`
- **LangSmith not showing traces**: Verify `LANGSMITH_API_KEY` and `LANGSMITH_PROJECT_NAME`

## Author
mr_captrox

## License
MIT
