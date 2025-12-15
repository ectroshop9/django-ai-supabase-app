FROM python:3.11-slim

# مكتبات نظام أساسية فقط
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# نسخ المتطلبات أولاً
COPY requirements.txt .

# تثبيت
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

# تنظيف
RUN find . -type f -name "*.pyc" -delete \
    && find . -type d -name "__pycache__" -delete

ENV PYTHONUNBUFFERED=1 DJANGO_SETTINGS_MODULE=config.settings

# مستخدم
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# CMD مع JSON format
CMD ["sh", "-c", "exec gunicorn config.wsgi:application --bind 0.0.0.0:\${PORT:-10000} --workers 1 --timeout 120"]
