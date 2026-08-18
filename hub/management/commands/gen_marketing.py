"""Generate branded marketing / advert images for the website and social media."""
from django.core.management.base import BaseCommand
from hub.marketing_images import generate_all


class Command(BaseCommand):
    help = "Generate branded marketing advert images (square, story, landscape, banner)."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Generating marketing images..."))
        paths = generate_all()
        for p in paths:
            self.stdout.write(f"  ✓ {p.name} ({p.stat().st_size // 1024} KB)")
        self.stdout.write(self.style.SUCCESS(f"\nGenerated {len(paths)} images in {paths[0].parent}."))
        self.stdout.write("Tip: copy them to media/gallery/ and re-run seed_demo to refresh the site gallery.")
