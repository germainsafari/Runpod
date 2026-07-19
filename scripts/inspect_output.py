import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

headers = {
    "Authorization": f"Bearer {os.getenv('RUNPOD_API_KEY')}",
    "Content-Type": "application/json",
}
endpoint = os.getenv("RUNPOD_ENDPOINT_ID")
payload = {
    "input": {
        "prompt": "A red apple on a wooden table",
        "width": 512,
        "height": 512,
        "num_inference_steps": 15,
    }
}

submit = requests.post(f"https://api.runpod.ai/v2/{endpoint}/runsync?wait=300000", headers=headers, json=payload, timeout=320)
print("status code", submit.status_code)
body = submit.json()
print(json.dumps(body, indent=2)[:4000])
