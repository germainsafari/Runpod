# Flux Studio — RunPod Serverless Case Study

Deploy **FLUX.1-dev** on RunPod Serverless and interact with it through a **ChatGPT/Claude-style** web app.

![Architecture](docs/architecture.svg)

## What this project delivers

| Deliverable | Location |
|-------------|----------|
| Serverless handler | `serverless/handler.py` |
| Docker worker image | `serverless/Dockerfile` |
| RunPod deployment guide | This README + `docs/DEPLOYMENT.md` |
| Chat UI | `app/frontend/` |
| API proxy | `app/backend/main.py` |
| CLI test tool | `scripts/test_endpoint.py` |
| Submission PDF | `docs/CASE_STUDY.pdf` |

## Quick start (local app)

```powershell
copy .env.example .env
# Fill in RUNPOD_API_KEY and RUNPOD_ENDPOINT_ID

cd app\frontend
npm install
npm run build

cd ..\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open **http://localhost:8000**

Or from project root:

```powershell
.\start.ps1 -BuildFrontend
```

## Deploy to the web

Host the **backend on Render** and the **frontend on Vercel** (recommended):

**[docs/DEPLOY_WEB.md](docs/DEPLOY_WEB.md)** — step-by-step guide with env vars and troubleshooting.

## RunPod deployment (summary)

1. Accept the [FLUX.1-dev license](https://huggingface.co/black-forest-labs/FLUX.1-dev)
2. Create Hugging Face + RunPod API tokens
3. Build and push the Docker image from `serverless/`
4. Create a Serverless endpoint (24 GB+ GPU, 50 GB disk)
5. Test with `python scripts/test_endpoint.py`

Full step-by-step instructions: **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**

## API contract

**Request**

```json
{
  "input": {
    "prompt": "A photo of a cat astronaut floating in space",
    "num_inference_steps": 28,
    "guidance_scale": 3.5,
    "width": 1024,
    "height": 1024,
    "seed": 42
  }
}
```

**Response**

```json
{
  "output": {
    "image_base64": "<base64 PNG>",
    "prompt": "...",
    "width": 1024,
    "height": 1024
  }
}
```

## Project structure

```
Runpod/
├── serverless/              # RunPod GPU worker
├── app/
│   ├── backend/             # FastAPI -> RunPod proxy
│   └── frontend/            # React chat UI
├── scripts/
│   ├── test_endpoint.py
│   ├── deploy.py
│   └── generate_case_study_pdf.py
├── docs/
│   ├── DEPLOYMENT.md
│   └── CASE_STUDY.pdf
└── README.md
```

## Submission

- **GitHub:** https://github.com/germainsafari/runpod-flux-studio
- **PDF case study:** `docs/CASE_STUDY.pdf`

## Author
Germain Safari
