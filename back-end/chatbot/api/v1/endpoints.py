"""
FastAPI endpoints for the chatbot application.
Handles chat requests, document uploads, traces, and health checks.
"""

import time
from functools import lru_cache
from typing import List, Optional

from fastapi import APIRouter, File, UploadFile, HTTPException
from langsmith import traceable
from google.genai import types

from chatbot.api.v1.schemas import (
    ChatRequest,
    ChatResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
    HealthResponse,
    QuotaResponse,
    AgentResponse,
    AgentType,
    Source,
)
from chatbot.core.config import settings
from chatbot.llm.llm_data import get_llm
from chatbot.llm.prompts import research_agent_prompt, rag_agent_prompt, image_agent_prompt
from chatbot.services.search_service import TavilySearchService
from chatbot.services.rag_service import RAGService
from chatbot.services.ocr_service import OCRService
from chatbot.utils.logging_config import logger
from chatbot.utils.rate_limiter import limiter

router = APIRouter(prefix="/api/v1", tags=["chatbot"])

@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    return RAGService(str(settings.vector_db_path))


@lru_cache(maxsize=1)
def get_search_service():
    """Returns TavilySearchService for web searches."""
    return TavilySearchService()


@lru_cache(maxsize=1)
def get_ocr_service() -> OCRService:
    return OCRService()


@router.get("/quota", response_model=QuotaResponse)
async def get_quota() -> QuotaResponse:
    """Get current rate limit status."""
    remaining, wait_time = limiter.get_status("chat_limit")
    return QuotaResponse(
        remaining=remaining,
        limit=limiter.limit,
        period_seconds=limiter.period,
        wait_time=wait_time
    )


@router.post("/chat", response_model=ChatResponse)
@traceable(name="chat_endpoint")
async def chat(request: ChatRequest) -> ChatResponse:
    limiter.check("chat_limit")
    """
    Main chat endpoint. Routes requests to appropriate agents.

    Args:
        request: ChatRequest with user message and configuration

    Returns:
        ChatResponse with bot response and agent details
    """
    trace_id = None  # Will be set by LangSmith
    agent_responses: List[AgentResponse] = []

    try:
        llm = get_llm()
        thread_id = request.thread_id

        # Research Agent
        if AgentType.RESEARCH in request.agent_types:
            research_response = await _research_agent(request.message, llm, thread_id=thread_id)
            agent_responses.append(research_response)

        # RAG Agent (Document+Knowledge Base Search)
        if AgentType.RAG in request.agent_types:
            rag_response = await _rag_agent(request.message, llm, thread_id=thread_id)
            agent_responses.append(rag_response)

        # Image Analysis Agent
        if AgentType.IMAGE_ANALYSIS in request.agent_types:
            image_response = await _image_agent(request.message, request.image_data, llm, thread_id=thread_id)
            agent_responses.append(image_response)

        # Synthesize responses
        if agent_responses:
            combined_message = _synthesize_responses(request.message, agent_responses)
        else:
            combined_message = "No agents were selected for this query."

        return ChatResponse(
            message=combined_message,
            agent_responses=agent_responses,
            trace_id=trace_id,
        )

    except Exception as e:
        logger.error(f"Chat error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


async def _research_agent(query: str, llm, thread_id: Optional[str] = None) -> AgentResponse:
    """
    Execute Research Agent using Tavily Search.

    Args:
        query: User query
        llm: LLM instance
        thread_id: Optional thread ID

    Returns:
        AgentResponse from research
    """
    try:
        search_service = get_search_service()
        # Get search results
        sources = search_service.search(query, num_results=3)

        # Format context
        context = "\n".join([
            f"- {s.title}: {s.excerpt}" for s in sources
        ])

        # Generate response
        prompt = research_agent_prompt.format(input=query)
        response = llm.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{prompt}\n\nContext:\n{context}"
        )

        return AgentResponse(
            agent_type=AgentType.RESEARCH,
            answer=response.text or "I searched but couldn't find a definitive answer.",
            confidence=0.8,
            sources=sources,
        )

    except Exception as e:
        logger.error(f"Research agent error: {str(e)}")
        return AgentResponse(
            agent_type=AgentType.RESEARCH,
            answer=f"Research failed: {str(e)}",
            confidence=0.0,
            sources=[],
        )


import base64
from io import BytesIO

async def _image_agent(
    query: str,
    image_data: Optional[str],
    llm,
    thread_id: Optional[str] = None
) -> AgentResponse:
    """
    Execute Image Analysis Agent using OCR.
    
    Args:
        query: User query
        image_data: Base64 encoded image
        llm: LLM instance
        thread_id: Optional thread ID
        
    Returns:
        AgentResponse from image analysis
    """
    try:
        if not image_data:
            return AgentResponse(
                agent_type=AgentType.IMAGE_ANALYSIS,
                answer="No image was provided for analysis. Please upload an image in the sidebar.",
                confidence=0.0,
                sources=[],
            )

        ocr_service = get_ocr_service()
        
        # Decode base64 image
        header, encoded = image_data.split(",", 1) if "," in image_data else (None, image_data)
        image_bytes = base64.b64decode(encoded)
        
        # Extract text
        ocr_result = ocr_service.extract_text_with_layout(image_bytes)
        extracted_text = ocr_result.get("extracted_text", "")
        
        if not extracted_text.strip():
            return AgentResponse(
                agent_type=AgentType.IMAGE_ANALYSIS,
                answer="I couldn't detect any text in the uploaded image.",
                confidence=0.5,
                sources=[],
            )

        # Generate response using LLM to interpret extracted text
        prompt = f"""
        User Query: {query}
        Extracted Text from Image:
        {extracted_text}
        
        Based on the extracted text, please answer the user's query contextually.
        """
        response = llm.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return AgentResponse(
            agent_type=AgentType.IMAGE_ANALYSIS,
            answer=response.text or "I extracted text from the image but could not interpret a specific answer.",
            confidence=ocr_result.get("average_confidence", 0.5),
            sources=[Source(title="OCR Extraction", relevance_score=1.0, excerpt=extracted_text[:200])],
        )

    except Exception as e:
        logger.error(f"Image agent error: {str(e)}")
        return AgentResponse(
            agent_type=AgentType.IMAGE_ANALYSIS,
            answer=f"Image analysis failed: {str(e)}",
            confidence=0.0,
            sources=[],
        )


async def _rag_agent(query: str, llm, thread_id: Optional[str] = None) -> AgentResponse:
    """
    Execute RAG Agent using vector store retrieval.

    Args:
        query: User query
        llm: LLM instance
        thread_id: Optional thread ID

    Returns:
        AgentResponse from RAG
    """
    try:
        rag_service = get_rag_service()
        # Search vector store
        context, sources = rag_service.search_and_format(query, k=3)

        # Generate response using LLM
        prompt = rag_agent_prompt.format(input=query, context=context)
        response = llm.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return AgentResponse(
            agent_type=AgentType.RAG,
            answer=response.text or "I retrieved relevant documents but could not generate a summary.",
            confidence=0.75,
            sources=sources,
        )

    except Exception as e:
        logger.error(f"RAG agent error: {str(e)}")
        return AgentResponse(
            agent_type=AgentType.RAG,
            answer=f"RAG retrieval failed: {str(e)}",
            confidence=0.0,
            sources=[],
        )


def _synthesize_responses(
    original_query: str,
    agent_responses: List[AgentResponse]
) -> str:
    """
    Synthesize responses from multiple agents into a coherent answer.

    Args:
        original_query: Original user query
        agent_responses: Responses from different agents

    Returns:
        Synthesized response string
    """
    if not agent_responses:
        return "No responses generated."

    if len(agent_responses) == 1:
        return agent_responses[0].answer

    # Multi-agent synthesis
    results: List[str] = ["Based on multiple sources:\n"]

    for resp in agent_responses:
        results.append(f"**{resp.agent_type.value.title()}:**\n{resp.answer}\n")

    results.append("**Sources:**")
    all_sources = set()
    for resp in agent_responses:
        for source in resp.sources:
            if source.title:
                all_sources.add(str(source.title))

    if all_sources:
        for s in sorted(all_sources):
            results.append(f"- {s}")
    else:
        results.append("- No specific sources referenced")

    return "\n".join(results)


@router.post("/upload-file", response_model=DocumentUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
) -> DocumentUploadResponse:
    """
    Upload a binary file (PDF, TXT) to knowledge base via multipart/form-data.
    """
    try:
        import os
        import tempfile
        
        # Save to temporary file for RAG processing
        suffix = os.path.splitext(file.filename)[1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name

        try:
            rag_service = get_rag_service()
            chunks_created = rag_service.add_documents_from_files([tmp_path])
            rag_service.save()
            
            return DocumentUploadResponse(
                success=True,
                document_id=f"file_{int(time.time())}",
                chunks_created=chunks_created,
                message=f"File '{file.filename}' processed with {chunks_created} chunks"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    except Exception as e:
        logger.error(f"File upload error: {str(e)}")
        return DocumentUploadResponse(
            success=False,
            chunks_created=0,
            message=f"File upload failed: {str(e)}"
        )


@router.post("/upload-document", response_model=DocumentUploadResponse)
async def upload_document(request: DocumentUploadRequest) -> DocumentUploadResponse:
    """
    Upload document to knowledge base.

    Args:
        request: DocumentUploadRequest with document details

    Returns:
        DocumentUploadResponse with upload status
    """
    try:
        chunks_created = 0
        rag_service = get_rag_service()

        if request.document_type == "url":
            chunks_created = rag_service.add_documents_from_urls([request.url])
        elif request.document_type in ["text", "raw"]:
            chunks_created = rag_service.add_documents_from_text(
                [request.content],
                metadata=[{
                    "name": request.document_name,
                    "tags": request.tags
                }]
            )
        else:
            chunks_created = rag_service.add_documents_from_text(
                [request.content],
                metadata=[{
                    "name": request.document_name,
                    "type": request.document_type,
                    "tags": request.tags
                }]
            )

        # Save vector store
        rag_service.save()

        return DocumentUploadResponse(
            success=True,
            document_id=f"doc_{int(time.time())}",
            chunks_created=chunks_created,
            message=f"Document uploaded with {chunks_created} chunks"
        )

    except Exception as e:
        logger.error(f"Document upload error: {str(e)}")
        return DocumentUploadResponse(
            success=False,
            chunks_created=0,
            message=f"Upload failed: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with service status
    """
    services = {
        "llm": "healthy",
        "vector_db": "healthy",
        "search": "healthy",
        "ocr": "healthy",
        "vector_db_size": str(0)
    }

    # Try to verify services
    try:
        get_llm()
    except Exception as e:
        services["llm"] = f"degraded: {str(e)}"

    try:
        rag_service = get_rag_service()
        services["vector_db_size"] = str(rag_service.get_store_size())
    except Exception as e:
        services["vector_db"] = f"degraded: {str(e)}"

    # Determine overall status
    status = "healthy"
    if any("degraded" in str(v) or "error" in str(v) for v in services.values()):
        status = "degraded"
    if any("error" in str(v) for v in services.values()):
        status = "down"

    return HealthResponse(
        status=status,
        version="1.0.0",
        timestamp=time.time(),
        services=services
    )


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str):
    """
    Retrieve trace information from LangSmith.

    Args:
        trace_id: LangSmith trace ID

    Returns:
        Trace details
    """
    # TODO: Implement LangSmith trace retrieval
    return {
        "trace_id": trace_id,
        "message": "LangSmith integration in progress"
    }
