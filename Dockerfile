# ============================================
# Production Dockerfile for Django + Render.com
# Optimized for Render.com (PORT=10000)
# ============================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=10000  # ⬅️ غيّر من 8080 إلى 10000

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles media logs

# Create non-root user for security
RUN useradd -m -u 1000 django && \
    chown -R django:django /app

USER django

# Expose port
EXPOSE 10000  # ⬅️ غيّر من 8080 إلى 10000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:$PORT/health/ || exit 1  # ⬅️ استخدم $PORT

# Run Gunicorn - USE $PORT NOT 8080
CMD ["gunicorn", "--bind", "0.0.0.0:$PORT", "config.wsgi:application"]  # ⬅️ غيّر إلى $PORT
