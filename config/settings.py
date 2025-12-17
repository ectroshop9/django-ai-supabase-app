"""
Django settings optimized for Render.com
"""

import os
from pathlib import Path
import dj_database_url
import warnings
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# ============= CORE SETTINGS =============
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-for-render')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Render.com specific
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS = [RENDER_EXTERNAL_HOSTNAME, 'localhost', '127.0.0.1']
else:
    ALLOWED_HOSTS = os.environ.get(
        'ALLOWED_HOSTS', 
        'localhost,127.0.0.1,*.onrender.com'
    ).split(',')

# App name for different platforms
APP_NAME = os.environ.get('APP_NAME', 'django-ai-supabase')

# ============= APPLICATIONS =============
INSTALLED_APPS = [
    # Django Core Apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    
    # Third Party Apps
    'rest_framework',
    'rest_framework_simplejwt',
    'storages',
    'django_redis',
    'corsheaders',
    
    # Project Apps
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'sales.apps.SalesConfig',
    'notifications.apps.NotificationsConfig',
]

# ============= MIDDLEWARE =============
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ============= CORS SETTINGS =============
CORS_ALLOWED_ORIGINS = [
    "https://*.onrender.com",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://*.supabase.co",
]

CORS_ALLOW_CREDENTIALS = True

# ============= DATABASE =============
# Render provides DATABASE_URL automatically
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
    print("✅ Using Render PostgreSQL database")
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    print("⚠️  Using SQLite (no DATABASE_URL found)")

# ============= CLOUDFLARE R2 CONFIGURATION =============
USE_R2 = os.environ.get('USE_R2', 'True') == 'True'
R2_ENABLED = USE_R2 and os.environ.get('R2_ACCESS_KEY_ID')

if R2_ENABLED:
    # R2 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', APP_NAME)
    AWS_S3_ENDPOINT_URL = os.environ.get('R2_ENDPOINT_URL')
    
    # R2 Specific Settings
    AWS_S3_REGION_NAME = 'auto'
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    AWS_QUERYSTRING_AUTH = False
    AWS_DEFAULT_ACL = 'public-read'
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    
    # Static Files on R2
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATIC_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/static/'
    
    # Media Files on R2 (Separate from Static)
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    MEDIA_URL = f'{AWS_S3_ENDPOINT_URL}/{AWS_STORAGE_BUCKET_NAME}/media/'
    
    print(f"✅ Cloudflare R2 enabled | Bucket: {AWS_STORAGE_BUCKET_NAME}")
    
else:
    # Fallback for Development (WhiteNoise)
    STATIC_URL = '/static/'
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'
    print("⚠️  R2 Disabled | Using WhiteNoise for static files")

# ============= UPSTASH REDIS CONFIGURATION =============
UPSTASH_REDIS_URL = os.environ.get('UPSTASH_REDIS_URL')

if UPSTASH_REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": UPSTASH_REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "CONNECTION_POOL_KWARGS": {"ssl_cert_reqs": None},
                "SOCKET_CONNECT_TIMEOUT": 5,
                "SOCKET_TIMEOUT": 5,
                "RETRY_ON_TIMEOUT": True,
                "MAX_CONNECTIONS": 50,
            },
            "KEY_PREFIX": f"{APP_NAME}_cache",
        }
    }
    
    # Session Cache
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
    
    # Cache timeouts
    CACHE_TTL = 60 * 15  # 15 minutes default
    
    print(f"✅ Upstash Redis enabled | App: {APP_NAME}")
    
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': f'{APP_NAME}_local_cache',
        }
    }
    print("⚠️  Upstash Redis disabled | Using Local Memory Cache")

# ============= REST FRAMEWORK CONFIGURATION =============
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
    ),
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/day',
        'user': '1000/day'
    },
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ] if DEBUG else [
        'rest_framework.renderers.JSONRenderer',
    ]
}

# ============= JWT CONFIGURATION =============
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    
    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    
    'JTI_CLAIM': 'jti',
    
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=60),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
}

# ============= SECURITY SETTINGS =============
CSRF_TRUSTED_ORIGINS = [
    'https://*.onrender.com',
    'https://*.fly.dev',
    'https://*.supabase.co',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
    'http://localhost:3000',
]

# Production Security
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
    
    # Rate limiting for production
    REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
        'anon': '50/day',
        'user': '500/day'
    }

# ============= TEMPLATES CONFIGURATION =============
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# ============= STATIC FILES =============
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / "static"] if (BASE_DIR / "static").exists() else []

# ============= AUTHENTICATION =============
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# ============= INTERNATIONALIZATION =============
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ============= URL CONFIGURATION =============
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============= RENDER.COM SETTINGS =============
PORT = int(os.environ.get('PORT', 10000))

# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# Print configuration summary
print(f"""
🚀 Django Application Configuration Summary:
===========================================
App Name:      {APP_NAME}
Debug Mode:    {DEBUG}
Database:      {'PostgreSQL' if DATABASE_URL else 'SQLite'}
Storage:       {'Cloudflare R2' if R2_ENABLED else 'Local (WhiteNoise)'}
Cache:         {'Upstash Redis' if UPSTASH_REDIS_URL else 'Local Memory'}
Port:          {PORT}
===========================================
""")

# Ignore warnings
warnings.filterwarnings('ignore', message='The directory.*in the STATICFILES_DIRS')
warnings.filterwarnings('ignore', category=UserWarning, module='whitenoise')
