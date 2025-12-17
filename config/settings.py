"""
Django settings with Supabase + R2 + Upstash + Fly.io support
Full-Stack Architecture: Cloudflare CDN + Fly.io + Supabase + R2 + Upstash
"""

import os
from pathlib import Path
import dj_database_url
import warnings
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# ============= CORE SETTINGS =============
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-for-development')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'

# Fly.io App Name
FLY_APP_NAME = os.environ.get('FLY_APP_NAME', 'django-ai-supabase')

# Dynamic ALLOWED_HOSTS for Fly.io + Cloudflare
DEFAULT_HOSTS = ['localhost', '127.0.0.1']
if FLY_APP_NAME:
    DEFAULT_HOSTS.append(f'{FLY_APP_NAME}.fly.dev')

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', ','.join(DEFAULT_HOSTS)).split(',')

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
    'storages',           # لـ Cloudflare R2
    'django_redis',       # لـ Upstash Redis
    'corsheaders',        # لـ CORS support
    
    # Project Apps
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'sales.apps.SalesConfig',
    'notifications.apps.NotificationsConfig',
]

# ============= MIDDLEWARE =============
MIDDLEWARE = [
    # Security & Performance
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # Fallback static files
    "corsheaders.middleware.CorsMiddleware",       # CORS support
    
    # Django Core
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ============= CORS SETTINGS =============
CORS_ALLOWED_ORIGINS = [
    f"https://{FLY_APP_NAME}.fly.dev",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://*.supabase.co",
]

CORS_ALLOW_CREDENTIALS = True

# ============= DATABASE CONFIGURATION =============
# Priority: Supabase > Render > Railway > SQLite
SUPABASE_DB_URL = os.environ.get('SUPABASE_DB_URL')
RENDER_DB_URL = os.environ.get('DATABASE_URL')
RAILWAY_DB_URL = os.environ.get('RAILWAY_DATABASE_URL')
DEFAULT_DB_URL = 'sqlite:///' + str(BASE_DIR / 'db.sqlite3')

# Determine which database to use
DATABASE_URL = SUPABASE_DB_URL or RENDER_DB_URL or RAILWAY_DB_URL or DEFAULT_DB_URL

DATABASES = {
    'default': dj_database_url.config(
        default=DATABASE_URL,
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# SSL Configuration for Supabase
if 'supabase' in DATABASE_URL and not DEBUG:
    DATABASES['default']['OPTIONS'] = {
        'sslmode': 'require',
        'sslrootcert': str(BASE_DIR / 'supabase.crt'),
    }
    # Create supabase.crt if it doesn't exist
    if not (BASE_DIR / 'supabase.crt').exists():
        with open(BASE_DIR / 'supabase.crt', 'w') as f:
            f.write("""-----BEGIN CERTIFICATE-----
MIIDQTCCAimgAwIBAgITBmyfz5m/jAo54vB4ikPmljZbyjANBgkqhkiG9w0BAQsF
ADA5MQswCQYDVQQGEwJVUzEPMA0GA1UEChMGQW1hem9uMRkwFwYDVQQDExBBbWF6
b24gUm9vdCBDQSAxMB4XDTE1MDUyNjAwMDAwMFoXDTM4MDExNzAwMDAwMFowOTEL
MAkGA1UEBhMCVVMxDzANBgNVBAoTBkFtYXpvbjEZMBcGA1UEAxMQQW1hem9uIFJv
b3QgQ0EgMTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBALJ4gHHKeNXj
ca9HgFB0fW7Y14h29Jlo91ghYPl0hAEvrAIthtOgQ3pOsqTQNroBvo3bSMgHFzZM
9O6II8c+6zf1tRn4SWiw3te5djgdYZ6k/oI2peVKVuRF4fn9tBb6dNqcmzU5L/qw
IFAGbHrQgLKm+a/sRxmPUDgH3KKHOVj4utWp+UhnMJbulHheb4mjUcAwhmahRWa6
VOujw5H5SNz/0egwLX0tdHA114gk957EWW67c4cX8jJGKLhD+rcdqsq08p8kDi1L
93FcXmn/6pUCyziKrlA4b9v7LWIbxcceVOF34GfID5yHI9Y/QCB/IIDEgEw+OyQm
jgSubJrIqg0CAwEAAaNCMEAwDwYDVR0TAQH/BAUwAwEB/zAOBgNVHQ8BAf8EBAMC
AYYwHQYDVR0OBBYEFIQYzIU07LwMlJQuCFmcx7IQTgoIMA0GCSqGSIb3DQEBCwUA
A4IBAQCY8jdaQZChGsV2USggNiMOruYou6r4lK5IpDB/G/wkjUu0yKGX9rbxenDI
U5PMCCjjmCXPI6T53iHTfIUJrU6adTrCC2qJeHZERxhlbI1Bjjt/msv0tadQ1wUs
N+gDS63pYaACbvXy8MWy7Vu33PqUXHeeE6V/Uq2V8viTO96LXFvKWlJbYK8U90vv
o/ufQJVtMVT8QtPHRh8jrdkPSHCa2XV4cdFyQzR1bldZwgJcJmApzyMZFo6IQ6XU
5MsI+yMRQ+hDKXJioaldXgjUkK642M4UwtBV8ob2xJNDd2ZhwLnoQdeXeGADbkpy
rqXRfboQnoZsG4q5WTP468SQvvG5
-----END CERTIFICATE-----""")

# ============= CLOUDFLARE R2 CONFIGURATION =============
USE_R2 = os.environ.get('USE_R2', 'True') == 'True'
R2_ENABLED = USE_R2 and os.environ.get('R2_ACCESS_KEY_ID')

if R2_ENABLED:
    # R2 Configuration
    AWS_ACCESS_KEY_ID = os.environ.get('R2_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('R2_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = os.environ.get('R2_BUCKET_NAME', FLY_APP_NAME or 'django-app')
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
            "KEY_PREFIX": f"{FLY_APP_NAME}_cache",
        }
    }
    
    # Session Cache
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
    
    # Cache timeouts
    CACHE_TTL = 60 * 15  # 15 minutes default
    
    print(f"✅ Upstash Redis enabled | App: {FLY_APP_NAME}")
    
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': f'{FLY_APP_NAME}_local_cache',
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
    f'https://{FLY_APP_NAME}.fly.dev',
    'https://*.fly.dev',
    'https://*.supabase.co',
    'https://*.onrender.com',
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
            BASE_DIR / "frontend/build",  # For React/Vue if added later
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
            'builtins': [
                'django.templatetags.static',
            ],
        },
    },
]

# ============= STATIC FILES CONFIGURATION =============
STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "frontend/build/static",  # For React/Vue if added
] if (BASE_DIR / "static").exists() else []

# Static files finders
STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
]

# ============= FILE UPLOAD SETTINGS =============
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_NUMBER_FIELDS = 1000

# ============= AUTHENTICATION SETTINGS =============
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

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# Password hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# ============= INTERNATIONALIZATION =============
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ============= LOGGING CONFIGURATION =============
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO' if DEBUG else 'WARNING',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['console', 'file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    },
}

# ============= PERFORMANCE OPTIMIZATIONS =============
# Database connection pooling
if 'postgres' in DATABASE_URL:
    DATABASES['default']['CONN_MAX_AGE'] = 600

# Session settings
SESSION_COOKIE_AGE = 1209600  # 2 weeks in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_SAVE_EVERY_REQUEST = True

# ============= FLY.IO SPECIFIC SETTINGS =============
# Port for Fly.io
PORT = int(os.environ.get('PORT', 8080))

# Health check settings
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # 90%
    'MEMORY_MIN': 100,     # 100MB
}

# ============= APPLICATION SPECIFIC SETTINGS =============
# Custom settings
MAX_PRODUCTS_PER_USER = 100
MAX_SALES_PER_DAY = 1000
NOTIFICATION_RETENTION_DAYS = 30

# API Version
API_VERSION = 'v1'
API_BASE_URL = f'/api/{API_VERSION}/'

# ============= URL CONFIGURATION =============
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"

# ============= DEFAULT AUTO FIELD =============
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============= FINAL INITIALIZATION =============
# Create logs directory
(BASE_DIR / 'logs').mkdir(exist_ok=True)

# Print configuration summary
print(f"""
🚀 Django Application Configuration Summary:
===========================================
App Name:      {FLY_APP_NAME}
Debug Mode:    {DEBUG}
Database:      {'Supabase' if 'supabase' in DATABASE_URL else 
                'Render' if 'render' in DATABASE_URL else 
                'Railway' if 'railway' in DATABASE_URL else 
                'SQLite'}
Storage:       {'Cloudflare R2' if R2_ENABLED else 'Local (WhiteNoise)'}
Cache:         {'Upstash Redis' if UPSTASH_REDIS_URL else 'Local Memory'}
Port:          {PORT}
===========================================
""")

# Ignore staticfiles warning
warnings.filterwarnings('ignore', message='The directory.*in the STATICFILES_DIRS')
warnings.filterwarnings('ignore', category=UserWarning, module='whitenoise')