import base64
import gc
import io
import os
import sys
import traceback

import runpod

HANDLER_VERSION = "v3-sequential-offload"
pipe = None

DEFAULT_WIDTH = 512
DEFAULT_HEIGHT = 512
MAX_SIDE_24GB = 512  # strict cap for 24GB GPUs


def load_model():
    global pipe
    if pipe is not None:
        return pipe

    import torch
    from diffusers import FluxPipeline

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available on this worker")

    device_name = torch.cuda.get_device_name(0)
    vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
    print(f"[{HANDLER_VERSION}] GPU: {device_name} ({vram_gb:.1f} GB VRAM)")

    dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    pipeline = FluxPipeline.from_pretrained(
        "black-forest-labs/FLUX.1-dev",
        torch_dtype=dtype,
        token=os.environ.get("HF_TOKEN"),
        low_cpu_mem_usage=True,
    )

    # Sequential offload: lowest VRAM footprint (required on 24GB cards)
    pipeline.enable_sequential_cpu_offload()
    if hasattr(pipeline, "vae") and pipeline.vae is not None:
        pipeline.vae.enable_slicing()
        pipeline.vae.enable_tiling()

    pipe = pipeline
    allocated = torch.cuda.memory_allocated() / (1024**3)
    print(f"[{HANDLER_VERSION}] Model ready. GPU allocated: {allocated:.2f} GB (should be <2 GB)")
    return pipe


def clamp_dimensions(width: int, height: int) -> tuple[int, int]:
    width = max(256, min(MAX_SIDE_24GB, (int(width) // 8) * 8))
    height = max(256, min(MAX_SIDE_24GB, (int(height) // 8) * 8))
    return width, height


def handler(job):
    try:
        import torch

        job_input = job.get("input") or {}
        prompt = str(job_input.get("prompt", "")).strip()
        if not prompt:
            return {"error": "Missing required field: prompt"}

        width, height = clamp_dimensions(
            job_input.get("width", DEFAULT_WIDTH),
            job_input.get("height", DEFAULT_HEIGHT),
        )
        num_inference_steps = min(int(job_input.get("num_inference_steps", 20)), 28)
        guidance_scale = float(job_input.get("guidance_scale", 3.5))
        seed = job_input.get("seed")

        print(f"[{HANDLER_VERSION}] Generating {width}x{height}: {prompt[:80]}")
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

        torch.cuda.empty_cache()
        gc.collect()

        return {
            "image_base64": base64.b64encode(buffer.getvalue()).decode("utf-8"),
            "prompt": prompt,
            "width": width,
            "height": height,
            "handler_version": HANDLER_VERSION,
        }
    except Exception as exc:
        import torch

        torch.cuda.empty_cache()
        gc.collect()
        tb = traceback.format_exc()
        print(tb, file=sys.stderr)
        return {"error": str(exc), "handler_version": HANDLER_VERSION}


if __name__ == "__main__":
    print(f"Starting Flux Studio worker [{HANDLER_VERSION}]...")
    runpod.serverless.start({"handler": handler})
