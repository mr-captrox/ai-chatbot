# Backend API

FastAPI backend for the AI Chatbot application.

## Quick Start

### 1. Navigate to Backend Directory
```bash
cd back-end
```

### 2. Activate Virtual Environment
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies
If not already installed:
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Copy `.env` template and fill in API keys:
```bash
# .env file should contain:
GROQ_API_KEY=your_groq_api_key
GOOGLE_GEMINI_API_KEY=your_google_gemini_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

### 5. Run FastAPI Server
```bash
python src/main.py
```

Server will start at: `http://127.0.0.1:8000`

## API Endpoints

### Chat
- **URL**: `POST /api/v1/chat`
- **Body**:
  ```json
  {
    "message": "What is machine learning?",
    "agent_types": ["research", "rag"],
    "use_image": false
  }
  ```

### Upload Document
- **URL**: `POST /api/v1/upload-document`
- **Body**:
  ```json
  {
    "document_name": "example.pdf",
    "document_type": "pdf",
    "content": "document content",
    "tags": ["tag1", "tag2"]
  }
  ```

### Health Check
- **URL**: `GET /api/v1/health`
- **Response**: Status of all services

## API Documentation
Interactive API docs available at: `http://127.0.0.1:8000/docs`

## Project Structure
```
back-end/
├── .venv/              # Virtual environment (do not commit)
├── src/
│   ├── chatbot/
│   │   ├── api/v1/     # FastAPI routes
│   │   ├── core/       # Configuration
│   │   ├── database/   # Vector store
│   │   ├── llm/        # LLM & agents
│   │   ├── services/   # Business logic
│   │   └── utils/      # Utilities
│   └── main.py         # App entry point
├── requirements.txt    # Python dependencies
└── .env               # Environment variables (git-ignored)
```

## Key Components

### Core
- `config.py`: Loads environment variables and centralizes settings

### LLM
- `llm_data.py`: Groq LLM initialization
- `embeddings.py`: HuggingFace embeddings provider
- `prompts.py`: Prompt templates for each agent
- `schemas.py`: Pydantic data models

### Database
- `vector_store.py`: FAISS wrapper for similarity search

### Services
- `search_service.py`: Google Search integration
- `ocr_service.py`: EasyOCR for text extraction
- `rag_service.py`: RAG pipeline
- `agent_service.py`: Agent orchestration

### API
- `endpoints.py`: FastAPI routes
- `schemas.py`: Request/response models

## Troubleshooting

### `ModuleNotFoundError: No module named 'langchain'`
- **Solution**: Ensure venv is activated and `pip install -r requirements.txt` completed

### `GROQ_API_KEY not found`
- **Solution**: Check `.env` file has `GROQ_API_KEY=your_key`

### Port 8000 already in use
- **Solution**: Change `API_PORT` in `.env` or kill process using port 8000

### FAISS import error
- **Solution**: `pip install faiss-cpu --upgrade`

## LangSmith Integration

All agent executions are automatically traced in LangSmith. To view traces:

1. Set `LANGSMITH_API_KEY` in `.env`
2. Set `LANGSMITH_PROJECT_NAME` in `.env`
3. Go to https://smith.langchain.com/
4. Select your project
5. See all traces with agent steps, tool calls, and timing

## Development Notes

- The application uses LangSmith's `@traceable` decorator for automatic tracing
- All tool calls and agent executions are captured
- Traces show the full execution flow with inputs/outputs
