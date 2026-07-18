#!/usr/bin/env python3
"""Send a test prompt to a deployed RunPod endpoint and save the image."""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def main() -> None:
    parser = argparse.ArgumentParser(description="Test a RunPod FLUX endpoint")
    parser.add_argument("--endpoint-id", default=os.getenv("RUNPOD_ENDPOINT_ID"))
    parser.add_argument("--api-key", default=os.getenv("RUNPOD_API_KEY"))
    parser.add_argument("--prompt", default="A photo of a cat astronaut floating in space")
    parser.add_argument("--output", default="output.png")
    parser.add_argument("--width", type=int, default=1024)
    parser.add_argument("--height", type=int, default=1024)
    parser.add_argument("--steps", type=int, default=28)
    args = parser.parse_args()

    if not args.endpoint_id or not args.api_key:
        print("Provide --endpoint-id and --api-key or set RUNPOD_ENDPOINT_ID and RUNPOD_API_KEY.", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {args.api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "input": {
            "prompt": args.prompt,
            "width": args.width,
            "height": args.height,
            "num_inference_steps": args.steps,
        }
    }

    base_url = f"https://api.runpod.ai/v2/{args.endpoint_id}"
    print("Submitting async job...")
    submit = requests.post(f"{base_url}/run", headers=headers, json=payload, timeout=60)
    submit.raise_for_status()
    job = submit.json()
    job_id = job["id"]
    print(f"Job id: {job_id}")

    while True:
        status = requests.get(f"{base_url}/status/{job_id}", headers=headers, timeout=60)
        status.raise_for_status()
        body = status.json()
        current = body.get("status")
        print(f"Status: {current}")

        if current == "COMPLETED":
            output = body.get("output", {})
            if "error" in output:
                print(output["error"], file=sys.stderr)
                sys.exit(1)

            image_base64 = output["image_base64"]
            with open(args.output, "wb") as handle:
                handle.write(base64.b64decode(image_base64))
            print(f"Saved image to {args.output}")
            print(json.dumps({k: v for k, v in body.items() if k != "output"}, indent=2))
            return

        if current in {"FAILED", "CANCELLED", "TIMED_OUT"}:
            print(json.dumps(body, indent=2), file=sys.stderr)
            sys.exit(1)

        time.sleep(3)


if __name__ == "__main__":
    main()
