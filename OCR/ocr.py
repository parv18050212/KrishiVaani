import os
import re
import boto3
from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from google.generativeai import configure, GenerativeModel
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# AWS Credentials
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
configure(api_key=GEMINI_API_KEY)

# Initialize Textract client
textract = boto3.client(
    'textract',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

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

@app.post("/analyze-soil")
async def analyze_soil(file: UploadFile = File(...)):
    try:
        # Read uploaded file
        file_bytes = await file.read()

        # Call AWS Textract to extract text
        response = textract.analyze_document(
            Document={'Bytes': file_bytes},
            FeatureTypes=['FORMS']
        )

        # Combine detected text
        extracted_text = ""
        for block in response["Blocks"]:
            if block["BlockType"] == "LINE":
                extracted_text += block["Text"] + "\n"

        # Debug print
        print("\nDEBUG: Extracted text:\n", extracted_text)

        # Extract NPK with unit (kg/ha)
        nitrogen_match = re.search(r"Available\s*Nitrogen.*?(\d+\.?\d*)", extracted_text, re.IGNORECASE | re.DOTALL)
        phosphorus_match = re.search(r"Available\s*Phosphorus.*?(\d+\.?\d*)", extracted_text, re.IGNORECASE | re.DOTALL)
        potassium_match = re.search(r"Available\s*Potassium.*?(\d+\.?\d*)", extracted_text, re.IGNORECASE | re.DOTALL)

        nitrogen = f"{nitrogen_match.group(1)} kg/ha" if nitrogen_match else None
        phosphorus = f"{phosphorus_match.group(1)} kg/ha" if phosphorus_match else None
        potassium = f"{potassium_match.group(1)} kg/ha" if potassium_match else None

        # Prepare soil data
        soil_data = {
            "Nitrogen (N)": nitrogen,
            "Phosphorus (P)": phosphorus,
            "Potassium (K)": potassium
        }

        # Prepare prompt for Gemini
        prompt = f"""
        The soil health card shows these nutrient levels:
        Nitrogen: {nitrogen}
        Phosphorus: {phosphorus}
        Potassium: {potassium}

        Based on this, provide actionable recommendations for a farmer to improve soil health and fertility.
        """

        # Get recommendation from Gemini
        gemini_response = model.generate_content(prompt)

        return {
            "status": "success",
            "soil_data": soil_data,
            "recommendation": gemini_response.text
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
