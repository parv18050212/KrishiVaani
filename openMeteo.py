import openmeteo_requests
import geocoder
import pandas as pd
import requests_cache
from retry_requests import retry
from openai import OpenAI
from dotenv import load_dotenv
from os import getenv

load_dotenv()
# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)
g = geocoder.ip('me')
lat, lon = g.latlng
# Make sure all required weather variables are listed here
# The order of variables in hourly or daily is important to assign them correctly below
url = "https://api.open-meteo.com/v1/forecast"
params = {
	"latitude": 30.7351,
	"longitude": 79.0669,
	"daily": ["weather_code", "temperature_2m_max", "temperature_2m_min", "rain_sum", "showers_sum", "snowfall_sum"],
	"hourly": ["temperature_2m", "rain", "snowfall", "cloud_cover", "wind_speed_10m", "soil_temperature_0cm", "soil_temperature_6cm", "soil_moisture_0_to_1cm", "soil_moisture_1_to_3cm", "weather_code", "surface_pressure"],
	"current": ["temperature_2m", "is_day", "rain", "showers", "snowfall", "precipitation", "relative_humidity_2m", "apparent_temperature", "weather_code", "cloud_cover", "pressure_msl", "surface_pressure", "wind_gusts_10m", "wind_direction_10m", "wind_speed_10m"],
	"timezone": "auto",
	"precipitation_unit": "inch",
}
responses = openmeteo.weather_api(url, params=params)

# Process first location. Add a for-loop for multiple locations or weather models
response = responses[0]
print(f"Coordinates: {response.Latitude()}°N {response.Longitude()}°E")
print(f"Elevation: {response.Elevation()} m asl")
print(f"Timezone: {response.Timezone()}{response.TimezoneAbbreviation()}")
print(f"Timezone difference to GMT+0: {response.UtcOffsetSeconds()}s")

# Process current data. The order of variables needs to be the same as requested.
current = response.Current()
current_temperature_2m = current.Variables(0).Value()
current_is_day = current.Variables(1).Value()
current_rain = current.Variables(2).Value()
current_showers = current.Variables(3).Value()
current_snowfall = current.Variables(4).Value()
current_precipitation = current.Variables(5).Value()
current_relative_humidity_2m = current.Variables(6).Value()
current_apparent_temperature = current.Variables(7).Value()
current_weather_code = current.Variables(8).Value()
current_cloud_cover = current.Variables(9).Value()
current_pressure_msl = current.Variables(10).Value()
current_surface_pressure = current.Variables(11).Value()
current_wind_gusts_10m = current.Variables(12).Value()
current_wind_direction_10m = current.Variables(13).Value()
current_wind_speed_10m = current.Variables(14).Value()

print(f"\nCurrent time: {current.Time()}")
print(f"Current temperature_2m: {current_temperature_2m}")
print(f"Current is_day: {current_is_day}")
print(f"Current rain: {current_rain}")
print(f"Current showers: {current_showers}")
print(f"Current snowfall: {current_snowfall}")
print(f"Current precipitation: {current_precipitation}")
print(f"Current relative_humidity_2m: {current_relative_humidity_2m}")
print(f"Current apparent_temperature: {current_apparent_temperature}")
print(f"Current weather_code: {current_weather_code}")
print(f"Current cloud_cover: {current_cloud_cover}")
print(f"Current pressure_msl: {current_pressure_msl}")
print(f"Current surface_pressure: {current_surface_pressure}")
print(f"Current wind_gusts_10m: {current_wind_gusts_10m}")
print(f"Current wind_direction_10m: {current_wind_direction_10m}")
print(f"Current wind_speed_10m: {current_wind_speed_10m}")

# Process hourly data. The order of variables needs to be the same as requested.
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

hourly_data = {"date": pd.date_range(
	start = pd.to_datetime(hourly.Time(), unit = "s", utc = True),
	end = pd.to_datetime(hourly.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = hourly.Interval()),
	inclusive = "left"
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

hourly_dataframe = pd.DataFrame(data = hourly_data)
print("\nHourly data\n", hourly_dataframe)

# Process daily data. The order of variables needs to be the same as requested.
daily = response.Daily()
daily_weather_code = daily.Variables(0).ValuesAsNumpy()
daily_temperature_2m_max = daily.Variables(1).ValuesAsNumpy()
daily_temperature_2m_min = daily.Variables(2).ValuesAsNumpy()
daily_rain_sum = daily.Variables(3).ValuesAsNumpy()
daily_showers_sum = daily.Variables(4).ValuesAsNumpy()
daily_snowfall_sum = daily.Variables(5).ValuesAsNumpy()

daily_data = {"date": pd.date_range(
	start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
	end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
	freq = pd.Timedelta(seconds = daily.Interval()),
	inclusive = "left"
)}

daily_data["weather_code"] = daily_weather_code
daily_data["temperature_2m_max"] = daily_temperature_2m_max
daily_data["temperature_2m_min"] = daily_temperature_2m_min
daily_data["rain_sum"] = daily_rain_sum
daily_data["showers_sum"] = daily_showers_sum
daily_data["snowfall_sum"] = daily_snowfall_sum

daily_dataframe = pd.DataFrame(data = daily_data)
print("\nDaily data\n", daily_dataframe)

crop = "okra"

client = OpenAI(
    api_key= "AIzaSyBcp40oWkENzGIzTI9VigKPQ5ewQU5p4rw",
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
# hourly_dataframe daily_dataframe
resp = client.chat.completions.create(
    model="gemini-2.5-pro",
    messages=[
        {"role": "user", "content":"""
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
             "content":f"Hourly dataframe - {hourly_dataframe}\nDaily dataframe - {daily_dataframe}\ncrop - {crop}"
         }
    ]
)
print("\n\n\n\n\n\n\n\n")
print(resp.choices[0].message.content)