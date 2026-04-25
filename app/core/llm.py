from config.settings import settings
from app.models import get_llm_provider
from app.models.base import BaseLLMProvider
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatbotLLM:
    """LangChain-based LLM wrapper for chatbot functionality."""
    
    def __init__(self):
        """Initialize the LLM with configured provider."""
        try:
            self.provider: BaseLLMProvider = get_llm_provider()
            logger.info(
                f"ChatbotLLM initialized with provider: {settings.llm_provider}, "
                f"extraction_level: {settings.extraction_level}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatbotLLM: {str(e)}")
            raise
    
    async def get_answer(
        self, 
        question: str, 
        context: Optional[str] = None,
        conversation_history: Optional[str] = None
    ) -> tuple[str, bool]:
        """
        Get an answer to a question using configured LLM provider.
        
        Args:
            question: The user's question
            context: Optional context for the question
            conversation_history: Optional previous conversation history
            
        Returns:
            Tuple of (answer, history_was_used)
        """
        try:
            # Prepare conversation context
            history_was_used = False
            if conversation_history and conversation_history.strip():
                conversation_context = f"""Previous Conversation:
{conversation_history}

Based on the conversation history above, please provide a contextual answer."""
                history_was_used = True
            else:
                conversation_context = ""
            
            # Prepare additional context
            additional_context = f"User Context: {context}" if context else ""
            
            logger.debug(f"Invoking LLM with provider={settings.llm_provider}, history_used={history_was_used}")
            
            # Invoke the provider
            answer = self.provider.invoke(
                question=question,
                conversation_context=conversation_context,
                additional_context=additional_context
            )
            
            return answer, history_was_used
            
        except Exception as e:
            logger.error(f"Error getting answer from LLM: {str(e)}")
            raise RuntimeError(f"Error getting answer from LLM: {str(e)}")
    
    def get_model_info(self) -> dict:
        """Get information about the current model."""
        return {
            "provider": settings.llm_provider,
            "model": self.provider.model_name,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens,
            "extraction_level": self.provider.get_extraction_level()
        }
    
    def set_extraction_level(self, level: int) -> None:
        """Set the extraction level for the provider."""
        try:
            self.provider.set_extraction_level(level)
            logger.info(f"Extraction level set to: {level}")
        except ValueError as e:
            logger.error(f"Invalid extraction level: {str(e)}")
            raise
    
    def get_extraction_level(self) -> int:
        """Get the current extraction level."""
        return self.provider.get_extraction_level()


# Global LLM instance
_llm_instance: Optional[ChatbotLLM] = None


def get_llm() -> ChatbotLLM:
    """Get or create the global LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = ChatbotLLM()
    return _llm_instance
