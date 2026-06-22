"""
Base settings shared by all environments.
"""
import os
from pathlib import Path

import dj_database_url
from decouple import config, Csv

# ── Paths ──────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent.parent  # backend/

# ── Security ───────────────────────────────────────────
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost,127.0.0.1', cast=Csv())

# ── Applications ───────────────────────────────────────
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party
    'rest_framework',
    'corsheaders',
    'django_filters',
    # Project apps
    'accounts',
    'core',
    'customers',
    'products',
    'invoices',
    'tasks',
    'providers',
    'purchases',
    'accounting_sync',
    'ecommerce_sync',
    'social_crm',
]

AUTH_USER_MODEL = 'accounts.User'

# ── Middleware ──────────────────────────────────────────
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
    'accounts.middleware.CompanyMiddleware',
]

ROOT_URLCONF = 'config.urls'

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

WSGI_APPLICATION = 'config.wsgi.application'

# ── Database ───────────────────────────────────────────
_DATABASE_URL = config('DATABASE_URL', default='')
if _DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.config(
            default=_DATABASE_URL,
            conn_max_age=600,
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# ── Password validation ───────────────────────────────
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ── Internationalization ──────────────────────────────
LANGUAGE_CODE = 'es-es'
TIME_ZONE = 'Europe/Madrid'
USE_I18N = True
USE_TZ = True

# ── Static files ──────────────────────────────────────
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

# ── Media files ───────────────────────────────────────
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# ── Default primary key ──────────────────────────────
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ── Django REST Framework ─────────────────────────────
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 25,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
}

# ── Facebook / Graph API ──────────────────────────────
FACEBOOK_APP_ID = config('FACEBOOK_APP_ID', default='')
FACEBOOK_APP_SECRET = config('FACEBOOK_APP_SECRET', default='')
FACEBOOK_GRAPH_VERSION = config('FACEBOOK_GRAPH_VERSION', default='v19.0')

# ── YouTube / Google OAuth 2.0 ────────────────────────
YOUTUBE_CLIENT_ID = config('YOUTUBE_CLIENT_ID', default='')
YOUTUBE_CLIENT_SECRET = config('YOUTUBE_CLIENT_SECRET', default='')

# ── X (Twitter) OAuth 2.0 ─────────────────────────────
TWITTER_CLIENT_ID = config('TWITTER_CLIENT_ID', default='')
TWITTER_CLIENT_SECRET = config('TWITTER_CLIENT_SECRET', default='')

# ── TikTok OAuth 2.0 ──────────────────────────────────
TIKTOK_CLIENT_KEY = config('TIKTOK_CLIENT_KEY', default='')
TIKTOK_CLIENT_SECRET = config('TIKTOK_CLIENT_SECRET', default='')

# ── Frontend URL (used as OAuth redirect base) ────────
FRONTEND_URL = config('FRONTEND_URL', default='http://localhost:5173')

# ── Integración Odoo ──────────────────────────────────
# Clave Fernet para cifrar credenciales de OdooConnection en BD.
# Generar con:
#   python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
ODOO_ENCRYPTION_KEY = config('ODOO_ENCRYPTION_KEY', default='')
# Intervalo de polling de pagos (minutos). Fijo global por decisión de proyecto.
ODOO_POLL_INTERVAL_MINUTES = config(
    'ODOO_POLL_INTERVAL_MINUTES', default=5, cast=int,
)
# Timeout por defecto de las llamadas XML-RPC a Odoo (segundos).
ODOO_RPC_TIMEOUT = config('ODOO_RPC_TIMEOUT', default=30, cast=int)
# Master password de Odoo (necesaria para crear BDs vía bootstrap_odoo).
ODOO_MASTER_PWD = config('ODOO_MASTER_PWD', default='')
# URL base del Odoo accesible desde el servidor Django (provisioning automático).
ODOO_BASE_URL = config('ODOO_BASE_URL', default='http://localhost:8069')

# ── Integración e-commerce (PrestaShop) ───────────────
# Clave Fernet para cifrar la API key de StoreConnection. Si no se define,
# se reutiliza ODOO_ENCRYPTION_KEY (ver ecommerce_sync/fields.py).
ECOMMERCE_ENCRYPTION_KEY = config('ECOMMERCE_ENCRYPTION_KEY', default='')
# Timeout por defecto de las llamadas HTTP al Webservice de la tienda (segundos).
ECOMMERCE_HTTP_TIMEOUT = config('ECOMMERCE_HTTP_TIMEOUT', default=30, cast=int)
# Intervalo de polling de pedidos (minutos). PrestaShop no tiene webhooks.
ECOMMERCE_POLL_INTERVAL_MINUTES = config(
    'ECOMMERCE_POLL_INTERVAL_MINUTES', default=10, cast=int,
)
