"""
Streamlit web interface for the Chatbot application.
Provides user-friendly chat UI, document upload, and visualization.
"""

import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
import base64
from typing import List, Optional

# Load environment
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)
import uuid

# Initialize session state for thread ID
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# API Configuration
API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000")
API_CHAT = f"{API_URL}/api/v1/chat"
API_UPLOAD = f"{API_URL}/api/v1/upload-document"
API_UPLOAD_FILE = f"{API_URL}/api/v1/upload-file"
API_HEALTH = f"{API_URL}/api/v1/health"
API_QUOTA = f"{API_URL}/api/v1/quota"


# Styling
st.markdown("""
<style>
    .chat-message {
        padding: 1.5rem; 
        border-radius: 0.5rem; 
        margin-bottom: 1rem; 
        display: flex
    }
    .chat-message.user {
        background-color: #e3f2fd
    }
    .chat-message.assistant {
        background-color: #f5f5f5
    }
    .source-box {
        background-color: #fffacd;
        padding: 1rem;
        border-left: 4px solid #ffd700;
        margin: 0.5rem 0;
        border-radius: 0.25rem;
    }
</style>
""", unsafe_allow_html=True)


def check_api_health() -> bool:
    """Check if API is running."""
    try:
        response = requests.get(API_HEALTH, timeout=5)
        return response.status_code == 200
    except:
        return False


def get_quota_status() -> Optional[dict]:
    """Get current rate limit status."""
    try:
        response = requests.get(API_QUOTA, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None


def send_message(message: str, agents: list, image_data: Optional[str] = None) -> Optional[dict]:
    """
    Send message to chatbot API.

    Args:
        message: User message
        agents: List of agents to use
        image_data: Optional base64 image data

    Returns:
        API response
    """
    try:
        payload = {
            "message": message,
            "agent_types": agents,
            "use_image": "image_analysis" in agents,
            "image_data": image_data,
            "thread_id": st.session_state.thread_id,
        }

        response = requests.post(
            API_CHAT,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            st.error(f"🛑 RATE LIMIT: {e.response.json().get('detail')}")
        else:
            st.error(f"❌ API Error: {str(e)}")
        return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to chatbot API. Is the backend server running?")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def upload_document(file_path: str, file_name: str) -> Optional[dict]:
    """
    Upload document to chatbot knowledge base.

    Args:
        file_path: Path to file
        file_name: Display name

    Returns:
        Upload response
    """
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f)}
            response = requests.post(
                API_UPLOAD_FILE,
                files=files,
                timeout=60,
            )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        st.error(f"❌ Upload failed: {str(e)}")
        return None


# Main UI
st.title("🤖 AI Chatbot")
st.markdown("*Powered by Meta Llama 3 via Groq, LangChain, and FAISS*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Initialize variables for conditional UI
    uploaded_file = None
    uploaded_image = None

    # Check API status
    if check_api_health():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline - Backend not running")
        st.info("Run: `python main.py` in the back-end directory")

    # Show Quota (Rate Limit)
    quota = get_quota_status()
    if quota:
        remaining = quota.get("remaining", 0)
        wait_time = quota.get("wait_time", 0)
        
        st.write(f"📊 **Request Sho-down**")
        if remaining > 0:
            st.info(f"Requests remaining: {remaining}/10")
        else:
            st.warning(f"LIMIT REACHED! Wait {wait_time}s")
            st.progress(0)
        
        if remaining < 10:
            # Simple visualization of used quota
            st.progress(remaining / 10)

    st.divider()

    # Agent selection
    st.subheader("👥 Agents")
    
    # New Chat / Reset Thread
    if st.button("🔄 New Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.thread_id = str(uuid.uuid4())
        st.rerun()

    use_research = st.checkbox("🔍 LLM & Research", value=True, help="General chat and web research")
    use_rag = st.checkbox("📚 RAG Agent", value=False, help="Chat with your documents")
    use_ocr = st.checkbox("🖼️ OCR Agent", value=False, help="Extract text from images")

    st.divider()

    # Conditional RAG uploader
    if use_rag:
        st.subheader("📖 Knowledge Base")
        
        # Get Knowledge Base Size
        try:
            kb_size = requests.get(f"{API_URL}/api/v1/health", timeout=2).json()["services"].get("vector_db_size", 0)
            st.caption(f"Status: {kb_size} document segments indexed.")
        except:
            pass

        uploaded_file = st.file_uploader(
            "Upload document (TXT, MD, PDF)",
            type=["txt", "md", "pdf"],
            key="rag_uploader"
        )

        if uploaded_file:
            if st.button("📤 Add to Knowledge Base", type="primary"):
                with st.spinner("Processing document..."):
                    import tempfile
                    temp_dir = tempfile.gettempdir()
                    temp_path = os.path.join(temp_dir, uploaded_file.name)
                    with open(temp_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    result = upload_document(temp_path, uploaded_file.name)
                    if result:
                        if result.get("success"):
                            st.session_state.upload_message = {"type": "success", "msg": f"✅ {result.get('chunks_created')} chunks indexed!"}
                            st.rerun()
                        else:
                            st.session_state.upload_message = {"type": "error", "msg": f"❌ {result.get('message', 'Upload failed without an error message.')}"}
                    
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
        
        # Display persistent upload message
        if "upload_message" in st.session_state:
            if st.session_state.upload_message["type"] == "success":
                st.success(st.session_state.upload_message["msg"])
            else:
                st.error(st.session_state.upload_message["msg"])
            # Clear it after showing once
            del st.session_state.upload_message
        st.divider()

    # Conditional OCR uploader
    if use_ocr:
        st.subheader("🖼️ Image Extraction")
        uploaded_image = st.file_uploader(
            "Upload image for OCR",
            type=["jpg", "png", "jpeg"],
            key="ocr_uploader"
        )
        
        if uploaded_image:
            st.image(uploaded_image, caption="Current Image", use_container_width=True)
            if st.button("🔍 Extract Text"):
                st.info("🔄 OCR is active. This will explain the text content to the Chatbot.")
        st.divider()

    # About
    st.subheader("ℹ️ About")
    st.markdown("""
    **AI Chatbot with Specialized Agents**

    - **LLM & Search**: General logic and web research
    - **RAG Agent**: Retrieves from uploaded documents
    - **Image Agent**: Extracts text from images

    **Tech Stack**
    - Backend: FastAPI + LangChain
    - LLM: Meta Llama 3 (via Groq)
    - Vector DB: FAISS
    - Search: Tavily AI
    - Frontend: Streamlit
    """)


# Main chat area
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("💬 Chat")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant"):
            st.write(message["content"])
            if "sources" in message and message["sources"]:
                st.markdown("**📚 Sources:**")
                for source in message["sources"]:
                    with st.expander(f"📖 {source.get('title', 'Unknown')}"):
                        st.write(source.get("excerpt", "No excerpt"))
                        if source.get("url"):
                            st.write(f"🔗 [Link]({source['url']})")

# Chat input
user_input = st.chat_input("Type your message...")

if user_input:
    # Add user message to session state
    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    # Display user message
    with st.chat_message("user"):
        st.write(user_input)

        # Prepare agents
        agents = []
        if use_research:
            agents.append("research")
        if use_rag:
            agents.append("rag")
        if use_ocr:
            agents.append("image_analysis")

        if not agents:
            st.error("❌ Please select at least one agent")
        else:
            # Process image if OCR is selected
            b64_image = None
            if use_ocr and uploaded_image:
                try:
                    img_bytes = uploaded_image.getvalue()
                    b64_image = base64.b64encode(img_bytes).decode("utf-8")
                except Exception as e:
                    st.error(f"Error encoding image: {str(e)}")

            # Get response from chatbot
            with st.spinner("🤔 Thinking..."):
                response = send_message(user_input, agents, image_data=b64_image)

        if response:
            # Display assistant response
            with st.chat_message("assistant"):
                st.write(response.get("message", "No response"))

                # Display sources from agents
                if response.get("agent_responses"):
                    all_sources = []
                    for agent_resp in response["agent_responses"]:
                        if agent_resp.get("sources"):
                            all_sources.extend(agent_resp["sources"])

                    if all_sources:
                        st.markdown("**📚 Sources:**")
                        for source in all_sources:
                            with st.expander(
                                f"📖 {source.get('title', 'Unknown')} "
                                f"({source.get('relevance_score', 0):.0%})"
                            ):
                                st.write(source.get("excerpt", "No excerpt"))
                                if source.get("url"):
                                    st.write(f"🔗 [Link]({source['url']})")

                # Show trace if available
                if response.get("trace_id"):
                    st.caption(f"🔗 Trace: {response['trace_id']}")

            # Add to session state
            st.session_state.messages.append({
                "role": "assistant",
                "content": response.get("message", "No response"),
                "sources": all_sources if all_sources else []
            })
