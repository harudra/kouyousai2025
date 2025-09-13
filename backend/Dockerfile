FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

WORKDIR /app

# Copy requirements first so Docker can cache installs when code changes
COPY requirements.txt .

# Install build deps, install python deps, then remove build deps and apt caches
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential gcc \
    && pip install --no-cache-dir -r requirements.txt \
    && apt-get purge -y --auto-remove build-essential gcc \
    && rm -rf /var/lib/apt/lists/*

COPY . .

# Use a non-root user for better security
RUN useradd --create-home appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Use Gunicorn with Uvicorn workers to run in production (Cloud Run).
# Use sh -c so ${PORT} is expanded from environment when container starts.
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT} --workers 1"]
