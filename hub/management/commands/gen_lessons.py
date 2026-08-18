"""Generate lesson-outline PDFs for all published courses and tracks."""
from django.core.management.base import BaseCommand
from hub.lesson_pdf import TRACKS, build_lesson_pdf
from hub.models import Course


class Command(BaseCommand):
    help = "Generate lesson-outline PDFs for every course x track (cached under media/lesson_docs/)."

    def handle(self, *args, **options):
        courses = list(Course.objects.filter(is_published=True))
        if not courses:
            self.stdout.write(self.style.WARNING("No published courses found."))
            return
        self.stdout.write(self.style.MIGRATE_HEADING(
            f"Generating lesson PDFs for {len(courses)} course(s) x {len(TRACKS)} track(s)..."
        ))
        count = 0
        for course in courses:
            for track_key in TRACKS:
                path = build_lesson_pdf(course, track_key)
                count += 1
                self.stdout.write(f"  ✓ {path.name}")
        self.stdout.write(self.style.SUCCESS(f"\nGenerated {count} lesson PDFs."))
