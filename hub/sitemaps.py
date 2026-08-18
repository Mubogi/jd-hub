"""Sitemap configuration for Jordan Design Hub."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from hub.models import Course, System


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["home", "enrol", "contact"]

    def location(self, item):
        return reverse(item)


class SystemSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return System.objects.filter(is_published=True)

    def location(self, obj):
        return reverse("system_pdf", kwargs={"slug": obj.slug})

    def lastmod(self, obj):
        return obj.updated_at


class CourseSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Course.objects.filter(is_published=True)

    def location(self, obj):
        # Courses are shown on the home page academy section.
        return f"{reverse('home')}#academy"

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "systems": SystemSitemap,
    "courses": CourseSitemap,
}
