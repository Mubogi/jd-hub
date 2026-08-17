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
