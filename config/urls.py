from django.contrib import admin
from django.urls import include, path

from apps.base.views import HealthCheckView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", HealthCheckView.as_view(), name="health_check"),
    path("api/v1/auth/", include("apps.users.urls.u1")),
    path("api/v1/users/", include("apps.users.urls.u1")),
]
