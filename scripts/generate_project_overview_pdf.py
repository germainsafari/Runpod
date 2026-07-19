#!/usr/bin/env python3
"""Generate docs/PROJECT_OVERVIEW.pdf with embedded screenshots."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = DOCS / "PROJECT_OVERVIEW.pdf"
REPO_URL = "https://github.com/germainsafari/Runpod"
ENDPOINT_ID = "7n4p3czd3nphae"


def ascii_safe(text: str) -> str:
    replacements = {
        "\u2014": "-",
        "\u2013": "-",
        "\u2022": "-",
        "\u2192": "->",
        "\u00d7": "x",
        "\u00b7": "-",
        "\u201c": '"',
        "\u201d": '"',
        "\u2018": "'",
        "\u2019": "'",
        "\u2502": "|",
        "\u2514": "L",
        "\u251c": "|",
        "\u2500": "-",
        "\u25bc": "v",
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    return text.encode("ascii", "replace").decode("ascii")


IMAGES = [
    ("dockerhub.png", "Docker Hub - sfrgermain/runpod-flux-studio (tags: latest, v3, ~15.4 GB)"),
    ("image (5).png", "RunPod endpoint overview - flux-studio-v2, ID 7n4p3czd3nphae, Running"),
    ("image (2).png", "Endpoint configuration - 141 GB GPU, max/active workers = 1, idle timeout 3600s"),
    ("image.png", "Workers tab - H200 SXM worker running (Version 4)"),
    ("image (1).png", "Worker telemetry - GPU, disk (80 GB), RAM, CUDA status"),
    ("image (3).png", "Logs - model load + 512x512 cyberpunk generation (v3-sequential-offload)"),
    ("image (4).png", "Metrics - 5 completed requests, execution time, cold starts"),
    ("image (6).png", "Release history - GPU filter updates, CUDA 12.1, worker scaling"),
    ("image (7).png", "Flux Studio chat UI - successful image generation (319.5s render)"),
]


class OverviewPDF(FPDF):
    def _txt(self, text: str) -> str:
        return ascii_safe(text)

    def header(self):
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(110, 110, 110)
        self.cell(
            0,
            7,
            self._txt("Flux Studio - RunPod Serverless Case Study"),
            align="R",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        self.ln(1)

    def footer(self):
        self.set_y(-14)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section(self, title: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 8, self._txt(title))
        self.ln(2)

    def subsection(self, title: str) -> None:
        self.ln(2)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 7, self._txt(title))
        self.ln(1)

    def body(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(35, 35, 35)
        self.multi_cell(0, 5.5, self._txt(text))
        self.ln(1.5)

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", 10)
        self.set_text_color(35, 35, 35)
        self.multi_cell(0, 5.5, self._txt(f"  -  {text}"))
        self.ln(0.5)

    def code_block(self, text: str) -> None:
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(245, 245, 245)
        self.set_text_color(25, 25, 25)
        for line in text.strip().splitlines():
            self.cell(0, 4.8, self._txt(f"  {line}"), new_x="LMARGIN", new_y="NEXT", fill=True)
        self.ln(2)

    def table_row(self, cols: list[str], bold: bool = False) -> None:
        style = "B" if bold else ""
        widths = [55, 45, 70]
        self.set_font("Helvetica", style, 9)
        self.set_text_color(35, 35, 35)
        for width, col in zip(widths, cols):
            self.cell(width, 6, self._txt(col[:42]), border=1)
        self.ln()

    def caption(self, text: str) -> None:
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(90, 90, 90)
        self.multi_cell(0, 5, self._txt(text))
        self.ln(2)

    def embed_image(self, filename: str, caption: str, max_width: float | None = None) -> None:
        path = DOCS / filename
        if not path.exists():
            self.body(f"[Image not found: {filename}]")
            return

        width = max_width or self.epw
        if self.get_y() > 240:
            self.add_page()

        try:
            self.image(str(path), w=width)
        except Exception as exc:
            self.body(f"[Could not embed {filename}: {exc}]")
            return

        self.ln(2)
        self.caption(f"Figure: {self._txt(caption)}")


def build_pdf() -> None:
    pdf = OverviewPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(18, 18, 18)
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()

    # Title page
    pdf.set_font("Helvetica", "B", 24)
    pdf.set_text_color(15, 15, 15)
    pdf.multi_cell(0, 12, "Flux Studio")
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(70, 70, 70)
    pdf.multi_cell(0, 8, "Complete Project Overview")
    pdf.ln(2)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, "RunPod Serverless Case Study - FLUX.1-dev Image Generation")
    pdf.ln(4)
    pdf.body(f"Author: Germain Safari")
    pdf.body(f"Repository: {REPO_URL}")
    pdf.body(f"Model: FLUX.1-dev (Black Forest Labs)")
    pdf.body(f"Platform: RunPod Serverless")
    pdf.body(f"Live endpoint: flux-studio-v2 - ID {ENDPOINT_ID}")

    # 1. Executive summary
    pdf.add_page()
    pdf.section("1. Executive Summary")
    pdf.body(
        "Flux Studio is an end-to-end AI image generation platform. A user types a text prompt "
        "in a ChatGPT-style browser interface. The React frontend calls a FastAPI backend, which "
        "submits an async job to RunPod Serverless. A GPU worker loads FLUX.1-dev, generates a PNG, "
        "and returns base64 image data. The UI displays the result in a chat thread with history, "
        "library, projects, and pinning."
    )
    pdf.subsection("Three-tier architecture")
    pdf.table_row(["Layer", "Technology", "Role"], bold=True)
    pdf.table_row(["GPU worker", "Python + Diffusers + Docker", "Runs FLUX.1-dev on RunPod GPUs"])
    pdf.table_row(["API proxy", "FastAPI (Render)", "Secrets, job submit, status polling"])
    pdf.table_row(["Chat UI", "React + Vite (Vercel)", "ChatGPT-style prompt to image"])
    pdf.ln(2)

    # 2. Deliverables
    pdf.section("2. What We Built")
    pdf.table_row(["Deliverable", "Status", "Location"], bold=True)
    rows = [
        ("Serverless handler", "Done", "serverless/handler.py"),
        ("Dockerfile", "Done", "serverless/Dockerfile"),
        ("RunPod endpoint", "Done", "flux-studio-v2"),
        ("Working inference", "Done", "Logs + UI screenshot"),
        ("ChatGPT-style UI", "Done", "app/frontend/"),
        ("API proxy", "Done", "app/backend/main.py"),
        ("CLI test script", "Done", "scripts/test_endpoint.py"),
        ("GitHub repository", "Done", "Public repo"),
        ("Documentation", "Done", "docs/"),
    ]
    for row in rows:
        pdf.table_row(list(row))
    pdf.ln(2)

    # 3. Architecture
    pdf.section("3. System Architecture")
    pdf.body("Flow: Browser -> FastAPI (Render) -> RunPod Serverless -> GPU Worker -> base64 PNG -> Chat UI")
    pdf.code_block(
        """
React Chat UI (Vercel)
    │  POST /api/chat/submit
    ▼
FastAPI Proxy (Render)
    │  POST /v2/{endpoint_id}/run
    ▼
RunPod Serverless (flux-studio-v2)
    │  handler(job)
    ▼
GPU Worker (Docker + FLUX.1-dev)
    │  { image_base64, prompt, width, height }
    ▼
Chat UI displays generated image
        """
    )
    pdf.body(
        "Why three tiers: (1) RunPod API keys stay server-side on Render. (2) Long GPU jobs use "
        "async submit + polling instead of blocking HTTP. (3) CORS is controlled via FRONTEND_URL."
    )

    # 4. Repository structure
    pdf.section("4. Repository Structure")
    pdf.code_block(
        """
Runpod/
├── serverless/          handler.py, Dockerfile (GPU worker)
├── app/backend/         FastAPI → RunPod proxy
├── app/frontend/        React chat UI
├── scripts/             test_endpoint.py, PDF generators
├── docs/                Documentation + screenshots
├── render.yaml          Render blueprint
└── start.ps1            Local startup script
        """
    )

    # 5. Phase 1 — Worker
    pdf.add_page()
    pdf.section("5. Phase 1 - Serverless GPU Worker")
    pdf.body(
        "The RunPod worker is a Python script invoked per job. It loads FLUX.1-dev once (cached), "
        "generates an image, and returns base64 PNG data."
    )
    pdf.subsection("Key handler design (serverless/handler.py)")
    pdf.bullet("Sequential CPU offload - keeps GPU VRAM low on 24 GB cards")
    pdf.bullet("VAE slicing/tiling - reduces peak memory during decode")
    pdf.bullet("Version marker v3-sequential-offload - visible in RunPod logs")
    pdf.code_block(
        """
HANDLER_VERSION = "v3-sequential-offload"

pipeline = FluxPipeline.from_pretrained("black-forest-labs/FLUX.1-dev", ...)
pipeline.enable_sequential_cpu_offload()
pipeline.vae.enable_slicing()
pipeline.vae.enable_tiling()

return {"image_base64": "...", "prompt": "...", "width": 512, "height": 512}
        """
    )
    pdf.subsection("Docker image (serverless/Dockerfile)")
    pdf.bullet("Base: nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04")
    pdf.bullet("Pinned: torch 2.5.1 (cu124), diffusers 0.32.2, transformers 4.47.1")
    pdf.bullet("Image: docker.io/sfrgermain/runpod-flux-studio:latest or :v3")

    # 6. Docker Hub
    pdf.add_page()
    pdf.section("6. Phase 2 - Docker Image on Docker Hub")
    pdf.body(
        "After building locally, the worker image was pushed to Docker Hub. RunPod pulls this "
        "image when starting workers."
    )
    pdf.embed_image("dockerhub.png", IMAGES[0][1])

    # 7. RunPod endpoint
    pdf.add_page()
    pdf.section("7. Phase 3 - RunPod Serverless Endpoint")
    pdf.subsection("7.1 Endpoint overview")
    pdf.body(f"Endpoint name: flux-studio-v2 - ID: {ENDPOINT_ID}")
    pdf.body("API URL: https://api.runpod.ai/v2/7n4p3czd3nphae/run")
    pdf.embed_image("image (5).png", IMAGES[1][1])

    pdf.subsection("7.2 GPU and scaling configuration")
    pdf.bullet("GPU: 141 GB VRAM tier (H200/H100 class)")
    pdf.bullet("Max workers: 1 - Active workers: 1 (warm worker for demos)")
    pdf.bullet("Idle timeout: 3600 s - Execution timeout: enabled")
    pdf.embed_image("image (2).png", IMAGES[2][1])

    pdf.add_page()
    pdf.subsection("7.3 Workers tab")
    pdf.embed_image("image.png", IMAGES[3][1])

    pdf.subsection("7.4 Worker telemetry")
    pdf.embed_image("image (1).png", IMAGES[4][1])

    pdf.add_page()
    pdf.subsection("7.5 Logs - successful generation")
    pdf.body(
        "Logs confirm fitness checks, model loading, and inference. Example prompt: "
        "'A futuristic city with flying cars at night, neon reflections, cyberpunk' at 512x512."
    )
    pdf.embed_image("image (3).png", IMAGES[5][1])

    pdf.add_page()
    pdf.subsection("7.6 Metrics")
    pdf.bullet("5 completed requests, 0 failed")
    pdf.bullet("~8 min total execution time (includes cold model loads)")
    pdf.bullet("6 cold starts, ~56 s total cold-start time")
    pdf.embed_image("image (4).png", IMAGES[6][1])

    pdf.subsection("7.7 Release history")
    pdf.embed_image("image (6).png", IMAGES[7][1])

    # 8. Chat app
    pdf.add_page()
    pdf.section("8. Phase 4 - Chat Application")
    pdf.subsection("Backend (app/backend/main.py)")
    pdf.bullet("GET /api/health - verify RunPod configuration")
    pdf.bullet("POST /api/chat/submit - submit async job, return job_id")
    pdf.bullet("GET /api/chat/status/{job_id} - poll until COMPLETED")
    pdf.subsection("Frontend features")
    pdf.bullet("New chat, recent history, pin chats, projects/folders")
    pdf.bullet("Library of all generated images")
    pdf.bullet("Search chats (Ctrl+K)")
    pdf.bullet("Settings: steps, guidance, resolution, seed")
    pdf.bullet("Download PNG and copy prompt per image")
    pdf.subsection("8.1 Working UI")
    pdf.embed_image("image (7).png", IMAGES[8][1])

    # 9. Web deployment
    pdf.add_page()
    pdf.section("9. Phase 5 - Web Deployment (Render + Vercel)")
    pdf.body("Production: Vercel (frontend) -> Render (backend) -> RunPod (GPU)")
    pdf.subsection("Render backend")
    pdf.bullet("Root Directory: app/backend")
    pdf.bullet("Language: Python 3 (not Docker)")
    pdf.bullet("Build: pip install -r requirements.txt")
    pdf.bullet("Start: uvicorn main:app --host 0.0.0.0 --port $PORT")
    pdf.bullet("Env: RUNPOD_API_KEY, RUNPOD_ENDPOINT_ID, FRONTEND_URL")
    pdf.subsection("Vercel frontend")
    pdf.bullet("Root Directory: app/frontend")
    pdf.bullet("Build: npm run build - Output: dist")
    pdf.bullet("Env: VITE_API_BASE_URL=https://your-api.onrender.com")
    pdf.body(
        "Important: Do not use 'cd app/frontend && npm run build' when Root Directory is "
        "already app/frontend - that causes a Vercel build failure."
    )

    # 10. API contract
    pdf.section("10. API Contract")
    pdf.subsection("RunPod input")
    pdf.code_block(
        """
{
  "input": {
    "prompt": "A futuristic city with flying cars at night",
    "width": 512,
    "height": 512,
    "num_inference_steps": 20,
    "guidance_scale": 3.5
  }
}
        """
    )
    pdf.subsection("Handler output")
    pdf.code_block(
        """
{
  "image_base64": "<base64 PNG>",
  "prompt": "...",
  "width": 512,
  "height": 512,
  "handler_version": "v3-sequential-offload"
}
        """
    )

    # 11. Challenges
    pdf.add_page()
    pdf.section("11. Challenges and Solutions")
    challenges = [
        ("HF gated model (403)", "Accept FLUX license; set HF_TOKEN"),
        ("transformers 5.x breaks FluxPipeline", "Pin diffusers 0.32.2, transformers 4.47.1"),
        ("CUDA driver mismatch", "Pin torch cu124; minCudaVersion 12.1 on endpoint"),
        ("CUDA OOM on 24 GB GPUs", "Sequential CPU offload, 512 cap, VAE tiling"),
        ("Workers stuck initializing", "80 GB container disk; correct Docker image tag"),
        ("Vercel build failure", "Root Directory = app/frontend; build = npm run build only"),
        ("Cold start latency", "Set workersMin=1 on RunPod endpoint"),
    ]
    pdf.table_row(["Problem", "Fix", ""], bold=True)
    for problem, fix in challenges:
        pdf.table_row([problem, fix, ""])
    pdf.ln(2)

    # 12. Performance
    pdf.section("12. Performance Snapshot")
    pdf.bullet("Cold start: ~56 s total (6 events observed)")
    pdf.bullet("Full generation (cold, 512x512): ~319 s (UI screenshot)")
    pdf.bullet("Warm worker (512x512): ~30-60 s")
    pdf.bullet("Queue delay: ~100 ms")
    pdf.bullet("Cost (141 GB tier): ~$0.00329/s while worker runs")

    # 13. Checklist
    pdf.section("13. Submission Checklist")
    checklist = [
        "handler.py implements prompt to base64 PNG",
        "Dockerfile builds and pushes to Docker Hub",
        "RunPod endpoint flux-studio-v2 running",
        "Logs show successful 512x512 generation",
        "Chat UI generates and displays images",
        "GitHub repo public",
        "Render backend deployed",
        "Vercel frontend deployed",
    ]
    for item in checklist:
        pdf.bullet(item)

    pdf.ln(4)
    pdf.set_font("Helvetica", "B", 11)
    pdf.body(f"GitHub: {REPO_URL}")
    pdf.body("Author: Germain Safari - RunPod Serverless Case Study")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    build_pdf()
