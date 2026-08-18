"""
Generate lesson-outline PDFs for academy courses.

A lesson PDF expands a course's curriculum into a structured, week-by-week plan
covering one of four tracks:

* ``beginner``   — a 2-week beginner intensive
* ``intermediate`` — a 2-week intermediate track
* ``advanced``   — a 2-week advanced track
* ``holiday``    — a holiday tutoring programme (revised pacing)

Each track re-uses the course curriculum list and splits it across two weeks,
with daily learning objectives, activities, and a weekly mini-project.
PDFs are cached under ``media/lesson_docs/``.
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

from hub.models import Course

# Brand palette — red + gold on white.
BRAND_PRIMARY = colors.HexColor("#C8102E")
BRAND_DARK = colors.HexColor("#8B0000")
BRAND_ACCENT = colors.HexColor("#D4AF37")
BRAND_LIGHT = colors.HexColor("#FBF7F0")
BRAND_MUTED = colors.HexColor("#5b6b7b")
BRAND_GOLD_DARK = colors.HexColor("#9B7B2E")

TRACKS = {
    "beginner": {
        "label": "2-Week Beginner Intensive",
        "blurb": (
            "This beginner track introduces the fundamentals over two focused weeks. "
            "No prior experience required — just a willingness to learn and practise daily."
        ),
        "weeks": 2,
        "days_per_week": 5,
    },
    "intermediate": {
        "label": "2-Week Intermediate Track",
        "blurb": (
            "For learners who already grasp the basics. This track deepens core skills and "
            "introduces professional workflows and real-world projects."
        ),
        "weeks": 2,
        "days_per_week": 5,
    },
    "advanced": {
        "label": "2-Week Advanced Track",
        "blurb": (
            "An advanced, project-driven track for confident learners. Focus is on mastery, "
            "automation, and portfolio-quality deliverables."
        ),
        "weeks": 2,
        "days_per_week": 5,
    },
    "holiday": {
        "label": "Holiday Tutoring Programme",
        "blurb": (
            "A relaxed holiday programme for students — shorter daily sessions with hands-on "
            "activities, games, and a showcase at the end of the holiday."
        ),
        "weeks": 2,
        "days_per_week": 4,
    },
}

# Track-specific framing prefixes for daily objectives.
DAY_PREFIX = {
    "beginner": "Understand and demonstrate",
    "intermediate": "Apply and extend",
    "advanced": "Master, optimise, and build",
    "holiday": "Explore and have fun with",
}

PROJECT_THEMES = {
    "beginner": ["a guided starter exercise", "a first complete mini-project"],
    "intermediate": ["a guided practice build", "a real-world mini-project"],
    "advanced": ["an optimisation challenge", "a portfolio-grade capstone project"],
    "holiday": ["a fun creative activity", "a holiday showcase piece"],
}


def _styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=22, leading=26, textColor=BRAND_DARK, spaceAfter=4,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Normal"], fontName="Helvetica",
            fontSize=12, leading=16, textColor=BRAND_GOLD_DARK, spaceAfter=8,
        ),
        "track": ParagraphStyle(
            "Track", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=13, leading=17, textColor=colors.white, spaceAfter=0,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, leading=18, textColor=BRAND_PRIMARY,
            spaceBefore=12, spaceAfter=6,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontName="Helvetica-Bold",
            fontSize=11.5, leading=15, textColor=BRAND_DARK,
            spaceBefore=8, spaceAfter=4,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=colors.HexColor("#1a1a1a"), spaceAfter=5,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor=colors.HexColor("#1a1a1a"),
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
        "callout": ParagraphStyle(
            "Callout", parent=base["Normal"], fontName="Helvetica-Oblique",
            fontSize=10, leading=14, textColor=BRAND_GOLD_DARK, spaceAfter=6,
        ),
    }


def _header_footer(canvas, doc):
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(BRAND_PRIMARY)
    canvas.rect(0, height - 18 * mm, width, 18 * mm, fill=1, stroke=0)
    canvas.setFillColor(colors.white)
    canvas.setFont("Helvetica-Bold", 12)
    canvas.drawString(20 * mm, height - 11 * mm, "JD HUB")
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(BRAND_ACCENT)
    canvas.drawRightString(width - 20 * mm, height - 11 * mm, "Academy & Tutoring Hub")
    canvas.setStrokeColor(BRAND_ACCENT)
    canvas.setLineWidth(1.2)
    canvas.line(0, height - 18 * mm, width, height - 18 * mm)
    canvas.setStrokeColor(BRAND_MUTED)
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 14 * mm, width - 20 * mm, 14 * mm)
    canvas.setFillColor(BRAND_MUTED)
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.drawString(20 * mm, 9 * mm, "Jordan Design Hub — Lesson Outline")
    canvas.drawRightString(width - 20 * mm, 9 * mm, f"Page {doc.page}")
    canvas.restoreState()


def _bullets(items, style):
    return [Paragraph(f"• {item}", style) for item in items]


def _track_banner(track_key: str, s: dict) -> Table:
    meta = TRACKS[track_key]
    t = Table([[Paragraph(meta["label"], s["track"])]], colWidths=[A4[0] - 40 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), BRAND_PRIMARY),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _meta_table(course: Course, track_key: str, s: dict) -> Table:
    meta = TRACKS[track_key]
    data = [
        [Paragraph("COURSE", s["meta_label"]), Paragraph(course.title, s["meta_value"])],
        [Paragraph("LEVEL", s["meta_label"]), Paragraph(course.level or meta["label"], s["meta_value"])],
        [Paragraph("DURATION", s["meta_label"]),
         Paragraph(f"{meta['weeks']} weeks × {meta['days_per_week']} days", s["meta_value"])],
        [Paragraph("TRACK", s["meta_label"]), Paragraph(meta["label"], s["meta_value"])],
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


def _week_block(course: Course, track_key: str, week_num: int, s: dict) -> list:
    """Build flowables for one week: daily objectives + a mini-project."""
    meta = TRACKS[track_key]
    days = meta["days_per_week"]
    curriculum = course.curriculum_list
    prefix = DAY_PREFIX[track_key]

    # Distribute curriculum topics across the two weeks.
    topics_for_week = _topics_for_week(curriculum, week_num, meta["weeks"], days)

    block: list = [Paragraph(f"Week {week_num}", s["h2"])]
    block.append(Paragraph(f"<b>Daily sessions (Days 1–{days})</b>", s["body"]))
    for day in range(1, days + 1):
        topic = topics_for_week[day - 1] if day - 1 < len(topics_for_week) else "Practical review & exercises"
        block.append(Paragraph(f"<b>Day {day}:</b> {prefix} {topic.lower()}.", s["body"]))
    block.append(Spacer(1, 3 * mm))
    project = PROJECT_THEMES[track_key][min(week_num - 1, 1)]
    block.append(Paragraph(f"End-of-week mini-project: {project}.", s["callout"]))
    block.append(Spacer(1, 2 * mm))
    return block


def _topics_for_week(curriculum: list, week_num: int, total_weeks: int, days: int) -> list:
    """Split the curriculum list across weeks and pad/rotate to fill the days."""
    if not curriculum:
        curriculum = ["Core concepts and fundamentals", "Guided practice",
                      "Independent exercises", "Review and Q&A", "Mini-project work"]
    per_week = max(1, len(curriculum) // total_weeks)
    start = (week_num - 1) * per_week
    slice_ = curriculum[start:start + per_week] if total_weeks > 1 else curriculum
    # For the final week, include any remainder.
    if week_num == total_weeks:
        slice_ = curriculum[start:]
    # Pad to fill the days.
    padded = list(slice_)
    idx = 0
    while len(padded) < days:
        padded.append(slice_[idx % len(slice_)] if slice_ else "Practical review")
        idx += 1
    return padded[:days]


def build_lesson_pdf(course: Course, track_key: str, output_path: Path | None = None) -> Path:
    """Render a lesson-outline PDF for a course + track and return its path."""
    if track_key not in TRACKS:
        raise ValueError(f"Unknown track: {track_key}")

    out_dir = Path(settings.MEDIA_ROOT) / "lesson_docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_path or (out_dir / f"{course.slug}-{track_key}.pdf")

    meta = TRACKS[track_key]
    s = _styles()
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=24 * mm,
        bottomMargin=18 * mm,
        title=f"{course.title} — {meta['label']}",
        author=settings.SITE_OWNER,
        subject="Lesson outline",
    )

    story: list = []
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(course.title, s["title"]))
    story.append(Paragraph(meta["label"], s["subtitle"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=BRAND_PRIMARY, spaceAfter=8))
    story.append(_track_banner(track_key, s))
    story.append(Spacer(1, 4 * mm))
    story.append(_meta_table(course, track_key, s))
    story.append(Spacer(1, 4 * mm))

    # Programme overview.
    story.append(Paragraph("Programme Overview", s["h2"]))
    story.append(Paragraph(meta["blurb"], s["body"]))
    if course.description:
        story.append(Paragraph(course.description, s["body"]))

    # Learning objectives.
    if course.curriculum_list:
        story.append(Paragraph("Learning Objectives", s["h2"]))
        story.extend(_bullets(course.curriculum_list, s["bullet"]))

    # Weekly breakdown.
    story.append(Paragraph("Weekly Breakdown", s["h2"]))
    for week in range(1, meta["weeks"] + 1):
        story.extend(_week_block(course, track_key, week, s))

    # Materials & expectations.
    story.append(Paragraph("What You'll Need", s["h2"]))
    story.extend(_bullets([
        "A laptop or desktop computer (or a phone for Scratch / mobile tracks).",
        "Notebook and pen for taking notes.",
        "Enthusiasm and a commitment to attend every session.",
    ], s["bullet"]))

    # Assessment & certificate.
    story.append(Paragraph("Assessment & Certification", s["h2"]))
    story.append(Paragraph(
        "Learners complete weekly mini-projects and a final showcase. On successful completion, "
        "each learner receives a Jordan Design Hub certificate of achievement.",
        s["body"],
    ))

    # Call to action.
    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=BRAND_MUTED, spaceAfter=8))
    story.append(Paragraph(
        f"Enrol on the Jordan Design Hub website or WhatsApp (+{getattr(settings, 'WHATSAPP_NUMBER', '')}). "
        "We'll confirm your slot and share payment details by MoMo or Airtel Money.",
        s["footer"],
    ))

    doc.build(story, onFirstPage=_header_footer, onLaterPages=_header_footer)
    return out_path
