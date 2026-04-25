from fastapi import APIRouter, HTTPException, status
from datetime import datetime
import uuid
from app.schemas.chat import (
    MessageRequest, 
    MessageResponse, 
    HealthResponse,
    ConversationHistory,
    ChatMessage,
    SessionInfo,
    ClearHistoryRequest,
    ClearHistoryResponse
)
from app.core.llm import get_llm
from app.core.memory import get_memory
from app.utils.logger import get_logger

router = APIRouter(prefix="/api", tags=["chat"])
logger = get_logger(__name__)


@router.post("/chat", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def chat(request: MessageRequest) -> MessageResponse:
    """
    Chat endpoint that takes a question and returns an answer.
    Supports conversation history for context-aware responses.
    
    Args:
        request: MessageRequest with question, optional context, and session_id
        
    Returns:
        MessageResponse with the model's answer and session info
    """
    try:
        logger.info(f"Received question: {request.question}")
        
        # Validate input
        if not request.question or not request.question.strip():
            logger.warning("Empty question received")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Question cannot be empty"
            )
        
        # Create or use provided session ID
        session_id = request.session_id or str(uuid.uuid4())
        logger.debug(f"Using session: {session_id}")
        
        # Get memory and LLM instances
        memory = get_memory()
        llm = get_llm()
        
        # Get conversation history
        history = memory.get_history_text(session_id, limit=5)  # Last 5 messages for context
        
        # Get answer with conversation history
        answer, history_was_used = await llm.get_answer(
            question=request.question,
            context=request.context,
            conversation_history=history
        )
        
        logger.info(f"Generated answer for question: {request.question} (history_used={history_was_used})")
        
        # Store messages in memory
        timestamp = datetime.utcnow()
        memory.add_message(session_id, "human", request.question, timestamp)
        memory.add_message(session_id, "assistant", answer, timestamp)
        
        # Create response
        response = MessageResponse(
            question=request.question,
            answer=answer,
            model=llm.get_model_info()["model"],
            session_id=session_id,
            timestamp=timestamp,
            history_used=history_was_used
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing question: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """
    Health check endpoint to verify the API is running.
    
    Returns:
        HealthResponse with status and version
    """
    try:
        from config.settings import settings
        logger.info("Health check requested")
        
        return HealthResponse(
            status="healthy",
            version=settings.api_version
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unavailable"
        )


@router.get("/info")
async def get_model_info():
    """
    Get information about the current model configuration.
    
    Returns:
        Dictionary with model information
    """
    try:
        llm = get_llm()
        logger.info("Model info requested")
        return llm.get_model_info()
    except Exception as e:
        logger.error(f"Error fetching model info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching model info"
        )


@router.get("/history/{session_id}", response_model=ConversationHistory, status_code=status.HTTP_200_OK)
async def get_conversation_history(session_id: str) -> ConversationHistory:
    """
    Get conversation history for a specific session.
    
    Args:
        session_id: The session ID to retrieve history for
        
    Returns:
        ConversationHistory with all messages in the session
    """
    try:
        memory = get_memory()
        logger.info(f"Retrieving history for session: {session_id}")
        
        history = memory.get_history(session_id)
        
        if not history:
            logger.warning(f"No history found for session: {session_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No conversation history found for session {session_id}"
            )
        
        # Convert to ChatMessage objects
        messages = [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=datetime.fromisoformat(msg["timestamp"])
            )
            for msg in history
        ]
        
        first_timestamp = datetime.fromisoformat(history[0]["timestamp"])
        last_timestamp = datetime.fromisoformat(history[-1]["timestamp"])
        
        return ConversationHistory(
            session_id=session_id,
            messages=messages,
            created_at=first_timestamp,
            updated_at=last_timestamp,
            message_count=len(messages)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving conversation history"
        )


@router.get("/session/{session_id}", response_model=SessionInfo, status_code=status.HTTP_200_OK)
async def get_session_info(session_id: str) -> SessionInfo:
    """
    Get information about a session.
    
    Args:
        session_id: The session ID
        
    Returns:
        SessionInfo with session details
    """
    try:
        memory = get_memory()
        logger.info(f"Getting session info for: {session_id}")
        
        summary = memory.get_session_summary(session_id)
        
        return SessionInfo(
            session_id=summary["session_id"],
            message_count=summary["message_count"],
            created_at=datetime.fromisoformat(summary["created_at"]) if summary["created_at"] else None,
            last_message_at=datetime.fromisoformat(summary["last_message_at"]) if summary["last_message_at"] else None
        )
        
    except Exception as e:
        logger.error(f"Error getting session info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving session information"
        )


@router.delete("/history/{session_id}", response_model=ClearHistoryResponse, status_code=status.HTTP_200_OK)
async def clear_conversation_history(session_id: str) -> ClearHistoryResponse:
    """
    Clear conversation history for a specific session.
    
    Args:
        session_id: The session ID to clear history for
        
    Returns:
        ClearHistoryResponse with status
    """
    try:
        memory = get_memory()
        logger.info(f"Clearing history for session: {session_id}")
        
        memory.clear_history(session_id)
        
        return ClearHistoryResponse(
            session_id=session_id,
            status="success",
            message=f"Conversation history cleared for session {session_id}"
        )
        
    except Exception as e:
        logger.error(f"Error clearing history: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error clearing conversation history"
        )


@router.delete("/session/{session_id}", response_model=ClearHistoryResponse, status_code=status.HTTP_200_OK)
async def delete_session(session_id: str) -> ClearHistoryResponse:
    """
    Delete a session completely.
    
    Args:
        session_id: The session ID to delete
        
    Returns:
        ClearHistoryResponse with status
    """
    try:
        memory = get_memory()
        logger.info(f"Deleting session: {session_id}")
        
        memory.delete_session(session_id)
        
        return ClearHistoryResponse(
            session_id=session_id,
            status="success",
            message=f"Session {session_id} deleted completely"
        )
        
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting session"
        )


@router.get("/sessions")
async def list_all_sessions():
    """
    Get list of all active sessions.
    
    Returns:
        List of session IDs and their info
    """
    try:
        memory = get_memory()
        logger.info("Listing all sessions")
        
        sessions = []
        for session_id in memory.get_all_sessions():
            summary = memory.get_session_summary(session_id)
            sessions.append({
                "session_id": session_id,
                "message_count": summary["message_count"],
                "created_at": summary["created_at"],
                "last_message_at": summary["last_message_at"]
            })
        
        return {
            "total_sessions": len(sessions),
            "sessions": sessions
        }
        
    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error listing sessions"
        )
