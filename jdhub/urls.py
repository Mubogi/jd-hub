"""
URL configuration for jdhub project.

Serves the marketing site (hub app), Django admin, a sitemap, and the PWA
manifest + service worker (served as static assets in production).
"""
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

from hub import views
from hub.sitemaps import sitemaps

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("enrol/", views.enrol, name="enrol"),
    path("contact/", views.contact, name="contact"),
    path("systems/<slug:slug>/pdf/", views.system_pdf, name="system_pdf"),
    path("courses/<slug:slug>/lessons/<str:track>/pdf/", views.course_lessons_pdf, name="course_lessons_pdf"),
    path("robots.txt", views.robots, name="robots"),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
]

# Serve media + a couple of PWA root-level files in development.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    # In production (Render), serve committed media files (gallery images,
    # system screenshots) directly from the filesystem. Generated PDFs are
    # streamed by their own views, so only static media needs this.
    from django.views.static import serve as serve_media

    urlpatterns += [
        re_path(
            r"^media/(?P<path>.*)$",
            serve_media,
            {"document_root": settings.MEDIA_ROOT},
        ),
    ]

# PWA manifest + service worker live at site root (re-served from static).
def _serve_root_static(name: str):
    from django.contrib.staticfiles.views import serve

    def _view(request):
        return serve(request, f"hub/{name}")

    return _view


urlpatterns += [
    path("manifest.webmanifest", _serve_root_static("manifest.webmanifest")),
    path("sw.js", _serve_root_static("sw.js")),
]


admin.site.site_header = "Jordan Design Hub Administration"
admin.site.site_title = "Jordan Design Hub Admin"
admin.site.index_title = "Ecosystem Management"
