import requests
import pandas as pd

url = "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
api_key = "579b464db66ec23bdd00000129bb1eb3e823497b5836d0d562d9081d"

state = input("Enter your state: ")
district = input("Enter your district: ")
crop = input("Enter crop name: ")

params = {
    "api-key": api_key,
    "format": "json",
    "limit": 50,
    "filters[state]": state,
    "filters[district]": district,
    "filters[commodity]": crop
}

response = requests.get(url, params=params)

if response.status_code == 200:
    data = response.json()["records"]
    if data:
        df = pd.DataFrame(data, columns=["market","district","state","commodity","modal_price"])
        df["modal_price"] = pd.to_numeric(df["modal_price"])
        
        print(f"\nMandi Prices for {crop} in {district}, {state}:")
        print(df[["market","modal_price"]])
        
        best = df.loc[df["modal_price"].idxmax()]
        print(f"\n✅ Best mandi nearby: {best['market']} at ₹{best['modal_price']}")
    else:
        print("No data found for your region/crop.")
else:
    print("Error:", response.status_code)
