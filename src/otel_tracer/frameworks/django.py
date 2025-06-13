"""
Django framework instrumentation module.
"""

import logging
from typing import Optional, Any

from ..tracer import TracingConfig, setup_tracing

logger = logging.getLogger(__name__)

# Global flag to prevent double instrumentation
_django_instrumented = False


def instrument_django(
        config: Optional[TracingConfig] = None,
        **kwargs: Any,
) -> None:
    """
    Instrument Django for OpenTelemetry tracing.

    Args:
        config: TracingConfig instance. If None, will be created from environment.
        **kwargs: Additional instrumentation parameters.
    """
    global _django_instrumented

    if _django_instrumented:
        logger.info("Django already instrumented, skipping")
        return

    try:
        from opentelemetry.instrumentation.django import DjangoInstrumentor
    except ImportError:
        raise ImportError(
            "Django instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-django"
        )

    # Setup core tracing first
    setup_tracing(config)

    # Instrument Django
    logger.info("Instrumenting Django application")
    DjangoInstrumentor().instrument(**kwargs)

    _django_instrumented = True
    logger.info("Django instrumentation completed")


def setup_django_tracing(
        service_name: Optional[str] = None,
        config: Optional[TracingConfig] = None,
        enable_database_tracing: bool = True,
        excluded_urls: Optional[list] = None,
        **kwargs: Any,
) -> Any:
    """
    Complete Django tracing setup with database instrumentation.

    Args:
        service_name: Service name for tracing.
        config: TracingConfig instance. If None, will be created.
        enable_database_tracing: Whether to enable database tracing.
        excluded_urls: List of URL patterns to exclude from tracing.
        **kwargs: Additional configuration parameters.
        
    Returns:
        The configured tracer instance.
    """
    if config is None:
        # Try to get service name from Django settings
        if service_name is None:
            try:
                from django.conf import settings
                service_name = getattr(settings, 'OTEL_SERVICE_NAME', None)
            except ImportError:
                pass

        config = TracingConfig.from_env(service_name=service_name)

    # Setup database tracing if enabled
    if enable_database_tracing:
        from ..database import setup_database_tracing
        setup_database_tracing()

    # Configure excluded URLs
    if excluded_urls:
        kwargs['excluded_urls'] = ','.join(excluded_urls)
    elif 'excluded_urls' not in kwargs:
        # Default excluded URLs for Django
        kwargs['excluded_urls'] = 'admin,health,metrics,favicon.ico'

    # Instrument Django
    instrument_django(config=config, **kwargs)
    
    # Return the tracer for the user
    from opentelemetry import trace
    return trace.get_tracer(__name__)


def setup_django_middleware() -> str:
    """
    Get the Django middleware class path for manual configuration.

    Returns:
        Middleware class path to add to MIDDLEWARE setting.
    """
    return "opentelemetry.instrumentation.django.middleware.otel_middleware"


def configure_django_settings() -> dict:
    """
    Get recommended Django settings for OpenTelemetry.

    Returns:
        Dictionary of Django settings to add to your settings.py
    """
    return {
        'OTEL_PYTHON_DJANGO_INSTRUMENT': True,
        'OTEL_PYTHON_DJANGO_TRACED_REQUEST_ATTRS': 'path_info,content_type,method',
        'OTEL_PYTHON_DJANGO_EXCLUDED_URLS': 'health,metrics,favicon.ico',
    }


def is_instrumented() -> bool:
    """Check if Django has been instrumented."""
    return _django_instrumented


def reset_django_instrumentation() -> None:
    """Reset Django instrumentation state (mainly for testing)."""
    global _django_instrumented
    _django_instrumented = False