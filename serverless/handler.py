import base64
import gc
import io
import os
import sys
import time
import traceback

import runpod

pipe = None

# Safe defaults for 24GB GPUs (RTX 3090, A5000, A40, etc.)
DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
MAX_SIDE_24GB = 768


def load_model():
    """Load FLUX with CPU offload so 24GB GPUs can run inference."""
    global pipe
    if pipe is not None:
        return pipe

    import torch
    from diffusers import FluxPipeline

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available on this worker")

    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"VRAM: {vram_gb:.1f} GB | torch={torch.__version__}")

    print("Loading FLUX.1-dev...")
    start = time.time()

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    pipeline = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=dtype,
        token=os.environ.get("HF_TOKEN"),
    )

    # Keep weights mostly on CPU; move layers to GPU only during forward pass.
    # Required on 24GB cards — full .to("cuda") uses ~23GB leaving no room to generate.
    pipeline.enable_model_cpu_offload()
    if hasattr(pipeline, "vae") and pipeline.vae is not None:
        pipeline.vae.enable_slicing()
        pipeline.vae.enable_tiling()

    pipe = pipeline
    print(f"Model ready in {time.time() - start:.1f}s (CPU offload enabled)")
    return pipe


def clamp_dimensions(width: int, height: int) -> tuple[int, int]:
    import torch

    width = max(256, min(MAX_SIDE_24GB, (width // 8) * 8))
    height = max(256, min(MAX_SIDE_24GB, (height // 8) * 8))

    if torch.cuda.is_available():
        vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
        if vram_gb < 40:
            # Extra safety on 24GB class GPUs
            width = min(width, MAX_SIDE_24GB)
            height = min(height, MAX_SIDE_24GB)

    return width, height


def handler(job):
    try:
        import torch

        job_input = job.get("input") or {}
        prompt = str(job_input.get("prompt", "")).strip()
        if not prompt:
            return {"error": "Missing required field: prompt"}

        num_inference_steps = int(job_input.get("num_inference_steps", 20))
        guidance_scale = float(job_input.get("guidance_scale", 3.5))
        width = int(job_input.get("width", DEFAULT_WIDTH))
        height = int(job_input.get("height", DEFAULT_HEIGHT))
        seed = job_input.get("seed")

        width, height = clamp_dimensions(width, height)
        print(f"Generating {width}x{height}: {prompt[:100]}")

        model = load_model()

        generator = None
        if seed is not None:
            generator = torch.Generator(device="cpu").manual_seed(int(seed))

        torch.cuda.empty_cache()
        gc.collect()

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

        torch.cuda.empty_cache()
        gc.collect()

        return {
            "image_base64": image_base64,
            "prompt": prompt,
            "seed": seed,
            "width": width,
            "height": height,
        }
    except Exception as exc:
        import torch

        torch.cuda.empty_cache()
        gc.collect()
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        return {"error": str(exc), "traceback": tb}


if __name__ == "__main__":
    print("Starting Flux Studio RunPod worker...")
    runpod.serverless.start({"handler": handler})
