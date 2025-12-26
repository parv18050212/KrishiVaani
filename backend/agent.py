"""
KrishiVaani Agentic AI Module
An intelligent agricultural advisory system using LangChain and LangGraph
with rollback capabilities for Indian farmers.

This module contains ONLY the agent logic - no FastAPI endpoints.
FastAPI endpoints are defined in main.py which imports from this module.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any, TypedDict, Annotated

import httpx
from dotenv import load_dotenv
from pathlib import Path

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

# Load environment variables from backend/.env
load_dotenv(Path(__file__).parent / ".env")

# Configure logging
logger = logging.getLogger(__name__)

# Configuration
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
if not PERPLEXITY_API_KEY:
    raise ValueError("PERPLEXITY_API_KEY environment variable is required")

# Backend service URLs (internal - all services run on same server now)
WEATHER_API_URL = os.getenv("WEATHER_API_URL", "http://localhost:8080")
PEST_API_URL = os.getenv("PEST_API_URL", "http://localhost:8080")
MARKET_API_URL = os.getenv("MARKET_API_URL", "http://localhost:8080")
OCR_API_URL = os.getenv("OCR_API_URL", "http://localhost:8080")

# Initialize LLM - Perplexity Sonar Pro via OpenAI-compatible API
llm = ChatOpenAI(
    model="sonar-pro",
    api_key=PERPLEXITY_API_KEY,
    base_url="https://api.perplexity.ai",
    temperature=0.7
)

# Session storage for conversation history
sessions: Dict[str, List[Dict]] = {}


# ==================== TOOLS ====================

@tool
async def get_weather_advisory(location: str, crop: Optional[str] = None) -> str:
    """
    Get weather information and agricultural advisory for a location.
    Use this when the user asks about weather, climate, rainfall, temperature,
    or needs weather-based farming advice.
    
    Args:
        location: The city or village name in India
        crop: Optional crop name for specific advisory
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {"location": location}
            if crop:
                params["crop"] = crop
            response = await client.get(f"{WEATHER_API_URL}/api/weather", params=params)
            if response.status_code == 200:
                data = response.json()
                return json.dumps(data, ensure_ascii=False)
            else:
                return f"Could not fetch weather data for {location}. Please try again."
    except Exception as e:
        logger.error(f"Weather API error: {e}")
        return f"Weather service temporarily unavailable. Error: {str(e)}"


@tool
async def get_pest_information(pest_name: str, crop: Optional[str] = None) -> str:
    """
    Get information about agricultural pests, diseases, and their management.
    Use this when the user asks about pest identification, pest control,
    disease management, or pesticide recommendations.
    
    Args:
        pest_name: Name of the pest or disease
        crop: Optional crop name for specific advice
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {"pest": pest_name}
            if crop:
                params["crop"] = crop
            response = await client.get(f"{PEST_API_URL}/api/pest", params=params)
            if response.status_code == 200:
                data = response.json()
                return json.dumps(data, ensure_ascii=False)
            else:
                return f"Could not fetch pest information for {pest_name}. Please try again."
    except Exception as e:
        logger.error(f"Pest API error: {e}")
        return f"Pest information service temporarily unavailable. Error: {str(e)}"


@tool
async def get_market_prices(commodity: str, location: str) -> str:
    """
    Get current market prices (mandi prices) for agricultural commodities.
    Use this when the user asks about crop prices, mandi rates, selling prices,
    or market information.
    
    Args:
        commodity: Name of the crop/commodity (e.g., wheat, rice, tomato)
        location: Market location or state name
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            params = {"commodity": commodity, "location": location}
            response = await client.get(f"{MARKET_API_URL}/api/market", params=params)
            if response.status_code == 200:
                data = response.json()
                return json.dumps(data, ensure_ascii=False)
            else:
                return f"Could not fetch market prices for {commodity} in {location}."
    except Exception as e:
        logger.error(f"Market API error: {e}")
        return f"Market price service temporarily unavailable. Error: {str(e)}"


@tool
async def get_fertilizer_recommendation(crop: str, soil_type: Optional[str] = None, location: Optional[str] = None) -> str:
    """
    Get fertilizer recommendations for crops based on soil type and region.
    Use this when the user asks about fertilizers, nutrients, soil health,
    or crop nutrition.
    
    Args:
        crop: Name of the crop
        soil_type: Type of soil (e.g., clay, sandy, loamy)
        location: Location for regional recommendations
    """
    recommendations = {
        "wheat": {
            "base": "NPK 120:60:40 kg/ha",
            "timing": "Apply 50% N + full P + full K at sowing, remaining N in 2 splits",
            "micronutrients": "Zinc sulfate 25 kg/ha if deficient"
        },
        "rice": {
            "base": "NPK 120:60:60 kg/ha",
            "timing": "Apply 50% N + full P + full K at transplanting",
            "micronutrients": "Zinc sulfate 25 kg/ha in zinc deficient soils"
        },
        "cotton": {
            "base": "NPK 150:60:60 kg/ha",
            "timing": "Apply in 3-4 splits during crop growth",
            "micronutrients": "Boron and Magnesium sprays during flowering"
        },
        "sugarcane": {
            "base": "NPK 250:60:60 kg/ha",
            "timing": "Apply N in 3 splits, P and K at planting",
            "micronutrients": "Iron and Zinc if deficient"
        },
        "tomato": {
            "base": "NPK 120:60:60 kg/ha",
            "timing": "Basal dose + top dressing at flowering",
            "micronutrients": "Calcium for preventing blossom end rot"
        }
    }
    
    crop_lower = crop.lower()
    if crop_lower in recommendations:
        rec = recommendations[crop_lower]
        result = {
            "crop": crop,
            "recommendation": rec,
            "soil_type": soil_type or "general",
            "location": location or "India",
            "note": "Get soil tested for precise recommendations. Contact your local KVK for detailed advice."
        }
    else:
        result = {
            "crop": crop,
            "recommendation": "General NPK 100:50:50 kg/ha as base. Adjust based on soil test.",
            "note": "For specific recommendations, please consult your local agricultural officer or KVK."
        }
    
    return json.dumps(result, ensure_ascii=False)


@tool
async def get_crop_calendar(crop: str, location: Optional[str] = None) -> str:
    """
    Get crop calendar and seasonal farming activities.
    Use this when the user asks about sowing time, harvesting time,
    crop seasons, or farming schedule.
    
    Args:
        crop: Name of the crop
        location: Location for regional calendar
    """
    calendars = {
        "wheat": {
            "season": "Rabi",
            "sowing": "October-November",
            "harvesting": "March-April",
            "duration": "120-150 days",
            "activities": [
                "Land preparation: September-October",
                "Sowing: October 15 - November 15",
                "First irrigation: 20-25 days after sowing",
                "Top dressing: 30-35 days after sowing",
                "Harvesting: March-April"
            ]
        },
        "rice": {
            "season": "Kharif",
            "sowing": "June-July (transplanting)",
            "harvesting": "October-November",
            "duration": "120-150 days",
            "activities": [
                "Nursery: May-June",
                "Transplanting: June-July",
                "Weeding: 20-40 days after transplanting",
                "Top dressing: Tillering and panicle stages",
                "Harvesting: October-November"
            ]
        },
        "cotton": {
            "season": "Kharif",
            "sowing": "April-May",
            "harvesting": "October-January",
            "duration": "150-180 days",
            "activities": [
                "Land preparation: March-April",
                "Sowing: April-May",
                "Thinning: 15-20 days after sowing",
                "First picking: October",
                "Multiple pickings till January"
            ]
        }
    }
    
    crop_lower = crop.lower()
    if crop_lower in calendars:
        result = calendars[crop_lower]
        result["crop"] = crop
        result["location"] = location or "North India (adjust for your region)"
    else:
        result = {
            "crop": crop,
            "message": "Crop calendar not available. Please consult local agricultural department.",
            "general_tip": "Kharif crops: June-October, Rabi crops: October-March, Zaid crops: March-June"
        }
    
    return json.dumps(result, ensure_ascii=False)


@tool
async def general_agriculture_query(query: str) -> str:
    """
    Handle general agricultural queries that don't fit other specific tools.
    Use this for questions about farming techniques, government schemes,
    organic farming, irrigation methods, seed selection, etc.
    
    Args:
        query: The user's agricultural question
    """
    return f"Please provide helpful agricultural advice for: {query}. Include practical tips relevant to Indian farmers."


# List of all tools
tools = [
    get_weather_advisory,
    get_pest_information,
    get_market_prices,
    get_fertilizer_recommendation,
    get_crop_calendar,
    general_agriculture_query
]


# ==================== AGENT STATE ====================

class AgentState(TypedDict):
    """State for the agricultural advisory agent."""
    messages: Annotated[List, add_messages]
    language: str
    user_location: Optional[str]
    current_crop: Optional[str]


# ==================== SYSTEM PROMPTS ====================

AGENT_SYSTEM_PROMPT = """You are KrishiVaani, an expert agricultural advisor for Indian farmers.

Your role:
- Provide practical, actionable farming advice
- Use simple language that farmers can understand
- Consider local conditions, seasons, and traditional practices
- Recommend government schemes when relevant (PM-KISAN, crop insurance, etc.)
- Always prioritize sustainable and cost-effective solutions

Guidelines:
- If asked about weather, use the weather tool
- If asked about pests or diseases, use the pest information tool
- If asked about prices, use the market prices tool
- If asked about fertilizers, use the fertilizer recommendation tool
- If asked about timing/seasons, use the crop calendar tool
- For general queries, use the general agriculture query tool

Always be respectful and supportive. Many farmers face difficult conditions.
Respond in the same language as the user's question when possible."""

SPEECH_SYSTEM_PROMPT = """You are KrishiVaani, a helpful agricultural advisor for Indian farmers.
Provide practical, actionable farming advice in simple language.
Consider local conditions, seasons, and cost-effective solutions.
Keep responses concise and helpful. Respond in the same language as the question."""


# ==================== AGENT GRAPH ====================

def create_agent():
    """Create the LangGraph agent with tools and checkpointing."""
    
    llm_with_tools = llm.bind_tools(tools)

    def should_continue(state: AgentState):
        """Determine if we should continue to tools or end."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return END

    async def call_model(state: AgentState):
        """Call the LLM with the current state."""
        messages = state["messages"]
        
        if not messages or not isinstance(messages[0], SystemMessage):
            messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)] + list(messages)
        
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)
    workflow = StateGraph(AgentState)
    
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)
    
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
    workflow.add_edge("tools", "agent")
    
    memory = MemorySaver()
    app = workflow.compile(checkpointer=memory)
    
    return app, memory


# Create the agent instance
agent_executor, memory_saver = create_agent()


# ==================== HELPER FUNCTIONS ====================

def get_session_id(provided_id: Optional[str] = None) -> str:
    """Generate or validate session ID."""
    if provided_id:
        return provided_id
    return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(4).hex()}"


def save_to_session(session_id: str, query: str, response: str):
    """Save conversation to session storage."""
    if session_id not in sessions:
        sessions[session_id] = []
    sessions[session_id].append({
        "query": query,
        "response": response,
        "timestamp": datetime.now().isoformat()
    })


def get_session_history(session_id: str) -> List[Dict]:
    """Get conversation history for a session."""
    return sessions.get(session_id, [])


def clear_session_history(session_id: str) -> bool:
    """Clear a session's history. Returns True if session existed."""
    if session_id in sessions:
        del sessions[session_id]
        return True
    return False


# ==================== AGENT INTERFACE FUNCTIONS ====================

async def process_chat(
    query: str,
    session_id: Optional[str] = None,
    language: str = "en",
    location: Optional[str] = None,
    crop: Optional[str] = None,
    chat_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    Process a chat query using the agentic AI with tools.
    
    Args:
        query: User's question
        session_id: Session ID for conversation continuity
        language: Preferred response language
        location: User's location
        crop: Current crop context
        chat_history: Previous conversation history
    
    Returns:
        Dict with answer, session_id, tools_used, and has_context
    """
    session_id = get_session_id(session_id)
    tools_used = []
    
    try:
        config = {"configurable": {"thread_id": session_id}}
        
        # Build messages from history
        messages = []
        for hist in (chat_history or []):
            if hist.get("role") == "user":
                messages.append(HumanMessage(content=hist["content"]))
            elif hist.get("role") == "assistant":
                messages.append(AIMessage(content=hist["content"]))
        
        messages.append(HumanMessage(content=query))
        
        state = {
            "messages": messages,
            "language": language,
            "user_location": location,
            "current_crop": crop
        }
        
        result = await agent_executor.ainvoke(state, config)
        
        final_messages = result.get("messages", [])
        answer = "I apologize, I could not process your request. Please try again."
        
        # Get the final AI response
        for msg in reversed(final_messages):
            if isinstance(msg, AIMessage) and msg.content:
                answer = msg.content
                break
        
        # Collect tools used
        for msg in final_messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    if tc.get("name") and tc["name"] not in tools_used:
                        tools_used.append(tc["name"])
        
        save_to_session(session_id, query, answer)
        
        return {
            "answer": answer,
            "session_id": session_id,
            "tools_used": tools_used,
            "has_context": len(tools_used) > 0
        }
    
    except Exception as e:
        logger.error(f"Chat error: {e}")
        
        # Attempt rollback on error
        try:
            config = {"configurable": {"thread_id": session_id}}
            state_history = list(agent_executor.get_state_history(config))
            if len(state_history) > 1:
                previous_state = state_history[1]
                agent_executor.update_state(config, previous_state.values)
                logger.info(f"Rolled back to previous state for session {session_id}")
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {rollback_error}")
        
        raise


async def process_speech_chat(
    query: str,
    session_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process a speech-to-text query using direct LLM call (faster response).
    
    Args:
        query: User's question from speech
        session_id: Session ID for conversation continuity
    
    Returns:
        Dict with answer and session_id
    """
    session_id = get_session_id(session_id)
    
    try:
        messages = [
            SystemMessage(content=SPEECH_SYSTEM_PROMPT),
            HumanMessage(content=query)
        ]
        
        response = await llm.ainvoke(messages)
        answer = response.content if response.content else "I could not process your request. Please try again."
        
        save_to_session(session_id, query, answer)
        
        return {
            "answer": answer,
            "session_id": session_id,
            "has_context": False,
            "tools_used": []
        }
    
    except Exception as e:
        logger.error(f"Speech chat error: {e}")
        raise


async def rollback_conversation(session_id: str, steps: int = 1) -> Dict[str, Any]:
    """
    Rollback a session to a previous state.
    
    Args:
        session_id: Session ID to rollback
        steps: Number of steps to rollback (1-10)
    
    Returns:
        Dict with status, message, and remaining history count
    """
    config = {"configurable": {"thread_id": session_id}}
    
    state_history = list(agent_executor.get_state_history(config))
    
    if len(state_history) <= steps:
        raise ValueError(f"Cannot rollback {steps} steps. Only {len(state_history)-1} previous states available.")
    
    target_state = state_history[steps]
    agent_executor.update_state(config, target_state.values)
    
    if session_id in sessions and len(sessions[session_id]) >= steps:
        sessions[session_id] = sessions[session_id][:-steps]
    
    return {
        "status": "success",
        "message": f"Rolled back {steps} step(s)",
        "session_id": session_id,
        "remaining_history": len(sessions.get(session_id, []))
    }
