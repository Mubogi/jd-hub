# Jordan Design Hub — Project Memory

## Overview
Production-ready Django marketing site for "Jordan Design Hub" (Uganda).
Red + gold brand theme. Deployed on Render free tier.

## Key Commands
- `python manage.py seed_demo` — seed/update systems, courses, services, media + regenerate system whitepaper PDFs
- `python manage.py gen_lessons` — regenerate all lesson-outline PDFs (courses x tracks)
- `python manage.py gen_marketing` — regenerate branded advert images (then copy to media/gallery/ + re-seed)
- `python manage.py runserver` — local dev (set `DJANGO_DEBUG=True` to disable SSL redirect)
- `python manage.py check` — system check (must pass clean)

## Models (hub/models.py)
- **System**: title, slug, tagline, category (education/finance/database/custom), features (text), tech_stack, **screenshots** (text, `path|caption` per line, relative to MEDIA_ROOT), icon
- **Course**: title, slug, category (stem/software/financials/ai), level, duration, curriculum (text), icon
- **MediaItem**: gallery portfolio item (image or video embed)
- **SiteSettings**: singleton site config

## PDF Generation
- `hub/pdf.py` → system whitepaper PDFs (cached in `media/system_docs/`)
  - `build_pdf(system)` — red+gold branded, embeds real screenshots via `_screenshot_block`
  - Screenshots field format: `system_shots/filename.png|Caption text`
- `hub/lesson_pdf.py` → lesson-outline PDFs (cached in `media/lesson_docs/`)
  - `build_lesson_pdf(course, track_key)` — 4 tracks: beginner/intermediate/advanced/holiday
  - Each track = 2 weeks, daily objectives + weekly mini-project

## Marketing Images (hub/marketing_images.py)
- `generate_all()` → 14 branded PNGs in `static/hub/img/marketing/`
- Sizes: square (1080×1080), story (1080×1920), landscape (1200×630), banner (1500×500)
- Copied to `media/gallery/` and seeded as MediaItems for the website gallery

## URLs
- `/systems/<slug>/pdf/` — download system whitepaper PDF
- `/courses/<slug>/lessons/<track>/pdf/` — download lesson outline PDF (track: beginner|intermediate|advanced|holiday)

## External Repos (throwaway clones in /tmp, NOT part of this repo)
- `/tmp/sms-main` — school management system (34 screenshots in screenshots/)
- `/tmp/attend-web` — Django attendance app (Django 4.2 compat patches applied locally)
- `/tmp/attend-android` — Kotlin Android app (no APK/screenshots in repo)
- Screenshots captured from these are stored in `media/system_shots/`

## Marketing Kit (scripts/gen_marketing_kit.py)
- Generates 90 posters (30 products × 3 formats: square/story/landscape) → `marketing/`
- **v2 design**: real stock photos (Pexels CC0) of people on each poster, gradient
  masks, glassmorphism, mesh gradients, noise texture, glow effects
- Photo mapping: `scripts/_marketing_photos.py` (PRODUCT_PHOTOS dict, 23 curated IDs)
- Photos cached in `marketing/_assets/pexels_<id>.jpg` (downloaded once)
- Posters downscaled to 1x (1080px) — chromium renders at 2x retina, Pillow downscales
- **Promo video**: vertical 1080×1920 (TikTok-native), AI voiceover via edge-tts
  (en-US-AndrewMultilingualNeural), synthesized music bed (C-Am-G-F chords),
  Ken Burns zoom + xfade transitions, ~40s, H.264+AAC
- **Brochure**: single PDF from JPEG-converted posters (~6MB, under GitHub 100MB limit)
- Run: `python scripts/gen_marketing_kit.py` (all) or `--posters`/`--video`/`--pdf`
- Chromium flags MUST use `--flag=value` syntax (not space-separated)
- ffmpeg music bed: use `sine` sources not `aevalsrc` (TAU/PI constants unsupported),
  output WAV (AAC encoder chokes on tiny amix buffers)
- edge-tts: use Python API (`asyncio.run`), CLI not available

## Completed Work
- Google Search Console verified; Google Meet integration (commit bc9c56c)
- MoMo/Airtel payment prompts on enrolment success + email
- Real screenshots embedded in system PDFs (SMS + Attendance Hub)
- 4 systems, 12 courses (incl. 6 Microsoft Office: Word/Excel/PowerPoint/Access/Word+Excel combo/Full Suite)
- 48 lesson PDFs (12 courses × 4 tracks), 14 marketing images, 10 gallery items
- Marketing kit v2: illustrated posters + TikTok video with AI voiceover (commit 4aa5c07)

## Brand Colours
- Red: #C8102E (primary), #8B0000 (dark)
- Gold: #D4AF37 (accent), #9B7B2E (dark gold for text)
- White: #FBF7F0 (warm off-white tint)
