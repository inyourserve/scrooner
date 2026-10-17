from django.contrib import admin
from django.urls import include, path

from cockpit.views import health

admin.site.site_header = "Scrooner Operations"
admin.site.site_title = "Scrooner Operations"
admin.site.index_title = "Administration"

urlpatterns = [
    path("health/", health, name="health"),
    path("admin/", admin.site.urls),
    path("", include("cockpit.urls")),
    path("coverage/", include("coverage.urls")),
    path("ops/", include("operations.urls")),
]
