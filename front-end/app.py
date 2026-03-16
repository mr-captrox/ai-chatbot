"""
Streamlit web interface for the Chatbot application.
Provides user-friendly chat UI, document upload, and visualization.
"""

import os
from pathlib import Path

import requests
import streamlit as st
from dotenv import load_dotenv
from PIL import Image

# Load environment
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# API Configuration
API_URL = os.getenv("STREAMLIT_API_URL", "http://localhost:8000")
API_CHAT = f"{API_URL}/api/v1/chat"
API_UPLOAD = f"{API_URL}/api/v1/upload-document"
API_HEALTH = f"{API_URL}/api/v1/health"


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


def send_message(message: str, agents: list) -> dict:
    """
    Send message to chatbot API.

    Args:
        message: User message
        agents: List of agents to use

    Returns:
        API response
    """
    try:
        payload = {
            "message": message,
            "agent_types": agents,
            "use_image": "image_analysis" in agents,
        }

        response = requests.post(
            API_CHAT,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to chatbot API. Is the backend server running?")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None


def upload_document(file_path: str, file_name: str) -> dict:
    """
    Upload document to chatbot knowledge base.

    Args:
        file_path: Path to file
        file_name: Display name

    Returns:
        Upload response
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        payload = {
            "document_name": file_name,
            "document_type": "text",
            "content": content,
            "tags": ["uploaded"],
        }

        response = requests.post(
            API_UPLOAD,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        return response.json()

    except Exception as e:
        st.error(f"❌ Upload failed: {str(e)}")
        return None


# Main UI
st.title("🤖 AI Chatbot")
st.markdown("*Powered by Groq LLM, LangChain, and FAISS*")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")

    # Check API status
    if check_api_health():
        st.success("✅ API Connected")
    else:
        st.error("❌ API Offline - Backend not running")
        st.info("Run: `python src/main.py` in the back-end directory")

    st.divider()

    # Agent selection
    st.subheader("👥 Agents")
    use_research = st.checkbox("🔍 LLM & Basic Searches", value=True)
    use_rag = st.checkbox("📚 RAG (Document)", value=True)
    use_ocr = st.checkbox("🖼️ Image Agent (OCR)", value=False)

    st.divider()

    # Knowledge base management
    st.subheader("📖 Knowledge Base")

    uploaded_file = st.file_uploader(
        "Upload document (TXT, MD, PDF)",
        type=["txt", "md", "pdf"]
    )

    if uploaded_file:
        if st.button("📤 Add to Knowledge Base"):
            with st.spinner("Uploading..."):
                # Save temp file using OS temporary directory
                import tempfile

                temp_dir = tempfile.gettempdir()
                temp_path = os.path.join(temp_dir, uploaded_file.name)
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getbuffer())

                # Upload
                result = upload_document(temp_path, uploaded_file.name)
                if result and result.get("success"):
                    st.success(f"✅ {result.get('chunks_created')} chunks added!")
                os.remove(temp_path)

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
    - LLM: Groq (GPT-OSS 120B)
    - Vector DB: FAISS
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
        # Get response from chatbot
        with st.spinner("🤔 Thinking..."):
            response = send_message(user_input, agents)

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
