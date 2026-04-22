"""
Production-specific settings.
"""
from .base import *  # noqa: F401, F403

DEBUG = False

# ── Security ──
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = 'DENY'

# ── CORS — configure for your domain ──
CORS_ALLOWED_ORIGINS = [
    # 'https://your-production-domain.com',
]

# ── JSON only in production ──
REST_FRAMEWORK['DEFAULT_RENDERER_CLASSES'] = [  # noqa: F405
    'rest_framework.renderers.JSONRenderer',
]
