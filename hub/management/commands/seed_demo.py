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
        "tagline": "Desktop + web platform for schools — runs even without the internet.",
        "category": "education",
        "icon": "fa-solid fa-school",
        "tech_stack": "Django, PWA, SQLite, PostgreSQL, Bootstrap, Service Worker, PyInstaller",
        "description": (
            "A desktop application (with PWA companion) built on Django that digitises the full "
            "school workflow — enrolment, attendance, grading, fee collection, and parent "
            "communication. Its offline-first architecture ensures teachers in low-connectivity "
            "areas keep working, with automatic synchronisation when the network returns. "
            "Hardware-bound licensing protects against unauthorised copying."
        ),
        "features": [
            "Student & staff records with role-based dashboards",
            "Attendance and assessment capture (offline-capable)",
            "Fee billing, receipts, and arrears tracking",
            "Parent portal with WhatsApp/email notifications at no cost",
            "Termly report cards and transcript generation",
            "QR parent kiosk for report access",
            "Hybrid backup (local, USB, cloud)",
        ],
        "screenshots": [
            ("system_shots/sms_landing_page.png", "Landing page — branded entry point"),
            ("system_shots/sms_admin_dashboard.png", "School admin dashboard"),
            ("system_shots/sms_student_list.png", "Student management list"),
            ("system_shots/sms_student_enroll.png", "Student enrolment form"),
            ("system_shots/sms_marks_entry.png", "Bulk marks entry"),
            ("system_shots/sms_receipts.png", "Fee receipts and payments"),
            ("system_shots/sms_whatsapp_queue.png", "WhatsApp notification queue"),
            ("system_shots/sms_parent_kiosk.png", "QR parent kiosk"),
        ],
        "sort_order": 10,
    },
    {
        "title": "Attendance Hub",
        "tagline": "Event & church attendance kiosk — desktop, web, and native Android.",
        "category": "education",
        "icon": "fa-solid fa-clipboard-check",
        "tech_stack": "Django, SQLite, Room (Android), Kotlin, PWA, Excel/CSV export",
        "description": (
            "A standalone attendance system for churches, conferences, and events — available as "
            "a Windows desktop app, a web kiosk, and a fully native Android app. No server, no "
            "computer, no internet required: everything runs on the device. The Android edition "
            "adds Wi-Fi device linking so multiple phones share one attendance dataset in real time."
        ),
        "features": [
            "One-tap check-in and quick member registration",
            "Searchable member database with attendance history",
            "Session-based attendance (services, conferences, workshops)",
            "Sunday school / children & dependent tracking",
            "Excel, CSV, and PDF report exports",
            "JSON backup export and restore",
            "Wi-Fi device linking (Android) — multi-phone shared dataset",
            "Works fully offline — on-device SQLite database",
        ],
        "screenshots": [
            ("system_shots/attendance_web_dashboard.png", "Registration dashboard — live counts & quick check-in"),
            ("system_shots/attendance_web_members.png", "Members database with filters"),
            ("system_shots/attendance_web_reports.png", "Reports — session summary, missed lists, exports"),
            ("system_shots/attendance_web_admin.png", "Admin dashboard — backup & reset"),
            ("system_shots/attendance_web_member_profile.png", "Member profile with attendance history"),
            ("system_shots/attendance_web_device_link.png", "Wi-Fi device linking — host & join sessions"),
        ],
        "sort_order": 15,
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
    {
        "title": "AI Optimization & Prompt Engineering",
        "category": "ai",
        "icon": "fa-solid fa-robot",
        "level": "Beginner to Intermediate",
        "duration": "4 weeks",
        "description": (
            "Learn to use AI tools effectively — writing better prompts, automating "
            "everyday tasks, and integrating AI into your work and business."
        ),
        "curriculum": [
            "How large language models work",
            "Prompt engineering fundamentals",
            "AI tools for productivity (writing, research, code)",
            "AI for business workflows & automation",
        ],
        "sort_order": 60,
    },
    {
        "title": "Microsoft Word",
        "category": "software",
        "icon": "fa-solid fa-file-word",
        "level": "Beginner to Intermediate",
        "duration": "2 weeks",
        "description": (
            "Master Microsoft Word — from formatting a simple letter to designing professional "
            "reports, CVs, and certificates. Learn single-tool mastery of the world's most-used "
            "word processor."
        ),
        "curriculum": [
            "Interface, ribbons, and document setup",
            "Text formatting, styles, and themes",
            "Tables, images, and page layout",
            "Headers, footers, and section breaks",
            "Mail merge, references, and table of contents",
            "Templates, review tools, and PDF export",
        ],
        "sort_order": 70,
    },
    {
        "title": "Microsoft Excel",
        "category": "software",
        "icon": "fa-solid fa-file-excel",
        "level": "Beginner to Advanced",
        "duration": "2 weeks",
        "description": (
            "Learn Microsoft Excel end-to-end — from entering data and basic formulas to building "
            "dashboards, pivot tables, and automation. The single most valuable office tool for "
            "data-driven work."
        ),
        "curriculum": [
            "Workbook, worksheets, and data entry",
            "Formatting, sorting, and filtering",
            "Formulas: SUM, IF, VLOOKUP, COUNTIF, SUMIF",
            "Charts and conditional formatting",
            "Pivot tables and pivot charts",
            "Data validation, protection, and dashboards",
            "Macros and automation basics",
        ],
        "sort_order": 80,
    },
    {
        "title": "Microsoft PowerPoint",
        "category": "software",
        "icon": "fa-solid fa-file-powerpoint",
        "level": "Beginner to Intermediate",
        "duration": "2 weeks",
        "description": (
            "Create compelling presentations with Microsoft PowerPoint — slides, transitions, "
            "animations, and professional design. Perfect for students, teachers, and business "
            "presenters."
        ),
        "curriculum": [
            "Slide master, layouts, and themes",
            "Text, shapes, and SmartArt",
            "Images, charts, and multimedia",
            "Transitions and animations",
            "Presenter tools and rehearsal",
            "Export to video and PDF",
        ],
        "sort_order": 90,
    },
    {
        "title": "Microsoft Access",
        "category": "software",
        "icon": "fa-solid fa-database",
        "level": "Intermediate to Advanced",
        "duration": "2 weeks",
        "description": (
            "Learn database design with Microsoft Access — tables, queries, forms, and reports. "
            "Build a working database application from scratch."
        ),
        "curriculum": [
            "Database concepts and table design",
            "Relationships and referential integrity",
            "Select, parameter, and action queries",
            "Forms for data entry and navigation",
            "Reports and grouping",
            "Macros and a simple navigation system",
        ],
        "sort_order": 100,
    },
    {
        "title": "Microsoft Word + Excel Combo",
        "category": "software",
        "icon": "fa-solid fa-file-lines",
        "level": "Beginner to Intermediate",
        "duration": "2 weeks",
        "description": (
            "Learn two Microsoft Office tools at once — Word and Excel. The ideal pair for office "
            "staff, administrators, and students who need documents and spreadsheets together."
        ),
        "curriculum": [
            "Word: formatting, styles, and professional documents",
            "Word: tables, images, and mail merge",
            "Excel: data entry, formulas, and formatting",
            "Excel: VLOOKUP, charts, and pivot tables",
            "Linking Excel data into Word documents",
            "Mini-project: report with embedded spreadsheet",
        ],
        "sort_order": 110,
    },
    {
        "title": "Microsoft Office Suite (All Tools)",
        "category": "software",
        "icon": "fa-solid fa-window-restore",
        "level": "Beginner to Advanced",
        "duration": "4 weeks",
        "description": (
            "Learn the full Microsoft Office Suite — Word, Excel, PowerPoint, Access, and Outlook. "
            "A complete office productivity programme for students, job-seekers, and professionals."
        ),
        "curriculum": [
            "Word: documents, mail merge, and templates",
            "Excel: formulas, pivot tables, and dashboards",
            "PowerPoint: design, animation, and delivery",
            "Access: databases, queries, and reports",
            "Outlook: email, calendar, and contacts",
            "Integration: linking Office tools together",
            "Capstone project across the full suite",
        ],
        "sort_order": 120,
    },
]

SERVICES = [
    {
        "title": "Web Design & Development",
        "icon": "fa-solid fa-code-branch",
        "description": (
            "Custom, fast, mobile-friendly websites and web apps built with Django "
            "and progressive web app technology — from design to deployment and support."
        ),
        "deliverables": [
            "Requirements & UX design",
            "Django backend + responsive frontend",
            "Deployment and staff training",
            "Ongoing maintenance & support",
        ],
        "sort_order": 10,
    },
    {
        "title": "Android & iOS App Development",
        "icon": "fa-solid fa-mobile-screen-button",
        "description": (
            "Native and cross-platform mobile applications for Android and iOS — "
            "from concept and wireframes to App Store / Play Store publishing."
        ),
        "deliverables": [
            "App design & prototyping",
            "Android + iOS development",
            "API integration & backend",
            "Store submission & updates",
        ],
        "sort_order": 20,
    },
    {
        "title": "Graphics Design",
        "icon": "fa-solid fa-pen-nib",
        "description": (
            "Logos, posters, flyers, social media kits, and brand identities — "
            "all kinds of graphics for events, business, and ministry."
        ),
        "deliverables": [
            "Logo & brand identity",
            "Posters, flyers & banners",
            "Social media graphics & kits",
            "Print-ready artwork",
        ],
        "sort_order": 30,
    },
    {
        "title": "Church Media & Training",
        "icon": "fa-solid fa-tower-broadcast",
        "description": (
            "End-to-end church media setup and hands-on training: livestreaming "
            "with OBS, lyric/projection with OpenLP, and audio post-production."
        ),
        "deliverables": [
            "OBS livestream configuration",
            "OpenLP projection setup",
            "Audio recording & editing workflow",
            "Operator training & runbooks",
        ],
        "sort_order": 40,
    },
    {
        "title": "Holiday Tutoring (Nursery–S6)",
        "icon": "fa-solid fa-user-graduate",
        "description": (
            "We connect students from Nursery to S6 with qualified holiday tutors "
            "online. Email us to book a tutor — classes happen over Google Meet."
        ),
        "deliverables": [
            "Match students to subject tutors",
            "Booked via email / WhatsApp",
            "Live Google Meet sessions",
            "Progress feedback for parents",
        ],
        "sort_order": 50,
    },
    {
        "title": "AI Optimization & Training",
        "icon": "fa-solid fa-robot",
        "description": (
            "Learn to use AI tools effectively — prompt engineering, AI-assisted "
            "productivity, and integrating AI into your work and business."
        ),
        "deliverables": [
            "Prompt engineering fundamentals",
            "AI tools for productivity",
            "AI for business workflows",
            "Hands-on guided practice",
        ],
        "sort_order": 60,
    },
    {
        "title": "ICT Infrastructure & Networking",
        "icon": "fa-solid fa-network-wired",
        "description": (
            "Local area networks, server setup, and workstation deployment for "
            "schools, offices, and small businesses — including cabling and Wi-Fi."
        ),
        "deliverables": [
            "Network design & cabling",
            "Server and router configuration",
            "Workstation setup & imaging",
            "Security hardening & documentation",
        ],
        "sort_order": 70,
    },
]

# Media gallery is intentionally empty for now — the user will add real
# portfolio items (posters, videos, screenshots) via the admin later.
MEDIA_ITEMS = [
    {
        "title": "Jordan Design Hub — Brand",
        "caption": "Software • Academy • Tutoring — Uganda's tech ecosystem.",
        "media_type": "image",
        "image": "gallery/brand-square.png",
        "sort_order": 10,
    },
    {
        "title": "School Management System",
        "caption": "Offline-first school platform — students, fees, marks, reports.",
        "media_type": "image",
        "image": "gallery/school-system-square.png",
        "sort_order": 20,
    },
    {
        "title": "Attendance Hub",
        "caption": "Church & event attendance — phone, web & desktop.",
        "media_type": "image",
        "image": "gallery/attendance-hub-square.png",
        "sort_order": 30,
    },
    {
        "title": "Microsoft Office Courses",
        "caption": "Word, Excel, PowerPoint, Access & Outlook — one tool or the full suite.",
        "media_type": "image",
        "image": "gallery/microsoft-office-square.png",
        "sort_order": 40,
    },
    {
        "title": "Excel Mastery",
        "caption": "From formulas to dashboards & automation.",
        "media_type": "image",
        "image": "gallery/microsoft-excel-square.png",
        "sort_order": 50,
    },
    {
        "title": "Coding & STEM for Kids",
        "caption": "Scratch, robotics & practical science — Uganda & Cambridge curricula.",
        "media_type": "image",
        "image": "gallery/coding-stem-square.png",
        "sort_order": 60,
    },
    {
        "title": "Holiday Tutoring Programme",
        "caption": "Learn. Build. Showcase. — with a certificate on completion.",
        "media_type": "image",
        "image": "gallery/holiday-tutoring-square.png",
        "sort_order": 70,
    },
    {
        "title": "Online Tutoring via Google Meet",
        "caption": "Learn from anywhere — MoMo / Airtel payment.",
        "media_type": "image",
        "image": "gallery/online-tutoring-square.png",
        "sort_order": 80,
    },
    {
        "title": "Graphic Design",
        "caption": "Canva & InShot — posters, logos & social media graphics.",
        "media_type": "image",
        "image": "gallery/design-square.png",
        "sort_order": 90,
    },
    {
        "title": "JD Hub Academy",
        "caption": "Coding • STEM • Microsoft Office • AI • Design.",
        "media_type": "image",
        "image": "gallery/academy-landscape.png",
        "sort_order": 100,
    },
]


class Command(BaseCommand):
    help = "Seed demo content (systems, courses, services, media) and generate PDF whitepapers."

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Seeding systems..."))
        for item in SYSTEMS:
            features = "\n".join(item.pop("features"))
            shots = item.pop("screenshots", [])
            screenshots = "\n".join(f"{p}|{c}" for p, c in shots)
            System.objects.update_or_create(
                title=item["title"], defaults={**item, "features": features, "screenshots": screenshots}
            )

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding courses..."))
        for item in COURSES:
            curriculum = "\n".join(item.pop("curriculum"))
            Course.objects.update_or_create(
                title=item["title"], defaults={**item, "curriculum": curriculum}
            )
        # Remove courses no longer in the seed list (stale placeholders).
        kept_course_titles = [c["title"] for c in COURSES]
        deleted_courses, _ = Course.objects.exclude(
            title__in=kept_course_titles
        ).delete()
        if deleted_courses:
            self.stdout.write(f"  ↻ Removed {deleted_courses} stale course(s).")

        self.stdout.write(self.style.MIGRATE_HEADING("Seeding services..."))
        for item in SERVICES:
            deliverables = "\n".join(item.pop("deliverables"))
            Service.objects.update_or_create(
                title=item["title"], defaults={**item, "deliverables": deliverables}
            )
        # Remove services no longer in the seed list (stale placeholders).
        kept_service_titles = [s["title"] for s in SERVICES]
        deleted_services, _ = Service.objects.exclude(
            title__in=kept_service_titles
        ).delete()
        if deleted_services:
            self.stdout.write(f"  ↻ Removed {deleted_services} stale service(s).")

        self.stdout.write(self.style.MIGRATE_HEADING("Syncing media portfolio..."))
        if MEDIA_ITEMS:
            for item in MEDIA_ITEMS:
                MediaItem.objects.update_or_create(
                    title=item["title"], defaults=item
                )
        # Remove placeholder media (no real uploads yet). Items without an
        # uploaded image file are considered placeholders and are deleted so
        # the gallery stays clean until the user adds real work via the admin.
        deleted_media, _ = MediaItem.objects.filter(image__isnull=True).exclude(
            title__in=[m["title"] for m in MEDIA_ITEMS]
        ).delete()
        if deleted_media:
            self.stdout.write(f"  ↻ Removed {deleted_media} placeholder media item(s).")

        self.stdout.write(self.style.MIGRATE_HEADING("Updating site settings..."))
        site = SiteSettings.get()
        # Refresh intro copy + contact info to the current defaults if they are
        # still on a known placeholder value from an earlier seed run.
        if site.whatsapp_number in {"", "256700000000"}:
            site.whatsapp_number = "256754687597"
        if site.contact_email in {"", "info@jdhub.example"}:
            site.contact_email = "jordandesignhub@gmail.com"
        if site.hero_subtitle in {"", "We design, build, and deploy offline-first "
                "software systems, run a practical skills academy, and deliver ICT "
                "consultancy — serving schools, SACCOs, and institutions across Uganda."}:
            site.hero_subtitle = (
                "We build web & mobile apps (Android and iOS), run a paid online "
                "academy on Google Meet, deliver church media training, connect "
                "holiday tutors to students (Nursery–S6), design graphics, and "
                "teach AI optimization — across Uganda and beyond."
            )
        if site.academy_intro in {"", "Practical, hands-on courses for adult "
                "learners and students."}:
            site.academy_intro = (
                "Paid, instructor-led online classes on Google Meet. Enrol and pay, "
                "then join live sessions for students (Nursery–S6) and adult learners."
            )
        site.save()

        self.stdout.write(self.style.MIGRATE_HEADING("Generating PDF whitepapers..."))
        for system in System.objects.all():
            path = build_pdf(system)
            self.stdout.write(f"  ✓ {system.title} → {path.name}")

        self.stdout.write(self.style.SUCCESS("Seed complete."))
