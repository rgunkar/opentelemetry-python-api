"""
FastAPI framework instrumentation module.
"""

import logging
from typing import Optional, Any

from ..tracer import TracingConfig, setup_tracing

logger = logging.getLogger(__name__)

# Global flag to prevent double instrumentation
_fastapi_instrumented = False


def instrument_fastapi(
        app: Optional[Any] = None,
        config: Optional[TracingConfig] = None,
        **kwargs: Any,
) -> None:
    """
    Instrument a FastAPI application for OpenTelemetry tracing.

    Args:
        app: FastAPI application instance. If None, will instrument all FastAPI apps.
        config: TracingConfig instance. If None, will be created from environment.
        **kwargs: Additional instrumentation parameters.
    """
    global _fastapi_instrumented

    if _fastapi_instrumented:
        logger.info("FastAPI already instrumented, skipping")
        return

    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
    except ImportError:
        raise ImportError(
            "FastAPI instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-fastapi"
        )

    # Setup core tracing first
    setup_tracing(config)

    # Instrument FastAPI
    logger.info("Instrumenting FastAPI application")

    if app is not None:
        # Instrument specific app
        FastAPIInstrumentor.instrument_app(app, **kwargs)
    else:
        # Instrument all FastAPI apps
        FastAPIInstrumentor().instrument(**kwargs)

    _fastapi_instrumented = True
    logger.info("FastAPI instrumentation completed")


def setup_fastapi_tracing(
        app: Any,
        service_name: Optional[str] = None,
        config: Optional[TracingConfig] = None,
        enable_database_tracing: bool = True,
        excluded_urls: Optional[list] = None,
        **kwargs: Any,
) -> Any:
    """
    Complete FastAPI tracing setup with database instrumentation.

    Args:
        app: FastAPI application instance.
        service_name: Service name for tracing. If None, will use app title or default.
        config: TracingConfig instance. If None, will be created.
        enable_database_tracing: Whether to enable database tracing.
        excluded_urls: List of URL patterns to exclude from tracing.
        **kwargs: Additional configuration parameters.
        
    Returns:
        The configured tracer instance.
    """
    if config is None:
        # Try to get service name from FastAPI app
        if service_name is None and hasattr(app, 'title'):
            service_name = app.title.lower().replace(' ', '-')

        config = TracingConfig.from_env(service_name=service_name)

    # Setup database tracing if enabled
    if enable_database_tracing:
        from ..database import setup_database_tracing
        setup_database_tracing()

    # Configure excluded URLs
    if excluded_urls:
        kwargs['excluded_urls'] = ','.join(excluded_urls)
    elif 'excluded_urls' not in kwargs:
        # Default excluded URLs for FastAPI
        kwargs['excluded_urls'] = 'health,metrics,docs,redoc,openapi.json,favicon.ico'

    # Instrument FastAPI
    instrument_fastapi(app=app, config=config, **kwargs)
    
    # Return the tracer for the user
    from opentelemetry import trace
    return trace.get_tracer(__name__)


def add_fastapi_middleware(
        app: Any,
        service_name: Optional[str] = None,
        config: Optional[TracingConfig] = None,
) -> None:
    """
    Add OpenTelemetry middleware to FastAPI app manually.

    This is an alternative to automatic instrumentation that gives more control.

    Args:
        app: FastAPI application instance.
        service_name: Service name for tracing.
        config: TracingConfig instance.
    """
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.starlette import StarletteInstrumentor
    except ImportError:
        raise ImportError(
            "FastAPI/Starlette instrumentation not available. "
            "Install with: pip install opentelemetry-instrumentation-fastapi"
        )

    if config is None:
        if service_name is None and hasattr(app, 'title'):
            service_name = app.title.lower().replace(' ', '-')
        config = TracingConfig.from_env(service_name=service_name)

    # Setup core tracing
    setup_tracing(config)

    # Add middleware
    logger.info("Adding OpenTelemetry middleware to FastAPI app")
    FastAPIInstrumentor.instrument_app(app)


def create_fastapi_tracer_middleware():
    """
    Create a custom middleware class for FastAPI tracing.

    Returns:
        Middleware class that can be added to FastAPI app.
    """
    try:
        from starlette.middleware.base import BaseHTTPMiddleware
        from opentelemetry import trace
        from opentelemetry.trace import Status, StatusCode
    except ImportError:
        raise ImportError("Starlette not available for custom middleware")

    class TracingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            tracer = trace.get_tracer(__name__)

            with tracer.start_as_current_span(
                    f"{request.method} {request.url.path}",
                    kind=trace.SpanKind.SERVER,
            ) as span:
                # Add request attributes
                span.set_attribute("http.method", request.method)
                span.set_attribute("http.url", str(request.url))
                span.set_attribute("http.scheme", request.url.scheme)
                span.set_attribute("http.host", request.url.hostname or "")
                span.set_attribute("http.target", request.url.path)

                try:
                    response = await call_next(request)
                    span.set_attribute("http.status_code", response.status_code)

                    if response.status_code >= 400:
                        span.set_status(Status(StatusCode.ERROR))

                    return response

                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

    return TracingMiddleware


def is_instrumented() -> bool:
    """Check if FastAPI has been instrumented."""
    return _fastapi_instrumented


def reset_fastapi_instrumentation() -> None:
    """Reset FastAPI instrumentation state (mainly for testing)."""
    global _fastapi_instrumented
    _fastapi_instrumented = False