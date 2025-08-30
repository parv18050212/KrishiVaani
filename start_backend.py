#!/usr/bin/env python3
"""
Startup script for KrishiVaani Pest Detection API
"""

import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Check if API key is configured
    api_key = os.getenv("perplexity_api")
    if not api_key:
        print("⚠️  Warning: PERPLEXITY_API environment variable not set!")
        print("Please create a .env file with your Perplexity API key:")
        print("perplexity_api=your_api_key_here")
        print("\nYou can get a free API key from: https://www.perplexity.ai/settings/api")
    
    print("🚀 Starting KrishiVaani Pest Detection API...")
    print("📡 API will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop the server")
    
    # Run the server
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
