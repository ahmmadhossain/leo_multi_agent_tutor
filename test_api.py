import os
import sys
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from openai import (
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    NotFoundError,
    RateLimitError,
)

load_dotenv()

API_KEY = os.getenv("API_KEY", "").strip()
BASE_URL = os.getenv("BASE_URL", "https://api.cheaperinference.com/v1").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "deepseek-v4.1-flash-1017").strip()


def test_api_key():
    if not API_KEY:
        print("FAIL: API_KEY is empty or missing in your .env file.")
        sys.exit(1)

    masked_key = f"{API_KEY[:6]}...{API_KEY[-4:]}" if len(API_KEY) > 10 else "***"
    print(f"Testing endpoint: {BASE_URL}")
    print(f"Testing model:    {MODEL_NAME}")
    print(f"Using API key:    {masked_key}\n")

    try:
        llm = ChatOpenAI(
            model=MODEL_NAME,
            api_key=API_KEY,
            base_url=BASE_URL,
            temperature=0.0,
            timeout=20,
        )
        print("Sending: Hi")
        response = llm.invoke("Hi")
        print("SUCCESS: API key is working!")
        print(f"Response: {response.content.strip()}")

    except AuthenticationError as e:
        print(f"FAIL (401 Authentication Error): Invalid or revoked API key.\nDetails: {e}")
        sys.exit(1)
    except NotFoundError as e:
        print(f"FAIL (404 Not Found): Check MODEL_NAME or BASE_URL.\nDetails: {e}")
        sys.exit(1)
    except RateLimitError as e:
        print(f"FAIL (429 Rate Limit / Quota): Key is valid, but rate-limited or out of credits.\nDetails: {e}")
        sys.exit(1)
    except BadRequestError as e:
        print(f"FAIL (400 Bad Request): Model name or request parameters were rejected.\nDetails: {e}")
        sys.exit(1)
    except APIConnectionError as e:
        print(f"FAIL (Connection Error): Could not reach {BASE_URL}.\nDetails: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"FAIL (Unexpected Error): {type(e).__name__}: {e}")
        sys.exit(1)


if __name__ == "__main__":
    test_api_key()