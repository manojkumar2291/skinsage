FROM python:3.11-slim

WORKDIR /app


RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Set ownership of the app directory
RUN chown -R appuser:appuser /app

# Switch to non-root user relative to the app directory
USER appuser

# command to run app (existing line)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]