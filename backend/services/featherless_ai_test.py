from openai import OpenAI
from dotenv import load_dotenv
import os
load_dotenv()
client = OpenAI(
    api_key=os.getenv("AIMLAPI_KEY"),
    base_url="https://api.aimlapi.com/v1",
    
  )

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "user",
            "content": "Who is Virat Kohli"
        }
    ],
    temperature=0.2
)

print(response.choices[0].message.content)