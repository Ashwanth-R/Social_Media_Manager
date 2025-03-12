from openai import OpenAI
import os
from dotenv import load_dotenv


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

response = client.images.generate(
    model="dall-e-3",
    prompt=" **Understanding Trump's Legal Battles** ⚖️ Did you know that Trump's administration is facing over 41 lawsuits challenging various executive actions? From halting funding for refugee resettlement to contentious immigration policies, these legal challenges could have significant implications for millions. 🌍 Stay informed and understand how these battles may shape our future. 👉 Swipe up to learn more!",
    size="1024x1024",
    quality="standard",
    n=1,
)

print(response.data[0].url)