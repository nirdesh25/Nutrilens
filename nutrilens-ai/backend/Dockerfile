# ---- Build stage ----
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system dependencies required for tensorflow / OpenCV / pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# ---- Runtime stage ----
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copy system libs only (not build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy app source
COPY . .

# Create directories for ML models and data
RUN mkdir -p ml_models datasets

# Expose FastAPI port
EXPOSE 8000

# Run database initializer then start the server
CMD ["sh", "-c", "python init_db.py && uvicorn main:app --host 0.0.0.0 --port 8000"]
