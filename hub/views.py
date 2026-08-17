"""
Views for the JD Hub core app.

- ``home`` renders the full single-page marketing site (all sections).
- ``contact`` stores leads and optionally redirects to WhatsApp.
- ``system_pdf`` generates (and caches) a whitepaper PDF on demand.
"""
from django.conf import settings
from django.core.mail import send_mail
from django.http import FileResponse, Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from hub.models import ContactSubmission, Course, MediaItem, Service, SiteSettings, System
from hub.pdf import build_pdf


def home(request):
    site = SiteSettings.get()
    context = {
        "site": site,
        "systems": System.objects.filter(is_published=True),
        "courses": Course.objects.filter(is_published=True),
        "services": Service.objects.filter(is_published=True),
        "media_items": MediaItem.objects.filter(is_published=True),
        "course_categories": Course.CATEGORY_CHOICES,
    }
    return render(request, "hub/home.html", context)


@require_http_methods(["GET", "POST"])
def contact(request):
    if request.method == "POST":
        # Honeypot anti-spam: a hidden field bots tend to fill in. Real users
        # never see it, so a non-empty value means "discard silently".
        if request.POST.get("company_url"):
            # Pretend success to bots; store nothing.
            return redirect(f"{reverse('contact')}?sent=1#contact-form")

        name = (request.POST.get("name") or "").strip()
        email = (request.POST.get("email") or "").strip()
        phone = (request.POST.get("phone") or "").strip()
        subject = (request.POST.get("subject") or "General inquiry").strip()
        message = (request.POST.get("message") or "").strip()
        via_whatsapp = request.POST.get("via_whatsapp") == "on"

        if name and email and message:
            submission = ContactSubmission.objects.create(
                name=name, email=email, phone=phone, subject=subject, message=message,
            )

            # Best-effort email notification (never block the user flow on it).
            try:
                site = SiteSettings.get()
                send_mail(
                    subject=f"[JD Hub] {subject}",
                    message=(
                        f"New inquiry from {name} <{email}>\n"
                        f"Phone: {phone or 'n/a'}\n\n{message}"
                    ),
                    from_email=settings.CONTACT_EMAIL,
                    recipient_list=[site.contact_email or settings.CONTACT_EMAIL],
                    fail_silently=True,
                )
            except Exception:
                pass

            if via_whatsapp:
                site = SiteSettings.get()
                wa_number = site.whatsapp_number or settings.WHATSAPP_NUMBER
                wa_text = (
                    f"Hello JD Hub, I'm {name}. Re: {subject}. {message}"
                    f"{' (Phone: ' + phone + ')' if phone else ''}"
                )
                import urllib.parse

                url = f"https://wa.me/{wa_number}?text={urllib.parse.quote(wa_text)}"
                return redirect(url)

            return redirect(f"{reverse('contact')}?sent=1#contact-form")

    site = SiteSettings.get()
    return render(request, "hub/contact.html", {"site": site, "sent": request.GET.get("sent") == "1"})


def system_pdf(request, slug: str):
    """Generate and stream the whitepaper PDF for a system (cached on disk)."""
    try:
        system = System.objects.get(slug=slug, is_published=True)
    except System.DoesNotExist:
        raise Http404("System not found.")

    out_dir = settings.MEDIA_ROOT / "system_docs"
    out_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = out_dir / f"{system.slug}.pdf"

    # Regenerate if missing or stale (system updated after last build).
    regenerate = (not pdf_path.exists()) or (
        pdf_path.stat().st_mtime < system.updated_at.timestamp()
    )
    if regenerate:
        build_pdf(system, pdf_path)

    if not pdf_path.exists():
        raise Http404("PDF could not be generated.")

    response = FileResponse(
        open(pdf_path, "rb"),
        content_type="application/pdf",
    )
    response["Content-Disposition"] = f'attachment; filename="{system.slug}-whitepaper.pdf"'
    response["Content-Length"] = str(pdf_path.stat().st_size)
    return response


def robots(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines) + "\n", content_type="text/plain")
