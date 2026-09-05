"""
Django settings for the Dream Palace backend.
Secrets and environment-specific values are read from environment
variables. Never commit real secrets.
"""
import os
import importlib
from pathlib import Path

# ✅ PyMySQL for MySQL connection
try:
    pymysql = importlib.import_module("pymysql")
    pymysql.install_as_MySQLdb()
except ImportError:
    pymysql = None

BASE_DIR = Path(__file__).resolve().parent.parent

# ✅ Load .env file
try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

def env(key, default=None):
    return os.environ.get(key, default)

# ============================================================
# CORE SETTINGS
# ============================================================
SECRET_KEY = env("DJANGO_SECRET_KEY", "insecure-dev-key-change-me")
DEBUG = env("DJANGO_DEBUG", "True") == "True"
ALLOWED_HOSTS = [
    h.strip()
    for h in env("DJANGO_ALLOWED_HOSTS", "*").split(",")
    if h.strip()
]

# ============================================================
# INSTALLED APPS
# ============================================================
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    
    "accounts",
    "listings",
    "bookings",
    "payments",
    "messaging",
]

# ============================================================
# ✅ MIDDLEWARE — CORS MUST BE 2ND!
# ============================================================
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",  # ← KEEP HERE!
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ============================================================
# URL / APPLICATION
# ============================================================
ROOT_URLCONF = "dream_palace.urls"
WSGI_APPLICATION = "dream_palace.wsgi.application"
ASGI_APPLICATION = "dream_palace.asgi.application"

# ============================================================
# TEMPLATES
# ============================================================
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

# ============================================================
# ✅ DATABASE — AlwaysData MySQL
# ============================================================
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE", "django.db.backends.mysql"),
        "NAME": env("DB_NAME", "ryacksonfungo_dream"),
        "USER": env("DB_USER", "ryacksonfungo"),
        "PASSWORD": env("DB_PASSWORD", "modcom2026"),
        "HOST": env("DB_HOST", "mysql-ryacksonfungo.alwaysdata.net"),
        "PORT": env("DB_PORT", "3306"),
    }
}

# ============================================================
# AUTHENTICATION
# ============================================================
AUTH_USER_MODEL = "accounts.User"
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ============================================================
# INTERNATIONALIZATION
# ============================================================
LANGUAGE_CODE = "en-us"
TIME_ZONE = env("DJANGO_TIME_ZONE", "Africa/Nairobi")
USE_I18N = True
USE_TZ = True

# ============================================================
# STATIC / MEDIA
# ============================================================
STATIC_URL = "static-assets/"
STATIC_ROOT = BASE_DIR / "staticfiles"
MEDIA_URL = "/static/images/"
MEDIA_ROOT = BASE_DIR / "media" / "images"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# ============================================================
# ✅ CORS — ALLOW ALL ORIGINS (TEMP FIX)
# ============================================================
CORS_ALLOW_ALL_ORIGINS = True  # ← DISABLES ALL CORS CHECKS
CORS_ALLOW_CREDENTIALS = True

# ============================================================
# ✅ CSRF — Trust ALL your domains
# ============================================================
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://ryacksonfungo.alwaysdata.net",
    "https://ryacksonfungo.alwaysdata.net",
]

# ============================================================
# M-PESA / DARAJA
# ============================================================
MPESA_ENV = env("MPESA_ENV", "sandbox")
MPESA_CONSUMER_KEY = env("MPESA_CONSUMER_KEY", "")
MPESA_CONSUMER_SECRET = env("MPESA_CONSUMER_SECRET", "")
MPESA_SHORTCODE = env("MPESA_SHORTCODE", "174379")
MPESA_PASSKEY = env("MPESA_PASSKEY", "")
MPESA_CALLBACK_URL = env("MPESA_CALLBACK_URL", "https://ryacksonfungo.alwaysdata.net/api/mpesa/callback/")
BOOKING_HOLD_MINUTES = int(env("BOOKING_HOLD_MINUTES", "15"))

# ============================================================
# EMAIL
# ============================================================
EMAIL_BACKEND = env("EMAIL_BACKEND", "django.core.mail.backends.smtp.EmailBackend")
EMAIL_HOST = env("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(env("EMAIL_PORT", "587"))
EMAIL_HOST_USER = env("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env("EMAIL_USE_TLS", "True") == "True"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", "no-reply@dreampalace.example")
ADMIN_NOTIFY_EMAIL = env("ADMIN_NOTIFY_EMAIL", "")