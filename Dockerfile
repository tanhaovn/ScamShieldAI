# ==========================================
# Giai doan 1: Build React Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /build

COPY frontend-react/package*.json ./
RUN npm ci --silent || npm install

COPY frontend-react/ ./
RUN npm run build

# ==========================================
# Giai doan 2: Backend FastAPI + PyTorch CPU + OCR
# ==========================================
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    USE_SQLITE=true \
    TESSDATA_PREFIX=/app/tessdata \
    PORT=8000

# Install system dependencies (Tesseract OCR, OpenCV runtime dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-vie \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install lightweight PyTorch CPU first to avoid heavy CUDA packages
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cpu

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code, trained models, and tessdata
COPY backend/ /app/backend/
COPY models/ /app/models/
COPY tessdata/ /app/tessdata/
COPY --from=frontend-builder /build/dist /app/frontend-react/dist

# Expose server port
EXPOSE 8000

# Run uvicorn dynamically bound to $PORT (supporting Render, Koyeb, Hugging Face)
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
