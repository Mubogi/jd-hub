"""
Generate branded marketing / advert images for Jordan Design Hub.

Produces share-ready graphics in standard social-media sizes:
- Square 1080×1080 (Instagram / Facebook post)
- Portrait 1080×1920 (Instagram / Facebook / WhatsApp story)
- Landscape 1200×630 (Facebook / LinkedIn / Twitter link preview)
- Wide 1500×500 (website hero / banner)

All images use the JD red + gold on white brand theme and are saved under
``static/hub/img/marketing/`` so they can be used on the website and shared
directly to social platforms.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Brand palette.
RED = (200, 16, 46)        # #C8102E
RED_DARK = (139, 0, 0)    # #8B0000
GOLD = (212, 175, 55)      # #D4AF37
GOLD_DARK = (155, 123, 46)  # #9B7B2E
WHITE = (255, 255, 255)
OFF_WHITE = (251, 247, 240)  # #FBF7F0
DARK = (26, 26, 26)
MUTED = (91, 107, 123)

STATIC_DIR = Path(__file__).resolve().parent.parent / "static" / "hub" / "img" / "marketing"

SIZES = {
    "square": (1080, 1080),
    "story": (1080, 1920),
    "landscape": (1200, 630),
    "banner": (1500, 500),
}


def _font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    """Load a font, falling back to default if none available."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, IOError):
            continue
    return ImageFont.load_default()


def _text_size(draw, text, font) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def _centered(draw, text, font, y, width, fill):
    w, _ = _text_size(draw, text, font)
    x = (width - w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return w


def _draw_gold_rule(draw, x1, x2, y, thickness=4):
    draw.rectangle([x1, y, x2, y + thickness], fill=GOLD)


def _draw_logo_badge(draw, cx, cy, radius):
    """Draw the JD Hub circular red-and-gold logo badge."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=RED, outline=GOLD, width=max(3, radius // 12))
    font = _font(max(16, radius // 2), bold=True)
    tw, th = _text_size(draw, "JD", font)
    draw.text((cx - tw // 2, cy - th // 2 - 2), "JD", font=font, fill=WHITE)


def _footer(draw, width, height, tagline=True):
    """Draw a gold rule + contact footer."""
    _draw_gold_rule(draw, 40, width - 40, height - 90, 3)
    font = _font(20, bold=False)
    draw.text((40, height - 70), "Jordan Design Hub", font=_font(22, bold=True), fill=RED_DARK)
    if tagline:
        draw.text((40, height - 42), "jordandesignhub@gmail.com  •  +256 754 687 597  •  jd-hub-8e5d.onrender.com",
                  font=font, fill=MUTED)


def generate_advert(
    name: str,
    size_key: str,
    headline: str,
    subheadline: str,
    bullets: list[str] | None = None,
    cta: str = "Enrol Now",
    accent: str = "red",
    logo: bool = True,
) -> Path:
    """Generate a single advert image and return its path."""
    width, height = SIZES[size_key]
    STATIC_DIR.mkdir(parents=True, exist_ok=True)

    img = Image.new("RGB", (width, height), OFF_WHITE)
    draw = ImageDraw.Draw(img)

    # Top accent bar.
    draw.rectangle([0, 0, width, 14], fill=RED)
    draw.rectangle([0, 14, width, 20], fill=GOLD)
    # Bottom accent bar.
    draw.rectangle([0, height - 14, width, height], fill=RED)
    draw.rectangle([0, height - 20, width, height - 14], fill=GOLD)

    # Logo.
    if logo:
        badge_r = 60 if size_key != "banner" else 40
        _draw_logo_badge(draw, width // 2, 110 if size_key != "banner" else 70, badge_r)

    # Determine scaling of font sizes by height.
    scale = height / 1080 if size_key in ("square", "story") else 0.6
    title_size = int(64 * scale) if size_key != "banner" else 44
    sub_size = int(30 * scale) if size_key != "banner" else 22
    bullet_size = int(26 * scale) if size_key != "banner" else 18

    # Headline.
    y = 200 if size_key == "square" else (260 if size_key == "story" else (90 if size_key == "banner" else 140))
    title_font = _font(title_size, bold=True)
    sub_font = _font(sub_size, bold=False)
    # Wrap headline across two lines if long.
    if len(headline) > 28 and size_key != "banner":
        mid = len(headline) // 2
        for split in (headline.rfind(" ", 0, mid), headline.find(" ", mid)):
            if split > 0:
                _centered(draw, headline[:split].strip(), title_font, y, width, RED_DARK)
                y += int(title_size * 1.15)
                _centered(draw, headline[split:].strip(), title_font, y, width, RED_DARK)
                y += int(title_size * 1.4)
                break
        else:
            _centered(draw, headline, title_font, y, width, RED_DARK)
            y += int(title_size * 1.4)
    else:
        _centered(draw, headline, title_font, y, width, RED_DARK)
        y += int(title_size * 1.4)

    # Gold rule under headline.
    _draw_gold_rule(draw, width // 2 - 120, width // 2 + 120, y, 3)
    y += 24

    # Subheadline.
    sub_color = GOLD_DARK
    _centered(draw, subheadline, sub_font, y, width, sub_color)
    y += int(sub_size * 1.8)

    # Bullets.
    if bullets:
        bf = _font(bullet_size, bold=True)
        for b in bullets:
            bw, _ = _text_size(draw, "✦  " + b, bf)
            x = (width - bw) // 2
            draw.text((x, y), "✦", font=bf, fill=GOLD)
            draw.text((x + int(bullet_size * 0.9), y), b, font=bf, fill=DARK)
            y += int(bullet_size * 1.8)

    # CTA button.
    if cta:
        cta_font = _font(int(34 * scale) if size_key != "banner" else 24, bold=True)
        ctaw, ctah = _text_size(draw, cta, cta_font)
        bx = (width - ctaw - 80) // 2
        by = y + 20 if size_key != "banner" else height - 80
        draw.rounded_rectangle([bx, by, bx + ctaw + 80, by + ctah + 30], radius=30, fill=RED, outline=GOLD, width=3)
        draw.text((bx + 40, by + 15), cta, font=cta_font, fill=WHITE)

    # Footer (except banner — too short).
    if size_key != "banner":
        _footer(draw, width, height)
    else:
        draw.text((width - 360, height - 44), "jd-hub-8e5d.onrender.com", font=_font(20, bold=False), fill=MUTED)

    out_path = STATIC_DIR / f"{name}.png"
    img.save(out_path, "PNG", optimize=True)
    return out_path


def generate_all() -> list[Path]:
    """Generate the full marketing set for website + social media."""
    paths: list[Path] = []

    # 1. Whole-website / brand advert (square + story + landscape).
    paths.append(generate_advert(
        "brand-square", "square",
        "Jordan Design Hub",
        "Software • Academy • Tutoring — Uganda's tech ecosystem",
        bullets=[
            "Flagship school & finance systems",
            "Coding, STEM & Microsoft Office courses",
            "Holiday tutoring & online Google Meet classes",
        ],
        cta="Visit jd-hub-8e5d.onrender.com",
    ))
    paths.append(generate_advert(
        "brand-story", "story",
        "Jordan Design Hub",
        "Software • Academy • Tutoring",
        bullets=[
            "Offline-first systems for schools & SACCOs",
            "Coding, STEM, AI & Microsoft Office",
            "Holiday tutoring + online Google Meet",
        ],
        cta="Enrol Today",
    ))
    paths.append(generate_advert(
        "brand-landscape", "landscape",
        "Jordan Design Hub — Uganda's Tech Ecosystem",
        "Software systems • Academy • Tutoring • Consultancy",
        cta="Explore our programmes",
    ))
    paths.append(generate_advert(
        "brand-banner", "banner",
        "Jordan Design Hub — Software, Academy & Tutoring",
        "Offline-first systems • Coding • STEM • Microsoft Office • Holiday Tutoring",
        cta="",
        logo=True,
    ))

    # 2. School Management System.
    paths.append(generate_advert(
        "school-system-square", "square",
        "School Management System",
        "Offline-first. Works without internet.",
        bullets=[
            "Students, fees, marks & report cards",
            "WhatsApp + email notifications — free",
            "QR parent kiosk & hybrid backup",
        ],
        cta="Request a Demo",
    ))

    # 3. Attendance Hub.
    paths.append(generate_advert(
        "attendance-hub-square", "square",
        "Attendance Hub",
        "Church & event attendance — phone, web & desktop",
        bullets=[
            "One-tap check-in, no internet needed",
            "Wi-Fi device linking across phones",
            "Excel, CSV & PDF report exports",
        ],
        cta="Get the App",
    ))

    # 4. Microsoft Office courses.
    paths.append(generate_advert(
        "microsoft-office-square", "square",
        "Learn Microsoft Office",
        "Word • Excel • PowerPoint • Access • Outlook",
        bullets=[
            "Pick one tool, two, or the full suite",
            "Beginner, Intermediate & Advanced tracks",
            "2-week intensives + holiday tutoring",
        ],
        cta="Enrol — 2 Weeks",
    ))
    paths.append(generate_advert(
        "microsoft-excel-square", "square",
        "Microsoft Excel Mastery",
        "From formulas to dashboards & automation",
        bullets=[
            "VLOOKUP, pivot tables, charts",
            "Data validation & dashboards",
            "Macros & automation basics",
        ],
        cta="Enrol Now",
    ))

    # 5. Coding & STEM (kids).
    paths.append(generate_advert(
        "coding-stem-square", "square",
        "Coding & STEM for Kids",
        "Scratch, robotics & practical science",
        bullets=[
            "Uganda & Cambridge curricula",
            "Ages 8+ — animations, games, robots",
            "Beginner to Intermediate",
        ],
        cta="Enrol Your Child",
    ))

    # 6. Holiday tutoring.
    paths.append(generate_advert(
        "holiday-tutoring-square", "square",
        "Holiday Tutoring Programme",
        "Learn. Build. Showcase.",
        bullets=[
            "Coding, STEM, Office & design",
            "Relaxed daily sessions + fun activities",
            "End-of-holiday showcase + certificate",
        ],
        cta="Book the Holiday Slot",
    ))
    paths.append(generate_advert(
        "holiday-tutoring-story", "story",
        "Holiday Tutoring",
        "Learn. Build. Showcase.",
        bullets=[
            "Coding & Microsoft Office",
            "STEM & graphic design",
            "Certificate on completion",
        ],
        cta="Enrol for the Holiday",
    ))

    # 7. Online Google Meet tutoring.
    paths.append(generate_advert(
        "online-tutoring-square", "square",
        "Online Tutoring via Google Meet",
        "Learn from anywhere in Uganda",
        bullets=[
            "Auto-generated Google Meet links",
            "1-on-1 & small group sessions",
            "MoMo / Airtel Money payment",
        ],
        cta="Book an Online Class",
    ))

    # 8. Academy general.
    paths.append(generate_advert(
        "academy-landscape", "landscape",
        "JD Hub Academy & Tutoring",
        "Coding • STEM • Microsoft Office • AI • Design",
        cta="Enrol Today",
    ))

    # 9. Graphic design.
    paths.append(generate_advert(
        "design-square", "square",
        "Graphic Design",
        "Canva & InShot for creators",
        bullets=[
            "Posters, logos & social media graphics",
            "Video editing for YouTube & TikTok",
            "Beginner-friendly, 2 weeks",
        ],
        cta="Start Designing",
    ))

    return paths


if __name__ == "__main__":
    for p in generate_all():
        print(f"  ✓ {p.name}")
    print(f"Generated {len(generate_all.__wrapped__ if hasattr(generate_all, '__wrapped__') else [])} images")
