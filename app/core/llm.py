from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from config.settings import settings
from langchain_groq import ChatGroq
from typing import Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatbotLLM:
    """LangChain-based LLM wrapper for chatbot functionality."""
    
    def __init__(self):
        """Initialize the LLM with OpenAI configuration."""
        # if not settings.openai_api_key:
        #     raise ValueError("OPENAI_API_KEY environment variable not set")
        if not settings.groq_api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        self.llm = ChatGroq(
            model_name=settings.model_name,
            # temperature=settings.temperature,
            # max_tokens=settings.max_tokens,
            api_key=settings.groq_api_key
        )
        
        # self.llm = ChatOpenAI(
        #     model_name=settings.model_name,
        #     temperature=settings.temperature,
        #     max_tokens=settings.max_tokens,
        #     api_key=settings.openai_api_key
        # )
        
        # System prompt template with conversation history support
        self.system_template = """You are a helpful and knowledgeable chatbot assistant. 
Your role is to provide clear, accurate, and helpful answers to user questions.
Always be respectful, professional, and concise in your responses.
If you don't know something, acknowledge it and suggest how the user might find the answer.

{conversation_context}

{additional_context}"""
        
        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_template),
            ("human", "{question}")
        ])
        
        self.chain = (
            self.prompt_template 
            | self.llm
        )
    
    async def get_answer(
        self, 
        question: str, 
        context: Optional[str] = None,
        conversation_history: Optional[str] = None
    ) -> tuple[str, bool]:
        """
        Get an answer to a question using LangChain with conversation history.
        
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
            
            logger.debug(f"Invoking LLM with history_used={history_was_used}")
            
            # Invoke the chain with context
            response = self.chain.invoke({
                "question": question,
                "conversation_context": conversation_context,
                "additional_context": additional_context
            })
            
            # Extract content from the response
            if hasattr(response, 'content'):
                answer = response.content
            else:
                answer = str(response)
            
            return answer, history_was_used
            
        except Exception as e:
            logger.error(f"Error getting answer from LLM: {str(e)}")
            raise RuntimeError(f"Error getting answer from LLM: {str(e)}")
    
    def get_model_info(self) -> dict:
        """Get information about the current model."""
        return {
            "model": settings.model_name,
            "temperature": settings.temperature,
            "max_tokens": settings.max_tokens
        }


# Global LLM instance
_llm_instance: Optional[ChatbotLLM] = None


def get_llm() -> ChatbotLLM:
    """Get or create the global LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = ChatbotLLM()
    return _llm_instance
