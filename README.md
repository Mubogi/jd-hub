# JD Hub

**Mubogi Gastavas Jordan Tech Ecosystem** — a production-ready, full-stack website built with Django, Bootstrap 5, and a PWA service worker.

JD Hub showcases flagship software systems, an adult-education & tutoring academy, consultancy services, a design & media gallery, and a WhatsApp-integrated contact form — all editable from the Django admin without touching code.

## Features

- **Hero section** with CTAs ("Explore Systems", "Join Academy")
- **Systems Showcase** with dynamic cards and downloadable PDF whitepapers (auto-generated via ReportLab from `media/system_docs/`)
  - Offline-First School Management System (PWA/Django)
  - SACCO Portfolio Quality & Microfinance System
  - Destiny College DBMS
- **Academy & Tutoring Hub** — interactive, filterable course catalog (All / STEM / Software / Financials): Scratch Coding, Basic Digital Literacy, Practical STEM, Graphic Design, Financial/SACCO Management
- **Services & Consultancy** — Custom Django/PWA builds, ICT Infrastructure/Networking, Media & Livestreaming (OBS/OpenLP/Audition)
- **Design & Media Gallery** — portfolio grid with YouTube/OBS video embeds
- **Contact & Lead Form** — submissions stored in admin with WhatsApp redirect (+256) and email
- **Django Admin** — manage Courses, Systems, PDF Whitepapers, Media Portfolio, Contact Submissions
- **PWA** — manifest + service worker for offline shell

## Tech Stack

| Layer       | Tech                                  |
|-------------|---------------------------------------|
| Backend     | Django 5.x (Python)                   |
| Database    | SQLite (PostgreSQL-ready via env)     |
| Frontend    | Bootstrap 5, FontAwesome, vanilla JS  |
| PDF engine  | ReportLab                             |
| PWA         | Web manifest + service worker         |

## Quickstart

```bash
# 1. Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. Configure environment (optional; defaults work for local SQLite)
export DJANGO_DEBUG=1
export DJANGO_SECRET_KEY="change-me-in-production"
export DJANGO_ALLOWED_HOSTS="localhost,127.0.0.1"

# 3. Migrate & create an admin user
python manage.py migrate
python manage.py createsuperuser

# 4. (Optional) Seed demo content + generate PDF whitepapers
python manage.py seed_demo

# 5. Run the server
python manage.py runserver
```

Visit:
- Site: <http://127.0.0.1:8000/>
- Admin: <http://127.0.0.1:8000/admin/>

## Deploying to Render (free tier)

This project ships with a [`render.yaml`](render.yaml) Blueprint for a one-click
deploy: a free Python web service + a free PostgreSQL database.

### One-time setup

1. Push this repo to GitHub (already done at <https://github.com/Mubogi/jd-hub>).
2. On <https://dashboard.render.com>: **New → Blueprint**, connect the GitHub repo.
3. Render detects `render.yaml` and proposes a **Web Service** (`jd-hub`) + **PostgreSQL** (`jd-hub-db`).
4. Before clicking **Apply**, set these **Environment Variables** on the web service (Render dashboard → *Environment*):
   - `DJANGO_SECRET_KEY` — generate a strong secret, e.g. run `python -c "import secrets;print(secrets.token_urlsafe(50))"` and paste it. **Required.**
   - `DJANGO_WHATSAPP_NUMBER` — e.g. `256700000000` (no `+`).
   - `DJANGO_CONTACT_EMAIL` — e.g. `you@example.com`.
   - `DJANGO_SUPERUSER_USERNAME` — e.g. `admin`
   - `DJANGO_SUPERUSER_EMAIL` — e.g. `admin@jdhub.example`
   - `DJANGO_SUPERUSER_PASSWORD` — a strong password (this creates your admin login on first deploy).
5. Click **Apply**. Render builds, runs `build.sh` (collectstatic → migrate → seed → ensuresuperuser), then launches gunicorn.
6. Open the service URL (e.g. `https://jd-hub.onrender.com`). Admin lives at `/admin/`.

> **Free-tier limits:** the web service spins down after ~15 min of inactivity (first request after idle takes ~30–60 s to wake). The free Postgres expires after 90 days unless upgraded — set a reminder or add a small disk for persistence.

### Production security checklist

- [x] `DEBUG=0` by default; stack traces never leak to users.
- [x] `SECRET_KEY` read from the environment (no hardcoded secrets in the repo).
- [x] HTTPS enforced via HSTS, secure cookies, and SSL redirect (Render terminates TLS).
- [x] `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` auto-include Render's `RENDER_EXTERNAL_URL`.
- [x] Static files served by WhiteNoise (compressed, cache-hashed).
- [x] Contact form has a honeypot anti-spam field; submissions validated server-side.
- [x] Sessions expire on browser close; 12-hour max age.
- [x] Dependencies are pinned to audited versions in `requirements.txt`.
- [ ] **You must:** set a strong `DJANGO_SECRET_KEY` (not the dev fallback).
- [ ] **You must:** set a strong `DJANGO_SUPERUSER_PASSWORD`.
- [ ] **You must:** [rotate the GitHub token](https://github.com/settings/tokens) you shared earlier.

### How to update the site (no code needed)

Almost everything is editable from the Django admin at `/admin/`:

1. Log in to `/admin/` with your superuser credentials.
2. Edit **Flagship Systems**, **Courses**, **Services**, **Media Portfolio**, or **Site Settings** — changes appear on the live site immediately.
3. **PDF whitepapers** regenerate automatically when you edit a System (or use the admin *Regenerate documentation PDFs* bulk action).
4. **Contact Submissions** appear under that section; change their status (New → In Progress → Resolved).

### How to update the code (developer)

```bash
git pull origin main              # stay in sync
# …make your changes…
python manage.py makemigrations   # if models changed
python manage.py migrate
python manage.py test             # if you add tests
git add -A && git commit -m "Describe change"
git push origin main              # Render auto-redeploys on push
```

Any push to `main` triggers a Render redeploy automatically.

## Project Structure

```
jdhub/                 # Django project (settings, urls, wsgi/asgi)
hub/                   # Core app
  models.py            # System, Course, Service, MediaItem, ContactSubmission
  admin.py             # Full admin integration
  views.py             # Home, contact, PDF download, sitemap
  management/commands/seed_demo.py
  templates/hub/       # Bootstrap 5 templates
  static/hub/          # CSS, JS, PWA manifest + service worker
media/system_docs/     # Generated PDF whitepapers (gitignored)
```

## Generating PDF Whitepapers

PDFs are generated on demand the first time a system's "Download Documentation PDF" button is clicked and cached in `media/system_docs/`. Re-running `python manage.py seed_demo` regenerates them.

## Configuration

Environment variables (all optional, sensible defaults provided):

| Variable                   | Purpose                                   |
|----------------------------|-------------------------------------------|
| `DJANGO_DEBUG`             | `1` for development                       |
| `DJANGO_SECRET_KEY`        | Secret key (auto-generated in dev)        |
| `DJANGO_ALLOWED_HOSTS`     | Comma-separated allowed hosts             |
| `DATABASE_URL`             | PostgreSQL URL for production DB          |

## License

MIT — © Mubogi Gastavas Jordan.
