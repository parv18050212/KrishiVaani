"""
KrishiVaani Pest Detection Router
Pest identification and treatment recommendations using AI
"""

from fastapi import APIRouter, File, UploadFile, HTTPException
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
from typing import Dict, List, Optional
from pathlib import Path

# Load environment variables from backend/.env
load_dotenv(Path(__file__).parent / ".env")

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/pest", tags=["Pest Detection"])

# Load pesticides data
try:
    # Try multiple paths for the CSV file
    csv_paths = [
        "backend/Pesticides.csv",
        "Pesticides.csv",
        os.path.join(os.path.dirname(__file__), "Pesticides.csv")
    ]
    df = pd.DataFrame()
    for path in csv_paths:
        if os.path.exists(path):
            df = pd.read_csv(path)
            logger.info(f"Pesticides data loaded from {path}")
            break
    if df.empty:
        logger.warning("Pesticides CSV not found, using empty dataframe")
except Exception as e:
    logger.error(f"Error loading pesticides data: {e}")
    df = pd.DataFrame()

# Initialize OpenAI client for Perplexity
try:
    client = OpenAI(
        api_key=os.getenv("PERPLEXITY_API_KEY"),
        base_url="https://api.perplexity.ai"
    )
    logger.info("Pest AI client initialized successfully")
except Exception as e:
    logger.error(f"Error initializing AI client: {e}")
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
            
            if width < 100 or height < 100:
                return 0.3
            elif width < 300 or height < 300:
                return 0.6
            elif width < 800 or height < 800:
                return 0.8
            else:
                return 0.95
        except Exception as e:
            logger.warning(f"Error analyzing image quality: {e}")
            return 0.5
    
    def calculate_pest_name_confidence(self, pest_name: str) -> float:
        """Calculate confidence based on pest name matching with known pests"""
        if not pest_name or len(pest_name.strip()) == 0:
            return 0.0
        
        pest_name_lower = pest_name.lower().strip()
        
        if pest_name_lower in self.known_pests:
            return 0.95
        
        for known_pest in self.known_pests:
            if pest_name_lower in known_pest or known_pest in pest_name_lower:
                return 0.85
        
        common_pest_words = ['aphid', 'beetle', 'worm', 'mite', 'fly', 'bug', 'hopper', 'borer', 'cricket', 'grasshopper']
        for word in common_pest_words:
            if word in pest_name_lower:
                return 0.7
        
        return 0.4
    
    def calculate_pesticide_availability_score(self, pesticides: List[str]) -> float:
        """Calculate confidence based on pesticide availability"""
        if not pesticides:
            return 0.3
        
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
        score = 0.5
        
        if treatment_info and len(treatment_info.strip()) > 10:
            score += 0.2
        
        valid_severities = ['low', 'medium', 'high']
        if severity.lower() in valid_severities:
            score += 0.2
        
        if pest_name and treatment_info:
            pest_related_words = ['pest', 'insect', 'bug', 'worm', 'mite', 'aphid', 'beetle']
            treatment_lower = treatment_info.lower()
            for word in pest_related_words:
                if word in treatment_lower:
                    score += 0.1
                    break
        
        return min(score, 1.0)
    
    def calculate_overall_confidence(self, 
                                   image_data: bytes, 
                                   pest_name: str, 
                                   pesticides: List[str], 
                                   treatment_info: str, 
                                   severity: str) -> Dict:
        """Calculate overall confidence score and breakdown"""
        
        image_score = self.calculate_image_quality_score(image_data)
        pest_name_score = self.calculate_pest_name_confidence(pest_name)
        pesticide_score = self.calculate_pesticide_availability_score(pesticides)
        consistency_score = self.calculate_response_consistency_score(pest_name, treatment_info, severity)
        
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


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "Pest Detection API",
        "pesticides_loaded": len(df) > 0,
        "ai_configured": client is not None,
        "total_pests": len(df)
    }


@router.post("/detect")
async def detect_pest(file: UploadFile = File(...)):
    """
    Detect pest from uploaded image and provide treatment recommendations
    """
    try:
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        image_data = await file.read()
        image_base64 = base64.b64encode(image_data).decode("utf-8")
        
        if not client:
            raise HTTPException(status_code=500, detail="AI service not configured")
        
        # Single API call to identify pest and get all information
        logger.info("Analyzing pest image...")
        response = client.chat.completions.create(
            model="sonar",  # Using faster model
            messages=[
                {
                    "role": "system",
                    "content": """You are an expert entomologist. Analyze the pest image and provide a JSON response with:
1. pest_name: Name of the pest (single word or short phrase)
2. severity: Low/Medium/High
3. treatment: One-line treatment recommendation
4. prevention: One-line prevention tip

Respond ONLY with valid JSON in this exact format:
{"pest_name": "name", "severity": "Medium", "treatment": "treatment text", "prevention": "prevention text"}"""
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Identify this pest and provide treatment:"},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            temperature=0.1
        )
        
        response_text = response.choices[0].message.content.strip()
        logger.info(f"AI Response: {response_text}")
        
        # Parse JSON response
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{[^{}]*\}', response_text)
            if json_match:
                pest_data = json.loads(json_match.group())
            else:
                pest_data = json.loads(response_text)
            
            pest_name = pest_data.get("pest_name", "Unknown pest")
            severity = pest_data.get("severity", "Medium")
            treatment_info = pest_data.get("treatment", "Consult local agricultural officer for treatment.")
            prevention_english = pest_data.get("prevention", "Keep field clean and maintain proper irrigation.")
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Could not parse JSON response: {e}")
            # Fallback: treat response as pest name and use defaults
            pest_name = response_text.split()[0] if response_text else "Unknown pest"
            severity = "Medium"
            treatment_info = "Consult local agricultural officer for specific treatment recommendations."
            prevention_english = "Keep field clean and maintain proper irrigation."
        
        logger.info(f"Pest identified: {pest_name}")
        
        # Find pesticides from CSV
        pesticides = []
        if len(df) > 0:
            try:
                escaped_pest_name = re.escape(pest_name)
                pest_row = df[df['Pest Name'].str.contains(escaped_pest_name, case=False, na=False)]
                if not pest_row.empty:
                    pesticides = pest_row['Most Commonly Used Pesticides'].iloc[0].split(', ')
            except Exception as e:
                logger.warning(f"Could not find pesticides for {pest_name}: {e}")
                pesticides = []
        
        # Calculate confidence score
        confidence_data = confidence_calculator.calculate_overall_confidence(
            image_data, pest_name, pesticides, treatment_info, severity
        )
        
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


@router.get("/pesticides")
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
