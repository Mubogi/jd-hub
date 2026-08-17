"""Context processors that expose global site settings to templates."""
from django.conf import settings

from hub.models import SiteSettings


def site_settings(request):
    """Inject site-wide settings + Django settings constants into every template."""
    try:
        site = SiteSettings.get()
        whatsapp = site.whatsapp_number or settings.WHATSAPP_NUMBER
        email = site.contact_email or settings.CONTACT_EMAIL
        address = site.address
        hero_subtitle = site.hero_subtitle
    except Exception:
        # Database not ready (e.g. during migrations) — fall back to project settings.
        whatsapp = settings.WHATSAPP_NUMBER
        email = settings.CONTACT_EMAIL
        address = "Kampala, Uganda"
        hero_subtitle = ""

    return {
        "SITE_NAME": settings.SITE_NAME,
        "SITE_TAGLINE": settings.SITE_TAGLINE,
        "SITE_OWNER": settings.SITE_OWNER,
        "WHATSAPP_NUMBER": whatsapp,
        "CONTACT_EMAIL": email,
        "SITE_ADDRESS": address,
        "HERO_SUBTITLE": hero_subtitle,
        "DEBUG": settings.DEBUG,
    }
