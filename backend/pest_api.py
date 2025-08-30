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
import re
import json
from typing import Dict, List, Tuple, Optional

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

class ConfidenceCalculator:
    """Calculate confidence score based on multiple factors"""
    
    def __init__(self, pesticides_df: pd.DataFrame):
        self.pesticides_df = pesticides_df
        self.known_pests = set(pesticides_df['Pest Name'].str.lower().tolist()) if len(pesticides_df) > 0 else set()
    
    def calculate_image_quality_score(self, image_data: bytes) -> float:
        """Calculate confidence based on image quality"""
        try:
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Check image dimensions
            if width < 100 or height < 100:
                return 0.3  # Very low confidence for tiny images
            elif width < 300 or height < 300:
                return 0.6  # Low confidence for small images
            elif width < 800 or height < 800:
                return 0.8  # Medium confidence for medium images
            else:
                return 0.95  # High confidence for large images
                
        except Exception as e:
            logger.warning(f"Error analyzing image quality: {e}")
            return 0.5  # Default medium confidence
    
    def calculate_pest_name_confidence(self, pest_name: str) -> float:
        """Calculate confidence based on pest name matching with known pests"""
        if not pest_name or len(pest_name.strip()) == 0:
            return 0.0
        
        pest_name_lower = pest_name.lower().strip()
        
        # Exact match
        if pest_name_lower in self.known_pests:
            return 0.95
        
        # Partial match (contains)
        for known_pest in self.known_pests:
            if pest_name_lower in known_pest or known_pest in pest_name_lower:
                return 0.85
        
        # Fuzzy match (common words)
        common_pest_words = ['aphid', 'beetle', 'worm', 'mite', 'fly', 'bug', 'hopper', 'borer', 'cricket', 'grasshopper']
        for word in common_pest_words:
            if word in pest_name_lower:
                return 0.7
        
        # If no match found, lower confidence
        return 0.4
    
    def calculate_pesticide_availability_score(self, pesticides: List[str]) -> float:
        """Calculate confidence based on pesticide availability"""
        if not pesticides:
            return 0.3  # Low confidence if no pesticides found
        
        # Higher confidence if more pesticides are available
        if len(pesticides) >= 3:
            return 0.9
        elif len(pesticides) == 2:
            return 0.8
        elif len(pesticides) == 1:
            return 0.7
        else:
            return 0.3
    
    def calculate_response_consistency_score(self, pest_name: str, treatment_info: str, severity: str) -> float:
        """Calculate confidence based on response consistency"""
        score = 0.5  # Base score
        
        # Check if treatment info is meaningful
        if treatment_info and len(treatment_info.strip()) > 10:
            score += 0.2
        
        # Check if severity is valid
        valid_severities = ['low', 'medium', 'high']
        if severity.lower() in valid_severities:
            score += 0.2
        
        # Check if pest name and treatment are related
        if pest_name and treatment_info:
            # Simple keyword matching
            pest_keywords = pest_name.lower().split()
            treatment_lower = treatment_info.lower()
            
            # Check if any pest-related keywords appear in treatment
            pest_related_words = ['pest', 'insect', 'bug', 'worm', 'mite', 'aphid', 'beetle']
            for word in pest_related_words:
                if word in treatment_lower:
                    score += 0.1
                    break
        
        return min(score, 1.0)  # Cap at 1.0
    
    def calculate_overall_confidence(self, 
                                   image_data: bytes, 
                                   pest_name: str, 
                                   pesticides: List[str], 
                                   treatment_info: str, 
                                   severity: str) -> Dict[str, any]:
        """Calculate overall confidence score and breakdown"""
        
        # Calculate individual scores
        image_score = self.calculate_image_quality_score(image_data)
        pest_name_score = self.calculate_pest_name_confidence(pest_name)
        pesticide_score = self.calculate_pesticide_availability_score(pesticides)
        consistency_score = self.calculate_response_consistency_score(pest_name, treatment_info, severity)
        
        # Weighted average (you can adjust these weights)
        weights = {
            'image_quality': 0.25,
            'pest_name_match': 0.35,
            'pesticide_availability': 0.25,
            'response_consistency': 0.15
        }
        
        overall_confidence = (
            image_score * weights['image_quality'] +
            pest_name_score * weights['pest_name_match'] +
            pesticide_score * weights['pesticide_availability'] +
            consistency_score * weights['response_consistency']
        )
        
        # Convert to percentage
        confidence_percentage = round(overall_confidence * 100, 1)
        
        return {
            'overall_confidence': f"{confidence_percentage}%",
            'confidence_score': confidence_percentage,
            'breakdown': {
                'image_quality': f"{image_score * 100:.1f}%",
                'pest_name_match': f"{pest_name_score * 100:.1f}%",
                'pesticide_availability': f"{pesticide_score * 100:.1f}%",
                'response_consistency': f"{consistency_score * 100:.1f}%"
            },
            'factors': {
                'image_size_adequate': image_score > 0.7,
                'pest_in_database': pest_name_score > 0.8,
                'pesticides_available': pesticide_score > 0.6,
                'response_consistent': consistency_score > 0.7
            }
        }

# Initialize confidence calculator
confidence_calculator = ConfidenceCalculator(df)

@app.get("/")
async def root():
    return {
        "service": "KrishiVaani Pest Detection API",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "detect_pest": "/detect-pest",
            "pesticides": "/pesticides"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "api_status": {
            "status": "healthy",
            "service": "KrishiVaani Pest Detection API",
            "version": "1.0.0"
        },
        "services": {
            "pesticides_loaded": len(df) > 0,
            "openai_configured": client is not None,
            "total_pests_available": len(df) if len(df) > 0 else 0
        }
    }

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
                escaped_pest_name = re.escape(pest_name)
                pest_row = df[df['Pest Name'].str.contains(escaped_pest_name, case=False, na=False)]
                if not pest_row.empty:
                    pesticides = pest_row['Most Commonly Used Pesticides'].iloc[0].split(', ')
            except Exception as e:
                logger.warning(f"Could not find pesticides for {pest_name}: {e}")
                pesticides = []
        
        # Parse severity and prevention info
        try:
            severity_data = json.loads(severity_prevention_info)
            severity = severity_data.get("severity", "Medium")
            prevention_english = severity_data.get("prevention_english", "Keep field clean. Maintain proper irrigation.")
        except:
            severity = "Medium"
            prevention_english = "Keep field clean. Maintain proper irrigation."
        
        # Calculate confidence score
        confidence_data = confidence_calculator.calculate_overall_confidence(
            image_data, pest_name, pesticides, treatment_info, severity
        )
        
        # Prepare response
        result = {
            "pest_detection": {
                "detected": True,
                "pest_name": pest_name,
                "severity": severity,
                "confidence": confidence_data['overall_confidence'],
                "confidence_score": confidence_data['confidence_score'],
                "confidence_breakdown": confidence_data['breakdown'],
                "confidence_factors": confidence_data['factors']
            },
            "treatment": {
                "recommendations": {
                    "english": treatment_info
                },
                "pesticides": pesticides,
                "prevention": {
                    "english": prevention_english
                }
            },
            "analysis": {
                "image_processed": True,
                "ai_model_used": "sonar-pro",
                "processing_time": "real-time"
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
            return {
                "pesticides_data": {
                    "total_pests": 0,
                    "data_loaded": False,
                    "pesticides": []
                }
            }
        
        pesticides_list = df.to_dict('records')
        return {
            "pesticides_data": {
                "total_pests": len(pesticides_list),
                "data_loaded": True,
                "last_updated": "Current",
                "pesticides": pesticides_list
            }
        }
    except Exception as e:
        logger.error(f"Error getting pesticides: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving pesticides data")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
