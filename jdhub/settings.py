"""
Django settings for jdhub project (JD Hub — Mubogi Gastavas Jordan Tech Ecosystem).

Configuration is environment-driven with sensible local defaults so the site
runs out of the box with SQLite, while being production-ready (PostgreSQL via
DATABASE_URL, secure cookies, etc.) when environment variables are provided.
"""
from pathlib import Path
import os

try:  # Optional: enables DATABASE_URL (PostgreSQL) support when installed.
    import dj_database_url
except ImportError:  # pragma: no cover
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent


# --- Environment helpers -----------------------------------------------------
def _env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(int(default))).lower() in {"1", "true", "yes", "on"}


def _env_list(name: str, default: str) -> list[str]:
    return [h.strip() for h in os.environ.get(name, default).split(",") if h.strip()]


# --- Core --------------------------------------------------------------------
# In production DEBUG must be False and SECRET_KEY must come from the environment.
SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    # A dev-only fallback so local runs work without configuration.
    "django-insecure-local-dev-key-change-me-in-production-7f3a9b2c1e",
)
DEBUG = _env_bool("DJANGO_DEBUG", False)  # Secure default: off.
# Allow RENDER_EXTERNAL_URL-style hosts when provided; otherwise localhost.
ALLOWED_HOSTS = _env_list("DJANGO_ALLOWED_HOSTS", "localhost,127.0.0.1,0.0.0.0")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "hub",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "jdhub.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "hub" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "hub.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "jdhub.wsgi.application"
ASGI_APPLICATION = "jdhub.asgi.application"

# --- Database ----------------------------------------------------------------
# Prefer DATABASE_URL (PostgreSQL) when present; otherwise fall back to SQLite.
if os.environ.get("DATABASE_URL") and dj_database_url is not None:
    DATABASES = {"default": dj_database_url.parse(os.environ["DATABASE_URL"])}
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- Auth --------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- Internationalisation ----------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Africa/Kampala"
USE_I18N = True
USE_TZ = True

# --- Static & Media ----------------------------------------------------------
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# WhiteNoise serves static files in production without a reverse proxy.
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        if not DEBUG
        else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Logging (production-friendly: never leak secrets/stack traces to client)-
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "[{asctime}] {levelname} {name}: {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
        "django.security": {"handlers": ["console"], "level": "WARNING", "propagate": False},
    },
}

# --- Site settings (used by hub context processor) ---------------------------
SITE_NAME = "Jordan Design Hub"
SITE_TAGLINE = "Innovation, Education, Apps, Media & AI Solutions"
# Public base URL (no trailing slash) used for canonical/OG tags. Override in
# production with the real deployed URL, e.g. https://jd-hub-xyz.onrender.com.
SITE_URL = os.environ.get("DJANGO_SITE_URL", "https://jd-hub.onrender.com")
WHATSAPP_NUMBER = os.environ.get("DJANGO_WHATSAPP_NUMBER", "256754687597")
CONTACT_EMAIL = os.environ.get("DJANGO_CONTACT_EMAIL", "jordandesignhub@gmail.com")
SITE_OWNER = "Jordan Design Hub"

# --- Security (production hardening) ----------------------------------------
if not DEBUG:
    SECURE_HSTS_SECONDS = 60 * 60 * 24 * 30
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"
else:
    # Allow YouTube embeds in the gallery during local development.
    X_FRAME_OPTIONS = "SAMEORIGIN"

CSRF_TRUSTED_ORIGINS = _env_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
    "http://localhost,http://127.0.0.1",
)

# Honour the Render-provided external URL if set, so the deploy works without
# manual ALLOWED_HOSTS configuration.
_render_url = os.environ.get("RENDER_EXTERNAL_URL")
if _render_url:
    _render_host = _render_url.replace("https://", "").replace("http://", "").rstrip("/")
    if _render_host and _render_host not in ALLOWED_HOSTS:
        ALLOWED_HOSTS.append(_render_host)
    if _render_url not in CSRF_TRUSTED_ORIGINS:
        CSRF_TRUSTED_ORIGINS.append(_render_url)

# Session security: shorten cookie lifetime and expire on browser close.
SESSION_COOKIE_AGE = 60 * 60 * 12  # 12 hours
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

