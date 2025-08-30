from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openmeteo_requests
import geocoder
import pandas as pd
import requests_cache
from retry_requests import retry
from openai import OpenAI
from dotenv import load_dotenv
from os import getenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KrishiVaani Weather API",
    description="Weather API for agricultural advisory",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Initialize OpenAI client
try:
    client = OpenAI(
        api_key=getenv("api"),
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {e}")
    client = None

class LocationRequest(BaseModel):
    latitude: float
    longitude: float

@app.get("/")
async def root():
    return {
        "service": "KrishiVaani Weather API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "weather": "/weather"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "api_status": {
            "status": "healthy",
            "service": "KrishiVaani Weather API",
            "version": "1.0.0"
        },
        "services": {
            "openai_configured": client is not None,
            "weather_api_available": True,
            "cache_enabled": True
        }
    }

@app.post("/weather")
async def get_weather_data(location: LocationRequest):
    """
    Get weather data and agricultural advisory for given coordinates
    """
    try:
        logger.info(f"Fetching weather data for coordinates: {location.latitude}, {location.longitude}")
        
        # Weather API parameters
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": location.latitude,
            "longitude": location.longitude,
            "daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "rain_sum", "showers_sum", "snowfall_sum", "uv_index_max", "sunshine_duration", "wind_speed_10m_max", "wind_gusts_10m_max"],
            "hourly": ["temperature_2m", "rain", "snowfall", "cloud_cover", "wind_speed_10m", "soil_temperature_0cm", "soil_temperature_6cm", "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "weather_code", "surface_pressure", "relative_humidity_2m", "precipitation", "showers", "vapour_pressure_deficit", "soil_moisture_3_to_9cm", "soil_moisture_9_to_27cm", "soil_temperature_18cm"],
            "current": ["temperature_2m", "relative_humidity_2m", "precipitation", "rain", "showers", "snowfall", "cloud_cover", "weather_code", "wind_speed_10m", "is_day", "apparent_temperature"],
            "timezone": "auto",
            "precipitation_unit": "inch",
        }
        
        responses = openmeteo.weather_api(url, params=params)
        response = responses[0]
        
        # Process current data
        current = response.Current()
        current_data = {
            "temperature": round(current.Variables(0).Value(), 1),
            "humidity": round(current.Variables(1).Value(), 1),
            "precipitation": round(current.Variables(2).Value(), 2),
            "rain": round(current.Variables(3).Value(), 2),
            "showers": round(current.Variables(4).Value(), 2),
            "snowfall": round(current.Variables(5).Value(), 2),
            "cloud_cover": round(current.Variables(6).Value(), 1),
            "weather_code": int(current.Variables(7).Value()),
            "wind_speed": round(current.Variables(8).Value(), 1),
            "is_day": bool(current.Variables(9).Value()),
            "apparent_temperature": round(current.Variables(10).Value(), 1)
        }
        
        # Process daily data for 7-day forecast
        daily = response.Daily()
        daily_weather_code = daily.Variables(0).ValuesAsNumpy()
        daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
        daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
        daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
        daily_showers_sum = daily.Variables(4).ValuesAsNumpy()
        daily_snowfall_sum = daily.Variables(5).ValuesAsNumpy()
        daily_uv_index_max = daily.Variables(6).ValuesAsNumpy()
        daily_sunshine_duration = daily.Variables(7).ValuesAsNumpy()
        daily_wind_speed_10m_max = daily.Variables(8).ValuesAsNumpy()
        daily_wind_gusts_10m_max = daily.Variables(9).ValuesAsNumpy()
        
        daily_data = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}
        
        daily_data["weather_code"] = daily_weather_code
        daily_data["temperature_2m_max"] = daily_temperature_2m_max
        daily_data["temperature_2m_min"] = daily_temperature_2m_min
        daily_data["rain_sum"] = daily_rain_sum
        daily_data["showers_sum"] = daily_showers_sum
        daily_data["snowfall_sum"] = daily_snowfall_sum
        daily_data["uv_index_max"] = daily_uv_index_max
        daily_data["sunshine_duration"] = daily_sunshine_duration
        daily_data["wind_speed_10m_max"] = daily_wind_speed_10m_max
        daily_data["wind_gusts_10m_max"] = daily_wind_gusts_10m_max
        
        daily_dataframe = pd.DataFrame(data=daily_data)
        
        # Process hourly data
        hourly = response.Hourly()
        hourly_temperature_2m = hourly.Variables(0).ValuesAsNumpy()
        hourly_rain = hourly.Variables(1).ValuesAsNumpy()
        hourly_snowfall = hourly.Variables(2).ValuesAsNumpy()
        hourly_cloud_cover = hourly.Variables(3).ValuesAsNumpy()
        hourly_wind_speed_10m = hourly.Variables(4).ValuesAsNumpy()
        hourly_soil_temperature_0cm = hourly.Variables(5).ValuesAsNumpy()
        hourly_soil_temperature_6cm = hourly.Variables(6).ValuesAsNumpy()
        hourly_soil_moisture_0_to_1cm = hourly.Variables(7).ValuesAsNumpy()
        hourly_soil_moisture_1_to_3cm = hourly.Variables(8).ValuesAsNumpy()
        hourly_weather_code = hourly.Variables(9).ValuesAsNumpy()
        hourly_surface_pressure = hourly.Variables(10).ValuesAsNumpy()
        hourly_relative_humidity_2m = hourly.Variables(11).ValuesAsNumpy()
        hourly_precipitation = hourly.Variables(12).ValuesAsNumpy()
        hourly_showers = hourly.Variables(13).ValuesAsNumpy()
        hourly_vapour_pressure_deficit = hourly.Variables(14).ValuesAsNumpy()
        hourly_soil_moisture_3_to_9cm = hourly.Variables(15).ValuesAsNumpy()
        hourly_soil_moisture_9_to_27cm = hourly.Variables(16).ValuesAsNumpy()
        hourly_soil_temperature_18cm = hourly.Variables(17).ValuesAsNumpy()
        
        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        
        hourly_data["temperature_2m"] = hourly_temperature_2m
        hourly_data["rain"] = hourly_rain
        hourly_data["snowfall"] = hourly_snowfall
        hourly_data["cloud_cover"] = hourly_cloud_cover
        hourly_data["wind_speed_10m"] = hourly_wind_speed_10m
        hourly_data["soil_temperature_0cm"] = hourly_soil_temperature_0cm
        hourly_data["soil_temperature_6cm"] = hourly_soil_temperature_6cm
        hourly_data["soil_moisture_0_to_1cm"] = hourly_soil_moisture_0_to_1cm
        hourly_data["soil_moisture_1_to_3cm"] = hourly_soil_moisture_1_to_3cm
        hourly_data["weather_code"] = hourly_weather_code
        hourly_data["surface_pressure"] = hourly_surface_pressure
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m
        hourly_data["precipitation"] = hourly_precipitation
        hourly_data["showers"] = hourly_showers
        hourly_data["vapour_pressure_deficit"] = hourly_vapour_pressure_deficit
        hourly_data["soil_moisture_3_to_9cm"] = hourly_soil_moisture_3_to_9cm
        hourly_data["soil_moisture_9_to_27cm"] = hourly_soil_moisture_9_to_27cm
        hourly_data["soil_temperature_18cm"] = hourly_soil_temperature_18cm
        
        hourly_dataframe = pd.DataFrame(data=hourly_data)
        
        # Get AI advisory if client is available
        advisory = "Weather data available. Check the forecast for agricultural planning."
        if client:
            try:
                logger.info("Generating AI advisory...")
                resp = client.chat.completions.create(
                    model="gemini-2.5-pro",
                    messages=[
                        {"role": "user", "content": """
You are an expert agricultural data analyst with strong skills in weather forecasting and crop advisory.

Task:
I will provide you with hourly and daily weather data in dataframe format.

Instructions:
1. Analyze the weather data to interpret future weather conditions and trends.
2. Identify key factors such as rainfall, temperature, humidity, and extreme events that may affect crop growth.
3. Based on the predicted weather, provide actionable recommendations for managing crops.
4. Advise on steps to protect, irrigate, fertilize, or harvest crops depending on the forecast.

Output Format:
- Start with a summary of the future weather conditions.
- Explain how these conditions could impact crops.
- Provide clear, practical recommendations in bullet points for the farmer to follow.
- Keep the response concise and actionable (max 200 words).
                        """},
                        {
                            "role": "assistant",
                            "content": "I'll analyze the weather data and provide agricultural recommendations."
                        },
                        {
                            "role": "user",
                            "content": f"Hourly dataframe - {hourly_dataframe}\nDaily dataframe - {daily_dataframe}"
                        }
                    ]
                )
                advisory = resp.choices[0].message.content
            except Exception as e:
                logger.error(f"Error generating AI advisory: {e}")
                advisory = "Weather data available. Check the forecast for agricultural planning."
        
        # Create 7-day forecast for frontend
        forecast = []
        for i in range(7):
            if i < len(daily_dataframe):
                day_data = daily_dataframe.iloc[i]
                forecast.append({
                    "day": day_data["date"].strftime("%A")[:3],  # First 3 letters of day
                    "temp": f"{int(day_data['temperature_2m_min'])}-{int(day_data['temperature_2m_max'])}°",
                    "rain": f"{int(day_data['rain_sum'] + day_data['showers_sum'])}%",
                    "weather_code": int(day_data["weather_code"])
                })
        
        # Get weather condition description
        weather_condition = get_weather_condition(current_data["weather_code"])
        
        result = {
            "weather_data": {
                "current": {
                    "temperature": current_data["temperature"],
                    "condition": weather_condition,
                    "humidity": current_data["humidity"],
                    "wind_speed": current_data["wind_speed"],
                    "visibility": "8 km",
                    "rain_chance": f"{int(current_data['rain'] + current_data['showers'])}%",
                    "apparent_temperature": current_data["apparent_temperature"],
                    "cloud_cover": current_data["cloud_cover"]
                },
                "forecast": forecast,
                "location": {
                    "coordinates": f"Lat: {location.latitude}, Long: {location.longitude}",
                    "latitude": location.latitude,
                    "longitude": location.longitude
                }
            },
            "agricultural_advisory": {
                "recommendations": advisory,
                "ai_generated": client is not None,
                "last_updated": "Current"
            },
            "data_quality": {
                "source": "Open-Meteo API",
                "forecast_days": 7,
                "hourly_data_available": True,
                "soil_data_available": True
            }
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error fetching weather data: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching weather data: {str(e)}")

def get_weather_condition(weather_code):
    """Convert weather code to human-readable condition"""
    weather_conditions = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Foggy",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        56: "Light freezing drizzle",
        57: "Dense freezing drizzle",
        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",
        66: "Light freezing rain",
        67: "Heavy freezing rain",
        71: "Slight snow fall",
        73: "Moderate snow fall",
        75: "Heavy snow fall",
        77: "Snow grains",
        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",
        85: "Slight snow showers",
        86: "Heavy snow showers",
        95: "Thunderstorm",
        96: "Thunderstorm with slight hail",
        99: "Thunderstorm with heavy hail"
    }
    return weather_conditions.get(weather_code, "Unknown")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
