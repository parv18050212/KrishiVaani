# from dotenv import load_dotenv
# from openai import OpenAI
# import os




from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

# Initialize Nominatim geocoder
geolocator = Nominatim(user_agent="my-geocoder-app") # Replace with a unique user_agent

    # Create a rate limiter to avoid hitting API limits if making multiple requests
reverse = RateLimiter(geolocator.reverse, min_delay_seconds=1)

    # Define your coordinates
latitude = 26.7674446
longitude = 81.109758

    # Perform reverse geocoding
location = reverse(f"{latitude}, {longitude}")

    # Extract state and district information
if location and location.raw and 'address' in location.raw:
        address_components = location.raw['address']
        state = address_components.get('state')
        district = address_components.get('county') # 'county' often represents district in Nominatim data

        print(f"State: {state}")
        print(f"District: {district}")
else:
        print("Could not retrieve location details.")






# client = OpenAI(
#     api_key=os.getenv("perplexity_api"),
#     base_url="https://api.perplexity.ai"
# )

# dist = "nainital"
# state = "uttarakhand"

# resp = client.chat.completions.create(
#     model="sonar-pro",
#     messages=[
#         {"role": "user", "content": f"Tell me about the mandi prices of crops in {dist},{state} compare them and tell which mandi have the lowest price and also give me the links from where you get this data."}
#     ]
# )
# print(resp.choices[0].message.content)