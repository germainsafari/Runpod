# RunPod Deployment Guide

This guide walks through deploying the FLUX.1-dev worker and connecting the chat application.

## Prerequisites

- RunPod account with credits
- Docker Desktop
- Docker Hub account
- Hugging Face account with FLUX.1-dev access
- Python 3.10+ and Node.js 18+

## 1. Create tokens

### RunPod
1. Open [RunPod Settings → API Keys](https://www.runpod.io/console/user/settings)
2. Create and copy an API key

### Hugging Face
1. Accept the license at [FLUX.1-dev](https://huggingface.co/black-forest-labs/FLUX.1-dev)
2. Create a read token at [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens)

## 2. Configure environment

```powershell
copy .env.example .env
```

Fill in:

```env
RUNPOD_API_KEY=...
RUNPOD_ENDPOINT_ID=...   # added after deployment
HF_TOKEN=...
DOCKER_USERNAME=...
```

## 3. Build the worker image

The build downloads ~30 GB of model weights.

```powershell
cd serverless

$env:HF_TOKEN = "hf_xxx"
$env:DOCKER_USERNAME = "your_dockerhub_username"

docker build --platform linux/amd64 `
  --build-arg HF_TOKEN=$env:HF_TOKEN `
  -t $env:DOCKER_USERNAME/runpod-flux-studio:latest .

docker login
docker push $env:DOCKER_USERNAME/runpod-flux-studio:latest
```

Expected build time: 30–90 minutes depending on network speed.

## 4. Deploy on RunPod Console

1. Go to [Serverless Console](https://www.runpod.io/console/serverless)
2. Click **+ New Endpoint**
3. Choose **Import from Docker Registry**
4. Image: `docker.io/YOUR_USER/runpod-flux-studio:latest`
5. Recommended settings:

| Setting | Value |
|---------|-------|
| Endpoint type | Queue |
| GPU | 24 GB+ (RTX 4090, A5000, A6000, A100) |
| Active workers (min) | 0 |
| Max workers | 1–3 |
| Container disk | 50 GB |
| Execution timeout | 600 s |

6. Environment variables:

| Key | Value |
|-----|-------|
| `HF_TOKEN` | Your Hugging Face token |
| `HF_HOME` | `/models` |

7. Deploy and copy the **Endpoint ID**

## 5. Verify inference

```powershell
$env:RUNPOD_API_KEY = "..."
$env:RUNPOD_ENDPOINT_ID = "..."

pip install requests
python scripts/test_endpoint.py --prompt "A serene mountain landscape at sunset"
```

Expected result: `output.png` saved in the project root.

First request after idle may take 2–5 minutes (cold start).

## 6. Launch the chat app

```powershell
.\start.ps1 -BuildFrontend
```

Open http://localhost:8000 and generate images from the chat UI.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Docker build fails on model download | Missing HF license/token | Accept FLUX license, verify `HF_TOKEN` |
| CUDA OOM | GPU too small or resolution too high | Use 24 GB GPU, test at 512x512 |
| 401 from RunPod | Invalid API key | Regenerate key in RunPod console |
| Job timeout | Cold start + inference > timeout | Increase execution timeout to 600s+ |
| UI shows "Configure API keys" | Missing env vars in backend | Set `RUNPOD_API_KEY` and `RUNPOD_ENDPOINT_ID` |

## Optional: deploy script

```powershell
python scripts/deploy.py create --image docker.io/YOUR_USER/runpod-flux-studio:latest
```

Note: Console deployment is recommended for first-time setup because GPU and timeout settings are easier to validate visually.
