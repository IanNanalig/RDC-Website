# rdc_site/settings.py
import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv

# load .env from backend/.env if present
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-local-dev-key')
DEBUG = os.environ.get('DEBUG', 'True').lower() in ('true', '1', 'yes')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
TIME_ZONE = os.environ.get('TIME_ZONE', 'Asia/Manila')
USE_TZ = True

AUTH_USER_MODEL = 'projects.User'  # Or 'users.User' if you have users app

ROOT_URLCONF = "rdc_site.urls"

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.postgres',  # Postgres-specific fields and functions
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'projects',  # Your app
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=int(os.environ.get('JWT_ACCESS_HOURS', '8'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.environ.get('JWT_REFRESH_DAYS', '7'))),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
}

# CORS Settings
default_cors_origins = "http://localhost:5173,http://localhost:3000"
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get("CORS_ALLOWED_ORIGINS", default_cors_origins).split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True

# Database configuration: prefer Postgres when env vars are present, otherwise use sqlite3 for local dev
# Allow forcing sqlite for one-off commands by setting FORCE_SQLITE=1 in the environment
def postgres_config_from_url(database_url):
    parsed = urlparse(database_url)
    return {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': parsed.path.lstrip('/'),
        'USER': parsed.username or '',
        'PASSWORD': parsed.password or '',
        'HOST': parsed.hostname or 'localhost',
        'PORT': str(parsed.port or 5432),
    }


if os.environ.get('FORCE_SQLITE', '').lower() in ('1', 'true', 'yes'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }
elif os.environ.get('DATABASE_URL'):
    DATABASES = {
        'default': postgres_config_from_url(os.environ['DATABASE_URL'])
    }
elif os.environ.get('POSTGRES_DB'):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB'),
            'USER': os.environ.get('POSTGRES_USER', ''),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', ''),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': str(BASE_DIR / 'db.sqlite3'),
        }
    }

# Connection pooling and transactional requests
CONN_MAX_AGE = int(os.environ.get('CONN_MAX_AGE', 600))
DATABASES['default']['CONN_MAX_AGE'] = CONN_MAX_AGE
DATABASES['default']['ATOMIC_REQUESTS'] = True

# Security: require SSL in production-managed DBs when provided
DB_SSLMODE = os.environ.get('POSTGRES_SSLMODE')
if DB_SSLMODE and DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
    DATABASES['default']['OPTIONS'] = {'sslmode': DB_SSLMODE}

# Minimal middleware and templates required for admin and management commands
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
# Minimal defaults for development; adjust STATIC_ROOT for production collectstatic.
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
try:
    STATIC_ROOT = BASE_DIR / 'staticfiles'
    STATICFILES_DIRS = [BASE_DIR / 'static']
except Exception:
    STATIC_ROOT = str(BASE_DIR / 'staticfiles')
    STATICFILES_DIRS = [str(BASE_DIR / 'static')]

# Email (SMTP)
email_backend_config = os.environ.get("EMAIL_BACKEND", "").lower()
if email_backend_config == "console":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
elif os.environ.get("EMAIL_HOST"):
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
if EMAIL_HOST.lower() == "smtp.gmail.com":
    EMAIL_HOST_PASSWORD = EMAIL_HOST_PASSWORD.replace(" ", "")
EMAIL_TIMEOUT = int(os.environ.get("EMAIL_TIMEOUT", "10"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "true").lower() in ("1", "true", "yes")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", EMAIL_HOST_USER or "no-reply@rdc-portal.local")
CONTACT_RECEIVER_EMAIL = os.environ.get("CONTACT_RECEIVER_EMAIL", "ian095108@gmail.com")
EMAIL_WEBHOOK_URL = os.environ.get("EMAIL_WEBHOOK_URL", "")
EMAIL_WEBHOOK_SECRET = os.environ.get("EMAIL_WEBHOOK_SECRET", "")
RESEND_API_KEY = os.environ.get("RESEND_API_KEY", "")
RESEND_FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", DEFAULT_FROM_EMAIL)

# Frontend base URL for setup links
FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:5173")

# Password reset request protections
PASSWORD_RESET_RATE_LIMIT_WINDOW = int(os.environ.get("PASSWORD_RESET_RATE_LIMIT_WINDOW", "3600"))
PASSWORD_RESET_RATE_LIMIT_EMAIL = int(os.environ.get("PASSWORD_RESET_RATE_LIMIT_EMAIL", "2"))
PASSWORD_RESET_RATE_LIMIT_IP = int(os.environ.get("PASSWORD_RESET_RATE_LIMIT_IP", "5"))

# Cloudflare Turnstile CAPTCHA (optional)
TURNSTILE_SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY", "")
TURNSTILE_REQUIRED = os.environ.get("TURNSTILE_REQUIRED", "false").lower() in ("1", "true", "yes")
