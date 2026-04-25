"""Factory for creating LLM providers based on configuration."""
from typing import Optional
from app.models.base import BaseLLMProvider
from app.models.openai import OpenAIProvider
from app.models.groq import GroqProvider
from app.models.gemini import GeminiProvider
from app.models.anthropic import AnthropicProvider
from app.utils.logger import get_logger
from config.settings import settings

logger = get_logger(__name__)


def get_llm_provider() -> BaseLLMProvider:
    """
    Factory function to get the appropriate LLM provider based on environment configuration.
    
    Returns:
        BaseLLMProvider: An instance of the configured LLM provider
        
    Raises:
        ValueError: If the provider is not supported or required credentials are missing
    """
    provider_name = settings.llm_provider.lower()
    
    try:
        if provider_name == "openai":
            logger.info("Loading OpenAI provider")
            return OpenAIProvider(
                api_key=settings.openai_api_key,
                model_name=settings.openai_model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                extraction_level=settings.extraction_level,
            )
        
        elif provider_name == "groq":
            logger.info("Loading Groq provider")
            return GroqProvider(
                api_key=settings.groq_api_key,
                model_name=settings.groq_model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                extraction_level=settings.extraction_level,
            )
        
        elif provider_name == "gemini":
            logger.info("Loading Gemini provider")
            return GeminiProvider(
                api_key=settings.google_api_key,
                model_name=settings.gemini_model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                extraction_level=settings.extraction_level,
            )
        
        elif provider_name == "anthropic":
            logger.info("Loading Anthropic provider")
            return AnthropicProvider(
                api_key=settings.anthropic_api_key,
                model_name=settings.anthropic_model_name,
                temperature=settings.temperature,
                max_tokens=settings.max_tokens,
                extraction_level=settings.extraction_level,
            )
        
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider_name}. "
                f"Supported providers: openai, groq, gemini, anthropic"
            )
    
    except ValueError as e:
        logger.error(f"Error creating LLM provider: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error creating LLM provider: {str(e)}")
        raise
