from datetime import timedelta 
from pathlib import Path
import os 
from dotenv import load_dotenv
import dj_database_url

load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG','False') =='True'

ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = [
    'https://localhost:8000',
    'http://127.0.0.1:8000',
    'https://127.0.0.1:8000',
    'http://localhost:8000',
    'https://*.github.dev',
    'https://*.app.github.dev',
    'https://*.koyeb.app',
    'https://upgraded-halibut-wrpvvx95v57vc5jr7-8000.app.github.dev',
    'https://*.onrender.com',      # ⬅️ أضف https://
    'https://*.koyeb.app',         # ⬅️ أضف https://
    'https://*.herokuapp.com',    # ⬅️ أضف https://
    'https://*.up.railway.app',   # ⬅️ أضف https://
]

# CORS للسماح لـ UptimeRobot بالوصول
CORS_ALLOWED_ORIGINS = [
    "https://uptimerobot.com",
    "https://api.uptimerobot.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_ALL_ORIGINS = True  # للتطوير فقط
CORS_ALLOW_CREDENTIALS = True
# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'rest_framework_simplejwt',
    'accounts.apps.AccountsConfig',
    'products.apps.ProductsConfig',
    'sales.apps.SalesConfig',
    'notifications.apps.NotificationsConfig',
   

]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
<<<<<<< HEAD
=======
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ⬅️ أضف هذا السطر
    'corsheaders.middleware.CorsMiddleware',  
>>>>>>> f1c56ae127f739e4d70a22eaa3c93a5903d638f6
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / 'config' / 'templates'],  # ⬅️ أضف هذا السطر
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

DATABASES = {
    'default': dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600  
    )
    
}
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'), # قراءة مفتاح Upstash
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}    
# [جديد] السماح بملفات تعريف الارتباط من أي بروتوكول آمن (HTTPS) في التطوير
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# [جديد] السماح بملفات تعريف الارتباط بين المجالات الفرعية
SESSION_COOKIE_SAMESITE = None 
# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True
# ============= UptimeRobot Settings =============

# Health Check Configuration
HEALTH_CHECK = {
    'ENABLED': True,
    'ENDPOINTS': [
        '/health/',
        '/api/health/',
        '/',  # الصفحة الرئيسية
    ],
    'CHECK_INTERVAL': 300,  # 5 دقائق (بالثواني)
}

# Monitoring Services
MONITORING_SERVICES = {
    'UPTIMEROBOT': {
        'ENABLED': True,
        'API_KEY': os.environ.get('UPTIMEROBOT_API_KEY', ''),
        'ALERT_CONTACTS': os.environ.get('UPTIMEROBOT_CONTACTS', ''),
    },
    'TELEGRAM': {
        'ENABLED': os.environ.get('TELEGRAM_ENABLED', 'False') == 'True',
        'BOT_TOKEN': os.environ.get('TELEGRAM_BOT_TOKEN', ''),
        'CHAT_ID': os.environ.get('TELEGRAM_CHAT_ID', ''),
    }
}

# Auto Ping Settings (لإبقاء الخدمة نشطة)
AUTO_PING = {
    'ENABLED': True,
    'SERVICES': [
        {
            'name': 'UptimeRobot',
            'url': 'https://api.uptimerobot.com/v2/getMonitors',
            'interval': 300,  # كل 5 دقائق
        }
    ]
}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = "static/"


# **********************************************
# إعدادات Django REST Framework
# **********************************************
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # [مهم] تحديد JWT كآلية المصادقة الافتراضية
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        # السماح بالقراءة للجميع افتراضياً، وسيتم تجاوزها بـ IsAuthenticated في الـ Views
        'rest_framework.permissions.AllowAny',
    )
}


# **********************************************
# إعدادات Simple JWT
# **********************************************
SIMPLE_JWT = {
    # 1. تخصيص الفئة التي تولد التوكنات بناءً على السيريال (Serial)
    # نستخدم فئة الـ Serializer المخصصة التي كتبناها في accounts
    'TOKEN_OBTAIN_SERIALIZER': 'accounts.serializers.CustomTokenObtainPairSerializer',
    
    # 2. تحديد مدة صلاحية التوكنات
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),  # مدة صلاحية توكن الوصول (Access)
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),    # مدة صلاحية توكن التحديث (Refresh)

    # 3. إعدادات فنية إضافية
    'ROTATE_REFRESH_TOKENS': True, # تدوير توكن التحديث عند كل استخدام (أمان أفضل)
    'BLACKLIST_AFTER_ROTATION': True, # إدراج التوكن القديم في القائمة السوداء
    'UPDATE_LAST_LOGIN': True, # تحديث حقل آخر تسجيل دخول للمستخدم
}

# **********************************************
# إعدادات المستخدم المخصص (لتشغيل JWT)
# **********************************************
# [مهم] هذا يضمن أن JWT يمكنه ربط التوكن بالعميل الصحيح (الذي تم ربطه بكائن User)
AUTH_USER_MODEL = 'auth.User'

# ============= إعدادات Static Files =============

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Render-specific settings
import os
PORT = os.environ.get('PORT', '8000')  # Render يمرر PORT

# Production security (لـ Render و Koyeb)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# إعدادات Cloudflare Worker
CLOUDFLARE_WORKER_ENABLED = os.environ.get('CLOUDFLARE_WORKER_ENABLED', 'False') == 'True'
CLOUDFLARE_WORKER_URL = os.environ.get('CLOUDFLARE_WORKER_URL', '')
CLOUDFLARE_WORKER_SECRET = os.environ.get('CLOUDFLARE_WORKER_SECRET', '')

# إعدادات الروابط المحمية
PROTECTED_LINKS = {
    'EXPIRY_HOURS': 2,  # صلاحية الرابط ساعتين
    'MAX_DOWNLOADS': 3,  # 3 تحميلات لكل شراء
    'WORKER_TIMEOUT': 5,  # ثواني للاتصال بالـ Worker
}
