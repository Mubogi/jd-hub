"""
Django admin configuration for JD Hub.

Provides rich, grouped management for all content so non-developers can update
the site without touching code.
"""
from django.contrib import admin

from hub.models import (
    ContactSubmission,
    Course,
    Enrolment,
    MediaItem,
    Service,
    SiteSettings,
    System,
)


class FeatureListMixin:
    """Render newline-separated text fields as textareas in the admin."""

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in ("features", "deliverables", "curriculum"):
            kwargs["widget"] = admin.widgets.AdminTextareaWidget(
                attrs={"rows": 6, "style": "font-family:monospace;"}
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)


@admin.register(System)
class SystemAdmin(FeatureListMixin, admin.ModelAdmin):
    list_display = ("title", "category", "tagline", "sort_order", "is_published", "updated_at")
    list_editable = ("sort_order", "is_published")
    list_filter = ("category", "is_published")
    search_fields = ("title", "tagline", "description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "tagline", "description", "category")}),
        ("Presentation", {"fields": ("icon", "tech_stack")}),
        ("Details", {"fields": ("features",)}),
        ("Publishing", {"fields": ("sort_order", "is_published")}),
    )
    actions = ["regenerate_pdfs"]

    @admin.action(description="Regenerate documentation PDFs")
    def regenerate_pdfs(self, request, queryset):
        from hub.pdf import build_pdf

        count = 0
        for system in queryset:
            build_pdf(system)
            count += 1
        self.message_user(request, f"Regenerated {count} PDF whitepaper(s).")


@admin.register(Course)
class CourseAdmin(FeatureListMixin, admin.ModelAdmin):
    list_display = ("title", "category", "level", "duration", "sort_order", "is_published")
    list_editable = ("sort_order", "is_published")
    list_filter = ("category", "is_published")
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "description", "category")}),
        ("Presentation", {"fields": ("icon", "level", "duration")}),
        ("Curriculum", {"fields": ("curriculum",)}),
        ("Publishing", {"fields": ("sort_order", "is_published")}),
    )


@admin.register(Service)
class ServiceAdmin(FeatureListMixin, admin.ModelAdmin):
    list_display = ("title", "sort_order", "is_published")
    list_editable = ("sort_order", "is_published")
    list_filter = ("is_published",)
    search_fields = ("title", "description")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "description", "icon")}),
        ("Deliverables", {"fields": ("deliverables",)}),
        ("Publishing", {"fields": ("sort_order", "is_published")}),
    )


@admin.register(MediaItem)
class MediaItemAdmin(admin.ModelAdmin):
    list_display = ("title", "media_type", "sort_order", "is_published", "created_at")
    list_editable = ("sort_order", "is_published")
    list_filter = ("media_type", "is_published")
    search_fields = ("title", "caption")
    fieldsets = (
        (None, {"fields": ("title", "caption", "media_type")}),
        ("Image", {"fields": ("image",), "classes": ("collapse",)}),
        ("Video", {"fields": ("video_url",), "classes": ("collapse",)}),
        ("Links & Publishing", {"fields": ("link", "sort_order", "is_published")}),
    )


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "subject", "status", "created_at")
    list_editable = ("status",)
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "phone", "subject", "message")
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("name", "email", "phone", "subject")}),
        ("Message", {"fields": ("message",)}),
        ("Workflow", {"fields": ("status", "created_at")}),
    )
    actions = ["mark_in_progress", "mark_resolved"]

    @admin.action(description="Mark selected as In Progress")
    def mark_in_progress(self, request, queryset):
        queryset.update(status="in_progress")

    @admin.action(description="Mark selected as Resolved")
    def mark_resolved(self, request, queryset):
        queryset.update(status="resolved")


@admin.register(Enrolment)
class EnrolmentAdmin(admin.ModelAdmin):
    list_display = (
        "student_name", "level", "course", "subject", "phone", "status", "created_at",
    )
    list_editable = ("status",)
    list_filter = ("status", "level", "created_at")
    search_fields = ("student_name", "email", "phone", "subject", "notes")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Student", {"fields": ("student_name", "email", "phone", "level")}),
        ("Class", {"fields": ("course", "subject", "schedule", "notes")}),
        ("Workflow", {"fields": ("status", "meet_link", "created_at", "updated_at")}),
    )
    actions = ["approve_and_notify", "mark_rejected", "mark_completed"]

    @admin.action(description="Approve & create + email Google Meet link")
    def approve_and_notify(self, request, queryset):
        """Approve enrolments, auto-create a Google Meet link (when Google
        service account is configured), and email it to the student.

        When Google is not configured yet, the enrolment is still marked
        approved and the admin can paste a Meet link manually in the
        meet_link field, then re-run this action to email it.
        """
        from datetime import datetime, timedelta
        from django.core.mail import send_mail
        from django.conf import settings

        from hub.meet import create_meet_link, is_configured

        meet_configured = is_configured()
        count = 0
        emailed = 0
        for enrolment in queryset.filter(status__in=["pending", "rejected"]):
            enrolment.status = "approved"

            # Auto-create a Meet link if Google is configured and none exists.
            if meet_configured and not enrolment.meet_link:
                # Default to tomorrow 10:00 EAT if no schedule hint parsed.
                start_dt = datetime.now() + timedelta(days=1)
                start_dt = start_dt.replace(hour=10, minute=0, second=0, microsecond=0)
                link = create_meet_link(
                    summary=f"Jordan Design Hub — {enrolment.student_name}",
                    start_dt=start_dt,
                    duration_minutes=60,
                    attendee_email=enrolment.email,
                    description=f"Online class for {enrolment.student_name} ({enrolment.get_level_display()}). "
                                f"Subject: {enrolment.subject or 'n/a'}.",
                )
                if link:
                    enrolment.meet_link = link

            enrolment.save()

            # Email the student their confirmation + Meet link.
            if enrolment.meet_link or meet_configured:
                try:
                    send_mail(
                        subject="Your Jordan Design Hub class is approved — Google Meet link inside",
                        message=self._approval_email_body(enrolment),
                        from_email=settings.CONTACT_EMAIL,
                        recipient_list=[enrolment.email],
                        fail_silently=True,
                    )
                    emailed += 1
                except Exception:
                    pass
            count += 1

        note = (
            f"Approved {count} enrolment(s); emailed {emailed}. "
            + ("Meet links created automatically." if meet_configured
               else "Google Meet not configured — paste meet_link manually then re-run to email.")
        )
        self.message_user(request, note)

    @staticmethod
    def _approval_email_body(enrolment) -> str:
        """Render the plain-text approval email body for a student."""
        site = SiteSettings.get()
        meet_line = f"\nJoin your class on Google Meet:\n{enrolment.meet_link}\n" if enrolment.meet_link else ""
        return (
            f"Hello {enrolment.student_name},\n\n"
            f"Your enrolment at Jordan Design Hub is approved. {meet_line}\n"
            f"If you have not yet paid, please complete payment before the first session:\n"
            f"  MTN MoMo: {site.momo_number} ({site.momo_name})\n"
            f"  Airtel Money: {site.airtel_number} ({site.airtel_name})\n"
            f"  Then confirm on WhatsApp: https://wa.me/{site.whatsapp_number}\n\n"
            f"We look forward to seeing you in class.\n\n"
            f"— Jordan Design Hub"
        )

    @admin.action(description="Mark selected as Rejected")
    def mark_rejected(self, request, queryset):
        updated = queryset.update(status="rejected")
        self.message_user(request, f"Rejected {updated} enrolment(s).")

    @admin.action(description="Mark selected as Completed")
    def mark_completed(self, request, queryset):
        updated = queryset.update(status="completed")
        self.message_user(request, f"Marked {updated} enrolment(s) as completed.")


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Hero / Intro Copy", {"fields": ("hero_subtitle", "academy_intro", "services_intro", "gallery_intro")}),
        ("Contact Channels", {"fields": ("whatsapp_number", "contact_email", "address")}),
        ("Payment Details (shown after enrolment)", {"fields": ("momo_name", "momo_number", "airtel_name", "airtel_number", "payment_instructions")}),
    )

    def has_add_permission(self, request):
        # Singleton: only one settings row is ever needed.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
