FROM nvidia/cuda:12.1.1-cudnn8-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/models

ARG HF_TOKEN
ENV HF_TOKEN=${HF_TOKEN}

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bake model weights into the image so cold starts only load VRAM, not Hugging Face.
RUN python3 -c "\
import os; \
from huggingface_hub import snapshot_download; \
snapshot_download( \
    repo_id='black-forest-labs/FLUX.1-dev', \
    token=os.environ.get('HF_TOKEN'), \
    cache_dir='/models', \
)"

COPY handler.py .

CMD ["python3", "-u", "handler.py"]
