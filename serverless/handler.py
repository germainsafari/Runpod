import base64
import io
import os
import time

import runpod
import torch
from diffusers import FluxPipeline
from PIL import Image

MODEL_ID = "black-forest-labs/FLUX.1-dev"
pipe = None


def load_model() -> FluxPipeline:
    global pipe
    if pipe is not None:
        return pipe

    print(f"Loading {MODEL_ID} into GPU memory...")
    start = time.time()

    pipeline = FluxPipeline.from_pretrained(
        MODEL_ID,
        torch_dtype=torch.bfloat16,
        token=os.environ.get("HF_TOKEN"),
    )
    pipeline.to("cuda")
    pipe = pipeline

    print(f"Model loaded in {time.time() - start:.1f}s")
    return pipe


def handler(job):
    job_input = job["input"]

    prompt = job_input.get("prompt")
    if not prompt or not prompt.strip():
        return {"error": "Missing required field: prompt"}

    num_inference_steps = int(job_input.get("num_inference_steps", 28))
    guidance_scale = float(job_input.get("guidance_scale", 3.5))
    width = int(job_input.get("width", 1024))
    height = int(job_input.get("height", 1024))
    seed = job_input.get("seed")

    print(f"Generating image for prompt: {prompt[:120]}...")

    model = load_model()

    generator = None
    if seed is not None:
        generator = torch.Generator(device="cuda").manual_seed(int(seed))

    image: Image.Image = model(
        prompt=prompt.strip(),
        num_inference_steps=num_inference_steps,
        guidance_scale=guidance_scale,
        width=width,
        height=height,
        generator=generator,
    ).images[0]

    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "image_base64": image_base64,
        "prompt": prompt.strip(),
        "seed": seed,
        "width": width,
        "height": height,
    }


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
