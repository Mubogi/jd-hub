"""
Curated stock photography for Jordan Design Hub marketing posters.
Each entry maps a product/category key to a Pexels photo ID (CC0, free to use).
Downloaded once into marketing/_assets/ and embedded into posters as the
"hero" image to make them feel alive and illustrated with real people.

Photo IDs verified downloadable via direct image URL (no API key needed).
Sources: Pexels (https://www.pexels.com/license/ - free for commercial use).
"""
from __future__ import annotations

# Per-product hero photos (Pexels photo IDs).
# Chosen to depict real people working, learning, and building — African
# professionals, students, coders, business owners where possible.
PRODUCT_PHOTOS: dict[str, int] = {
    # ---- Systems ----
    "system-offline-first-school-management-system": 5212317,   # students classroom
    "system-attendance-hub": 8617763,                           # student raising hand / attendance
    "system-sacco-portfolio-quality-microfinance-system": 4386466,  # money/finance hands
    "system-destiny-college-dbms": 7926633,                      # college students

    # ---- Courses ----
    "course-scratch-coding-uganda-cambridge-curricula": 5905833,   # child coding laptop
    "course-basic-digital-literacy": 6147521,                       # person at computer
    "course-practical-stem": 8432356,                               # kids science experiment
    "course-graphic-design-canva-inshot": 2102416,                 # designer at work
    "course-financial-sacco-management": 4386466,                   # finance/calculation
    "course-ai-optimization-prompt-engineering": 8386440,          # AI / tech abstract
    "course-microsoft-word": 267350,                                # typing/document
    "course-microsoft-excel": 265087,                              # spreadsheet screen
    "course-microsoft-powerpoint": 1181467,                        # presentation screen
    "course-microsoft-access": 1181271,                            # database/laptop
    "course-microsoft-word-excel-combo": 7688336,                   # office work
    "course-microsoft-office-suite-all-tools": 3184465,            # office team

    # ---- Services ----
    "service-web-design-development": 1778038,                # web dev screen
    "service-android-ios-app-development": 4348404,          # phone/app dev
    "service-graphics-design": 2102416,                      # graphic designer
    "service-church-media-training": 9307214,                # church/media
    "service-holiday-tutoring-nurserys6": 8386663,           # kids learning
    "service-ai-optimization-training": 8386440,             # AI abstract
    "service-ict-infrastructure-networking": 6050432,        # server/network

    # ---- Groups ----
    "group-brand": 3184465,                # diverse business team
    "group-systems": 3184292,               # team at computers
    "group-academy": 5212317,               # students
    "group-microsoft-office": 3184465,      # office team
    "group-holiday-tutoring": 8534080,      # kids stem
    "group-online-tutoring": 4226140,       # video call/learning
    "group-services": 3184292,              # team at work
}

# Fallbacks if a specific photo fails to download or isn't mapped.
FALLBACK_PHOTO = 3184465  # diverse business team


def photo_url(pid: int, width: int = 1200) -> str:
    return (
        f"https://images.pexels.com/photos/{pid}/pexels-photo-{pid}.jpeg"
        f"?auto=compress&cs=tinysrgb&w={width}"
    )
