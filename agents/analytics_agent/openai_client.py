import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_openai_client() -> OpenAI:
    """Create and return an OpenAI client."""
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing from .env")

    return OpenAI(api_key=api_key)


def get_model_name() -> str:
    """Return the OpenAI model name from environment."""
    return os.getenv("OPENAI_MODEL", "gpt-4.1")