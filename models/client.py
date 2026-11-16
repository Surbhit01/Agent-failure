"""One OpenAI-compatible client. Ollama and OpenRouter differ only in base URL and model name."""
from openai import OpenAI

OLLAMA_URL = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3.1:8b"


def make_client(base_url: str = OLLAMA_URL, api_key: str = "ollama") -> OpenAI:
    # Ollama ignores the key, but the client library requires a non-empty one.
    return OpenAI(base_url=base_url, api_key=api_key)
