import requests
import json
from config import OLLAMA_URL,MODEL_NAME
def warmup_model():

    print("Warming up model...")

    data = {
        "model": MODEL_NAME,
        "prompt": "hello",
        "stream": False,
        "keep_alive": -1
    }
    requests.post(OLLAMA_URL, json=data)
    print("Model ready.")

    
def call_llama(prompt):
    """
    非流式调用（用于判断 / 决策）
    """

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "keep_alive": -1
    }

    try:
        response = requests.post(OLLAMA_URL, json=data, timeout=10)

        if response.status_code != 200:
            return ""

        result = response.json()
        return result.get("response", "").strip()

    except Exception as e:
        print("LLM error:", e)
        return ""

def call_llama_stream(prompt):

    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "keep_alive": -1
    }

    response = requests.post(OLLAMA_URL, json=data, stream=True)

    print("\nAI: ", end="", flush=True)

    sentence_end = {".", "?", "!"}

    for line in response.iter_lines():

        if line:

            chunk = json.loads(line)
            text = chunk.get("response", "")

            for char in text:
                print(char, end="", flush=True)

                if char in sentence_end:
                    print("\n", end="", flush=True)

    print()