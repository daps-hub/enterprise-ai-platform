import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def get_openai_client():
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY not found.")

    return OpenAI(api_key=api_key)


def get_model_name():
    return os.getenv("OPENAI_MODEL", "gpt-4.1")