from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from config.settings import settings
from app.api.routes import router
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage the lifespan of the FastAPI application.
    """
    # Startup
    logger.info("Starting Chatbot API")
    logger.info(f"Using provider: {settings.llm_provider}")
    logger.info(f"Extraction level: {settings.extraction_level}")
    yield
    # Shutdown
    logger.info("Shutting down Chatbot API")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description="A chatbot API powered by LangChain and OpenAI",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router)


@app.get("/", tags=["root"])
async def read_root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": "A chatbot API powered by LangChain and OpenAI",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat",
            "info": "/api/info",
            "docs": "/docs"
        }
    }


if __name__ == "__main__":
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
