import os

from dotenv import load_dotenv
from google.genai.errors import APIError
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv(override=True)

print("1. Program started", flush=True)

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found!")

print("2. API key loaded", flush=True)

model = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    timeout=20,
    max_retries=0
)

print("3. Model initialized", flush=True)

try:
    print("4. Sending request to Gemini...", flush=True)

    response = model.invoke("Say hello in one sentence.")

    print("5. Response received!", flush=True)
    print(response.content)

except (APIError, TimeoutError, ConnectionError) as e:
    print(f"API or connection error: {e}")