from dotenv import load_dotenv
from google import genai
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

print("Checking available Gemini models...\n")

for model in client.models.list():
    supported_actions = model.supported_actions or []

    if "generateContent" in supported_actions:
        print(model.name)