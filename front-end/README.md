# Frontend - Streamlit UI

Interactive web interface for the AI Chatbot application.

## Quick Start

### 1. Navigate to Frontend Directory
```bash
cd front-end
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

**Note**: If you don't have a global Python environment, use the backend's venv:
```bash
# Activate backend venv first
cd ../back-end
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Then navigate to frontend and install
cd ../front-end
pip install -r requirements.txt
```

### 3. Run Streamlit App
```bash
streamlit run app.py
```

The app will automatically open at: `http://localhost:8501`

## Features

### 💬 Chat Interface
- Send messages to the chatbot
- View conversation history
- See agent responses and sources

### 👥 Agent Selection
- **Research Agent**: Search the web for current information
- **RAG Agent**: Query your uploaded documents
- **Image Agent**: Extract text from images (when integrated)

### 📖 Knowledge Base Management
- Upload TXT, Markdown, and PDF files
- Documents are automatically processed into chunks
- Indexed in FAISS for semantic search

### 📚 Source Display
- View sources for each retrieved document
- Click links to visit original sources
- See relevance scores

### ⚙️ Settings
- Toggle agents on/off
- Monitor API connection status
- Manage knowledge base

## Usage Tips

1. **Start the Backend First**
   - Open terminal and run: `cd back-end && python src/main.py`
   - Wait for "Application startup complete"

2. **Upload Documents**
   - Use sidebar to upload PDF/TXT files
   - Documents are processed into chunks for RAG
   - Check knowledge base size in sidebar

3. **Ask Questions**
   - Select which agents to use
   - Type your question in the chat box
   - View multi-agent responses with sources

4. **Use Web Search**
   - Enable Research Agent
   - Questions trigger web search
   - Results are cited with links

## Configuration

Create `.env` file in `front-end/` directory:
```env
STREAMLIT_API_URL=http://localhost:8000
```

## Troubleshooting

### "Cannot connect to chatbot API"
- **Solution**: Start backend: `python src/main.py` in `back-end/` directory
- **Check**: API should be running on `http://localhost:8000`

### Streamlit not starting
- **Solution**: `pip install streamlit --upgrade`
- **Check**: Python 3.8+ is required

### File upload not working
- **Solution**: Ensure backend is running and `/upload-document` endpoint is accessible
- **Check**: Backend logs for errors

### Slow responses
- **Solution**: Reduce number of agents or RAG search results
- **Note**: First response may be slow as models load into memory

## Project Structure
```
front-end/
├── app.py              # Streamlit application
├── config.py          # Frontend settings (optional)
├── requirements.txt   # Python dependencies
└── .env              # Environment variables
```

## Advanced Usage

### Custom API Endpoint
Edit `.env`:
```env
STREAMLIT_API_URL=http://your-server:8000
```

### Adding Chat Persistence
Modify session state handling in `app.py` to save messages to a database.

### Custom Styling
Edit the CSS in the `st.markdown()` components to match your branding.

## Performance Notes

- First chat may take 3-5 seconds as LLM loads
- RAG searches are faster after initial load
- Web searches depend on internet speed
- Image OCR processing depends on image size

## Development

### Hot Reload
Streamlit automatically reloads when you save changes to `app.py`.

### Debug Mode
Run with: `streamlit run app.py --logger.level=debug`

### Caching
Streamlit caches API responses. Clear cache with: `Ctrl+C` in the browser or restart Streamlit.
