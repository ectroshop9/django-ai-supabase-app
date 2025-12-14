FROM python:3.11-slim

# 1. تثبيت dependencies النظام
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# 2. إنشاء مجلد التطبيق
WORKDIR /app

# 3. نسخ requirements وتثبيتها
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 4. نسخ باقي الملفات
COPY . .

# 5. إعدادات البيئة
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

# 6. جمع الملفات الساكنة
RUN python manage.py collectstatic --noinput

# 7. إنشاء مستخدم غ
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# 8. تشغيل التطبيق
CMD gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile - --error-logfile -
