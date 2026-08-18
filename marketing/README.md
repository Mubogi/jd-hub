# Jordan Design Hub — Marketing Kit

Beautiful, downloadable marketing assets for **every product**, **product groups**,
and the **whole brand**. All in red + gold. Share on WhatsApp, Facebook,
Instagram, or print them.

> Live site: https://jd-hub-8e5d.onrender.com/
> WhatsApp: +256 754 687 597  ·  Email: jordandesignhub@gmail.com

---

## What's inside

### 📁 `brand/` — the whole website
Posters showcasing the entire Jordan Design Hub ecosystem (Apps · Academy · Media · AI).
- `group-brand-square.png` / `.pdf` — square (1080×1080)
- `group-brand-story.png` / `.pdf` — story (1080×1920)
- `group-brand-landscape.png` / `.pdf` — landscape (1200×630)

### 📁 `groups/` — product group posters
One poster per product *group*:
- `group-systems-*` — all 4 flagship software systems
- `group-academy-*` — JD Hub Academy (all 12 courses)
- `group-microsoft-office-*` — Microsoft Office bundle
- `group-holiday-tutoring-*` — Holiday Tutoring Programme
- `group-online-tutoring-*` — Online Tutoring via Google Meet
- `group-services-*` — Design & Development Services

### 📁 `systems/` — software system posters (4)
One square + story + landscape (PNG + PDF) for each:
- Offline-First School Management System
- Attendance Hub
- SACCO Portfolio Quality & Microfinance System
- Destiny College DBMS

### 📁 `courses/` — academy course posters (12)
One set per course: Scratch Coding, Basic Digital Literacy, Practical STEM,
Graphic Design (Canva & InShot), Financial & SACCO Management, AI Optimization
& Prompt Engineering, Microsoft Word/Excel/PowerPoint/Access, Word+Excel Combo,
Microsoft Office Suite.

### 📁 `services/` — service posters (7)
Web & App Development, Graphics Design, Church Media, Holiday Tutoring,
AI Training, ICT Infrastructure, Android & iOS.

### 🎬 `JD-Hub-Promo.mp4`
A 42-second promotional video (1080×1080, H.264) cycling through the brand
and group posters with fade in/out. Perfect for WhatsApp status, Instagram
reels, and Facebook ads.

### 📕 `JD-Hub-Marketing-Brochure.pdf`
A single PDF brochure containing every square + landscape poster — handy for
emailing to clients or printing as a catalog.

---

## Formats explained

| File suffix | Dimensions | Best for |
|---|---|---|
| `-square` | 1080×1080 | Instagram/Facebook posts, WhatsApp |
| `-story` | 1080×1920 | Instagram/Facebook/WhatsApp stories |
| `-landscape` | 1200×630 | Facebook link previews, Twitter, website banners |

Each poster is available as both **PNG** (image) and **PDF** (print-ready).

---

## How to download

**Single file:** click the file in GitHub → **Download** button (or **Raw**).

**Whole folder:** use Git to clone the repo, or use GitHub's
"Download ZIP" on the repo page, then extract the `marketing/` folder.

**Everything at once:**
```bash
git clone https://github.com/Mubogi/jd-hub.git
# the marketing folder is at jd-hub/marketing/
```

---

## Regenerating the kit

The posters are generated from the live Django database by a script, so they
always match the real product data. To regenerate (needs chromium + ffmpeg):

```bash
pip install Pillow img2pdf
sudo apt-get install -y chromium ffmpeg fonts-noto

PYTHONPATH=. python scripts/gen_marketing_kit.py            # everything
PYTHONPATH=. python scripts/gen_marketing_kit.py --posters  # posters only
PYTHONPATH=. python scripts/gen_marketing_kit.py --pdf       # brochure only
PYTHONPATH=. python scripts/gen_marketing_kit.py --video     # video only
```

The generator lives at `scripts/gen_marketing_kit.py`.
