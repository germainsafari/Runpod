FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/models

RUN apt-get update && \
    apt-get install -y --no-install-recommends python3 python3-pip git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir \
        torch==2.5.1 \
        torchvision==0.20.1 \
        --index-url https://download.pytorch.org/whl/cu124 && \
    pip install --no-cache-dir \
        "diffusers==0.32.2" \
        "transformers==4.47.1" \
        "accelerate==0.34.2" \
        "sentencepiece==0.2.0" \
        "protobuf==4.25.3" \
        "pillow>=10.0.0" \
        "huggingface-hub==0.26.5" \
        "safetensors==0.4.5" \
        "runpod>=1.7.0"

COPY handler.py .

CMD ["python3", "-u", "handler.py"]
