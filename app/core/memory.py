"""
Conversation memory management for maintaining chat history.
"""

from datetime import datetime
from typing import List, Dict, Optional
from collections import defaultdict
import json
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ConversationMemory:
    """In-memory storage for conversation history."""
    
    def __init__(self, max_history_per_session: int = 50):
        """
        Initialize conversation memory.
        
        Args:
            max_history_per_session: Maximum number of messages to keep per session
        """
        self.max_history_per_session = max_history_per_session
        # Store conversations: {session_id: List[message_dict]}
        self.conversations: Dict[str, List[Dict]] = defaultdict(list)
        logger.info("Conversation memory initialized")
    
    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        timestamp: Optional[datetime] = None
    ) -> None:
        """
        Add a message to the conversation history.
        
        Args:
            session_id: Unique session identifier
            role: Message role ('human', 'assistant', or 'system')
            content: Message content
            timestamp: Message timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.utcnow()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp.isoformat()
        }
        
        self.conversations[session_id].append(message)
        
        # Trim history if it exceeds max length
        if len(self.conversations[session_id]) > self.max_history_per_session:
            self.conversations[session_id] = self.conversations[session_id][-self.max_history_per_session:]
        
        logger.debug(f"Message added to session {session_id}: {role}")
    
    def get_history(self, session_id: str) -> List[Dict]:
        """
        Get conversation history for a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            List of message dictionaries
        """
        return self.conversations.get(session_id, [])
    
    def get_history_text(
        self,
        session_id: str,
        limit: Optional[int] = None
    ) -> str:
        """
        Get conversation history as formatted text.
        
        Args:
            session_id: Unique session identifier
            limit: Maximum number of messages to include
            
        Returns:
            Formatted conversation history
        """
        history = self.get_history(session_id)
        
        if limit:
            history = history[-limit:]
        
        if not history:
            return ""
        
        formatted_history = []
        for msg in history:
            role = msg["role"].capitalize()
            content = msg["content"]
            formatted_history.append(f"{role}: {content}")
        
        return "\n".join(formatted_history)
    
    def get_last_n_messages(
        self,
        session_id: str,
        n: int = 5
    ) -> List[Dict]:
        """
        Get the last N messages from a session.
        
        Args:
            session_id: Unique session identifier
            n: Number of messages to retrieve
            
        Returns:
            List of message dictionaries
        """
        history = self.get_history(session_id)
        return history[-n:] if len(history) > 0 else []
    
    def clear_history(self, session_id: str) -> None:
        """
        Clear conversation history for a session.
        
        Args:
            session_id: Unique session identifier
        """
        if session_id in self.conversations:
            self.conversations[session_id].clear()
            logger.info(f"History cleared for session {session_id}")
    
    def delete_session(self, session_id: str) -> None:
        """
        Delete a session completely.
        
        Args:
            session_id: Unique session identifier
        """
        if session_id in self.conversations:
            del self.conversations[session_id]
            logger.info(f"Session {session_id} deleted")
    
    def get_all_sessions(self) -> List[str]:
        """Get all active session IDs."""
        return list(self.conversations.keys())
    
    def get_session_summary(self, session_id: str) -> Dict:
        """
        Get summary information about a session.
        
        Args:
            session_id: Unique session identifier
            
        Returns:
            Dictionary with session information
        """
        history = self.get_history(session_id)
        
        if not history:
            return {
                "session_id": session_id,
                "message_count": 0,
                "created_at": None,
                "last_message_at": None
            }
        
        return {
            "session_id": session_id,
            "message_count": len(history),
            "created_at": history[0]["timestamp"],
            "last_message_at": history[-1]["timestamp"]
        }


# Global memory instance
_memory_instance: Optional[ConversationMemory] = None


def get_memory() -> ConversationMemory:
    """Get or create the global conversation memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ConversationMemory()
    return _memory_instance
