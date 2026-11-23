import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("BASE_URL", "https://api.cheaperinference.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-v4.1-flash-1017")
API_KEY = os.getenv("API_KEY") or os.getenv("OPENAI_API_KEY")

def validate_config():
    if not API_KEY:
        raise RuntimeError(
            "API key not found. Add API_KEY=... to your .env file. "
            "Never commit .env to GitHub."
        )
