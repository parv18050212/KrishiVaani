"""
KrishiVaani - Unified Backend Server
Agricultural Advisory System for Indian Farmers

This is the main entry point that imports all modules from the backend folder
and provides a unified FastAPI application on port 8000.

Routes:
- /chat/* - Agentic AI chat endpoints (defined here, using backend.agent)
- /api/weather/* - Weather data and agricultural advisory
- /api/pest/* - Pest detection and treatment
- /api/market/* - Market prices and mandi information
- /api/soil/* - Soil analysis and fertilizer recommendations
"""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional, List, Dict, Any

import httpx
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from backend/.env
backend_env = Path(__file__).parent / "backend" / ".env"
load_dotenv(backend_env)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import agent functions from backend.agent (no router, just functions)
from backend.agent import (
    process_chat,
    process_speech_chat,
    rollback_conversation,
    get_session_history,
    clear_session_history
)

# Import routers from backend folder
from backend.weather import router as weather_router
from backend.pest import router as pest_router
from backend.market import router as market_router
from backend.soil import router as soil_router

# HTTP client for internal use
http_client = None


# ==================== PYDANTIC MODELS FOR CHAT ====================

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    query: str = Field(..., min_length=1, description="User's question")
    session_id: Optional[str] = Field(None, description="Session ID for conversation continuity")
    language: Optional[str] = Field("en", description="Preferred response language")
    location: Optional[str] = Field(None, description="User's location")
    crop: Optional[str] = Field(None, description="Current crop context")
    chat_history: Optional[List[Dict[str, str]]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    answer: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    session_id: str
    has_context: bool = False
    tools_used: List[str] = Field(default_factory=list)


class RollbackRequest(BaseModel):
    """Request model for rollback endpoint."""
    steps: int = Field(1, ge=1, le=10, description="Number of steps to rollback")


# ==================== CHAT ROUTER ====================

chat_router = APIRouter(prefix="/chat", tags=["Chat & AI"])


@chat_router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint with agentic AI capabilities.
    Supports tool use, conversation memory, and rollback.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        result = await process_chat(
            query=request.query,
            session_id=request.session_id,
            language=request.language or "en",
            location=request.location,
            crop=request.crop,
            chat_history=request.chat_history
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=[],
            session_id=result["session_id"],
            has_context=result["has_context"],
            tools_used=result["tools_used"]
        )
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@chat_router.post("/speech", response_model=ChatResponse)
async def speech_chat(request: ChatRequest):
    """
    Specialized endpoint for speech-to-text queries.
    Uses direct LLM call for faster response.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        result = await process_speech_chat(
            query=request.query,
            session_id=request.session_id
        )
        
        return ChatResponse(
            answer=result["answer"],
            sources=[],
            session_id=result["session_id"],
            has_context=result["has_context"],
            tools_used=result["tools_used"]
        )
    
    except Exception as e:
        logger.error(f"Speech chat error: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


@chat_router.post("/simple")
async def simple_chat(query: str):
    """Simplified chat endpoint for quick queries."""
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    request = ChatRequest(query=query)
    response = await chat(request)
    return {"answer": response.answer, "has_context": response.has_context}


@chat_router.post("/rollback/{session_id}")
async def rollback_session(session_id: str, request: RollbackRequest):
    """
    Rollback a session to a previous state.
    Useful for undoing unwanted responses or recovering from errors.
    """
    try:
        result = await rollback_conversation(session_id, request.steps)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Rollback error: {e}")
        raise HTTPException(status_code=500, detail=f"Rollback failed: {str(e)}")


@chat_router.get("/session/{session_id}/history")
async def get_history(session_id: str):
    """Get conversation history for a session."""
    history = get_session_history(session_id)
    return {
        "session_id": session_id,
        "history": history,
        "message_count": len(history)
    }


@chat_router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """Clear a session's history."""
    clear_session_history(session_id)
    return {"status": "success", "message": f"Session {session_id} cleared"}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan."""
    global http_client
    http_client = httpx.AsyncClient(timeout=30.0)
    logger.info("=" * 50)
    logger.info("KrishiVaani Backend Server Started")
    logger.info("=" * 50)
    logger.info("Available endpoints:")
    logger.info("  - POST /chat - AI Chat")
    logger.info("  - POST /chat/speech - Speech Chat")
    logger.info("  - POST /api/weather - Weather Data")
    logger.info("  - POST /api/pest/detect - Pest Detection")
    logger.info("  - POST /api/market/prices - Market Prices")
    logger.info("  - POST /api/soil/analyze - Soil Analysis")
    logger.info("=" * 50)
    yield
    await http_client.aclose()
    logger.info("KrishiVaani Backend Server Stopped")


# Create FastAPI app
app = FastAPI(
    title="KrishiVaani API",
    description="Intelligent Agricultural Advisory System for Indian Farmers",
    version="2.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(chat_router)       # /chat/* - defined in main.py, uses backend.agent
app.include_router(weather_router)    # /api/weather/*
app.include_router(pest_router)       # /api/pest/*
app.include_router(market_router)     # /api/market/*
app.include_router(soil_router)       # /api/soil/*


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "service": "KrishiVaani API",
        "version": "2.0.0",
        "status": "healthy",
        "description": "Intelligent Agricultural Advisory System for Indian Farmers",
        "endpoints": {
            "chat": {
                "POST /chat": "AI-powered chat with agricultural advisory",
                "POST /chat/speech": "Speech-to-text optimized chat",
                "POST /chat/simple": "Simple query chat",
                "POST /chat/rollback/{session_id}": "Rollback conversation state"
            },
            "weather": {
                "POST /api/weather": "Get weather data and agricultural advisory",
                "GET /api/weather/health": "Weather service health check"
            },
            "pest": {
                "POST /api/pest/detect": "Detect pest from image",
                "GET /api/pest/pesticides": "Get pesticides database",
                "GET /api/pest/health": "Pest service health check"
            },
            "market": {
                "POST /api/market/prices": "Get market prices for location",
                "GET /api/market/health": "Market service health check"
            },
            "soil": {
                "POST /api/soil/analyze": "Analyze soil health card",
                "GET /api/soil/health": "Soil service health check"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


@app.get("/health")
async def health_check():
    """Overall system health check."""
    return {
        "status": "healthy",
        "service": "KrishiVaani API",
        "version": "2.0.0",
        "services": {
            "chat": "operational",
            "weather": "operational",
            "pest": "operational",
            "market": "operational",
            "soil": "operational"
        }
    }


# Legacy endpoint mappings for backward compatibility
# These redirect old endpoints to new ones

@app.post("/detect-pest")
async def legacy_detect_pest(file):
    """Legacy endpoint - redirects to /api/pest/detect"""
    from backend.pest import detect_pest
    return await detect_pest(file)


@app.post("/weather")
async def legacy_weather(location):
    """Legacy endpoint - redirects to /api/weather"""
    from backend.weather import get_weather_data
    return await get_weather_data(location)


@app.post("/market-prices")
async def legacy_market(location):
    """Legacy endpoint - redirects to /api/market/prices"""
    from backend.market import get_market_prices
    return await get_market_prices(location)


@app.post("/analyze-soil")
async def legacy_soil(file):
    """Legacy endpoint - redirects to /api/soil/analyze"""
    from backend.soil import analyze_soil
    return await analyze_soil(file)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True
        # log_level="info"
    )
