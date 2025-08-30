import os
import re
import json
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.generativeai import configure, GenerativeModel
from dotenv import load_dotenv
import base64
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
configure(api_key=GEMINI_API_KEY)

# Initialize FastAPI
app = FastAPI()

# Allow CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gemini Model
model = GenerativeModel("gemini-1.5-flash")

def extract_npk_values_from_image(image_bytes):
    """Extract NPK values from soil health card image using Gemini Vision"""
    try:
        # Convert image bytes to base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Create prompt for Gemini Vision
        prompt = """
        Analyze this soil health card image and extract the following information in JSON format:
        {
            "nitrogen": {
                "value": "extracted value with unit",
                "level": "Low/Medium/High based on value",
                "percentage": "percentage score 0-100"
            },
            "phosphorus": {
                "value": "extracted value with unit", 
                "level": "Low/Medium/High based on value",
                "percentage": "percentage score 0-100"
            },
            "potassium": {
                "value": "extracted value with unit",
                "level": "Low/Medium/High based on value", 
                "percentage": "percentage score 0-100"
            },
            "ph": {
                "value": "extracted pH value",
                "level": "Good/Neutral/Poor based on value",
                "percentage": "percentage score 0-100"
            }
        }
        
        Only return the JSON object, no additional text.
        """
        
        # Call Gemini Vision API
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_base64}
        ])
        
        # Parse JSON response
        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # Fallback to regex extraction if JSON parsing fails
            return extract_npk_with_regex(image_bytes)
            
    except Exception as e:
        print(f"Error in Gemini Vision extraction: {e}")
        return extract_npk_with_regex(image_bytes)

def extract_npk_with_regex(image_bytes):
    """Fallback method using OCR with regex patterns"""
    try:
        # Convert image to text using Gemini (simplified approach)
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        prompt = "Extract all text from this soil health card image. Return only the raw text content."
        
        response = model.generate_content([
            prompt,
            {"mime_type": "image/jpeg", "data": image_base64}
        ])
        
        extracted_text = response.text
        
        # Extract NPK values using regex
        nitrogen_match = re.search(r"Available\s*Nitrogen.*?(\d+\.?\d*)", extracted_text, re.IGNORECASE | re.DOTALL)
        phosphorus_match = re.search(r"Available\s*Phosphorus.*?(\d+\.?\d*)", extracted_text, re.IGNORECASE | re.DOTALL)
        potassium_match = re.search(r"Available\s*Potassium.*?(\d+\.?\d*)", extracted_text, re.IGNORECASE | re.DOTALL)
        ph_match = re.search(r"pH.*?(\d+\.?\d*)", extracted_text, re.IGNORECASE | re.DOTALL)
        
        # Determine levels and percentages based on extracted values
        def get_level_and_percentage(value_str, nutrient_type):
            if not value_str:
                return {"value": "Not detected", "level": "Unknown", "percentage": 50}
            
            try:
                value = float(value_str)
                if nutrient_type == "nitrogen":
                    if value < 140: return {"value": f"{value} kg/ha", "level": "Low", "percentage": 30}
                    elif value < 280: return {"value": f"{value} kg/ha", "level": "Medium", "percentage": 60}
                    else: return {"value": f"{value} kg/ha", "level": "High", "percentage": 90}
                elif nutrient_type == "phosphorus":
                    if value < 10: return {"value": f"{value} kg/ha", "level": "Low", "percentage": 25}
                    elif value < 22: return {"value": f"{value} kg/ha", "level": "Medium", "percentage": 60}
                    else: return {"value": f"{value} kg/ha", "level": "High", "percentage": 85}
                elif nutrient_type == "potassium":
                    if value < 108: return {"value": f"{value} kg/ha", "level": "Low", "percentage": 35}
                    elif value < 280: return {"value": f"{value} kg/ha", "level": "Medium", "percentage": 65}
                    else: return {"value": f"{value} kg/ha", "level": "High", "percentage": 90}
                elif nutrient_type == "ph":
                    if value < 6.0: return {"value": f"{value}", "level": "Acidic", "percentage": 40}
                    elif value < 7.5: return {"value": f"{value}", "level": "Good", "percentage": 75}
                    else: return {"value": f"{value}", "level": "Alkaline", "percentage": 60}
            except:
                return {"value": f"{value_str} kg/ha", "level": "Unknown", "percentage": 50}
        
        nitrogen = get_level_and_percentage(nitrogen_match.group(1) if nitrogen_match else None, "nitrogen")
        phosphorus = get_level_and_percentage(phosphorus_match.group(1) if phosphorus_match else None, "phosphorus")
        potassium = get_level_and_percentage(potassium_match.group(1) if potassium_match else None, "potassium")
        ph = get_level_and_percentage(ph_match.group(1) if ph_match else None, "ph")
        
        return {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "ph": ph
        }
        
    except Exception as e:
        print(f"Error in regex extraction: {e}")
        # Return default values if extraction fails
        return {
            "nitrogen": {"value": "Not detected", "level": "Unknown", "percentage": 50},
            "phosphorus": {"value": "Not detected", "level": "Unknown", "percentage": 50},
            "potassium": {"value": "Not detected", "level": "Unknown", "percentage": 50},
            "ph": {"value": "Not detected", "level": "Unknown", "percentage": 50}
        }

def generate_fertilizer_plan(soil_data):
    """Generate fertilizer plan based on soil data using Gemini"""
    try:
        prompt = f"""
        Based on this soil health data:
        Nitrogen: {soil_data['nitrogen']['value']} ({soil_data['nitrogen']['level']})
        Phosphorus: {soil_data['phosphorus']['value']} ({soil_data['phosphorus']['level']})
        Potassium: {soil_data['potassium']['value']} ({soil_data['potassium']['level']})
        pH: {soil_data['ph']['value']} ({soil_data['ph']['level']})

        Generate a detailed fertilizer plan in this exact JSON format:
        {{
            "crop_data": {{
                "name": "Wheat",
                "stage": "Flowering Stage",
                "progress": 65,
                "nextFertilizer": "In 15 days"
            }},
            "current_plan": [
                {{
                    "fertilizer": "Urea",
                    "amount": "50 kg/acre",
                    "timing": "Now",
                    "method": "Broadcasting",
                    "status": "pending",
                    "priority": "high"
                }},
                {{
                    "fertilizer": "DAP",
                    "amount": "25 kg/acre", 
                    "timing": "In 7 days",
                    "method": "Mix in soil",
                    "status": "upcoming",
                    "priority": "medium"
                }},
                {{
                    "fertilizer": "Potash",
                    "amount": "20 kg/acre",
                    "timing": "In 20 days", 
                    "method": "Broadcasting",
                    "status": "future",
                    "priority": "low"
                }}
            ],
            "recommendations": {{
                "english": "Detailed recommendation based on soil analysis"
            }}
        }}

        Only return the JSON object, no additional text. Adjust fertilizer types, amounts, and timing based on the soil deficiencies.
        """
        
        response = model.generate_content(prompt)
        
        try:
            result = json.loads(response.text)
            return result
        except json.JSONDecodeError:
            # Return default plan if JSON parsing fails
            return get_default_fertilizer_plan(soil_data)
            
    except Exception as e:
        print(f"Error generating fertilizer plan: {e}")
        return get_default_fertilizer_plan(soil_data)

def get_default_fertilizer_plan(soil_data):
    """Default fertilizer plan based on soil deficiencies"""
    recommendations = []
    
    if soil_data['nitrogen']['level'] == 'Low':
        recommendations.append("Apply urea immediately to address nitrogen deficiency")
    if soil_data['phosphorus']['level'] == 'Low':
        recommendations.append("Apply DAP or SSP for phosphorus deficiency")
    if soil_data['potassium']['level'] == 'Low':
        recommendations.append("Apply potash for potassium deficiency")
    
    if not recommendations:
        recommendations.append("Soil nutrients are balanced. Apply maintenance doses.")
    
    recommendation_text = ". ".join(recommendations) + ". Apply fertilizer after irrigation for better absorption."
    
    return {
        "crop_data": {
            "name": "Wheat",
            "stage": "Flowering Stage", 
            "progress": 65,
            "nextFertilizer": "In 15 days"
        },
        "current_plan": [
            {
                "fertilizer": "Urea" if soil_data['nitrogen']['level'] == 'Low' else "NPK Mix",
                "amount": "50 kg/acre",
                "timing": "Now",
                "method": "Broadcasting",
                "status": "pending",
                "priority": "high"
            },
            {
                "fertilizer": "DAP" if soil_data['phosphorus']['level'] == 'Low' else "SSP",
                "amount": "25 kg/acre",
                "timing": "In 7 days", 
                "method": "Mix in soil",
                "status": "upcoming",
                "priority": "medium"
            },
            {
                "fertilizer": "Potash" if soil_data['potassium']['level'] == 'Low' else "MOP",
                "amount": "20 kg/acre",
                "timing": "In 20 days",
                "method": "Broadcasting", 
                "status": "future",
                "priority": "low"
            }
        ],
        "recommendations": {
            "english": recommendation_text
        }
    }

@app.post("/analyze-soil")
async def analyze_soil(file: UploadFile = File(...)):
    try:
        # Read uploaded file
        file_bytes = await file.read()
        
        # Extract soil data from image
        soil_data = extract_npk_values_from_image(file_bytes)
        
        # Generate fertilizer plan
        fertilizer_plan = generate_fertilizer_plan(soil_data)
        
        # Combine all data
        result = {
            "status": "success",
            "soil_health": soil_data,
            "fertilizer_plan": fertilizer_plan
        }
        
        return result
        
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e),
            "soil_health": {
                "nitrogen": {"value": "Error", "level": "Unknown", "percentage": 50},
                "phosphorus": {"value": "Error", "level": "Unknown", "percentage": 50},
                "potassium": {"value": "Error", "level": "Unknown", "percentage": 50},
                "ph": {"value": "Error", "level": "Unknown", "percentage": 50}
            },
            "fertilizer_plan": get_default_fertilizer_plan({
                "nitrogen": {"value": "Error", "level": "Unknown", "percentage": 50},
                "phosphorus": {"value": "Error", "level": "Unknown", "percentage": 50},
                "potassium": {"value": "Error", "level": "Unknown", "percentage": 50},
                "ph": {"value": "Error", "level": "Unknown", "percentage": 50}
            })
        }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "OCR Soil Analysis"}
