from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_title: str = "Chatbot API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    # LangChain Configuration
    openai_api_key: str = ""
    model_name: str = "gpt-3.5-turbo"
    temperature: float = 0.7
    max_tokens: int = 2048

     # LangChain Configuration for groq
    groq_api_key: str = ""
    model_name: str = "llama-3.1-8b-instant"
    temperature: float = 0.7
    max_tokens: int = 2048
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Logging
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
