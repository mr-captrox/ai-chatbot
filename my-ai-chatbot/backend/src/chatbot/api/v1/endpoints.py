"""
FastAPI endpoints for the AI chatbot API.

This module defines all REST API endpoints:
- POST /chat - Chat with the AI agent
- POST /ingest/document - Upload documents for RAG
- POST /ingest/image - Upload images for OCR
- GET /health - Health check
"""

from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from ...core.config import settings
from ...llm.workflow import invoke_agent
from ...services.ocr_service import analyze_image
from ...services.rag_service import ingest_document
from .schemas import ChatRequest, ChatResponse, HealthResponse, IngestResponse

# Initialize FastAPI app
app = FastAPI(
    title="AI Chatbot API",
    description="Full-stack AI chatbot with RAG, OCR, and web search capabilities",
    version="1.0.0",
)

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (message history)
# In production, use a real database
session_history: dict[str, list[dict[str, str]]] = {}
session_uploads: dict[str, dict[str, Optional[bytes]]] = {}


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        JSON response with status "ok" if the API is operational.
    """
    return HealthResponse(status="ok")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat endpoint to interact with the AI agent.
    
    The agent:
    1. Accesses conversation history from session_id
    2. Appends the new user message
    3. Invokes the LangGraph ReAct agent
    4. Stores assistant response in history
    5. Returns response to client
    
    Args:
        request: ChatRequest with message, session_id, and collection_name.
        
    Returns:
        ChatResponse with assistant's response and session_id.
        
    Raises:
        HTTPException 400: If session_id is invalid or message is empty.
        HTTPException 500: If agent invocation fails.
        
    Example:
        POST /chat
        {
            "message": "What is in my document?",
            "session_id": "550e8400...",
            "collection_name": "default"
        }
    """
    try:
        session_id = request.session_id
        message = request.message.strip()
        collection_name = request.collection_name

        if not message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        # Initialize session if new
        if session_id not in session_history:
            session_history[session_id] = []
            session_uploads[session_id] = {"document": None, "image": None}

        # Append user message to history
        session_history[session_id].append({"role": "user", "content": message})

        # Get any uploaded files/images for this session
        uploaded_doc = session_uploads[session_id].get("document")
        uploaded_img = session_uploads[session_id].get("image")

        # Invoke the agent with session history
        response = invoke_agent(
            messages=session_history[session_id],
            uploaded_file_bytes=uploaded_doc,
            uploaded_image_bytes=uploaded_img,
        )

        # Store assistant response in history
        session_history[session_id].append({"role": "assistant", "content": response})

        return ChatResponse(response=response, session_id=session_id)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid request: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Agent error: {str(e)}",
        )


@app.post("/ingest/document", response_model=IngestResponse)
async def ingest_document_endpoint(
    file: UploadFile = File(...),
    collection_name: str = "default",
):
    """
    Ingest a document (PDF or TXT) into the RAG system.
    
    The document is:
    1. Read and validated (PDF or TXT only)
    2. Split into chunks
    3. Embedded using GoogleGenerativeAIEmbeddings
    4. Stored in ChromaDB collection
    
    Args:
        file: Uploaded file (PDF or TXT).
        collection_name: Collection to store in (default: "default").
        
    Returns:
        IngestResponse with ingestion status and message.
        
    Raises:
        HTTPException 400: If file format is not PDF or TXT.
        HTTPException 500: If ingestion fails.
        
    Example:
        POST /ingest/document
        Content-Type: multipart/form-data
        file: <binary PDF/TXT file>
        collection_name: my_docs
    """
    try:
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="File name is required")

        # Validate file extension
        if not filename.lower().endswith((".pdf", ".txt")):
            raise HTTPException(
                status_code=400,
                detail="Only PDF and TXT files are supported",
            )

        # Read file content
        file_bytes = await file.read()
        if not file_bytes:
            raise HTTPException(status_code=400, detail="File is empty")

        # Ingest document
        result_message = ingest_document(file_bytes, filename, collection_name)

        return IngestResponse(
            status="success",
            message=result_message,
            collection_name=collection_name,
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Ingestion error: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to ingest document: {str(e)}",
        )


@app.post("/ingest/image", response_model=IngestResponse)
async def ingest_image_endpoint(
    file: UploadFile = File(...),
    session_id: Optional[str] = None,
):
    """
    Upload an image for OCR analysis.
    
    The image is:
    1. Validated (PNG, JPG, JPEG only)
    2. Stored in session state for OCR reference
    
    The next /chat request can then analyze this image.
    
    Args:
        file: Uploaded image file (PNG, JPG, JPEG).
        session_id: Optional session ID. If not provided, a new one is generated.
        
    Returns:
        IngestResponse with success status and new/existing session_id in message.
        
    Raises:
        HTTPException 400: If file format is not PNG/JPG/JPEG.
        HTTPException 500: If image storage fails.
        
    Example:
        POST /ingest/image
        Content-Type: multipart/form-data
        file: <binary PNG/JPG file>
        session_id: 550e8400-...
    """
    try:
        filename = file.filename
        if not filename:
            raise HTTPException(status_code=400, detail="File name is required")

        # Validate file extension
        if not filename.lower().endswith((".png", ".jpg", ".jpeg")):
            raise HTTPException(
                status_code=400,
                detail="Only PNG, JPG, and JPEG images are supported",
            )

        # Read image content
        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Image file is empty")

        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid4())

        # Initialize session if new
        if session_id not in session_uploads:
            session_history[session_id] = []
            session_uploads[session_id] = {"document": None, "image": None}

        # Store image in session
        session_uploads[session_id]["image"] = image_bytes

        return IngestResponse(
            status="success",
            message=f"Image uploaded successfully. Session ID: {session_id}. Include this session ID in your next chat request to analyze the image.",
            collection_name=session_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}",
        )


# Additional helper endpoint: get session info
@app.get("/session/{session_id}")
async def get_session_info(session_id: str):
    """
    Get conversation history for a session (for debugging/monitoring).
    
    Args:
        session_id: Session identifier.
        
    Returns:
        JSON with conversation history for the session.
    """
    if session_id not in session_history:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "messages": session_history[session_id],
        "has_document": session_uploads[session_id]["document"] is not None,
        "has_image": session_uploads[session_id]["image"] is not None,
    }


if __name__ == "__main__":
    import uvicorn

    # Run the development server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
    )
