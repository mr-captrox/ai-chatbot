"""
Streamlit frontend for the AI Chatbot application.

This module provides a user-friendly web interface for interacting with
the AI chatbot that includes:
- Document upload (PDF/TXT) for RAG
- Image upload (PNG/JPG) for OCR
- Chat interface with conversation history
- Session management

Run with: streamlit run app.py
"""

import io
import requests
import streamlit as st
from uuid import uuid4
from pathlib import Path

# Configuration
BACKEND_URL = "http://localhost:8000"
UPLOAD_SIZE_LIMIT = 20 * 1024 * 1024  # 20 MB


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid4())
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "collection_name" not in st.session_state:
        st.session_state.collection_name = "default"
    
    if "uploaded_image" not in st.session_state:
        st.session_state.uploaded_image = None
    
    if "uploaded_image_name" not in st.session_state:
        st.session_state.uploaded_image_name = None

    if "api_status" not in st.session_state:
        st.session_state.api_status = None


def check_api_health():
    """Check if the backend API is running."""
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def upload_document(uploaded_file, collection_name: str) -> bool:
    """
    Upload a document to the backend for RAG processing.
    
    Args:
        uploaded_file: Streamlit UploadedFile object.
        collection_name: Collection name for storage.
        
    Returns:
        True if upload succeeded, False otherwise.
    """
    try:
        files = {
            "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        params = {"collection_name": collection_name}
        
        response = requests.post(
            f"{BACKEND_URL}/ingest/document",
            files=files,
            params=params,
            timeout=30,
        )
        
        if response.status_code == 200:
            result = response.json()
            st.success(f"✓ {result['message']}")
            return True
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"✗ Upload failed: {error_detail}")
            return False
    except requests.exceptions.RequestException as e:
        st.error(f"✗ Connection error: {str(e)}")
        return False
    except Exception as e:
        st.error(f"✗ Error: {str(e)}")
        return False


def upload_image(uploaded_file, session_id: str):
    """
    Upload an image to the backend for OCR processing.
    
    Args:
        uploaded_file: Streamlit UploadedFile object.
        session_id: Current session ID.
    """
    try:
        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
        params = {"session_id": session_id}
        
        response = requests.post(
            f"{BACKEND_URL}/ingest/image",
            files=files,
            params=params,
            timeout=30,
        )
        
        if response.status_code == 200:
            result = response.json()
            st.session_state.uploaded_image = uploaded_file.getvalue()
            st.session_state.uploaded_image_name = uploaded_file.name
            st.success(f"✓ Image uploaded: {uploaded_file.name}")
        else:
            error_detail = response.json().get("detail", "Unknown error")
            st.error(f"✗ Image upload failed: {error_detail}")
    except requests.exceptions.RequestException as e:
        st.error(f"✗ Connection error: {str(e)}")
    except Exception as e:
        st.error(f"✗ Error: {str(e)}")


def send_message(user_message: str) -> str:
    """
    Send a user message to the chatbot and get a response.
    
    Args:
        user_message: Text message from the user.
        
    Returns:
        Assistant response or error message.
    """
    try:
        # If image is uploaded, mention it
        if st.session_state.uploaded_image_name:
            full_message = f"{user_message}\n[Image uploaded: {st.session_state.uploaded_image_name}]"
        else:
            full_message = user_message
        
        payload = {
            "message": full_message,
            "session_id": st.session_state.session_id,
            "collection_name": st.session_state.collection_name,
        }
        
        response = requests.post(
            f"{BACKEND_URL}/chat",
            json=payload,
            timeout=60,
        )
        
        if response.status_code == 200:
            result = response.json()
            return result["response"]
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return f"Error: {error_detail}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. The agent took too long to respond."
    except requests.exceptions.RequestException as e:
        return f"Error: Connection failed - {str(e)}"
    except Exception as e:
        return f"Error: {str(e)}"


def render_sidebar():
    """Render the sidebar with upload controls and settings."""
    with st.sidebar:
        st.title("⚙️ Settings")
        
        # Collection name input
        st.session_state.collection_name = st.text_input(
            "Collection Name",
            value=st.session_state.collection_name,
            help="ChromaDB collection for RAG storage",
        )
        
        st.divider()
        
        # Document upload section
        st.subheader("📄 Upload Document (RAG)")
        st.write("Upload PDF or TXT files to enable document-based Q&A")
        
        doc_file = st.file_uploader(
            "Choose a document",
            type=["pdf", "txt"],
            key="doc_uploader",
        )
        
        if doc_file:
            if st.button("📤 Upload Document", key="upload_doc_btn"):
                with st.spinner("Uploading document..."):
                    upload_document(doc_file, st.session_state.collection_name)
        
        st.divider()
        
        # Image upload section
        st.subheader("🖼️ Upload Image (OCR)")
        st.write("Upload images for text extraction and analysis")
        
        img_file = st.file_uploader(
            "Choose an image",
            type=["png", "jpg", "jpeg"],
            key="img_uploader",
        )
        
        if img_file:
            if st.button("📤 Upload Image", key="upload_img_btn"):
                with st.spinner("Uploading image..."):
                    upload_image(img_file, st.session_state.session_id)
        
        # Show uploaded image
        if st.session_state.uploaded_image_name:
            st.success(f"✓ Image loaded: {st.session_state.uploaded_image_name}")
        
        st.divider()
        
        # API health check
        if st.button("🔍 Check API Status"):
            if check_api_health():
                st.success("✓ API is running at http://localhost:8000")
            else:
                st.error("✗ Cannot connect to backend API at http://localhost:8000")
        
        st.divider()
        
        # Session info
        st.subheader("📋 Session Info")
        st.write(f"**Session ID:**")
        st.code(st.session_state.session_id, language=None)
        st.write(f"**Messages:** {len(st.session_state.messages)}")
        st.write(f"**Collection:** {st.session_state.collection_name}")
        
        # LangSmith info
        st.divider()
        st.subheader("🔗 LangSmith Tracing")
        st.write(
            "Chat traces are automatically sent to **LangSmith** project: `final-chatbot`"
        )
        st.markdown(
            "[View traces on LangSmith →](https://smith.langchain.com/)",
            unsafe_allow_html=True,
        )


def render_main_chat():
    """Render the main chat area."""
    st.title("🤖 AI Chatbot")
    st.write("Ask me anything! I can search documents, the web, analyze images, and more.")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    user_input = st.chat_input("Type your message here...")
    
    if user_input:
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get response from backend
        with st.spinner("🤔 Thinking..."):
            response = send_message(user_input)
        
        # Add assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
        })
        
        # Display assistant message
        with st.chat_message("assistant"):
            st.write(response)


def main():
    """Main application entry point."""
    # Configure Streamlit page
    st.set_page_config(
        page_title="AI Chatbot",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Custom CSS for better styling
    st.markdown(
        """
        <style>
        .main {
            max-width: 1000px;
        }
        .stChatMessage {
            padding: 1rem;
            border-radius: 0.5rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Render UI
    render_sidebar()
    render_main_chat()


if __name__ == "__main__":
    main()
