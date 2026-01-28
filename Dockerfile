FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install CPU-Only PyTorch & Transformers explicitly
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir transformers

COPY requirements.txt .

RUN grep -vE "torch|transformers" requirements.txt > requirements_cleaned.txt

RUN pip install --no-cache-dir -r requirements_cleaned.txt

COPY . .

RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/data/.cache/huggingface && \
    chown -R appuser:appuser /app

ENV HF_HOME=/app/data/.cache/huggingface

USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]