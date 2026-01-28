FROM python:3.11-slim

WORKDIR /app

# 1. Install system dependencies
# 'libgl1' and 'libglib2.0-0' are REQUIRED for image processing (cv2)
# 'curl' is for healthchecks
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install CPU-Only PyTorch & Transformers explicitly
# We do this BEFORE requirements.txt to prevent overwriting
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir transformers

# 3. Install remaining dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy app code
COPY . .

# 5. Fix Permissions (Crucial for Transformers cache)
# Create a user, set up cache dir, and assign permissions
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/data/.cache/huggingface && \
    chown -R appuser:appuser /app

# Set the cache directory environment variable
ENV HF_HOME=/app/data/.cache/huggingface

USER appuser

# 6. Sanity Check (Build will fail here if torch is broken)
# This prevents deploying a broken container
RUN python -c "import torch; print(f'Torch successful: {torch.__version__}'); from transformers import pipeline; print('Pipeline successful')"

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]