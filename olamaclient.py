"""
Simple Python client for a remote Ollama instance on your LAN.

Usage:
    1. Edit OLLAMA_HOST below to your Windows PC's LAN IP.
    2. pip install requests
    3. python ollama_client.py
"""

import requests

# --- Configuration ---
OLLAMA_HOST = "http://192.168.1.25:11434"  # <-- change to your PC's LAN IP
MODEL = "llama3"  # <-- change to a model you have pulled


def list_models():
    """Show which models are available on the remote Ollama server."""
    resp = requests.get(f"{OLLAMA_HOST}/api/tags")
    resp.raise_for_status()
    models = resp.json().get("models", [])
    print("Available models:")
    for m in models:
        print(" -", m["name"])
    return models


def generate(prompt, model=MODEL, stream=False):
    """Send a prompt and get a full (non-streaming) response."""
    resp = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={"model": model, "prompt": prompt, "stream": stream},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"]


def chat(messages, model=MODEL):
    """Use the chat endpoint with a list of {'role': ..., 'content': ...} messages."""
    resp = requests.post(
        f"{OLLAMA_HOST}/api/chat",
        json={"model": model, "messages": messages, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["message"]["content"]


if __name__ == "__main__":
    list_models()

    print("\n--- generate() example ---")
    answer = generate("Give me one fun fact about the ocean.")
    print(answer)

    print("\n--- chat() example ---")
    reply = chat([{"role": "user", "content": "Hello! What model are you?"}])
    print(reply)
