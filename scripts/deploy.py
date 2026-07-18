#!/usr/bin/env python3
"""Create RunPod serverless template + endpoint for Flux Studio."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

RUNPOD_API_URL = "https://rest.runpod.io/v1"


def headers() -> dict[str, str]:
    api_key = os.environ.get("RUNPOD_API_KEY")
    if not api_key:
        print("Error: RUNPOD_API_KEY missing in .env", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def create_template(image: str, hf_token: str) -> str:
    payload = {
        "name": "flux-studio-serverless",
        "imageName": image,
        "isServerless": True,
        "containerDiskInGb": 50,
        "env": {
            "HF_TOKEN": hf_token,
            "HF_HOME": "/models",
        },
    }
    response = requests.post(f"{RUNPOD_API_URL}/templates", headers=headers(), json=payload, timeout=60)
    if response.status_code >= 400:
        raise RuntimeError(f"Template creation failed: {response.status_code} {response.text}")
    template_id = response.json()["id"]
    print(f"Created template: {template_id}")
    return template_id


def create_endpoint(template_id: str, name: str) -> dict:
    payload = {
        "name": name,
        "templateId": template_id,
        "gpuTypeIds": [
            "NVIDIA GeForce RTX 4090",
            "NVIDIA RTX A6000",
            "NVIDIA RTX A5000",
            "NVIDIA A40",
        ],
        "workersMin": 0,
        "workersMax": 1,
        "idleTimeout": 5,
        "scalerType": "QUEUE_DELAY",
        "scalerValue": 4,
        "executionTimeoutMs": 600000,
    }
    response = requests.post(f"{RUNPOD_API_URL}/endpoints", headers=headers(), json=payload, timeout=60)
    if response.status_code >= 400:
        raise RuntimeError(f"Endpoint creation failed: {response.status_code} {response.text}")
    data = response.json()
    print(json.dumps(data, indent=2))
    return data


def list_endpoints() -> None:
    response = requests.get(f"{RUNPOD_API_URL}/endpoints", headers=headers(), timeout=60)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


def delete_endpoint(endpoint_id: str) -> None:
    response = requests.delete(f"{RUNPOD_API_URL}/endpoints/{endpoint_id}", headers=headers(), timeout=60)
    response.raise_for_status()
    print(f"Deleted endpoint {endpoint_id}")


def update_env_endpoint_id(endpoint_id: str) -> None:
    env_path = ROOT / ".env"
    lines = env_path.read_text(encoding="utf-8").splitlines()
    updated = False
    new_lines = []
    for line in lines:
        if line.startswith("RUNPOD_ENDPOINT_ID="):
            new_lines.append(f"RUNPOD_ENDPOINT_ID={endpoint_id}")
            updated = True
        else:
            new_lines.append(line)
    if not updated:
        new_lines.append(f"RUNPOD_ENDPOINT_ID={endpoint_id}")
    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    print(f"Updated {env_path} with RUNPOD_ENDPOINT_ID")


def main() -> None:
    parser = argparse.ArgumentParser(description="Deploy Flux Studio to RunPod")
    subparsers = parser.add_subparsers(dest="command", required=True)

    deploy_parser = subparsers.add_parser("deploy", help="Create template and endpoint")
    deploy_parser.add_argument(
        "--image",
        default=f"{os.getenv('DOCKER_USERNAME', 'sfrgermain')}/runpod-flux-studio:latest",
    )
    deploy_parser.add_argument("--name", default="flux-studio-endpoint")

    subparsers.add_parser("list", help="List endpoints")
    delete_parser = subparsers.add_parser("delete", help="Delete endpoint")
    delete_parser.add_argument("endpoint_id")

    args = parser.parse_args()

    if args.command == "deploy":
        hf_token = os.environ.get("HF_TOKEN")
        if not hf_token:
            print("Error: HF_TOKEN missing in .env", file=sys.stderr)
            sys.exit(1)
        image = args.image if "/" in args.image else f"{os.getenv('DOCKER_USERNAME', 'sfrgermain')}/{args.image}"
        template_id = create_template(image, hf_token)
        endpoint = create_endpoint(template_id, args.name)
        endpoint_id = endpoint.get("id")
        if endpoint_id:
            update_env_endpoint_id(endpoint_id)
            print(f"\nEndpoint ready: {endpoint_id}")
            print(f"API URL: https://api.runpod.ai/v2/{endpoint_id}/run")
    elif args.command == "list":
        list_endpoints()
    elif args.command == "delete":
        delete_endpoint(args.endpoint_id)


if __name__ == "__main__":
    main()
