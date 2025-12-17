FROM python:3.11-slim

# متغيرات البيئة
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=10000

WORKDIR /app

# 1. تثبيت تبعيات النظام فقط (الأساسية للغاية)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libpq-dev \
    curl \
    libjpeg62-turbo \
    libpng16-16 \
    libwebp7 \
    zlib1g \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/* /var/tmp/*

# 2. تحديث pip وتثبيت requirements بدون cache
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt

# 3. نسخ المشروع فقط (باستخدام .dockerignore جيد)
COPY . .

# 4. تنظيف الملفات غير الضرورية
RUN find /app -type f -name "*.pyc" -delete && \
    find /app -type d -name "__pycache__" -delete && \
    rm -rf /root/.cache/pip

# 5. إنشاء المجلدات
RUN mkdir -p staticfiles media

# 6. مستخدم غير root
RUN useradd -m -u 1000 django && \
    chown -R django:django /app

USER django

# إضافة pip packages إلى PATH
ENV PATH=/home/django/.local/bin:$PATH

# 7. الأمر النهائي
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn --bind 0.0.0.0:${PORT:-10000} config.wsgi:application"]
