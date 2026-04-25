from pydantic_settings import BaseSettings
from typing import Optional, Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_title: str = "Chatbot API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # LLM Provider Configuration
    llm_provider: Literal["openai", "groq", "gemini", "anthropic"] = "groq"
    
    # Extraction Level Configuration (1=minimal, 2=medium, 3=detailed)
    extraction_level: int = 1
    
    # Common LLM Settings
    temperature: float = 0.7
    max_tokens: int = 2048
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model_name: str = "gpt-3.5-turbo"
    
    # Groq Configuration
    groq_api_key: str = ""
    groq_model_name: str = "llama-3.1-8b-instant"
    
    # Google Gemini Configuration
    google_api_key: str = ""
    gemini_model_name: str = "gemini-pro"
    
    # Anthropic Claude Configuration
    anthropic_api_key: str = ""
    anthropic_model_name: str = "claude-3-sonnet-20240229"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
