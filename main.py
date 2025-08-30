import os
import json
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import httpx

# Supabase
from supabase import create_client, Client

# Gemini
import google.generativeai as genai

# -----------------------
# Config
# -----------------------
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
SUPABASE_TABLE = os.getenv("SUPABASE_TABLE", "rag_documents")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_EMBEDDING_MODEL = os.getenv("GEMINI_EMBEDDING_MODEL", "models/embedding-001")

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_MODEL = os.getenv("PERPLEXITY_MODEL", "llama-3.1-sonar-large-128k-online")

TOP_K = int(os.getenv("TOP_K", "4"))

if not all([SUPABASE_URL, SUPABASE_KEY, GEMINI_API_KEY, PERPLEXITY_API_KEY]):
    raise RuntimeError("Missing one or more required env vars.")

# -----------------------
# Clients
# -----------------------
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
genai.configure(api_key=GEMINI_API_KEY)

# -----------------------
# FastAPI
# -----------------------
app = FastAPI(title="KrishiVaani RAG Chat API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# Chat Schemas
# -----------------------
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[ChatMessage]] = []
    metadata_filter: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = None
    use_context: Optional[bool] = True  # Whether to use RAG context or just LLM

class ChatResponse(BaseModel):
    answer: str
    sources: List[Dict[str, Any]]
    chat_id: Optional[str] = None
    has_context: bool

class StreamChatRequest(BaseModel):
    query: str
    chat_history: Optional[List[ChatMessage]] = []
    metadata_filter: Optional[Dict[str, Any]] = None
    top_k: Optional[int] = None

# -----------------------
# Core Chat Functions
# -----------------------
def embed_query(text: str) -> List[float]:
    """Generate embedding for query text using Gemini."""
    r = genai.embed_content(model=GEMINI_EMBEDDING_MODEL, content=text)
    return r["embedding"]

def similarity_search(
    query_vec: List[float], 
    top_k: int = TOP_K, 
    metadata_filter: Optional[Dict[str, Any]] = None
) -> List[Dict]:
    """Search for similar documents in Supabase vector store."""
    payload = {
        "query_embedding": query_vec,
        "match_count": top_k,
        "filter": metadata_filter
    }
    res = supabase.rpc("match_documents", payload).execute()
    if res.error:
        raise HTTPException(status_code=500, detail=f"Vector search error: {res.error.message}")
    return res.data or []

def format_chat_history(chat_history: List[ChatMessage]) -> str:
    """Format chat history for context."""
    if not chat_history:
        return ""
    
    formatted = []
    for msg in chat_history[-6:]:  # Last 6 messages for context
        role = "Human" if msg.role == "user" else "Assistant"
        formatted.append(f"{role}: {msg.content}")
    
    return "\n".join(formatted)

async def generate_response(
    context_blocks: List[str], 
    question: str, 
    chat_history: List[ChatMessage] = None
) -> str:
    """Generate response using Perplexity AI with context and chat history."""
    
    # Enhanced system prompt for agriculture domain
    system_prompt = (
        "You are KrishiVaani, an expert agricultural assistant for Indian farmers, "
        "especially small and marginal farmers. You provide practical, actionable advice "
        "based on Indian farming conditions and practices.\n\n"
        "Guidelines:\n"
        "- Use ONLY the provided context when available\n"
        "- Be concise, practical, and farmer-friendly\n"
        "- Provide dosages in local units (kg/acre, ml/liter, etc.)\n"
        "- Consider Indian climate, soil, and crop conditions\n"
        "- If information is not in context, clearly state limitations\n"
        "- Prioritize safe, sustainable farming practices\n"
        "- Use simple Hindi/English terms that farmers understand"
    )
    
    # Build user message with context and history
    user_parts = []
    
    # Add chat history if available
    if chat_history:
        history_text = format_chat_history(chat_history)
        if history_text:
            user_parts.append(f"Previous conversation:\n{history_text}\n")
    
    # Add context if available
    if context_blocks:
        context_text = "\n\n".join([f"[Context {i+1}]\n{c}" for i, c in enumerate(context_blocks)])
        user_parts.append(f"Relevant information from knowledge base:\n{context_text}\n")
    
    # Add current question
    user_parts.append(f"Current question: {question}\n\nPlease provide a helpful response:")
    
    user_message = "\n".join(user_parts)

    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "model": PERPLEXITY_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        "temperature": 0.3,
        "max_tokens": 800,
    }
    
    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            "https://api.perplexity.ai/chat/completions", 
            headers=headers, 
            json=payload
        )
        response.raise_for_status()
        data = response.json()
        return data["choices"][0]["message"]["content"]

# -----------------------
# Chat Routes
# -----------------------
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Main chat endpoint with RAG functionality."""
    
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    sources = []
    context_blocks = []
    has_context = False
    
    # Perform RAG search if enabled
    if request.use_context:
        try:
            # Generate query embedding
            query_embedding = embed_query(request.query)
            
            # Search for relevant documents
            matches = similarity_search(
                query_embedding, 
                top_k=request.top_k or TOP_K, 
                metadata_filter=request.metadata_filter
            )
            
            if matches:
                has_context = True
                # Process search results
                for match in matches:
                    sources.append({
                        "id": match["id"],
                        "metadata": match.get("metadata", {}),
                        "similarity_score": match.get("distance", 0),
                        "preview": match["document_text"][:200] + "..." if len(match["document_text"]) > 200 else match["document_text"]
                    })
                    
                    # Prepare context block (limit length for token efficiency)
                    block = match["document_text"]
                    if len(block) > 1500:
                        block = block[:1500] + "..."
                    context_blocks.append(block)
        
        except Exception as e:
            # Log error but continue without context
            print(f"RAG search error: {e}")
    
    # Generate response
    try:
        answer = await generate_response(
            context_blocks, 
            request.query, 
            request.chat_history
        )
        
        return ChatResponse(
            answer=answer,
            sources=sources,
            has_context=has_context
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Response generation error: {str(e)}")

@app.post("/chat/simple")
async def simple_chat(query: str):
    """Simplified chat endpoint without RAG context."""
    
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    try:
        answer = await generate_response([], query, [])
        return {"answer": answer, "has_context": False}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/chat/models")
def get_available_models():
    """Get information about available models and configuration."""
    return {
        "embedding_model": GEMINI_EMBEDDING_MODEL,
        "chat_model": PERPLEXITY_MODEL,
        "max_context_chunks": TOP_K,
        "features": {
            "rag_search": True,
            "chat_history": True,
            "metadata_filtering": True,
            "agriculture_domain": True
        }
    }

@app.get("/health")
def health_check():
    """Health check endpoint."""
    try:
        # Test Supabase connection
        supabase.table(SUPABASE_TABLE).select("id").limit(1).execute()
        return {
            "status": "healthy",
            "services": {
                "supabase": "connected",
                "gemini": "configured",
                "perplexity": "configured"
            }
        }
    except Exception as e:
        return {
            "status": "degraded",
            "error": str(e)
        }

# -----------------------
# Advanced Chat Features
# -----------------------
@app.post("/chat/with-filters")
async def chat_with_filters(
    query: str,
    crop_type: Optional[str] = None,
    region: Optional[str] = None,
    season: Optional[str] = None,
    language: Optional[str] = None
):
    """Chat with specific filters for better context matching."""
    
    metadata_filter = {}
    if crop_type:
        metadata_filter["crop_type"] = crop_type
    if region:
        metadata_filter["region"] = region  
    if season:
        metadata_filter["season"] = season
    if language:
        metadata_filter["language"] = language
    
    request = ChatRequest(
        query=query,
        metadata_filter=metadata_filter if metadata_filter else None,
        use_context=True
    )
    
    return await chat(request)

@app.get("/chat/stats")
def get_chat_stats():
    """Get statistics about the knowledge base."""
    try:
        # Get document count
        result = supabase.table(SUPABASE_TABLE).select("id", count="exact").execute()
        doc_count = result.count if result.count else 0
        
        # Get metadata distribution (if available)
        metadata_result = supabase.table(SUPABASE_TABLE).select("metadata").limit(100).execute()
        
        return {
            "total_documents": doc_count,
            "status": "active"
        }
    except Exception as e:
        return {
            "total_documents": 0,
            "status": "error",
            "error": str(e)
        }