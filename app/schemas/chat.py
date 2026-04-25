from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MessageRequest(BaseModel):
    """Request model for chat messages."""
    question: str = Field(..., min_length=1, description="The question to ask")
    context: Optional[str] = Field(None, description="Optional context for the question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation history (optional)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Python?",
                "context": "General programming knowledge",
                "session_id": "session_123"
            }
        }


class MessageResponse(BaseModel):
    """Response model for chat messages."""
    question: str
    answer: str
    model: str
    session_id: str
    timestamp: datetime
    history_used: bool = Field(default=False, description="Whether conversation history was used")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Python?",
                "answer": "Python is a high-level programming language...",
                "model": "gpt-3.5-turbo",
                "session_id": "session_123",
                "timestamp": "2024-01-15T10:30:00",
                "history_used": False
            }
        }


class ChatMessage(BaseModel):
    """Individual message in conversation history."""
    role: str = Field(..., description="Message role: 'human', 'assistant', or 'system'")
    content: str
    timestamp: datetime


class ConversationHistory(BaseModel):
    """Model for storing conversation history."""
    session_id: str
    messages: List[ChatMessage]
    created_at: datetime
    updated_at: datetime
    message_count: int


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str


class SessionInfo(BaseModel):
    """Information about a chat session."""
    session_id: str
    message_count: int
    created_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None


class ClearHistoryRequest(BaseModel):
    """Request model for clearing conversation history."""
    session_id: str


class ClearHistoryResponse(BaseModel):
    """Response for clearing conversation history."""
    session_id: str
    status: str
    message: str


class ExtractionLevelRequest(BaseModel):
    """Request model for setting extraction level."""
    level: int = Field(..., ge=1, le=3, description="Extraction level: 1=minimal, 2=medium, 3=detailed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "level": 2
            }
        }


class ExtractionLevelResponse(BaseModel):
    """Response for extraction level operations."""
    extraction_level: int
    description: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "extraction_level": 2,
                "description": "Medium extraction - include relevant context and examples"
            }
        }

