"""
URL configuration for config project.
"""
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path
from core.main import api


def health_check(request):
    """Endpoint de santé pour Render (et load balancers)."""
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/", api.urls),
    path("health/", health_check, name="health"),
]