import asyncio
import os
import time
from pathlib import Path

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

load_dotenv(Path(__file__).resolve().parents[2] / ".env")
load_dotenv()

RUNPOD_API_KEY = os.getenv("RUNPOD_API_KEY", "")
RUNPOD_ENDPOINT_ID = os.getenv("RUNPOD_ENDPOINT_ID", "")
RUNPOD_BASE_URL = "https://api.runpod.ai/v2"

app = FastAPI(title="Flux Studio API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    num_inference_steps: int = Field(default=28, ge=1, le=50)
    guidance_scale: float = Field(default=3.5, ge=1.0, le=20.0)
    width: int = Field(default=1024, ge=256, le=1536)
    height: int = Field(default=1024, ge=256, le=1536)
    seed: int | None = None


class SubmitResponse(BaseModel):
    job_id: str


class StatusResponse(BaseModel):
    status: str
    image_base64: str | None = None
    execution_time_ms: int | None = None
    error: str | None = None


def runpod_headers() -> dict[str, str]:
    if not RUNPOD_API_KEY:
        raise HTTPException(status_code=500, detail="RUNPOD_API_KEY is not configured")
    return {
        "Authorization": f"Bearer {RUNPOD_API_KEY}",
        "Content-Type": "application/json",
    }


def ensure_endpoint_configured() -> None:
    if not RUNPOD_ENDPOINT_ID:
        raise HTTPException(status_code=500, detail="RUNPOD_ENDPOINT_ID is not configured")


def build_payload(request: ChatRequest) -> dict:
    payload = {
        "input": {
            "prompt": request.prompt,
            "num_inference_steps": request.num_inference_steps,
            "guidance_scale": request.guidance_scale,
            "width": request.width,
            "height": request.height,
        }
    }
    if request.seed is not None:
        payload["input"]["seed"] = request.seed
    return payload


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "endpoint_configured": bool(RUNPOD_ENDPOINT_ID),
        "api_key_configured": bool(RUNPOD_API_KEY),
        "endpoint_id": RUNPOD_ENDPOINT_ID or None,
    }


@app.post("/api/chat/submit", response_model=SubmitResponse)
async def submit_chat(request: ChatRequest):
    ensure_endpoint_configured()

    async with httpx.AsyncClient(timeout=60.0) as client:
        submit = await client.post(
            f"{RUNPOD_BASE_URL}/{RUNPOD_ENDPOINT_ID}/run",
            headers=runpod_headers(),
            json=build_payload(request),
        )
        if submit.status_code >= 400:
            raise HTTPException(status_code=submit.status_code, detail=submit.text)

        job = submit.json()
        job_id = job.get("id")
        if not job_id:
            raise HTTPException(status_code=502, detail="RunPod did not return a job id")

        return SubmitResponse(job_id=job_id)


@app.get("/api/chat/status/{job_id}", response_model=StatusResponse)
async def chat_status(job_id: str):
    ensure_endpoint_configured()

    async with httpx.AsyncClient(timeout=60.0) as client:
        status_response = await client.get(
            f"{RUNPOD_BASE_URL}/{RUNPOD_ENDPOINT_ID}/status/{job_id}",
            headers=runpod_headers(),
        )
        if status_response.status_code >= 400:
            raise HTTPException(status_code=status_response.status_code, detail=status_response.text)

        status_payload = status_response.json()
        status = status_payload.get("status", "UNKNOWN")
        output = status_payload.get("output") or {}

        if status == "COMPLETED":
            if output.get("error"):
                return StatusResponse(status=status, error=output["error"])
            return StatusResponse(
                status=status,
                image_base64=output.get("image_base64"),
                execution_time_ms=status_payload.get("executionTime"),
            )

        if status in {"FAILED", "CANCELLED", "TIMED_OUT"}:
            return StatusResponse(
                status=status,
                error=status_payload.get("error", f"Job {status.lower()}"),
            )

        return StatusResponse(status=status)


@app.post("/api/chat")
async def chat(request: ChatRequest):
    """Backward-compatible single-shot endpoint."""
    ensure_endpoint_configured()

    submit = await submit_chat(request)
    deadline = time.time() + 540

    while time.time() < deadline:
        status = await chat_status(submit.job_id)
        if status.status == "COMPLETED":
            if status.error:
                raise HTTPException(status_code=400, detail=status.error)
            if not status.image_base64:
                raise HTTPException(status_code=502, detail="RunPod completed without an image")
            return {
                "image_base64": status.image_base64,
                "prompt": request.prompt,
                "job_id": submit.job_id,
                "execution_time_ms": status.execution_time_ms,
            }
        if status.status in {"FAILED", "CANCELLED", "TIMED_OUT"}:
            raise HTTPException(status_code=502, detail=status.error or status.status.lower())
        await asyncio.sleep(2)

    raise HTTPException(status_code=504, detail="Image generation timed out")


frontend_dir = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
