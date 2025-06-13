"""
Core tracing setup module with idempotent initialization.
"""

import os
import logging
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from threading import Lock

from opentelemetry import trace
from opentelemetry.trace import get_tracer_provider
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.urllib3 import URLLib3Instrumentor

from .exporters import ExporterType, create_exporter

logger = logging.getLogger(__name__)

# Global state for idempotent setup
_tracer_initialized = False
_tracer_lock = Lock()


@dataclass
class TracingConfig:
    """Configuration for OpenTelemetry tracing setup."""

    service_name: str
    service_version: str = "1.0.0"
    exporter_type: Union[ExporterType, str] = ExporterType.CONSOLE
    exporter_endpoint: Optional[str] = None
    exporter_headers: Optional[Dict[str, str]] = None
    sample_rate: float = 1.0
    environment: str = "development"
    additional_resource_attributes: Optional[Dict[str, str]] = None

    @classmethod
    def from_env(cls, service_name: Optional[str] = None) -> "TracingConfig":
        """Create TracingConfig from environment variables."""
        return cls(
            service_name=service_name or os.getenv("OTEL_SERVICE_NAME", "unknown-service"),
            service_version=os.getenv("OTEL_SERVICE_VERSION", "1.0.0"),
            exporter_type=os.getenv("OTEL_EXPORTER_TYPE", "console"),
            exporter_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"),
            exporter_headers=_parse_headers(os.getenv("OTEL_EXPORTER_OTLP_HEADERS", "")),
            sample_rate=float(os.getenv("OTEL_SAMPLE_RATE", "1.0")),
            environment=os.getenv("OTEL_ENVIRONMENT", "development"),
            additional_resource_attributes=_parse_resource_attributes(
                os.getenv("OTEL_RESOURCE_ATTRIBUTES", "")
            ),
        )


def _parse_headers(headers_str: str) -> Optional[Dict[str, str]]:
    """Parse header string in format 'key1=value1,key2=value2'."""
    if not headers_str:
        return None

    headers = {}
    for header in headers_str.split(","):
        if "=" in header:
            key, value = header.split("=", 1)
            headers[key.strip()] = value.strip()
    return headers


def _parse_resource_attributes(attrs_str: str) -> Optional[Dict[str, str]]:
    """Parse resource attributes string in format 'key1=value1,key2=value2'."""
    if not attrs_str:
        return None

    attributes = {}
    for attr in attrs_str.split(","):
        if "=" in attr:
            key, value = attr.split("=", 1)
            attributes[key.strip()] = value.strip()
    return attributes


def is_tracer_already_initialized() -> bool:
    """
    Check if OpenTelemetry tracer is already initialized by external code.
    
    This function checks if a TracerProvider is already set up in the system,
    which could indicate that another library or application code has already
    configured OpenTelemetry tracing.
    
    Returns:
        bool: True if a TracerProvider is already initialized, False otherwise.
    """
    try:
        tracer_provider = get_tracer_provider()
        return isinstance(tracer_provider, TracerProvider)
    except Exception as e:
        logger.debug(f"Error checking tracer provider: {e}")
        return False


def setup_tracing(config: Optional[TracingConfig] = None, force_reinit: bool = False) -> trace.Tracer:
    """
    Set up OpenTelemetry tracing with idempotent initialization.

    Args:
        config: TracingConfig instance. If None, will be created from environment variables.
        force_reinit: If True, forces re-initialization even if already set up.

    Returns:
        Configured tracer instance.

    Raises:
        ValueError: If configuration is invalid.
        RuntimeError: If OpenTelemetry is already initialized by external code.
    """
    global _tracer_initialized

    with _tracer_lock:
        # Check if our library has already initialized tracing
        if _tracer_initialized and not force_reinit:
            logger.info("Tracing already initialized by this library, returning existing tracer")
            return trace.get_tracer(__name__)

        # Check if OpenTelemetry is already initialized by external code
        if is_tracer_already_initialized() and not force_reinit:
            logger.warning(
                "OpenTelemetry TracerProvider is already initialized by external code. "
                "This may cause conflicts. Use force_reinit=True to override, or ensure "
                "only one tracing setup is used in your application."
            )
            # Return a tracer from the existing provider instead of failing
            return trace.get_tracer(__name__)

        if config is None:
            config = TracingConfig.from_env()

        if is_tracer_already_initialized() and force_reinit:
            logger.warning(
                f"Force re-initializing tracing for service: {config.service_name}. "
                "This will override existing OpenTelemetry configuration."
            )
        else:
            logger.info(f"Initializing tracing for service: {config.service_name}")

        # Create resource with service information
        resource_attributes = {
            SERVICE_NAME: config.service_name,
            SERVICE_VERSION: config.service_version,
            "environment": config.environment,
        }

        if config.additional_resource_attributes:
            resource_attributes.update(config.additional_resource_attributes)

        resource = Resource.create(resource_attributes)

        # Create tracer provider
        tracer_provider = TracerProvider(resource=resource)

        # Create and configure exporter
        try:
            exporter = create_exporter(
                exporter_type=config.exporter_type,
                endpoint=config.exporter_endpoint,
                headers=config.exporter_headers,
            )

            # Add span processor
            span_processor = BatchSpanProcessor(exporter)
            tracer_provider.add_span_processor(span_processor)

        except Exception as e:
            logger.error(f"Failed to create exporter: {e}")
            raise ValueError(f"Invalid exporter configuration: {e}")

        # Set the tracer provider
        trace.set_tracer_provider(tracer_provider)

        # Instrument common HTTP libraries
        _instrument_http_libraries()

        _tracer_initialized = True
        logger.info("Tracing setup completed successfully")

        return trace.get_tracer(__name__)


def _instrument_http_libraries() -> None:
    """Instrument common HTTP libraries for automatic tracing."""
    try:
        if not RequestsInstrumentor().is_instrumented_by_opentelemetry:
            RequestsInstrumentor().instrument()
            logger.debug("Instrumented requests library")
    except Exception as e:
        logger.warning(f"Failed to instrument requests library: {e}")

    try:
        if not URLLib3Instrumentor().is_instrumented_by_opentelemetry:
            URLLib3Instrumentor().instrument()
            logger.debug("Instrumented urllib3 library")
    except Exception as e:
        logger.warning(f"Failed to instrument urllib3 library: {e}")


def get_tracer(name: str = __name__) -> trace.Tracer:
    """
    Get a tracer instance.

    Args:
        name: Name for the tracer.

    Returns:
        Tracer instance.
    """
    return trace.get_tracer(name)


def is_initialized() -> bool:
    """Check if tracing has been initialized."""
    return _tracer_initialized


def reset_tracing() -> None:
    """Reset tracing state (mainly for testing)."""
    global _tracer_initialized
    with _tracer_lock:
        _tracer_initialized = False
