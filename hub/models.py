"""
Models for the JD Hub core app.

Everything here is editable from the Django admin so content managers can add
systems, courses, services, media, and review contact submissions without
touching code.
"""
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.text import slugify


class System(models.Model):
    """A flagship software product showcased on the home page."""

    CATEGORY_CHOICES = [
        ("education", "Education / School"),
        ("finance", "Finance / SACCO"),
        ("database", "Database / DBMS"),
        ("custom", "Custom Software"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    tagline = models.CharField(max_length=255, help_text="One-line value proposition.")
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="custom")
    icon = models.CharField(
        max_length=50,
        default="fa-solid fa-microchip",
        help_text="FontAwesome class, e.g. 'fa-solid fa-school'.",
    )
    features = models.TextField(
        blank=True,
        help_text="One feature per line. Rendered as a checklist.",
    )
    tech_stack = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated, e.g. 'Django, PWA, SQLite, Bootstrap'.",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "Flagship System"
        verbose_name_plural = "Flagship Systems"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def feature_list(self) -> list[str]:
        return [line.strip() for line in self.features.splitlines() if line.strip()]

    @property
    def tech_list(self) -> list[str]:
        return [t.strip() for t in self.tech_stack.split(",") if t.strip()]


class Course(models.Model):
    """A course offered by the Academy & Tutoring Hub."""

    CATEGORY_CHOICES = [
        ("stem", "STEM"),
        ("software", "Software"),
        ("financials", "Financials"),
        ("ai", "AI"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="software")
    icon = models.CharField(
        max_length=50,
        default="fa-solid fa-graduation-cap",
        help_text="FontAwesome class.",
    )
    level = models.CharField(max_length=50, blank=True, help_text="e.g. Beginner, Intermediate.")
    duration = models.CharField(max_length=80, blank=True, help_text="e.g. 8 weeks.")
    curriculum = models.TextField(
        blank=True,
        help_text="One topic per line.",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "Course"
        verbose_name_plural = "Courses"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def curriculum_list(self) -> list[str]:
        return [line.strip() for line in self.curriculum.splitlines() if line.strip()]


class Service(models.Model):
    """A consultancy / professional service offering."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default="fa-solid fa-screwdriver-wrench")
    deliverables = models.TextField(
        blank=True,
        help_text="One deliverable per line.",
    )
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["sort_order", "pk"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def deliverable_list(self) -> list[str]:
        return [line.strip() for line in self.deliverables.splitlines() if line.strip()]


class MediaItem(models.Model):
    """A portfolio / gallery item — image poster or embedded video."""

    MEDIA_TYPES = [
        ("image", "Image / Poster"),
        ("video", "Video Embed"),
    ]

    title = models.CharField(max_length=200)
    caption = models.CharField(max_length=255, blank=True)
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPES, default="image")
    image = models.ImageField(upload_to="gallery/", blank=True, null=True)
    video_url = models.URLField(
        blank=True,
        help_text="YouTube (or other embeddable) URL for video items.",
    )
    link = models.URLField(blank=True, help_text="Optional external link / project page.")
    sort_order = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-pk"]
        verbose_name = "Media Item"
        verbose_name_plural = "Media Portfolio"

    def __str__(self) -> str:
        return self.title

    @property
    def youtube_embed_url(self) -> str:
        """Return an embeddable YouTube URL if video_url is a YouTube link."""
        url = self.video_url or ""
        if "youtu.be/" in url:
            vid = url.split("youtu.be/")[-1].split("?")[0]
            return f"https://www.youtube.com/embed/{vid}"
        if "youtube.com/watch?v=" in url:
            vid = url.split("watch?v=")[-1].split("&")[0]
            return f"https://www.youtube.com/embed/{vid}"
        if "/embed/" in url:
            return url
        return ""


class ContactSubmission(models.Model):
    """A lead captured by the contact form."""

    STATUS_CHOICES = [
        ("new", "New"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("spam", "Spam"),
    ]

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200, default="General inquiry")
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"

    def __str__(self) -> str:
        return f"{self.name} — {self.subject} ({self.created_at:%Y-%m-%d})"


class SiteSettings(models.Model):
    """Singleton-style global settings (whatsapp number, intro copy, etc.)."""

    hero_subtitle = models.TextField(
        default=(
            "We build web & mobile apps (Android and iOS), run a paid online academy "
            "on Google Meet, deliver church media training, connect holiday tutors to "
            "students (Nursery–S6), design graphics, and teach AI optimization — "
            "across Uganda and beyond."
        ),
    )
    academy_intro = models.TextField(
        blank=True,
        default=(
            "Paid, instructor-led online classes on Google Meet. Enrol and pay, then "
            "join live sessions for students (Nursery–S6) and adult learners."
        ),
    )
    services_intro = models.TextField(blank=True)
    gallery_intro = models.TextField(blank=True)
    whatsapp_number = models.CharField(
        max_length=20,
        default="256754687597",
        help_text="International format, no '+', e.g. 256754687597.",
    )
    contact_email = models.EmailField(default="jordandesignhub@gmail.com")
    address = models.CharField(max_length=255, blank=True, default="Kampala, Uganda")

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self) -> str:
        return "Site Settings"

    @classmethod
    def get(cls) -> "SiteSettings":
        obj, _ = cls.objects.get_or_create(pk=1, defaults={})
        return obj


class Enrolment(models.Model):
    """A student enrolment request for the online academy / tutoring."""

    LEVEL_CHOICES = [
        ("nursery", "Nursery"),
        ("p1_p3", "P1 – P3"),
        ("p4_p6", "P4 – P6"),
        ("p7", "P7"),
        ("s1_s2", "S1 – S2"),
        ("s3_s4", "S3 – S4 (O-Level)"),
        ("s5_s6", "S5 – S6 (A-Level)"),
        ("adult", "Adult Learner"),
    ]

    STATUS_CHOICES = [
        ("pending", "Pending Payment"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("completed", "Completed"),
    ]

    student_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    course = models.ForeignKey(
        Course, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="enrolments",
        help_text="Optional — pick a course if relevant.",
    )
    subject = models.CharField(
        max_length=200, blank=True,
        help_text="Specific subject or topic (e.g. Mathematics, English, Prompt Engineering).",
    )
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default="adult")
    schedule = models.CharField(
        max_length=255, blank=True,
        help_text="Preferred day/time or 'flexible'.",
    )
    notes = models.TextField(blank=True, help_text="Anything the student wants us to know.")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    meet_link = models.URLField(
        blank=True,
        help_text="Google Meet link — set automatically when approved (once Google Meet is wired up).",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Enrolment"
        verbose_name_plural = "Enrolments"

    def __str__(self) -> str:
        return f"{self.student_name} — {self.get_level_display()} ({self.created_at:%Y-%m-%d})"
