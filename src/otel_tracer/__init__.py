"""
otel-tracer: Vendor-agnostic OpenTelemetry tracing library for Python web frameworks.

This library provides a simple, unified interface for setting up OpenTelemetry tracing
across different Python web frameworks (Flask, Django, FastAPI) with support for
multiple observability backends.
"""

from .tracer import TracingConfig, setup_tracing, is_initialized, reset_tracing
from .exporters import ExporterType, create_exporter, VendorConfigs
from .database import setup_database_tracing

# Import framework-specific functions
from .frameworks.flask import setup_flask_tracing
from .frameworks.django import setup_django_tracing  
from .frameworks.fastapi import setup_fastapi_tracing

# Import framework modules for advanced usage
from .frameworks import flask, django, fastapi

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

__all__ = [
    # Core functionality
    "TracingConfig",
    "setup_tracing",
    "is_initialized", 
    "reset_tracing",
    "ExporterType",
    "create_exporter",
    "VendorConfigs",
    "setup_database_tracing",
    
    # Simplified framework functions (main API)
    "setup_flask_tracing",
    "setup_django_tracing",
    "setup_fastapi_tracing",
    
    # Framework modules for advanced usage
    "flask",
    "django", 
    "fastapi",
]
