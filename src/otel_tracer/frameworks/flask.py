"""
Flask framework instrumentation module.
"""

import logging
from typing import Optional, Any, Callable

from ..tracer import TracingConfig, setup_tracing

# Import FlaskInstrumentor at module level for testing purposes
# This will be None if dependencies are not installed
try:
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
except ImportError:
    FlaskInstrumentor = None  # type: ignore[assignment]

# Import setup_database_tracing at module level for testing purposes
try:
    from ..database import setup_database_tracing
except ImportError:
    setup_database_tracing = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)

# Global flag to prevent double instrumentation
_flask_instrumented = False

# Add type annotations for these at the top
FlaskInstrumentor: Optional[type] = FlaskInstrumentor
setup_database_tracing: Optional[Callable[..., None]] = setup_database_tracing


def instrument_flask(
        app: Optional[Any] = None,
        config: Optional[TracingConfig] = None,
        **kwargs: Any,
) -> None:
    """
    Instrument a Flask application for OpenTelemetry tracing.

    Args:
        app: Flask application instance. If None, will instrument all Flask apps.
        config: TracingConfig instance. If None, will be created from environment.
        **kwargs: Additional instrumentation parameters.
    """
    global _flask_instrumented

    if _flask_instrumented:
        logger.info("Flask already instrumented, skipping")
        return

    if FlaskInstrumentor is None:
        raise ImportError(
            "Flask instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-flask"
        )

    # Setup core tracing first
    setup_tracing(config)

    # Instrument Flask
    logger.info("Instrumenting Flask application")

    if app is not None:
        # Instrument specific app
        FlaskInstrumentor().instrument_app(app, **kwargs)
    else:
        # Instrument all Flask apps
        FlaskInstrumentor().instrument(**kwargs)

    _flask_instrumented = True
    logger.info("Flask instrumentation completed")


def setup_flask_tracing(
        app: Any,
        service_name: Optional[str] = None,
        config: Optional[TracingConfig] = None,
        enable_database_tracing: bool = True,
        excluded_urls: Optional[list] = None,
        **kwargs: Any,
) -> Any:
    """
    Complete Flask tracing setup with database instrumentation.

    Args:
        app: Flask application instance.
        service_name: Service name for tracing. If None, will use app name or default.
        config: TracingConfig instance. If None, will be created.
        enable_database_tracing: Whether to enable database tracing.
        excluded_urls: List of URL patterns to exclude from tracing.
        **kwargs: Additional configuration parameters.
        
    Returns:
        The configured tracer instance.
    """
    if config is None:
        # Try to get service name from Flask app
        if service_name is None and hasattr(app, 'name'):
            service_name = app.name

        config = TracingConfig.from_env(service_name=service_name)

    # Setup database tracing if enabled
    if enable_database_tracing:
        setup_database_tracing()

    # Configure excluded URLs
    if excluded_urls:
        # Strip leading slashes from URLs and join them
        cleaned_urls = [url.lstrip('/') for url in excluded_urls]
        kwargs['excluded_urls'] = ','.join(cleaned_urls)
    elif 'excluded_urls' not in kwargs:
        # Default excluded URLs for Flask
        kwargs['excluded_urls'] = 'health,metrics,favicon.ico'

    # Instrument Flask
    instrument_flask(app=app, config=config, **kwargs)
    
    # Return the tracer for the user
    from opentelemetry import trace
    return trace.get_tracer(__name__)


def is_instrumented() -> bool:
    """Check if Flask has been instrumented."""
    return _flask_instrumented


def reset_flask_instrumentation() -> None:
    """Reset Flask instrumentation state (mainly for testing)."""
    global _flask_instrumented
    _flask_instrumented = False