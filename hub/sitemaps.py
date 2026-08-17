"""Sitemap configuration for JD Hub."""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from hub.models import Course, System


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return ["home", "contact"]

    def location(self, item):
        return reverse(item)


class SystemSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.7

    def items(self):
        return System.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class CourseSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Course.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "systems": SystemSitemap,
    "courses": CourseSitemap,
}
