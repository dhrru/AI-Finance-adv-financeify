import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Initialize the new 2026 SDK Client
client = genai.Client(api_key=api_key)

print("--- 🔍 Finding Available Gemini Models ---")
try:
    # Query the models available to your specific API key
    for model in client.models.list():
        print(f"✅ Model: {model.name}")
except Exception as e:
    print(f"❌ Error: {e}")