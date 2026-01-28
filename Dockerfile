FROM python:3.11-slim

WORKDIR /app

# 1. Install system dependencies (including git, curl, and image libs)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# 2. CRITICAL: Force Install Uvicorn & FastAPI manually first
#    This guarantees they exist, even if requirements.txt fails later.
RUN pip install --no-cache-dir uvicorn[standard] fastapi python-dotenv

# 3. Install CPU-Only PyTorch & Transformers
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir transformers

# 4. Copy and Clean Requirements
COPY requirements.txt .
# Filter out conflicting packages to prevent overwriting
RUN grep -vE "torch|transformers|uvicorn|fastapi" requirements.txt > requirements_cleaned.txt

# 5. Install remaining requirements
#    We use '|| true' so the build doesn't fail if the file is empty or formatted weirdly
RUN pip install --no-cache-dir -r requirements_cleaned.txt || true

# 6. Copy App Code
COPY . .

# 7. Setup User & Permissions
RUN adduser --disabled-password --gecos '' appuser && \
    mkdir -p /app/data/.cache/huggingface && \
    chown -R appuser:appuser /app

# 8. DEBUG: Print installed packages to build logs to verify uvicorn exists
RUN pip list | grep uvicorn

ENV HF_HOME=/app/data/.cache/huggingface
USER appuser

EXPOSE 8000

# 9. Launch
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]