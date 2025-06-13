"""
URL configuration for django_app project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def health_check(request):
    """Simple health check endpoint."""
    return JsonResponse({"status": "healthy"})

def root_view(request):
    """Root endpoint."""
    return JsonResponse({
        "message": "Hello from Django with OpenTelemetry!",
        "service": "django-example-app",
        "version": "1.0.0"
    })

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', root_view, name='root'),
    path('health/', health_check, name='health'),
    path('api/', include('api.urls')),
] 