import base64
import io
import os
import sys
import time
import traceback

import runpod

pipe = None


def load_model():
    """Load FLUX once per worker lifetime. Lazy so fitness checks can pass first."""
    global pipe
    if pipe is not None:
        return pipe

    import torch
    from diffusers import FluxPipeline

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available on this worker")

    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    print(f"torch={torch.__version__} cuda={torch.version.cuda}")

    print("Loading FLUX.1-dev into GPU memory...")
    start = time.time()

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    pipeline = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=dtype,
        token=os.environ.get("HF_TOKEN"),
    )
    pipeline.to("cuda")
    pipe = pipeline
    print(f"Model loaded in {time.time() - start:.1f}s")
    return pipe


def handler(job):
    try:
        import torch

        job_input = job.get("input") or {}
        prompt = str(job_input.get("prompt", "")).strip()
        if not prompt:
            return {"error": "Missing required field: prompt"}

        num_inference_steps = int(job_input.get("num_inference_steps", 28))
        guidance_scale = float(job_input.get("guidance_scale", 3.5))
        width = int(job_input.get("width", 1024))
        height = int(job_input.get("height", 1024))
        seed = job_input.get("seed")

        # Keep dimensions divisible by 8 (FLUX requirement)
        width = max(256, (width // 8) * 8)
        height = max(256, (height // 8) * 8)

        print(f"Generating: {prompt[:100]}")
        model = load_model()

        generator = None
        if seed is not None:
            generator = torch.Generator(device="cuda").manual_seed(int(seed))

        image = model(
            prompt=prompt,
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
            "prompt": prompt,
            "seed": seed,
            "width": width,
            "height": height,
        }
    except Exception as exc:
        # Return error instead of crashing the worker process
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        return {"error": str(exc), "traceback": tb}


if __name__ == "__main__":
    print("Starting Flux Studio RunPod worker...")
    runpod.serverless.start({"handler": handler})
