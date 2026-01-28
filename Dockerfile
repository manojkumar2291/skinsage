FROM python:3.11-slim

WORKDIR /app

# 1. Install system dependencies (essential for cv2 and healthchecks)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. Install CPU-Only PyTorch & Transformers
# We install these FIRST to ensure they are the correct CPU versions
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir transformers

# 3. Clean Requirements & Install Rest
COPY requirements.txt .
# Filter out 'torch' and 'transformers' from requirements.txt so they don't overwrite our CPU versions
RUN grep -vE "torch|transformers" requirements.txt > requirements_cleaned.txt
RUN pip install --no-cache-dir -r requirements_cleaned.txt

# 4. Copy Application Code
COPY . .

# 5. Security & Permissions (Required for HuggingFace downloads)
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/data/.cache/huggingface && \
    chown -R appuser:appuser /app

# Set Cache Directory
ENV HF_HOME=/app/data/.cache/huggingface

# Switch to non-root user
USER appuser

# 6. Expose Port
EXPOSE 8000

# 7. THE FIX: Run uvicorn via python module (-m)
# This bypasses the PATH error by asking Python to locate the uvicorn module
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]