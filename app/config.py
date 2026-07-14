import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))

if not GROQ_API_KEY:
    print(
        "[WARNING] GROQ_API_KEY not set. Add it to a .env file "
        "(copy .env.example -> .env and fill it in)."
    )

# AutoGen-style LLM config pointing at Groq's OpenAI-compatible endpoint.
# Groq offers a free tier: https://console.groq.com/keys
LLM_CONFIG = {
    "config_list": [
        {
            "model": GROQ_MODEL,
            "api_key": GROQ_API_KEY,
            "base_url": "https://api.groq.com/openai/v1",
        }
    ],
    "temperature": 0.4,
    "timeout": 120,
}
