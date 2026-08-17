"""
Django admin configuration for JD Hub.

Provides rich, grouped management for all content so non-developers can update
the site without touching code.
"""
from django.contrib import admin

from hub.models import (
    ContactSubmission,
    Course,
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
