from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64
import pandas as pd
import io
from PIL import Image
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="KrishiVaani Pest Detection API",
    description="API for detecting pests and providing treatment recommendations",
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

# Load pesticides data
try:
    df = pd.read_csv("Pesticides.csv")
    logger.info("Pesticides data loaded successfully")
except Exception as e:
    logger.error(f"Error loading pesticides data: {e}")
    df = pd.DataFrame()

# Initialize OpenAI client
try:
    client = OpenAI(
        api_key=os.getenv("perplexity_api"),
        base_url="https://api.perplexity.ai"
    )
    logger.info("OpenAI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing OpenAI client: {e}")
    client = None

@app.get("/")
async def root():
    return {"message": "KrishiVaani Pest Detection API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "pesticides_loaded": len(df) > 0, "openai_configured": client is not None}

@app.post("/detect-pest")
async def detect_pest(file: UploadFile = File(...)):
    """
    Detect pest from uploaded image and provide treatment recommendations
    """
    try:
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Read and process image
        image_data = await file.read()
        
        # Convert to base64
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        if not client:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        # Step 1: Identify the pest
        logger.info("Identifying pest from image...")
        response0 = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert entomologist. You have to identify the pest in the image I will send. And just tell the name do not explain how you can tell it only on word answer."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Identify this pest:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            temperature=0.1
        )
        
        pest_name = response0.choices[0].message.content.strip()
        logger.info(f"Pest identified: {pest_name}")
        
        # Step 2: Get treatment recommendations and severity assessment
        logger.info("Getting treatment recommendations...")
        response1 = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "system",
                    "content": f"You are an expert entomologist. I will send you name of an insect or a pest, you have to tell me if it is bad for my crop and how to get rid of it. If they are harmful to my crop then give a valid treatment guide, in one line like a summary only. You can use {df} data set to suggest the name of pesticide according to the pest. Do not use [3] or with anyother number and ** in you output"
                },
                {
                    "role": "user",
                    "content": f"{pest_name}"
                }
            ]
        )
        
        treatment_info = response1.choices[0].message.content.strip()
        
        # Step 3: Get severity and prevention recommendations
        logger.info("Getting severity and prevention recommendations...")
        response2 = client.chat.completions.create(
            model="sonar-pro",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert entomologist. For the given pest, provide: 1) Severity level (Low/Medium/High), 2) Prevention tips in English. Format as JSON: {\"severity\": \"Low/Medium/High\", \"prevention_english\": \"text\"}"
                },
                {
                    "role": "user",
                    "content": f"Pest: {pest_name}"
                }
            ]
        )
        
        severity_prevention_info = response2.choices[0].message.content.strip()
        
        # Find pesticides from CSV
        pesticides = []
        if len(df) > 0:
            try:
                # Escape special regex characters in pest_name
                import re
                escaped_pest_name = re.escape(pest_name)
                pest_row = df[df['Pest Name'].str.contains(escaped_pest_name, case=False, na=False)]
                if not pest_row.empty:
                    pesticides = pest_row['Most Commonly Used Pesticides'].iloc[0].split(', ')
            except Exception as e:
                logger.warning(f"Could not find pesticides for {pest_name}: {e}")
                pesticides = []
        
        # Parse severity and prevention info
        try:
            import json
            severity_data = json.loads(severity_prevention_info)
            severity = severity_data.get("severity", "Medium")
            prevention_english = severity_data.get("prevention_english", "Keep field clean. Maintain proper irrigation.")
        except:
            severity = "Medium"
            prevention_english = "Keep field clean. Maintain proper irrigation."
        
        # Prepare response
        result = {
            "pestDetected": True,
            "pestName": pest_name,
            "severity": severity,
            "confidence": "85%",  # Default confidence
            "treatment": {
                "english": treatment_info
            },
            "pesticides": pesticides,
            "prevention": {
                "english": prevention_english
            }
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        logger.error(f"Error in pest detection: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@app.get("/pesticides")
async def get_pesticides():
    """
    Get list of all pests and their recommended pesticides
    """
    try:
        if len(df) == 0:
            return {"pesticides": []}
        
        pesticides_list = df.to_dict('records')
        return {"pesticides": pesticides_list}
    except Exception as e:
        logger.error(f"Error getting pesticides: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving pesticides data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
