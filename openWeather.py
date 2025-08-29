import requests
import geocoder
from dotenv import load_dotenv
from os import getenv
from openai import OpenAI
load_dotenv()
# g = geocoder.ip('me')
# lat, lon = g.latlng
lat = 30.7351
lon = 79.0669
key = getenv("weather_api")
crop = "okra"


url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={key}&units=metric"
r = requests.get(url)

client = OpenAI(
    api_key=r"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",
    base_url="https://api.perplexity.ai"
)
c0op = ""
client1 = OpenAI(
    api_key="xyz",
    base_url="hgvro"
)

# hourly_dataframe daily_dataframe
resp = client.chat.completions.create(
    model="sonar-pro",
    messages=[
        {
            "role": "user",
            "content":"""
You are an expert agricultural data analyst with strong skills in weather forecasting and crop advisory.

Task:
I will provide you with hourly and daily weather data in dataframe format, along with the type of crop I am growing.

Instructions:

Analyze the weather data to interpret future weather conditions and trends.

Identify key factors such as rainfall, temperature, humidity, and extreme events that may affect crop growth.

Based on the predicted weather, provide actionable recommendations for managing the crop.

Advise on steps to protect, irrigate, fertilize, or harvest the crop depending on the forecast.

Output Format:

Start with a summary of the future weather conditions.

Explain how these conditions could impact the given crop.

Provide clear, practical recommendations in bullet points for the farmer to follow.
         """},
         {
             "role" : "assistant",
             "content":"Please upload or provide the hourly and daily weather data in dataframe format to proceed with a detailed analysis. Once the data is available, a thorough examination will be performed to identify patterns, trends, anomalies, and key insights as requested."
         },
         {
             "role" : "user",
             "content":f"I don't have data frames at the moment but i have the weather data - {r.content}\ncrop - {crop}"
         }
    ]
)
print("\n\n\n\n\n\n\n\n")
print(resp.choices[0].message.content)