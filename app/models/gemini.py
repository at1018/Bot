"""Google Gemini LLM provider."""
from langchain_google_genai import ChatGoogleGenerativeAI
from app.models.base import BaseLLMProvider
from app.utils.logger import get_logger

logger = get_logger(__name__)


class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider implementation."""
    
    def __init__(
        self,
        api_key: str,
        model_name: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        extraction_level: int = 1,
    ):
        """
        Initialize Gemini provider.
        
        Args:
            api_key: Google API key for Gemini
            model_name: Model name (e.g., gemini-pro, gemini-pro-vision)
            temperature: Temperature for sampling
            max_tokens: Maximum tokens in response
            extraction_level: Data extraction level (1-3)
        """
        super().__init__(model_name, temperature, max_tokens, extraction_level)
        self.api_key = api_key
        self.initialize()
    
    def initialize(self):
        """Initialize Google Gemini ChatGoogleGenerativeAI client."""
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=self.model_name,
                temperature=self.temperature,
                google_api_key=self.api_key
            )
            self.setup_chain()
            logger.info(f"Gemini provider initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini provider: {str(e)}")
            raise
    
    def invoke(self, question: str, conversation_context: str = "", additional_context: str = "") -> str:
        """Invoke Gemini model."""
        try:
            # Detect intent to know how to format response
            intent = self._detect_intent(question)
            
            # Invoke the chain with dynamic system prompt
            response = self.chain.invoke({
                "question": question,
                "conversation_context": conversation_context,
                "additional_context": additional_context,
            })
            
            # Extract response content
            response_text = response.content if hasattr(response, 'content') else str(response)
            
            # Format based on detected intent (lightweight formatting)
            formatted = self._format_response(response_text, intent)
            
            return formatted
        except Exception as e:
            logger.error(f"Error invoking Gemini: {str(e)}")
            raise
