#!/usr/bin/env python3
"""Generate the submission PDF case study."""

from __future__ import annotations

from pathlib import Path

from fpdf import FPDF

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "CASE_STUDY.pdf"
REPO_URL = "https://github.com/germainsafari/runpod-flux-studio"


class CaseStudyPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(90, 90, 90)
        self.cell(0, 8, "RunPod Serverless Case Study", align="R", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(130, 130, 130)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

    def section_title(self, title: str) -> None:
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 20, 20)
        self.multi_cell(0, 8, title)
        self.ln(2)

    def body_text(self, text: str) -> None:
        self.set_font("Helvetica", "", 11)
        self.set_text_color(35, 35, 35)
        self.multi_cell(self.epw, 6, text)
        self.ln(2)

    def bullet(self, text: str) -> None:
        self.set_font("Helvetica", "", 11)
        self.set_text_color(35, 35, 35)
        self.multi_cell(self.epw, 6, f"- {text}")
        self.ln(1)


def build_pdf() -> None:
    pdf = CaseStudyPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(15, 15, 15)
    pdf.multi_cell(0, 10, "RunPod Serverless Case Study")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 7, "FLUX.1-dev Image Generation with a ChatGPT-Style Web Interface")
    pdf.ln(4)

    pdf.body_text(
        "This project deploys the FLUX.1-dev text-to-image model on RunPod Serverless and exposes "
        "it through a polished chat-style web application. Users enter natural-language prompts and "
        "receive generated images as model responses, similar to conversational AI products such "
        "as ChatGPT or Claude."
    )

    pdf.section_title("Objective")
    pdf.body_text(
        "Build a production-ready RunPod serverless endpoint capable of receiving prompt requests "
        "and returning generated images, then demonstrate the endpoint through a clean, responsive "
        "chat UI suitable for senior-level evaluation."
    )

    pdf.section_title("Architecture")
    pdf.bullet("RunPod Serverless worker (handler.py) loads FLUX.1-dev on GPU and serves inference requests.")
    pdf.bullet("Docker image packages CUDA runtime, Python dependencies, and pre-cached model weights.")
    pdf.bullet("FastAPI backend proxies requests to RunPod and keeps API credentials server-side.")
    pdf.bullet("React frontend provides a ChatGPT/Claude-style experience with conversation history.")
    pdf.body_text("Flow: Browser -> FastAPI -> RunPod endpoint -> GPU worker -> base64 PNG -> chat UI.")

    pdf.section_title("RunPod Deployment")
    pdf.bullet("Built a CUDA 12.1 Docker image with FLUX.1-dev weights baked in for faster cold starts.")
    pdf.bullet("Deployed as a queue-based serverless endpoint on a 24 GB+ GPU.")
    pdf.bullet("Configured HF_TOKEN and HF_HOME environment variables for gated model access.")
    pdf.bullet("Validated inference using scripts/test_endpoint.py and the RunPod console.")

    pdf.section_title("Application Features")
    pdf.bullet("Chat-style prompt input with loading states and retry on failure.")
    pdf.bullet("Conversation sidebar with local persistence.")
    pdf.bullet("Generation settings: steps, guidance, resolution, seed.")
    pdf.bullet("Download generated images directly from the UI.")
    pdf.bullet("Mobile-responsive layout with sidebar navigation.")

    pdf.section_title("Technical Highlights")
    pdf.bullet("Async job submission with status polling for long-running GPU inference.")
    pdf.bullet("Model loaded once per worker instance to minimize per-request overhead.")
    pdf.bullet("Clear separation between serverless worker, API layer, and frontend.")
    pdf.bullet("Complete setup documentation for reproducible deployment.")

    pdf.section_title("Testing")
    pdf.body_text(
        "The endpoint accepts JSON input with a required prompt field and optional generation "
        "parameters. Successful responses return a base64-encoded PNG image. The included CLI "
        "test script saves output.png, and the web app demonstrates end-to-end prompt-to-image flow."
    )

    pdf.section_title("Deliverables")
    pdf.bullet("handler.py serverless worker")
    pdf.bullet("Dockerfile and requirements")
    pdf.bullet("RunPod deployment instructions")
    pdf.bullet("ChatGPT-style React UI")
    pdf.bullet("GitHub repository with setup guide")

    pdf.section_title("GitHub Repository")
    pdf.set_font("Helvetica", "U", 11)
    pdf.set_text_color(0, 102, 204)
    pdf.multi_cell(0, 7, REPO_URL)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(35, 35, 35)
    pdf.body_text(
        "Clone the repository, configure .env with RUNPOD_API_KEY, RUNPOD_ENDPOINT_ID, and HF_TOKEN, "
        "then follow README.md to build the worker image, deploy on RunPod, and launch the chat app."
    )

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(OUTPUT))
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
