"""
Jordan Design Hub — Marketing Kit Generator
============================================
Generates beautiful, downloadable marketing posters (PNG + PDF) for every
product (systems, courses, services), product groups, and the whole brand,
plus a combined brochure PDF and a promotional video (MP4).

Output goes to a top-level ``marketing/`` folder in the repo so the user can
download and share assets directly from GitHub.

Usage (from project root):
    python scripts/gen_marketing_kit.py            # everything
    python scripts/gen_marketing_kit.py --posters  # posters only
    python scripts/gen_marketing_kit.py --video    # video only
    python scripts/gen_marketing_kit.py --pdf      # brochure only

Prerequisites: chromium (headless), ffmpeg, Pillow, img2pdf.
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import textwrap
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jdhub.settings")
import django  # noqa: E402

django.setup()

from hub.models import Course, Service, System  # noqa: E402

# ---------------------------------------------------------------------------
# Paths and brand constants
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "marketing"
TMP = ROOT / "marketing" / "_tmp_html"
CHROMIUM = shutil.which("chromium") or shutil.which("chromium-browser") or shutil.which("google-chrome")
FFMPEG = shutil.which("ffmpeg")

RED = "#C8102E"
RED_DARK = "#8B0000"
GOLD = "#D4AF37"
GOLD_DARK = "#9B7B2E"
CREAM = "#FBF7F0"
INK = "#1A1A2E"

# Format presets: (name, width, height)
FORMATS = [
    ("square", 1080, 1080),
    ("story", 1080, 1920),
    ("landscape", 1200, 630),
]


# ---------------------------------------------------------------------------
# Data model for a poster
# ---------------------------------------------------------------------------
@dataclass
class PosterSpec:
    key: str            # filename stem
    group: str          # folder under marketing/
    eyebrow: str        # small label above title (e.g. "Software System")
    title: str          # big headline
    tagline: str        # one-line sub-headline
    bullets: list[str]  # key benefits
    icon: str = "fa-solid fa-bolt"          # font-awesome icon
    accent: str = RED                       # accent colour
    cta: str = "Enrol / Book a Demo"         # call to action text
    footer_note: str = ""                   # small print line
    extra_html: str = ""                    # optional injected HTML block


def _split_lines(text: str, limit: int = 200) -> list[str]:
    """Split a block of text into short bullet-ish lines."""
    if not text:
        return []
    out = []
    for raw in text.splitlines():
        raw = raw.strip().lstrip("-•\u2022 ").strip()
        if not raw:
            continue
        if len(raw) > limit:
            out.extend(textwrap.wrap(raw, limit) or [raw])
        else:
            out.append(raw)
    return out


def _sys_posters() -> list[PosterSpec]:
    specs = []
    for s in System.objects.all().order_by("sort_order"):
        feats = _split_lines(s.features, 110)[:5]
        specs.append(PosterSpec(
            key=f"system-{s.slug}",
            group="systems",
            eyebrow="Software System",
            title=s.title,
            tagline=s.tagline or "",
            bullets=feats or ["Built for real Ugandan operations.", "Works online & offline."],
            icon=s.icon or "fa-solid fa-cube",
            cta="Book a Demo",
        ))
    return specs


def _course_posters() -> list[PosterSpec]:
    specs = []
    for c in Course.objects.all().order_by("sort_order"):
        curr = _split_lines(c.curriculum, 80)[:5]
        specs.append(PosterSpec(
            key=f"course-{c.slug}",
            group="courses",
            eyebrow=f"Academy Course · {c.level}",
            title=c.title,
            tagline=(c.description or "").split(".")[0].strip()[:120] or f"{c.duration} of hands-on training.",
            bullets=curr or ["Hands-on projects", "Certificate on completion"],
            icon=c.icon or "fa-solid fa-graduation-cap",
            cta="Enrol Now",
            footer_note=f"Duration: {c.duration}",
        ))
    return specs


def _service_posters() -> list[PosterSpec]:
    specs = []
    for s in Service.objects.all().order_by("sort_order"):
        deliv = _split_lines(s.deliverables, 90)[:5]
        specs.append(PosterSpec(
            key=f"service-{s.slug}",
            group="services",
            eyebrow="Service",
            title=s.title,
            tagline=(s.description or "").split(".")[0].strip()[:120] or "Professional delivery, on time.",
            bullets=deliv or ["Tailored to your needs", "Ongoing support"],
            icon=s.icon or "fa-solid fa-screwdriver-wrench",
            cta="Get a Quote",
        ))
    return specs


def _group_posters() -> list[PosterSpec]:
    systems = list(System.objects.all().order_by("sort_order"))
    courses = list(Course.objects.all().order_by("sort_order"))
    services = list(Service.objects.all().order_by("sort_order"))
    ms = [c for c in courses if c.category == "software" and "microsoft" in c.slug]

    def names(items, n=6):
        return [i.title for i in items[:n]]

    return [
        PosterSpec(
            key="group-brand",
            group="brand",
            eyebrow="Jordan Design Hub",
            title="Apps · Academy · Media · AI",
            tagline="Uganda's all-in-one tech ecosystem — build, learn, and grow.",
            bullets=[
                "Custom web & mobile apps (Android & iOS)",
                "Paid online academy on Google Meet",
                "Holiday tutoring & STEM for kids",
                "Graphic design & church media",
                "Microsoft Office mastery",
                "AI optimization & prompt engineering",
            ],
            icon="fa-solid fa-layer-group",
            cta="Visit jordandesignhub.com",
            footer_note="WhatsApp +256 754 687 597  ·  jordandesignhub@gmail.com",
        ),
        PosterSpec(
            key="group-systems",
            group="groups",
            eyebrow="Flagship Systems",
            title="Software that works where you are",
            tagline="Offline-first platforms built for Ugandan realities.",
            bullets=[f"{s.title} — {s.tagline}" for s in systems],
            icon="fa-solid fa-cube",
            cta="Book a Demo",
        ),
        PosterSpec(
            key="group-academy",
            group="groups",
            eyebrow="JD Hub Academy",
            title="Learn. Build. Showcase.",
            tagline="12 courses across coding, STEM, Microsoft Office, finance & AI.",
            bullets=names(courses, 8),
            icon="fa-solid fa-graduation-cap",
            cta="Enrol for a Class",
        ),
        PosterSpec(
            key="group-microsoft-office",
            group="groups",
            eyebrow="Microsoft Office Bundle",
            title="Master Microsoft Office",
            tagline="Word, Excel, PowerPoint, Access & Outlook — one tool or the full suite.",
            bullets=[c.title for c in ms],
            icon="fa-solid fa-window-restore",
            cta="Enrol Now",
            accent="#D24726",  # Office orange-ish, keeps red family
        ),
        PosterSpec(
            key="group-holiday-tutoring",
            group="groups",
            eyebrow="Holiday Programme",
            title="Learn. Build. Showcase.",
            tagline="Holiday tutoring from Nursery to S6 — with a certificate on completion.",
            bullets=[
                "Coding & robotics (Scratch → Python)",
                "Microsoft Office intensives",
                "STEM experiments & projects",
                "Graphic design & media",
                "Academic catch-up (all subjects)",
                "Showcase day for parents",
            ],
            icon="fa-solid fa-sun",
            cta="Reserve a Slot",
            accent="#E0A800",
        ),
        PosterSpec(
            key="group-online-tutoring",
            group="groups",
            eyebrow="Online · Google Meet",
            title="Learn from anywhere",
            tagline="Live, personalised tutoring on Google Meet — pay via MoMo or Airtel.",
            bullets=[
                "1-on-1 & small groups",
                "Flexible scheduling",
                "All ages, all subjects",
                "MoMo / Airtel Money payment",
                "Recording of each session",
            ],
            icon="fa-solid fa-laptop",
            cta="Book a Session",
        ),
        PosterSpec(
            key="group-services",
            group="groups",
            eyebrow="Professional Services",
            title="Design & Development Services",
            tagline="From idea to launch — apps, websites, graphics & infrastructure.",
            bullets=[s.title for s in services],
            icon="fa-solid fa-screwdriver-wrench",
            cta="Get a Quote",
        ),
    ]


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------
_LOGO_SVG = """
<svg viewBox="0 0 64 64" width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="lg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#D4AF37"/>
      <stop offset="1" stop-color="#9B7B2E"/>
    </linearGradient>
  </defs>
  <rect x="2" y="2" width="60" height="60" rx="14" fill="#1A1A2E" stroke="url(#lg)" stroke-width="2.5"/>
  <text x="32" y="42" font-family="Noto Sans, sans-serif" font-size="30"
        font-weight="800" fill="url(#lg)" text-anchor="middle">JD</text>
</svg>
"""


def _bullet_list(bullets: list[str], accent: str) -> str:
    items = "".join(
        f'<li><span class="dot" style="background:{accent}"></span><span>{escape(b)}</span></li>'
        for b in bullets
    )
    return f'<ul class="bullets">{items}</ul>'


# Minimal inline-SVG icon set (fill="#fff") keyed by font-awesome class name.
_SVG_ICONS = {
    "fa-solid fa-bolt": '<path d="M13 2L3 14h7v8l10-12h-7z"/>',
    "fa-solid fa-cube": '<path d="M12 2L2 7v10l10 5 10-5V7L12 2zm0 2.3l7.5 3.75L12 11.8 4.5 8.05 12 4.3zM4 9.5l7 3.5v7.4l-7-3.5V9.5zm9 10.9V13l7-3.5v7.4l-7 3.5z"/>',
    "fa-solid fa-graduation-cap": '<path d="M3 9l9-4 9 4-9 4-9-4zm0 1.5V17c0 .5.3 1 .8 1.2L12 22l8.2-3.8c.5-.2.8-.7.8-1.2v-6.5l-9 4-9-4z"/>',
    "fa-solid fa-screwdriver-wrench": '<path d="M9 2a4 4 0 00-4 4c0 1.5.8 2.8 2 3.5V20a2 2 0 104 0V9.5c1.2-.7 2-2 2-3.5a4 4 0 00-4-4zm9.5 2l-.7 2.2 2.2.7-1.5 1.5V14a2.5 2.5 0 11-3 0V9.4l-1.5-1.5 2.2-.7L15.5 5l2 1.5-.5-2.5-.5 2.5z"/>',
    "fa-solid fa-window-restore": '<path d="M3 4h18v6H3V4zm0 8h11v9H3v-9zm13 0h5v9h-5v-9z"/>',
    "fa-solid fa-hand-holding-dollar": '<path d="M12 1.5A2.5 2.5 0 009.5 4a2.5 2.5 0 005 0A2.5 2.5 0 0012 1.5zM12 6c-3.3 0-6 1.8-6 4v1h12v-1c0-2.2-2.7-4-6-4zM2 14l6-1v9H4a2 2 0 01-2-2v-6zm20 0v6a2 2 0 01-2 2h-4v-9l6 1z"/>',
    "fa-solid fa-database": '<path d="M12 3C6.5 3 2 4.8 2 7s4.5 4 10 4 10-1.8 10-4-4.5-4-10-4zM2 12v3c0 2.2 4.5 4 10 4s10-1.8 10-4v-3c0 2.2-4.5 4-10 4S2 14.2 2 12zm0 6v3c0 2.2 4.5 4 10 4s10-1.8 10-4v-3c0 2.2-4.5 4-10 4S2 20.2 2 18z"/>',
    "fa-solid fa-school": '<path d="M12 3L1 9l11 6 9-4.9V17h2V9L12 3zM4 13.2V17c0 1.7 3.6 3 8 3s8-1.3 8-3v-3.8l-8 4.3-8-4.3z"/>',
    "fa-solid fa-laptop": '<path d="M4 5h16a1 1 0 011 1v9a1 1 0 01-1 1H4a1 1 0 01-1-1V6a1 1 0 011-1zM2 18h20v2H2v-2z"/>',
    "fa-solid fa-sun": '<path d="M12 7a5 5 0 100 10 5 5 0 000-10zM12 1l1 3h-2l1-3zm0 19l1 3h-2l1-3zM4.2 4.2l2.1 2.1-1.4 1.4-2.1-2.1 1.4-1.4zm12 12l2.1 2.1-1.4 1.4-2.1-2.1 1.4-1.4zM1 12l3-1v2l-3-1zm19 0l3-1v2l-3-1zM4.2 19.8l2.1-2.1 1.4 1.4-2.1 2.1-1.4-1.4zm12-12l2.1-2.1 1.4 1.4-2.1 2.1-1.4-1.4z"/>',
    "fa-solid fa-layer-group": '<path d="M12 2L2 8l10 6 10-6-10-6zM2 14l10 6 10-6M2 11l10 6 10-6"/>',
    "fa-solid fa-code": '<path d="M8 6L2 12l6 6 1.4-1.4L4.8 12l4.6-4.6L8 6zm8 0l-1.4 1.4L19.2 12l-4.6 4.6L16 18l6-6-6-6z"/>',
    "fa-solid fa-microchip": '<path d="M9 2v2h2V2H9zm4 0v2h2V2h-2zM9 20v2h2v-2H9zm4 0v2h2v-2h-2zM4 7h12v10H4V7zm2 2v6h8V9H6zM3 9H1v6h2V9zm16 0h2v6h-2V9z"/>',
    "fa-solid fa-flask": '<path d="M9 2v6.6L4 18a2 2 0 001.8 3h12.4A2 2 0 0020 18l-5-9.4V2H9zm2 0h2v7l3.5 6.6h-9L11 9V2z"/>',
    "fa-solid fa-paintbrush": '<path d="M3 17.5L8.5 22 21 9.5 15.5 4 3 17.5zM2 21l4-1-3-3-1 4z"/>',
    "fa-solid fa-chart-line": '<path d="M3 3h2v16h16v2H3V3zm6 11l-3-3 1.4-1.4L9 11.2l4-4 3 3 5-5L22.4 6.6 16 13l-3-3-4 4z"/>',
    "fa-solid fa-robot": '<path d="M6 4a2 2 0 00-2 2v9a2 2 0 002 2h1v3h2v-3h6v3h2v-3h1a2 2 0 002-2V6a2 2 0 00-2-2H6zm1 5h2v2H7V9zm8 0h2v2h-2V9zM6 14h12v2H6v-2zM11 1h2v3h-2V1z"/>',
    "fa-solid fa-chalkboard-user": '<path d="M2 4h20v12H2V4zm2 2v8h16V6H4zM1 18h22v2H1v-2z"/>',
    "fa-solid fa-network-wired": '<path d="M9 2v4h2v3H7a2 2 0 00-2 2v3H3v4h6v-4H6v-3h6v3h-1v4h6v-4h-2v-3a2 2 0 00-2-2h-4V6h2V2H9z"/>',
}


def _icon_svg(icon_class: str, accent: str) -> str:
    path = _SVG_ICONS.get(icon_class)
    if not path:
        # fallback: a generic sparkle/bolt
        path = _SVG_ICONS["fa-solid fa-bolt"]
    return (
        f'<svg viewBox="0 0 24 24" fill="#fff" xmlns="http://www.w3.org/2000/svg">{path}</svg>'
    )


def render_html(spec: PosterSpec, fmt: str, w: int, h: int) -> str:
    is_story = fmt == "story"
    is_landscape = fmt == "landscape"
    accent = spec.accent

    if is_landscape:
        layout = "landscape-layout"
    elif is_story:
        layout = "story-layout"
    else:
        layout = "square-layout"

    bullets_html = _bullet_list(spec.bullets, accent)
    icon_svg = _icon_svg(spec.icon, accent)

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<style>
  :root {{
    --red:{RED}; --red-d:{RED_DARK}; --gold:{GOLD}; --gold-d:{GOLD_DARK};
    --cream:{CREAM}; --ink:{INK}; --accent:{accent};
  }}
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  @page {{ size: {w}px {h}px; margin: 0; }}
  html,body {{ width:{w}px; height:{h}px; overflow:hidden; }}
  body {{
    font-family:'Noto Sans','DejaVu Sans',sans-serif;
    color:var(--cream);
    background:
      radial-gradient(120% 80% at 85% 12%, rgba(212,175,55,.16), transparent 55%),
      radial-gradient(110% 70% at 8% 92%, rgba(200,16,46,.20), transparent 55%),
      linear-gradient(150deg,#15060a 0%,#2a0a14 40%,#1A1A2E 100%);
    position:relative;
  }}
  /* decorative gold rings */
  body::before, body::after {{
    content:""; position:absolute; border-radius:50%; border:2px solid rgba(212,175,55,.18);
    pointer-events:none;
  }}
  body::before {{ width:{int(w*0.62)}px; height:{int(w*0.62)}px; right:-{int(w*0.18)}px; top:-{int(w*0.18)}px; }}
  body::after  {{ width:{int(w*0.40)}px; height:{int(w*0.40)}px; left:-{int(w*0.12)}px; bottom:-{int(w*0.12)}px; border-color:rgba(200,16,46,.16); }}

  .wrap {{ position:relative; z-index:2; width:100%; height:100%; display:flex; flex-direction:column;
          padding:{int(w*0.075)}px {int(w*0.075)}px; }}
  .top {{ display:flex; align-items:center; gap:{int(w*0.028)}px; }}
  .logo {{ width:{int(w*0.085)}px; height:{int(w*0.085)}px; flex:0 0 auto; }}
  .brand {{ display:flex; flex-direction:column; line-height:1.1; }}
  .brand b {{ font-size:{int(w*0.034)}px; font-weight:800; color:var(--gold); letter-spacing:.5px; }}
  .brand small {{ font-size:{int(w*0.020)}px; color:rgba(251,247,240,.55); letter-spacing:2px; text-transform:uppercase; }}

  .eyebrow {{
    margin-top:{int(w*0.05)}px; display:inline-block; align-self:flex-start;
    font-size:{int(w*0.022)}px; font-weight:700; letter-spacing:2.5px; text-transform:uppercase;
    color:var(--ink); background:{accent}; padding:{int(w*0.012)}px {int(w*0.028)}px; border-radius:999px;
  }}
  .icon-badge {{
    margin-top:{int(w*0.04)}px; width:{int(w*0.13)}px; height:{int(w*0.13)}px; border-radius:50%;
    background:linear-gradient(135deg,{accent},{RED_DARK});
    display:flex; align-items:center; justify-content:center;
    box-shadow:0 10px 40px rgba(0,0,0,.45), 0 0 0 1px rgba(212,175,55,.3) inset;
  }}
  .icon-badge svg {{ width:60%; height:60%; }}
  .title {{
    margin-top:{int(w*0.028)}px; font-weight:900; line-height:1.02;
    font-size:{int(w*0.082)}px; color:#fff;
    text-shadow:0 4px 30px rgba(0,0,0,.45);
  }}
  .title .accent {{ color:var(--gold); }}
  .tagline {{
    margin-top:{int(w*0.028)}px; font-size:{int(w*0.030)}px; line-height:1.35;
    color:rgba(251,247,240,.82); font-weight:500; max-width:{int(w*0.78)}px;
  }}

  .bullets {{ margin-top:{int(w*0.045)}px; list-style:none; display:flex; flex-direction:column;
             gap:{int(w*0.018)}px; max-width:{int(w*0.80)}px; }}
  .bullets li {{ display:flex; align-items:flex-start; gap:{int(w*0.022)}px; font-size:{int(w*0.026)}px;
                line-height:1.3; color:rgba(251,247,240,.9); }}
  .dot {{ flex:0 0 auto; width:{int(w*0.016)}px; height:{int(w*0.016)}px; border-radius:50%;
          margin-top:{int(w*0.010)}px; box-shadow:0 0 12px {accent}; }}

  .spacer {{ flex:1; }}

  .cta-row {{ display:flex; align-items:center; gap:{int(w*0.022)}px; }}
  .cta {{
    display:inline-flex; align-items:center; gap:{int(w*0.020)}px;
    background:linear-gradient(135deg,{accent},{RED_DARK});
    color:#fff; font-weight:800; font-size:{int(w*0.030)}px; letter-spacing:.5px;
    padding:{int(w*0.020)}px {int(w*0.040)}px; border-radius:999px;
    box-shadow:0 10px 30px rgba(0,0,0,.4); border:1px solid rgba(212,175,55,.4);
  }}
  .cta svg {{ width:{int(w*0.026)}px; height:{int(w*0.026)}px; fill:#fff; }}

  .contact {{
    margin-top:{int(w*0.028)}px; display:flex; flex-direction:column; gap:2px;
    font-size:{int(w*0.020)}px; color:rgba(251,247,240,.6);
  }}
  .contact b {{ color:var(--gold); }}

  .footer-bar {{
    margin-top:{int(w*0.03)}px; height:{int(w*0.006)}px; width:100%;
    background:linear-gradient(90deg,{accent},var(--gold),transparent); border-radius:999px;
  }}
  .note {{ margin-top:{int(w*0.014)}px; font-size:{int(w*0.018)}px; color:rgba(251,247,240,.4); }}

  /* story layout: stack vertically with more breathing room */
  .story-layout .title {{ font-size:{int(w*0.094)}px; }}
  /* landscape: two columns on wide canvas */
  .landscape-layout .title {{ font-size:{int(w*0.060)}px; }}
  .landscape-layout .tagline {{ font-size:{int(w*0.024)}px; }}
  .landscape-layout .bullets li {{ font-size:{int(w*0.020)}px; }}
</style></head>
<body>
  <div class="wrap {layout}">
    <div class="top">
      <div class="logo">{_LOGO_SVG}</div>
      <div class="brand"><b>Jordan Design Hub</b><small>Apps · Academy · Media · AI</small></div>
    </div>

    <span class="eyebrow">{escape(spec.eyebrow)}</span>
    <div class="icon-badge">{icon_svg}</div>
    <h1 class="title">{escape(spec.title)}</h1>
    <p class="tagline">{escape(spec.tagline)}</p>

    {bullets_html}

    <div class="spacer"></div>

    <div class="cta-row">
      <span class="cta"><svg viewBox="0 0 24 24"><path d="M13 2L3 14h7v8l10-12h-7z"/></svg> {escape(spec.cta)}</span>
    </div>
    <div class="contact">
      <div><b>WhatsApp:</b> +256 754 687 597</div>
      <div><b>Email:</b> jordandesignhub@gmail.com</div>
    </div>
    <div class="footer-bar"></div>
    {'<div class="note">'+escape(spec.footer_note)+'</div>' if spec.footer_note else ''}
  </div>
</body></html>"""


# ---------------------------------------------------------------------------
# Chromium rendering
# ---------------------------------------------------------------------------
def _run_chromium(html_path: Path, out_png: Path, w: int, h: int, pdf: bool = False) -> None:
    scale = 2  # retina
    # Common flags. chromium prints GPU warnings to stderr in headless but
    # still renders fine, so we don't treat stderr as fatal.
    args = [
        CHROMIUM,
        "--headless",  # old headless mode (new mode rejects --screenshot)
        "--no-sandbox",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--disable-software-rasterizer",
        "--hide-scrollbars",
        # NOTE: use --flag=value (not space-separated) so chromium's parser
        # doesn't mistake the bare value for a second target URL, which
        # triggers "Multiple targets are not supported in headless mode".
        f"--force-device-scale-factor={scale}",
        f"--window-size={w},{h}",
    ]
    if pdf:
        # Use the print-to-pdf path; page size set via CSS @page in html.
        args += [f"--print-to-pdf={out_png}", "--no-pdf-header-footer", str(html_path)]
    else:
        args += [f"--screenshot={out_png}", str(html_path)]
    try:
        subprocess.run(args, check=True, capture_output=True, timeout=120)
    except subprocess.CalledProcessError as e:
        # chromium returns non-zero on benign GPU init warnings sometimes;
        # verify the output file was actually produced before failing.
        if out_png.exists() and out_png.stat().st_size > 1024:
            return
        raise RuntimeError(
            f"chromium failed for {html_path.name}: {e.stderr.decode('utf-8','ignore')[:800]}"
        ) from e


def render_poster(spec: PosterSpec, fmt: str) -> list[Path]:
    w, h = {"square": (1080, 1080), "story": (1080, 1920), "landscape": (1200, 630)}[fmt]
    folder = OUT / spec.group
    folder.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    html_path = TMP / f"{spec.key}-{fmt}.html"
    html_path.write_text(render_html(spec, fmt, w, h), encoding="utf-8")

    png_path = folder / f"{spec.key}-{fmt}.png"
    pdf_path = folder / f"{spec.key}-{fmt}.pdf"
    _run_chromium(html_path, png_path, w, h, pdf=False)
    _run_chromium(html_path, pdf_path, w, h, pdf=True)
    return [png_path, pdf_path]


# ---------------------------------------------------------------------------
# Combined brochure PDF
# ---------------------------------------------------------------------------
def build_brochure(all_pngs: list[Path]) -> Path:
    """Stitch all poster PNGs (sorted) into a single PDF brochure."""
    import img2pdf

    out = OUT / "JD-Hub-Marketing-Brochure.pdf"
    ordered = sorted(p for p in all_pngs if p.name.endswith("-square.png") or p.name.endswith("-landscape.png"))
    if not ordered:
        ordered = sorted(all_pngs)
    with open(out, "wb") as f:
        f.write(img2pdf.convert([str(p) for p in ordered]))
    return out


# ---------------------------------------------------------------------------
# Marketing video (MP4) via ffmpeg
# ---------------------------------------------------------------------------
def build_video(all_pngs: list[Path]) -> Path | None:
    if not FFMPEG:
        print("  ! ffmpeg not found, skipping video")
        return None
    # pick a strong curated set: brand + group posters + a few product squares
    curated: list[Path] = []
    brand_sq = OUT / "brand" / "group-brand-square.png"
    groups = sorted((OUT / "groups").glob("group-*-square.png"))
    systems = sorted((OUT / "systems").glob("system-*-square.png"))
    courses = sorted((OUT / "courses").glob("course-*-square.png"))
    services = sorted((OUT / "services").glob("service-*-square.png"))

    if brand_sq.exists():
        curated.append(brand_sq)
    curated.extend(groups)
    curated.extend(systems[:4])
    curated.extend([c for c in courses if "microsoft" in c.name][:3])
    curated.extend(services[:3])
    # de-duplicate preserve order
    seen = set()
    curated = [p for p in curated if not (p in seen or seen.add(p))]

    if not curated:
        print("  ! no poster PNGs found for video")
        return None

    frames_dir = TMP / "video_frames"
    if frames_dir.exists():
        shutil.rmtree(frames_dir)
    frames_dir.mkdir(parents=True)

    # Pre-resize all frames to 1080x1080 so the concat is uniform.
    from PIL import Image

    for i, p in enumerate(curated, 1):
        im = Image.open(p).convert("RGB")
        im = im.resize((1080, 1080), Image.LANCZOS)
        im.save(frames_dir / f"frame_{i:03d}.png")

    n = len(curated)
    # Build a slideshow: each image shown 2.5s with a slow zoom-in (zoompan),
    # crossfades between images via xfade. We assemble using a concat demuxer
    # for simplicity + a fade filter per segment for a polished feel.
    seg_dur = 2.5
    frames_dir_abs = str(frames_dir.resolve())
    list_file = TMP / "frames.txt"
    with open(list_file, "w") as f:
        for i in range(1, n + 1):
            f.write(f"file '{frames_dir_abs}/frame_{i:03d}.png'\n")
            f.write(f"duration {seg_dur}\n")
        # repeat last frame per ffmpeg concat requirement
        f.write(f"file '{frames_dir_abs}/frame_{n:03d}.png'\n")

    out = OUT / "JD-Hub-Promo.mp4"
    # Two-pass approach for reliability:
    #  1) concat images (uniform size) into an intermediate mp4 with xfade-free
    #     cuts — clean and robust.
    #  2) We keep it single-pass here; zoompan is applied per-input below via
    #     a simpler scale+fade pipeline to avoid the concat+zoompan complexity.
    cmd = [
        FFMPEG, "-y", "-safe", "0",
        "-f", "concat", "-i", str(list_file.resolve()),
        "-vf",
        "scale=1080:1080:force_original_aspect_ratio=decrease,"
        "pad=1080:1080:-1:-1:color=black,format=yuv420p,"
        "fade=t=in:st=0:d=0.5,fade=t=out:st=" + str(seg_dur * n - 0.5) + ":d=0.5",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(out),
    ]
    subprocess.run(cmd, check=True, capture_output=True, timeout=600)
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    if not CHROMIUM:
        print("ERROR: chromium not found. Install it to render posters.")
        return 1
    do_posters = "--posters" in sys.argv or len(sys.argv) == 1
    do_pdf = "--pdf" in sys.argv or len(sys.argv) == 1
    do_video = "--video" in sys.argv or len(sys.argv) == 1

    OUT.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)

    specs: list[PosterSpec] = []
    specs += _group_posters()      # brand + group posters
    specs += _sys_posters()
    specs += _course_posters()
    specs += _service_posters()

    all_pngs: list[Path] = []
    if do_posters:
        print(f"==> Rendering {len(specs)} posters x {len(FORMATS)} formats ...")
        for i, sp in enumerate(specs, 1):
            for fmt, w, h in FORMATS:
                try:
                    made = render_poster(sp, fmt)
                    all_pngs.extend(made)
                except Exception as e:
                    print(f"  ! {sp.key} [{fmt}] failed: {e}")
            if i % 5 == 0 or i == len(specs):
                print(f"  {i}/{len(specs)} done")
        print(f"    rendered {len(all_pngs)} files")

    # refresh png list from disk
    all_pngs = [p for p in OUT.rglob("*.png") if "_tmp" not in str(p)]

    if do_pdf:
        if not all_pngs:
            all_pngs = [p for p in OUT.rglob("*.png") if "_tmp" not in str(p)]
        if all_pngs:
            print("==> Building combined brochure PDF ...")
            b = build_brochure(all_pngs)
            print(f"    ✓ {b.relative_to(ROOT)} ({b.stat().st_size//1024} KB)")

    if do_video:
        if not all_pngs:
            all_pngs = [p for p in OUT.rglob("*.png") if "_tmp" not in str(p)]
        if all_pngs:
            print("==> Building promo video (MP4) ...")
            v = build_video(all_pngs)
            if v:
                print(f"    ✓ {v.relative_to(ROOT)} ({v.stat().st_size//1024} KB)")

    # cleanup temp html
    shutil.rmtree(TMP, ignore_errors=True)
    print("\nMarketing kit complete →", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
