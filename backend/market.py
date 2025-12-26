"""
KrishiVaani Market API Router
Market prices and mandi information using AI and geocoding
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import os
import logging
import json
from pathlib import Path

# Load environment variables from backend/.env
load_dotenv(Path(__file__).parent / ".env")

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/market", tags=["Market Prices"])

# Initialize Nominatim geocoder
geolocator = Nominatim(user_agent="krishivaani-market-app")
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

# Initialize OpenAI client for Perplexity
try:
    client = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai"
    )
    logger.info("Market AI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing AI client: {e}")
    client = None


class LocationRequest(BaseModel):
    latitude: float
    longitude: float


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Market Prices API",
        "ai_configured": client is not None,
        "geocoding_available": True
    }


@router.post("/prices")
async def get_market_prices(location: LocationRequest):
    """
    Get market prices for agricultural commodities based on location
    """
    try:
        logger.info(f"Fetching market prices for coordinates: {location.latitude}, {location.longitude}")
        
        # Perform reverse geocoding to get state and district
        location_info = reverse(f"{location.latitude}, {location.longitude}")
        
        if not location_info or not location_info.raw or 'address' not in location_info.raw:
            raise HTTPException(status_code=400, detail="Could not retrieve location details")
        
        address_components = location_info.raw['address']
        state = address_components.get('state', 'Unknown State')
        district = address_components.get('county', 'Unknown District')
        
        logger.info(f"Location: {district}, {state}")
        
        if not client:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        # Create a comprehensive prompt for market price analysis
        prompt = f"""
        Provide current market prices for agricultural commodities in {district}, {state} in JSON format.
        
        Return ONLY a valid JSON object with this exact structure:
        {{
            "current_prices": [
                {{
                    "crop": "Wheat",
                    "current_price": "2,150",
                    "yesterday_price": "2,100",
                    "trend": "up",
                    "change": "+50",
                    "unit": "per quintal"
                }}
            ],
            "nearby_mandis": [
                {{
                    "name": "Local Mandi",
                    "distance": "2 km",
                    "status": "Open",
                    "timing": "6:00 AM - 12:00 PM"
                }}
            ],
            "recommendations": "Wheat prices are rising. Wait for 2-3 days. Mustard prices are stable, you can sell now."
        }}
        
        Include 5-8 major crops with realistic prices. Include 3-4 nearby mandis. Keep recommendations concise.
        """
        
        logger.info("Generating market price analysis...")
        resp = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        try:
            market_data = json.loads(resp.choices[0].message.content)
            
            result = {
                "market_data": {
                    "location": {
                        "district": district,
                        "state": state,
                        "coordinates": f"Lat: {location.latitude}, Long: {location.longitude}",
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    },
                    "current_prices": market_data.get("current_prices", []),
                    "nearby_mandis": market_data.get("nearby_mandis", [])
                },
                "recommendations": {
                    "trading_advice": market_data.get("recommendations", "Market data available."),
                    "ai_generated": True,
                    "last_updated": "Current"
                },
                "data_quality": {
                    "source": "AI Analysis",
                    "geocoding_used": True,
                    "real_time_data": True
                }
            }
        except json.JSONDecodeError:
            logger.warning("AI response not in JSON format, using fallback data")
            result = {
                "market_data": {
                    "location": {
                        "district": district,
                        "state": state,
                        "coordinates": f"Lat: {location.latitude}, Long: {location.longitude}",
                        "latitude": location.latitude,
                        "longitude": location.longitude
                    },
                    "current_prices": [
                        {"crop": "Wheat", "current_price": "2,150", "yesterday_price": "2,100", "trend": "up", "change": "+50", "unit": "per quintal"},
                        {"crop": "Rice", "current_price": "1,950", "yesterday_price": "2,000", "trend": "down", "change": "-50", "unit": "per quintal"},
                        {"crop": "Corn", "current_price": "1,750", "yesterday_price": "1,720", "trend": "up", "change": "+30", "unit": "per quintal"},
                        {"crop": "Mustard", "current_price": "5,200", "yesterday_price": "5,180", "trend": "up", "change": "+20", "unit": "per quintal"},
                        {"crop": "Chickpea", "current_price": "4,800", "yesterday_price": "4,850", "trend": "down", "change": "-50", "unit": "per quintal"}
                    ],
                    "nearby_mandis": [
                        {"name": f"{district} Mandi", "distance": "2 km", "status": "Open", "timing": "6:00 AM - 12:00 PM"},
                        {"name": "District Mandi", "distance": "15 km", "status": "Open", "timing": "5:00 AM - 1:00 PM"},
                        {"name": "APMC Mandi", "distance": "25 km", "status": "Open", "timing": "24/7"}
                    ]
                },
                "recommendations": {
                    "trading_advice": f"Market data for {district}, {state}. Check current prices above for trading decisions.",
                    "ai_generated": False,
                    "last_updated": "Current"
                },
                "data_quality": {
                    "source": "Fallback Data",
                    "geocoding_used": True,
                    "real_time_data": False
                }
            }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error fetching market prices: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching market prices: {str(e)}")
