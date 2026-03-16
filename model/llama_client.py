import requests
import json
from config import OLLAMA_URL,MODEL_NAME
import subprocess
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

    process = subprocess.Popen(
        ["ollama", "run", "llama3.1:8b"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    output, _ = process.communicate(prompt)

    return output  
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