#!/usr/bin/env python3
"""
Startup script for KrishiVaani Weather API
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Check if API key is configured
    api_key = os.getenv("api")
    if not api_key:
        print("⚠️  Warning: API environment variable not set!")
        print("Please create a .env file with your Google AI API key:")
        print("api=your_google_ai_api_key_here")
        print("\nYou can get a free API key from: https://makersuite.google.com/app/apikey")
    
    print("🚀 Starting KrishiVaani Weather API...")
    print("📡 API will be available at: http://localhost:8001")
    print("📚 API Documentation: http://localhost:8001/docs")
    print("🔍 Health Check: http://localhost:8001/health")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the server
    uvicorn.run(
        "weather_api:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
