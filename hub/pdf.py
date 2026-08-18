"""
Auto-generate PDF whitepapers for flagship systems using ReportLab.

Each system gets a branded, multi-section document covering features, architecture,
offline-sync strategy, and database capabilities. PDFs are cached under
``media/system_docs/`` and regenerated on demand.
"""
from __future__ import annotations

from pathlib import Path

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import KeepTogether

from hub.models import System

# Brand palette (kept in sync with the site CSS).
BRAND_PRIMARY = colors.HexColor("#0d6efd")
BRAND_DARK = colors.HexColor("#0b1f3a")
BRAND_ACCENT = colors.HexColor("#14b8a6")
BRAND_LIGHT = colors.HexColor("#f5f7fb")
BRAND_MUTED = colors.HexColor("#5b6b7b")


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=24, leading=28, textColor=BRAND_DARK, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=12, leading=16, textColor=BRAND_MUTED, spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, leading=18, textColor=BRAND_PRIMARY,
            spaceBefore=14, spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=BRAND_DARK, spaceAfter=6,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=BRAND_DARK,
            leftIndent=14, bulletIndent=2, spaceAfter=2,
        ),
        "footer": ParagraphStyle(
            "Footer", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=8, leading=10, textColor=BRAND_MUTED,
        ),
        "meta_label": ParagraphStyle(
            "MetaLabel", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=9, leading=12, textColor=BRAND_MUTED,
        ),
        "meta_value": ParagraphStyle(
            "MetaValue", parent=base["Normal"], fontName="Helvetica",
            fontSize=9, leading=12, textColor=BRAND_DARK,
        ),
    }


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    # Header band.
    canvas.setFillColor(BRAND_DARK)
    canvas.rect(0, height - 18 * mm, width, 18 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(20 * mm, height - 11 * mm, "JD HUB")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(BRAND_ACCENT)
    canvas.drawRightString(width - 20 * mm, height - 11 * mm, "Jordan Design Hub")
    # Footer.
    canvas.setStrokeColor(BRAND_MUTED)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 14 * mm, width - 20 * mm, 14 * mm)
    canvas.setFillColor(BRAND_MUTED)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawString(20 * mm, 9 * mm, "Confidential — Technical Whitepaper")
    canvas.drawRightString(width - 20 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _bullets(items: list[str], style) -> list:
    return [Paragraph(f"• {item}", style) for item in items]


def _meta_table(system: System, s: dict) -> Table:
    data = [
        [Paragraph("CATEGORY", s["meta_label"]), Paragraph(system.get_category_display().title(), s["meta_value"])],
        [Paragraph("TECH STACK", s["meta_label"]), Paragraph(", ".join(system.tech_list) or "—", s["meta_value"])],
        [Paragraph("DOCUMENT", s["meta_label"]), Paragraph("Technical Whitepaper v1.0", s["meta_value"])],
    ]
    t = Table(data, colWidths=[35 * mm, 120 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_LIGHT),
        ("BOX", (0, 0), (-1, -1), 0.5, BRAND_MUTED),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def build_pdf(system: System, output_path: Path | None = None) -> Path:
    """Render a whitepaper PDF for the given system and return its path."""
    out_dir = Path(settings.MEDIA_ROOT) / "system_docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_path or (out_dir / f"{system.slug}.pdf")

    s = _styles()
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=24 * mm,
        bottomMargin=18 * mm,
        title=f"{system.title} — Technical Whitepaper",
        author=settings.SITE_OWNER,
        subject="Technical whitepaper",
    )

    story: list = []
    # Title block.
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(system.title, s["title"]))
    story.append(Paragraph(system.tagline, s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND_PRIMARY, spaceAfter=10))
    story.append(_meta_table(system, s))
    story.append(Spacer(1, 6 * mm))

    # Overview.
    story.append(Paragraph("1. Overview", s["h2"]))
    story.append(Paragraph(system.description, s["body"]))

    # Features.
    if system.feature_list:
        story.append(Paragraph("2. Key Features", s["h2"]))
        story.extend(_bullets(system.feature_list, s["bullet"]))

    # Architecture (generic, tailored per category).
    story.append(Paragraph("3. System Architecture", s["h2"]))
    story.append(Paragraph(_architecture_text(system), s["body"]))

    # Offline sync.
    story.append(Paragraph("4. Offline-First & Sync Strategy", s["h2"]))
    story.append(Paragraph(_offline_text(system), s["body"]))

    # Database capabilities.
    story.append(Paragraph("5. Database Capabilities", s["h2"]))
    story.append(Paragraph(_database_text(system), s["body"]))

    # Security & deployment.
    story.append(Paragraph("6. Security & Deployment", s["h2"]))
    story.extend(_bullets(_security_points(system), s["bullet"]))

    # Call to action.
    story.append(Spacer(1, 8 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_MUTED, spaceAfter=8))
    story.append(Paragraph(
        f"For a live demonstration, deployment, or customisation, contact {settings.SITE_OWNER} "
        f"via the Jordan Design Hub website or WhatsApp (+{getattr(settings, 'WHATSAPP_NUMBER', '')}).",
        s["footer"],
    ))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return out_path


# --- Section copy helpers (tailored by system category) ---------------------
def _architecture_text(system: System) -> str:
    base = (
        f"<b>{system.title}</b> is built on a layered Django architecture: a presentation tier "
        "(server-rendered Bootstrap 5 templates + a progressive web app shell), an application tier "
        "(Django views, class-based business logic, and REST endpoints), and a data tier "
        f"({', '.join(system.tech_list) or 'Django ORM + SQLite/PostgreSQL'}). "
    )
    extras = {
        "education": (
            "The school system exposes role-based dashboards for administrators, teachers, students, "
            "and parents, with a service worker caching the app shell and key pages for offline use."
        ),
        "finance": (
            "The SACCO system isolates financial transactions into a double-entry ledger module with "
            "audit trails, portfolio-quality analytics, and batch loan-repayment processing."
        ),
        "database": (
            "The DBMS layer normalises academic records (students, enrolment, grading, transcripts) "
            "with referential integrity, indexed lookups, and scheduled backups."
        ),
        "custom": (
            "Modules are isolated as Django apps with clear interfaces, enabling independent testing "
            "and future microservice extraction where scale demands."
        ),
    }
    return base + extras.get(system.category, extras["custom"])


def _offline_text(system: System) -> str:
    if system.category == "education":
        return (
            "A service worker precaches the app shell, navigation routes, and core assets, so the "
            "system remains usable in areas with intermittent connectivity. Mutations made offline "
            "(attendance, fee entries, assessments) are queued in IndexedDB and synchronised via a "
            "background sync queue when connectivity returns, with conflict resolution by "
            "last-writer-wins plus server-side audit timestamps."
        )
    if system.category == "finance":
        return (
            "Field officers capture member transactions offline on PWA-enabled devices; entries are "
            "stored locally with a cryptographic checksum and pushed to the central ledger on reconnect. "
            "Reconciliation reports flag duplicate or out-of-order syncs for manual review."
        )
    return (
        "The PWA shell is cached for offline access, and a background-sync queue replays pending writes "
        "when the network is restored. Read-heavy pages are served from cache with a network-first "
        "strategy to keep content fresh while remaining resilient to outages."
    )


def _database_text(system: System) -> str:
    tech = ", ".join(system.tech_list) or "Django ORM, SQLite/PostgreSQL"
    generic = (
        f"The data tier uses the Django ORM over {tech}, with normalised schemas, foreign-key "
        "constraints, and database-level validation. Indexed columns accelerate common lookups, and "
        "soft-deletion preserves an auditable history. Backups are automated and exportable to CSV/Excel."
    )
    extras = {
        "finance": " Transactions follow double-entry bookkeeping with immutable audit logs.",
        "education": " Per-term snapshots enable longitudinal performance analytics across cohorts.",
        "database": " Schemas are versioned via Django migrations for safe, reversible evolution.",
    }
    return generic + extras.get(system.category, "")


def _security_points(system: System) -> list[str]:
    base = [
        "Role-based access control enforced at view and template level.",
        "CSRF protection, secure cookies, and HSTS in production.",
        "Parameterised queries via the ORM to prevent SQL injection.",
        "Automated daily database backups with offsite replication.",
        "Centralised logging and activity audit trails.",
    ]
    if system.category == "finance":
        base.append("PCI-aware handling of member data; no raw card storage on the server.")
    return base
