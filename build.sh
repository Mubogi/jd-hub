#!/usr/bin/env bash
# Render release/build step: run on every deploy before the app starts.
# Safe to re-run (idempotent via Django's update_or_create + get_or_create).
set -e

echo "==> Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "==> Running migrations..."
python manage.py migrate --noinput

echo "==> Seeding demo content + generating PDF whitepapers..."
python manage.py seed_demo || echo "seed_demo failed (non-fatal)"

# Create/ensure an admin user for the dashboard.
# Credentials come from environment variables; no defaults for safety.
if [ -n "$DJANGO_SUPERUSER_USERNAME" ] && [ -n "$DJANGO_SUPERUSER_EMAIL" ] && [ -n "$DJANGO_SUPERUSER_PASSWORD" ]; then
  echo "==> Ensuring superuser '$DJANGO_SUPERUSER_USERNAME' exists..."
  python manage.py ensuresuperuser || echo "ensuresuperuser failed (non-fatal)"
else
  echo "==> Skipping superuser creation (DJANGO_SUPERUSER_* env vars not set)."
  echo "    Set them in the Render dashboard, then redeploy to create an admin."
fi

echo "==> Build step complete."
