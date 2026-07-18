#!/usr/bin/env python3
"""Create, list, and delete RunPod serverless endpoints."""

from __future__ import annotations

import argparse
import json
import os
import sys

import requests

RUNPOD_API_URL = "https://rest.runpod.io/v1"


def headers() -> dict[str, str]:
    api_key = os.environ.get("RUNPOD_API_KEY")
    if not api_key:
        print("Error: set RUNPOD_API_KEY in your environment.", file=sys.stderr)
        sys.exit(1)
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }


def create_endpoint(image: str, name: str) -> None:
    payload = {
        "name": name,
        "templateId": None,
        "gpuIds": "AMPERE_24",
        "workersMin": 0,
        "workersMax": 1,
        "idleTimeout": 5,
        "scalerType": "QUEUE_DELAY",
        "scalerValue": 4,
        "dockerArgs": "",
        "containerDiskInGb": 50,
        "env": {
            "HF_HOME": "/models",
            "HF_TOKEN": os.environ.get("HF_TOKEN", ""),
        },
        "imageName": image,
        "isServerless": True,
    }

    response = requests.post(f"{RUNPOD_API_URL}/endpoints", headers=headers(), json=payload, timeout=60)
    response.raise_for_status()
    data = response.json()
    print(json.dumps(data, indent=2))
    print(f"\nEndpoint created. Set RUNPOD_ENDPOINT_ID={data.get('id')}")


def list_endpoints() -> None:
    response = requests.get(f"{RUNPOD_API_URL}/endpoints", headers=headers(), timeout=60)
    response.raise_for_status()
    print(json.dumps(response.json(), indent=2))


def delete_endpoint(endpoint_id: str) -> None:
    response = requests.delete(f"{RUNPOD_API_URL}/endpoints/{endpoint_id}", headers=headers(), timeout=60)
    response.raise_for_status()
    print(f"Deleted endpoint {endpoint_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Manage RunPod serverless endpoints")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create", help="Create a new endpoint")
    create_parser.add_argument("--image", required=True, help="Docker image, e.g. docker.io/user/runpod-flux:latest")
    create_parser.add_argument("--name", default="flux-chat-endpoint", help="Endpoint name")

    subparsers.add_parser("list", help="List endpoints")
    delete_parser = subparsers.add_parser("delete", help="Delete an endpoint")
    delete_parser.add_argument("endpoint_id")

    args = parser.parse_args()

    if args.command == "create":
        create_endpoint(args.image, args.name)
    elif args.command == "list":
        list_endpoints()
    elif args.command == "delete":
        delete_endpoint(args.endpoint_id)


if __name__ == "__main__":
    main()
