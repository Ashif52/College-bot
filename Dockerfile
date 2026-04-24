# Stage 1: Build the Vite React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend

# Copy frontend package.json and install dependencies
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install

# Copy frontend source and build it
COPY frontend/ ./
RUN npm run build

# Stage 2: Setup the Python FastAPI Backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies if required (e.g., for building some python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download the sentence-transformers model so the first request isn't slow
# and the container doesn't time out on Railway during startup.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

# Copy backend source code
COPY . .

# Copy the built frontend static files from Stage 1
# This ensures that main.py's "if FRONTEND_DIST_DIR.exists():" works
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# Expose the port Railway will use
EXPOSE 8080

# Start the application using Uvicorn
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
