"""Groq LLM provider."""
from langchain_groq import ChatGroq
from app.models.base import BaseLLMProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GroqProvider(BaseLLMProvider):
    """Groq LLM provider implementation."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "llama-3.1-8b-instant",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        extraction_level: int = 1,
    ):
        """
        Initialize Groq provider.
        
        Args:
            api_key: Groq API key
            model_name: Model name (e.g., llama-3.1-8b-instant)
            temperature: Temperature for sampling
            max_tokens: Maximum tokens in response
            extraction_level: Data extraction level (1-3)
        """
        super().__init__(model_name, temperature, max_tokens, extraction_level)
        self.api_key = api_key
        self.initialize()
    
    def initialize(self):
        """Initialize Groq ChatGroq client."""
        if not self.api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")
        
        try:
            self.llm = ChatGroq(
                model_name=self.model_name,
                temperature=self.temperature,
                api_key=self.api_key
            )
            self.setup_chain()
            logger.info(f"Groq provider initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Groq provider: {str(e)}")
            raise
    
    def invoke(self, question: str, conversation_context: str = "", additional_context: str = "") -> str:
        """Invoke Groq model."""
        try:
            response = self.chain.invoke({
                "question": question,
                "conversation_context": conversation_context,
                "additional_context": additional_context,
            })
            # Format response to ensure proper code formatting
            return self._format_code_response(response.content)
        except Exception as e:
            logger.error(f"Error invoking Groq: {str(e)}")
            raise
