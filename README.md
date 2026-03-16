# 🤖 Full-Stack AI Chatbot with LangGraph ReAct Agent

A complete full-stack AI chatbot application featuring:
- **LLM**: Google Gemini 1.5 Flash with LangSmith tracing
- **Agent**: LangGraph ReAct (Reasoning + Action) pattern
- **RAG**: ChromaDB vector database with document ingestion
- **Search**: Google Custom Search integration for web queries
- **OCR**: Gemini Vision for image text extraction
- **Frontend**: Streamlit web UI
- **Backend**: FastAPI with async/await

---

## 📋 Table of Contents

1. [Architecture Overview](#-architecture-overview)
2. [Project Structure](#-project-structure)
3. [Prerequisites](#-prerequisites)
4. [Setup Instructions](#-setup-instructions)
5. [Getting API Keys](#-getting-api-keys)
6. [Running the Application](#-running-the-application)
7. [API Endpoints](#-api-endpoints)
8. [Troubleshooting](#-troubleshooting)

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT FRONTEND (Port 8501)               │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Sidebar: Document/Image Upload, Settings               │  │
│  │  Main: Chat Interface with History                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │ HTTP/REST API Calls              │
└──────────────────────────────┼───────────────────────────────────┘
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│               FASTAPI BACKEND (Port 8000)                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  POST /chat          - Chat with ReAct Agent             │  │
│  │  POST /ingest/*      - Upload Documents/Images           │  │
│  │  GET /health         - Health Check                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌──────────┬────────────┬───────────────┬──────────────────┐  │
│  │          │            │               │                  │  │
│  ▼          ▼            ▼               ▼                  ▼  │
│ ┌─────┐ ┌─────┐ ┌──────────┐ ┌──────────────┐ ┌──────────┐  │
│ │ RAG │ │ OCR │ │  Search  │ │  LangGraph   │ │ ChromaDB │  │
│ │Tool │ │Tool │ │   Tool   │ │  ReAct Agent │ │(Persist) │  │
│ └─────┘ └─────┘ └──────────┘ └──────────────┘ └──────────┘  │
│              │                      │                          │
│              └──────────────────────┴──────────────┐           │
│                                                    ▼           │
│                            ┌─────────────────────────────┐    │
│                            │  Gemini 1.5 Flash LLM       │    │
│                            │  (via google-generativeai)  │    │
│                            └─────────────────────────────┘    │
│                                    │                           │
│                                    ▼                           │
│                        ┌──────────────────────┐               │
│                        │  LangSmith Tracer    │               │
│                        │  (Automatic via env) │               │
│                        └──────────────────────┘               │
└─────────────────────────────────────────────────────────────────┘
         │           │           │
         ▼           ▼           ▼
    ┌────────┐ ┌────────┐ ┌──────────┐
    │ .env   │ │chroma_ │ │  Google  │
    │Config  │ │db/     │ │   APIs   │
    └────────┘ └────────┘ └──────────┘
```

### Data Flow

1. **User Input** → Streamlit app sends message to FastAPI backend
2. **Message Processing** → Backend concatenates message with chat history
3. **Agent Invocation** → LangGraph ReAct agent decides which tool to use:
   - **RAG Tool**: Search uploaded documents
   - **Search Tool**: Query Google Custom Search
   - **OCR Tool**: Analyze uploaded images
   - **Direct Chat**: Answer from LLM knowledge
4. **LangSmith Tracing** → All agent interactions automatically traced
5. **Response** → Agent response sent back to frontend and displayed

---

## 📁 Project Structure

```
my-ai-chatbot/
├── backend/
│   ├── .venv/                      # Virtual environment (gitignored)
│   ├── src/chatbot/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── endpoints.py     # FastAPI routes
│   │   │       └── schemas.py       # Pydantic models
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py            # Configuration from .env
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   └── chromadb_client.py   # ChromaDB persistence
│   │   ├── llm/
│   │   │   ├── __init__.py
│   │   │   ├── llm_client.py        # Gemini LLM singleton
│   │   │   ├── embeddings.py        # Embedding model singleton
│   │   │   ├── prompts.py           # System prompts
│   │   │   ├── schemas.py           # Type definitions
│   │   │   └── workflow.py          # LangGraph ReAct agent
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── rag_service.py       # Document ingestion & retrieval
│   │   │   ├── search_service.py    # Internet search
│   │   │   └── ocr_service.py       # Image analysis
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── file_utils.py        # PDF/text/image utilities
│   └── requirements.txt
│
├── frontend/
│   └── app.py                       # Streamlit application
│
├── .env                             # Environment variables (create from .env.example)
├── .env.example                     # Example environment config
├── .gitignore                       # Git ignore rules
└── README.md                        # This file
```

---

## 📋 Prerequisites

- **Python 3.10+** (test with `python --version`)
- **pip** package manager (included with Python)
- **Git** (for version control)
- **API Keys:**
  - Google API Key (for Gemini LLM and embeddings)
  - Google Custom Search Engine ID & API Key (for web search)
  - LangSmith API Key (for agent tracing)

---

## 🚀 Setup Instructions

### Step 1: Clone/Create Project
```bash
cd c:\Users\captr\Downloads\my-ai-chatbot
```

### Step 2: Create Python Virtual Environment

**Windows (PowerShell):**
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**
```cmd
cd backend
python -m venv .venv
.venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (backend web framework)
- LangChain & LangGraph (agent orchestration)
- Streamlit (frontend)
- ChromaDB (vector database)
- Google Generative AI (LLM)
- And all other required packages

### Step 4: Setup Environment Variables

Copy `.env.example` to `.env`:

**Windows (PowerShell):**
```powershell
Copy-Item .\.env.example .\.env
```

**Mac/Linux:**
```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys (see [Getting API Keys](#-getting-api-keys) section):

```
GOOGLE_API_KEY=your_key_here
GOOGLE_CSE_ID=your_cse_id_here
GOOGLE_CSE_API_KEY=your_cse_api_key_here
LANGCHAIN_API_KEY=your_langsmith_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=final-chatbot
CHROMA_PERSIST_DIR=./chroma_db
```

---

## 🔑 Getting API Keys

### 1. Google API Key (for Gemini LLM & Embeddings)

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click **"Create API Key"**
3. Copy the key to `GOOGLE_API_KEY` in `.env`
4. **Note:** Free tier available with rate limits

### 2. Google Custom Search (for Internet Search)

**Create a Custom Search Engine:**

1. Visit [Programmable Search Engine](https://programmablesearchengine.google.com/)
2. Sign in with your Google account
3. Click **"Create"**
4. Set up to search the "Entire Web"
5. Get your **Search Engine ID (cx)** → `GOOGLE_CSE_ID`

**Get API Key:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable **"Custom Search API"**
4. Create credentials → **API Key**
5. Copy to `GOOGLE_CSE_API_KEY` in `.env`
6. **Note:** Free tier: 100 searches/day

### 3. LangSmith API Key (for Tracing)

1. Visit [LangSmith](https://smith.langchain.com/)
2. Create a free account
3. Go to **Settings** → **API Keys**
4. Create a new API key
5. Copy to `LANGCHAIN_API_KEY` in `.env`
6. **Note:** Free tier available; traces appear in web dashboard

---

## 🏃 Running the Application

### Terminal 1: Start Backend API

```bash
cd backend
# Activate venv if not already activated
# Windows: .\.venv\Scripts\Activate.ps1
# Mac/Linux: source .venv/bin/activate

# Run FastAPI server
uvicorn src.chatbot.api.v1.endpoints:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### Terminal 2: Start Frontend

Open a **NEW terminal** (keep the backend running):

```bash
cd frontend

# Activate venv (same virtual environment)
# Windows: ..\backend\.venv\Scripts\Activate.ps1
# Mac/Linux: source ../backend/.venv/bin/activate

# Run Streamlit app
streamlit run app.py
```

You should see:
```
  You can now view your Streamlit app in your browser.
  Local URL: http://localhost:8501
```

### Access the Application

Open your browser to: **http://localhost:8501**

---

## 📡 API Endpoints

### Health Check
```
GET /health
Response: {"status": "ok"}
```

### Chat with Agent
```
POST /chat
Body: {
  "message": "What is the capital of France?",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "collection_name": "default"
}
Response: {
  "response": "The capital of France is Paris...",
  "session_id": "550e8400-..."
}
```

### Ingest Document (PDF/TXT)
```
POST /ingest/document
Body: multipart/form-data
  - file: <PDF or TXT file>
  - collection_name: "default"
  
Response: {
  "status": "success",
  "message": "Successfully ingested document.pdf: stored 5 chunks",
  "collection_name": "default"
}
```

### Upload Image (PNG/JPG)
```
POST /ingest/image
Body: multipart/form-data
  - file: <PNG or JPG image>
  - session_id: "550e8400-..."
  
Response: {
  "status": "success",
  "message": "Image uploaded successfully. Session ID: ...",
  "collection_name": "550e8400-..."
}
```

### View Session Info
```
GET /session/{session_id}
Response: {
  "session_id": "550e8400-...",
  "messages": [...],
  "has_document": true,
  "has_image": false
}
```

---

## 🔍 Using LangSmith Tracing

LangSmith tracing is **automatically enabled** via environment variables:
- `LANGCHAIN_TRACING_V2=true`
- `LANGCHAIN_PROJECT=final-chatbot`

### View Traces

1. Visit [LangSmith Dashboard](https://smith.langchain.com/)
2. Go to **Projects** → **final-chatbot**
3. Each chat request creates a **trace** with:
   - Messages sent to the agent
   - Tools invoked (RAG, Search, OCR)
   - Tool inputs and outputs
   - Final response
   - Execution time and tokens used

### Example Trace Flow
```
Chat Request
    ↓
LangGraph Agent Execution
    ├→ Thinks about which tool to use
    ├→ Invokes RAG Tool (search documents)
    ├→ Invokes Internet Search Tool (if needed)
    ├→ Invokes OCR Tool (if image present)
    └→ Generates final response
    ↓
LangSmith Shows Complete Trace
```

---

## 🧪 Testing the Application

### Test 1: Health Check
```bash
curl http://localhost:8000/health
# Output: {"status":"ok"}
```

### Test 2: Simple Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is Python?",
    "session_id": "test-session",
    "collection_name": "default"
  }'
```

### Test 3: Upload Document & Query
1. Open Streamlit at http://localhost:8501
2. In sidebar, upload a PDF or TXT file
3. In chat, ask: "What is in the document?"
4. Agent should use RAG Tool to retrieve relevant content

### Test 4: Image Upload & Analysis
1. Upload an image (PNG/JPG) in sidebar
2. In chat, ask: "What's in the image?"
3. Agent should use OCR Tool to analyze the image

### Test 5: Internet Search
1. Ask: "What are the latest AI news from 2024?"
2. Agent should use Internet Search Tool
3. Response should include recent information

---

## 🐛 Troubleshooting

### Issue: Backend won't start
**Error:** `Address already in use`

**Solution:**
```bash
# Kill process on port 8000
# Windows PowerShell
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Mac/Linux
lsof -ti:8000 | xargs kill -9
```

### Issue: API key errors
**Error:** `GOOGLE_API_KEY environment variable is not set`

**Solution:**
1. Check `.env` file exists in project root
2. Verify all required keys are filled in
3. Restart backend after updating `.env`

### Issue: ChromaDB errors
**Error:** `Failed to initialize ChromaDB`

**Solution:**
1. Ensure `./chroma_db` directory is writable
2. Delete `chroma_db/` folder to reset database:
   ```bash
   rm -r chroma_db/  # Mac/Linux
   rmdir /s chroma_db  # Windows
   ```
3. Restart backend

### Issue: Frontend can't connect to backend
**Error:** `Cannot connect to backend API at http://localhost:8000`

**Solution:**
1. Verify backend is running (Terminal 1)
2. Check backend logs for errors
3. Ensure port 8000 is not blocked by firewall
4. Check CORS is enabled in `endpoints.py`

### Issue: Streamlit port already in use
**Error:** `Port 8501 is already running`

**Solution:**
```bash
# Run on different port
streamlit run app.py --server.port 8502
```

---

## 📚 How It Works

### ReAct Agent Loop

The agent follows this reasoning pattern:

```
User: "Analyze this image and tell me what it says"
     │
     ▼
Agent Thinks: "This request is about image analysis → Use OCR Tool"
     │
     ├─→ Invokes OCR Tool with image bytes
     │
     ├─→ Receives: "Image contains text: 'Hello World'"
     │
     ├─→ Thinks: "I have the image analysis, let me form response"
     │
     └─→ Returns: "The image contains the text 'Hello World'. [explanation]"
     │
     ▼
Frontend: Displays response to user
```

### Document RAG Flow

```
User: Uploads document.pdf
     │
     ▼
Backend: (ingest_document)
     │
     ├─→ Read PDF → extract text
     ├─→ Split into chunks (1000 char, 200 overlap)
     ├─→ Embed each chunk (GoogleGenerativeAIEmbeddings)
     ├─→ Store in ChromaDB with metadata
     │
     └─→ Ready for retrieval
     │
User: "What's in my document?"
     │
     ▼
Backend: (query_rag)
     │
     ├─→ Embed user question
     ├─→ Search ChromaDB for similar chunks
     ├─→ Return top-4 relevant chunks
     │
     └─→ Agent includes in response
```

---

## 📦 Dependencies Overview

| Package | Purpose |
|---------|---------|
| `fastapi` | Web framework for backend API |
| `uvicorn` | ASGI server to run FastAPI |
| `langchain` | LLM framework and tools |
| `langgraph` | Agent/workflow orchestration |
| `google-generativeai` | Gemini LLM access |
| `langchain-google-genai` | LangChain integration for Gemini |
| `chromadb` | Vector database for RAG |
| `streamlit` | Frontend web app framework |
| `pypdf` | PDF text extraction |
| `pillow` | Image processing |
| `pydantic-settings` | Configuration management |
| `requests` | HTTP client (frontend→backend) |

---

## 🔐 Security Considerations

**Current Implementation (Development):**
- ✓ API keys loaded from `.env` (not hardcoded)
- ✓ CORS enabled for frontend communication
- ✗ No authentication/authorization (use session_id only)
- ✗ No rate limiting
- ✗ Session data in memory only (lost on restart)

**For Production, Add:**
- User authentication (JWT tokens, OAuth)
- Database for persistent session storage
- Rate limiting (e.g., using Redis)
- HTTPS/TLS encryption
- Input validation and sanitization
- SQL injection protection (use ORM)
- API key rotation strategy
- Monitoring and alerts

---

## 🚀 Deployment

### Option 1: Heroku / Cloud Run

```bash
# Create requirements-prod.txt
pip freeze > requirements-prod.txt

# Deploy to Cloud Run
gcloud run deploy my-ai-chatbot \
  --source . \
  --platform managed \
  --region us-central1
```

### Option 2: Docker

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000 8501

CMD ["sh", "-c", "uvicorn src.chatbot.api.v1.endpoints:app --host 0.0.0.0 &  streamlit run frontend/app.py --server.port 8501"]
```

---

## 📝 Environment Variables Reference

```bash
# Google API Configuration
GOOGLE_API_KEY=your_gemini_api_key              # Required
GOOGLE_CSE_ID=your_search_engine_id             # Required for search
GOOGLE_CSE_API_KEY=your_google_search_api_key   # Required for search

# LangSmith Configuration (for tracing)
LANGCHAIN_API_KEY=your_langsmith_api_key        # Required
LANGCHAIN_TRACING_V2=true                       # Enable tracing
LANGCHAIN_PROJECT=final-chatbot                 # Project name

# Database Configuration
CHROMA_PERSIST_DIR=./chroma_db                  # Vector DB location
```

---

## 📞 Support & Resources

- **LangChain Docs:** https://python.langchain.com/
- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Streamlit Docs:** https://docs.streamlit.io/
- **ChromaDB Docs:** https://docs.trychroma.com/
- **Google AI Studio:** https://aistudio.google.com/

---

## 📜 License

This project is provided as-is for educational and development purposes.

---

## 🎯 Next Steps

1. **Set up API keys** (see [Getting API Keys](#-getting-api-keys))
2. **Install dependencies** with `pip install -r requirements.txt`
3. **Start backend** with `uvicorn src.chatbot.api.v1.endpoints:app --reload`
4. **Start frontend** with `streamlit run app.py`
5. **Chat with your AI agent!** 🚀

---

**Happy chatting! 🤖💬**
