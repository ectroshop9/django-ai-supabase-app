FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# تثبيت جميع المكتبات من requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN find . -type f -name "*.pyc" -delete \
    && find . -type d -name "__pycache__" -delete

ENV PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=config.settings

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# ✅ الحل الصحيح: JSON format مع shell expansion للـ PORT
CMD ["sh", "-c", "gunicorn config.wsgi:application --bind 0.0.0.0:${PORT:-10000} --workers 1 --timeout 120"]
