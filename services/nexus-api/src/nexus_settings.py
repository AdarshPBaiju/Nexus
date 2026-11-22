"""Minimal Django settings for linting and test execution."""

SECRET_KEY = "nexus-insecure-test-secret-key-only"
DEBUG = True
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
]
USE_TZ = True
