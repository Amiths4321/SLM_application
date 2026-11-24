
import os
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL")


def generate_response(prompt):

    if not OLLAMA_URL or not OLLAMA_MODEL:
        raise ValueError("Ollama configuration missing from .env")

    response = requests.post(
        f"{OLLAMA_URL.rstrip('/')}/api/generate",
        json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        },
        timeout=180
    )

    response.raise_for_status()

    return response.json()["response"]


if __name__ == "__main__":
    result = generate_response(
        "Return JSON with a message field containing "
        "the text: Remote warehouse AI is connected."
    )

    print(result)
