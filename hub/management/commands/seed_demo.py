"""
Seed demo content and generate PDF whitepapers.

Usage:
    python manage.py seed_demo
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from hub.models import Course, MediaItem, Service, SiteSettings, System
from hub.pdf import build_pdf


SYSTEMS = [
    {
        "title": "Offline-First School Management System",
        "tagline": "PWA/Django platform for schools — runs even without the internet.",
        "category": "education",
        "icon": "fa-solid fa-school",
        "tech_stack": "Django, PWA, SQLite, PostgreSQL, Bootstrap, Service Worker",
        "description": (
            "A progressive web app built on Django that digitises the full school workflow — "
            "enrolment, attendance, grading, fee collection, and parent communication. Its "
            "offline-first architecture ensures teachers in low-connectivity areas keep working, "
            "with automatic synchronisation when the network returns."
        ),
        "features": [
            "Student & staff records with role-based dashboards",
            "Attendance and assessment capture (offline-capable)",
            "Fee billing, receipts, and arrears tracking",
            "Parent portal with SMS/email notifications",
            "Termly report cards and transcript generation",
            "Backup and restore to CSV/Excel",
        ],
        "sort_order": 10,
    },
    {
        "title": "SACCO Portfolio Quality & Microfinance System",
        "tagline": "Double-entry ledger, loans, and portfolio analytics for SACCOs.",
        "category": "finance",
        "icon": "fa-solid fa-hand-holding-dollar",
        "tech_stack": "Django, PostgreSQL, ReportLab, Bootstrap",
        "description": (
            "A microfinance management system for Savings and Credit Cooperatives (SACCOs). It "
            "manages member savings, share capital, loan origination, repayment schedules, and "
            "portfolio-quality analytics — with a double-entry ledger and full audit trail."
        ),
        "features": [
            "Member onboarding and share-capital management",
            "Savings products (ordinary, fixed, deposits)",
            "Loan application, approval workflow, and amortisation",
            "Repayment collection and arrears/penalty automation",
            "Portfolio-at-Risk (PAR) and write-off reporting",
            "Double-entry ledger with immutable audit logs",
        ],
        "sort_order": 20,
    },
    {
        "title": "Destiny College DBMS",
        "tagline": "Normalised academic database with grading and transcript analytics.",
        "category": "database",
        "icon": "fa-solid fa-database",
        "tech_stack": "Django, PostgreSQL, SQLite, Bootstrap",
        "description": (
            "A relational Database Management System tailored to Destiny College's academic records. "
            "It normalises students, courses, enrolment, and grading, and powers longitudinal "
            "performance analytics across cohorts and terms."
        ),
        "features": [
            "Normalised schema for students, courses, and enrolments",
            "Referential integrity and database-level validation",
            "Grading schemes (Cambridge & Uganda curricula)",
            "Transcript and cohort performance reports",
            "Versioned migrations for safe schema evolution",
            "Automated daily backups with CSV/Excel export",
        ],
        "sort_order": 30,
    },
]

COURSES = [
    {
        "title": "Scratch Coding (Uganda & Cambridge Curricula)",
        "category": "software",
        "icon": "fa-solid fa-code",
        "level": "Beginner",
        "duration": "8 weeks",
        "description": (
            "Block-based programming for ages 8+, aligned to both the Uganda and Cambridge "
            "curricula. Students build animations, games, and interactive stories while learning "
            "core computational thinking."
        ),
        "curriculum": [
            "Sequencing, loops, and events",
            "Conditional logic and variables",
            "Sprite animation and story design",
            "Mini-projects: quiz game, maze, animation",
            "Curriculum-aligned assessment tasks",
        ],
        "sort_order": 10,
    },
    {
        "title": "Basic Digital Literacy",
        "category": "software",
        "icon": "fa-solid fa-laptop",
        "level": "Beginner",
        "duration": "4 weeks",
        "description": (
            "Foundational computer skills for adult learners: operating systems, file management, "
            "email, internet safety, and productivity basics."
        ),
        "curriculum": [
            "Computer hardware & operating systems",
            "File management and cloud storage",
            "Email, calendars, and online safety",
            "Introduction to Word processing & spreadsheets",
        ],
        "sort_order": 20,
    },
    {
        "title": "Practical STEM",
        "category": "stem",
        "icon": "fa-solid fa-flask",
        "level": "Beginner to Intermediate",
        "duration": "10 weeks",
        "description": (
            "Hands-on STEM sessions combining basic electronics, simple robotics, and inquiry-based "
            "science experiments to build problem-solving skills."
        ),
        "curriculum": [
            "Scientific method and observation",
            "Basic circuits and electronics",
            "Introductory robotics with block kits",
            "Maths modelling with real data",
        ],
        "sort_order": 30,
    },
    {
        "title": "Graphic Design (Canva & InShot)",
        "category": "software",
        "icon": "fa-solid fa-pen-ruler",
        "level": "Beginner",
        "duration": "6 weeks",
        "description": (
            "Create posters, social media graphics, and short videos using Canva and InShot. "
            "Covers brand basics, typography, and mobile-first content creation."
        ),
        "curriculum": [
            "Design principles & colour theory",
            "Canva for posters and social media",
            "InShot for short-form video editing",
            "Brand kits and templates",
        ],
        "sort_order": 40,
    },
    {
        "title": "Financial & SACCO Management",
        "category": "financials",
        "icon": "fa-solid fa-chart-line",
        "level": "Intermediate",
        "duration": "6 weeks",
        "description": (
            "Practical financial literacy and SACCO record-keeping: savings discipline, loan "
            "management, bookkeeping, and using the JD Hub SACCO system."
        ),
        "curriculum": [
            "Personal & group financial planning",
            "Bookkeeping basics and double-entry",
            "SACCO savings and loan cycles",
            "Portfolio quality and arrears management",
        ],
        "sort_order": 50,
    },
]

SERVICES = [
    {
        "title": "Custom Django / PWA Software Builds",
        "icon": "fa-solid fa-code-branch",
        "description": (
            "Bespoke, offline-first web applications built with Django and progressive web app "
            "technology — from requirements gathering to deployment and support."
        ),
        "deliverables": [
            "Requirements analysis & system design",
            "Django backend + PWA frontend",
            "Deployment and staff training",
            "Ongoing maintenance & support",
        ],
        "sort_order": 10,
    },
    {
        "title": "ICT Infrastructure & Networking",
        "icon": "fa-solid fa-network-wired",
        "description": (
            "Local area networks, server setup, and workstation deployment for schools, SACCOs, "
            "and small offices — including structured cabling and Wi-Fi."
        ),
        "deliverables": [
            "Network design & cabling",
            "Server and router configuration",
            "Workstation setup & imaging",
            "Security hardening & documentation",
        ],
        "sort_order": 20,
    },
    {
        "title": "Media & Livestreaming Setup",
        "icon": "fa-solid fa-tower-broadcast",
        "description": (
            "End-to-end media setup for events and worship: OBS for livestreaming, OpenLP for "
            "lyric/projection, and Adobe Audition for audio post-production."
        ),
        "deliverables": [
            "OBS livestream configuration",
            "OpenLP projection setup",
            "Adobe Audition audio workflow",
            "Operator training & runbooks",
        ],
        "sort_order": 30,
    },
]

MEDIA_ITEMS = [
    {
        "title": "School Management Dashboard",
        "caption": "Admin dashboard for the offline-first school system.",
        "media_type": "image",
        "sort_order": 10,
    },
    {
        "title": "SACCO Analytics Report",
        "caption": "Portfolio-at-Risk analytics view.",
        "media_type": "image",
        "sort_order": 20,
    },
    {
        "title": "JD Hub Academy Promo",
        "caption": "Promo video for the adult-education academy.",
        "media_type": "video",
        "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "sort_order": 30,
    },
    {
        "title": "OBS Livestream Setup",
        "caption": "Live event streaming configuration.",
        "media_type": "video",
        "video_url": "https://www.youtube.com/watch?v=ScMzIvxBSi4",
        "sort_order": 40,
    },
    {
        "title": "Event Poster Design",
        "caption": "Canva poster for a community tech bootcamp.",
        "media_type": "image",
        "sort_order": 50,
    },
    {
        "title": "Scratch Coding Showcase",
        "caption": "Student projects from the Scratch coding course.",
        "media_type": "image",
        "sort_order": 60,
    },
]


class Command(BaseCommand):
    help = "Seed demo content (systems, courses, services, media) and generate PDF whitepapers."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding systems..."))
        for item in SYSTEMS:
            features = "\n".join(item.pop("features"))
            System.objects.update_or_create(
                title=item["title"], defaults={**item, "features": features}
            )

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding courses..."))
        for item in COURSES:
            curriculum = "\n".join(item.pop("curriculum"))
            Course.objects.update_or_create(
                title=item["title"], defaults={**item, "curriculum": curriculum}
            )

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding services..."))
        for item in SERVICES:
            deliverables = "\n".join(item.pop("deliverables"))
            Service.objects.update_or_create(
                title=item["title"], defaults={**item, "deliverables": deliverables}
            )

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding media portfolio..."))
        for item in MEDIA_ITEMS:
            MediaItem.objects.update_or_create(
                title=item["title"], defaults=item
            )

        self.stdout.write(self.style.MIGRATE_HEADING("Ensuring site settings exist..."))
        SiteSettings.get()

        self.stdout.write(self.style.MIGRATE_HEADING("Generating PDF whitepapers..."))
        for system in System.objects.all():
            path = build_pdf(system)
            self.stdout.write(f"  ✓ {system.title} → {path.name}")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
