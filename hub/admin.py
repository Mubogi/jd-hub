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

    @admin.action(description="Approve & email Meet link to student")
    def approve_and_notify(self, request, queryset):
        """Approve enrolments and (once Google Meet is wired up) email the link.

        Today this marks the enrolment approved and, if a meet_link is present,
        emails it to the student. When the Google Calendar service account is
        configured, approving will also create the Meet link automatically.
        """
        from django.core.mail import send_mail
        from django.conf import settings

        count = 0
        for enrolment in queryset.filter(status__in=["pending", "rejected"]):
            enrolment.status = "approved"
            enrolment.save()
            # Email the student their confirmation (and Meet link if set).
            if enrolment.meet_link:
                try:
                    send_mail(
                        subject="Your Jordan Design Hub class is approved — Google Meet link inside",
                        message=(
                            f"Hello {enrolment.student_name},\n\n"
                            f"Your enrolment is approved. Join your class on Google Meet:\n"
                            f"{enrolment.meet_link}\n\n"
                            f"If you have not yet paid, please complete payment via WhatsApp "
                            f"before the first session.\n\n"
                            f"— Jordan Design Hub"
                        ),
                        from_email=settings.CONTACT_EMAIL,
                        recipient_list=[enrolment.email],
                        fail_silently=True,
                    )
                except Exception:
                    pass
            count += 1
        self.message_user(request, f"Approved {count} enrolment(s).")

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
    )

    def has_add_permission(self, request):
        # Singleton: only one settings row is ever needed.
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
