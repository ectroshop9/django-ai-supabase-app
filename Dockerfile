# ============================================
# Django Dockerfile for Render.com
# PORT: 10000 (Render.com free tier requirement)
# ============================================

FROM python:3.11-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p staticfiles media logs

# Create non-root user
RUN useradd -m -u 1000 django && \
    chown -R django:django /app

USER django

# Expose port (Render.com uses 10000)
EXPOSE 10000

# Run Gunicorn with dynamic PORT
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:$PORT"]
