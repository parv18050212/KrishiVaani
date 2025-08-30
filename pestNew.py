from openai import OpenAI 
from dotenv import load_dotenv
import os
import base64
import pandas as pd

df = pd.read_csv("Pesticides.csv")

load_dotenv()

client0 = OpenAI(
    api_key=os.getenv("perplexity_api"),
    base_url="https://api.perplexity.ai"
)

with open("67867.jpg", "rb") as f:
    a = base64.b64encode(f.read()).decode("utf-8")

response0 = client0.chat.completions.create(
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
                            {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{a}"}}
            ]
        }
    ],
    temperature=0.1
)
client1 = OpenAI(
    api_key=os.getenv("perplexity_api"),
    base_url="https://api.perplexity.ai"
)

response1 = client0.chat.completions.create(
    model="sonar-pro",
    messages=[
        {
            "role": "system",
            "content": f"You are an expert entomologist. I will send you name of an insect or a pest, you have to tell me if it is bad for my crop and how to get rid of it. If they are harmful to my crop then give a valid treatment guide, in one line like a summary only. You can use {df} data set to suggest the name of pesticide according to the pest."
        },
        {
            "role": "user",
            "content": f"{response0.choices[0].message.content}"
        }
    ]
)

print(response1.choices[0].message.content)
