"""
Exporter configuration module supporting multiple observability backends.
"""

import logging
from enum import Enum
from typing import Optional, Dict, Any, Union

from opentelemetry.sdk.trace.export import SpanExporter, ConsoleSpanExporter

# Import exporters at module level for testing purposes
# These will be None if dependencies are not installed
try:
    from opentelemetry.exporter.jaeger.thrift import JaegerExporter
except ImportError:
    JaegerExporter = None

try:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter as OTLPHTTPSpanExporter
except ImportError:
    OTLPHTTPSpanExporter = None

try:
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter as OTLPGRPCSpanExporter
except ImportError:
    OTLPGRPCSpanExporter = None

try:
    from opentelemetry.sdk.trace.export import MultiSpanExporter
except ImportError:
    MultiSpanExporter = None

# For backward compatibility, expose the HTTP version as OTLPSpanExporter
OTLPSpanExporter = OTLPHTTPSpanExporter

logger = logging.getLogger(__name__)


class ExporterType(Enum):
    """Supported exporter types."""
    CONSOLE = "console"
    JAEGER = "jaeger"
    OTLP = "otlp"
    OTLP_HTTP = "otlp_http"
    OTLP_GRPC = "otlp_grpc"
    MULTI = "multi"  # Support for multiple exporters


def create_exporter(
        exporter_type: Union[ExporterType, str],
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
) -> SpanExporter:
    """
    Create an exporter based on the specified type and configuration.

    Args:
        exporter_type: Type of exporter to create.
        endpoint: Endpoint URL for the exporter.
        headers: Additional headers for the exporter.
        **kwargs: Additional configuration parameters.

    Returns:
        Configured SpanExporter instance.

    Raises:
        ValueError: If exporter type is not supported or configuration is invalid.
        ImportError: If required dependencies are not installed.
    """
    if isinstance(exporter_type, str):
        try:
            exporter_type = ExporterType(exporter_type.lower())
        except ValueError:
            raise ValueError(f"Unsupported exporter type: {exporter_type}")

    if exporter_type == ExporterType.CONSOLE:
        return _create_console_exporter(**kwargs)

    elif exporter_type == ExporterType.JAEGER:
        return _create_jaeger_exporter(endpoint, headers, **kwargs)

    elif exporter_type in (ExporterType.OTLP, ExporterType.OTLP_HTTP):
        return _create_otlp_http_exporter(endpoint, headers, **kwargs)

    elif exporter_type == ExporterType.OTLP_GRPC:
        return _create_otlp_grpc_exporter(endpoint, headers, **kwargs)

    elif exporter_type == ExporterType.MULTI:
        return _create_multi_exporter(endpoint, headers, **kwargs)

    else:
        raise ValueError(f"Unsupported exporter type: {exporter_type}")


def _create_console_exporter(**kwargs: Any) -> SpanExporter:
    """Create a console exporter for development/debugging."""
    logger.info("Creating console exporter")
    return ConsoleSpanExporter()


def _create_jaeger_exporter(
        endpoint: Optional[str] = None, 
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any
) -> SpanExporter:
    """Create a Jaeger exporter."""
    if JaegerExporter is None:
        raise ImportError(
            "Jaeger exporter dependencies not installed. "
            "Install with: pip install opentelemetry-exporter-jaeger"
        )

    # Default Jaeger endpoint
    agent_host_name = kwargs.get("agent_host_name", "localhost")
    agent_port = kwargs.get("agent_port", 6831)

    if endpoint:
        # Parse endpoint if provided
        # This is a simplified parser - in production you might want more robust URL parsing
        if "://" in endpoint:
            # HTTP endpoint format
            collector_endpoint = endpoint
            logger.info(f"Creating Jaeger HTTP exporter with endpoint: {collector_endpoint}")
            exporter_kwargs = {"collector_endpoint": collector_endpoint}
            if headers:
                exporter_kwargs.update(kwargs)  # Add any additional headers/auth
            return JaegerExporter(**exporter_kwargs)
        else:
            # Assume host:port format
            parts = endpoint.split(":")
            if len(parts) == 2:
                agent_host_name = parts[0]
                agent_port = int(parts[1])

    logger.info(f"Creating Jaeger UDP exporter with agent: {agent_host_name}:{agent_port}")
    return JaegerExporter(
        agent_host_name=agent_host_name,
        agent_port=agent_port,
    )


def _create_otlp_http_exporter(
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
) -> SpanExporter:
    """Create an OTLP HTTP exporter."""
    if OTLPHTTPSpanExporter is None:
        raise ImportError(
            "OTLP HTTP exporter dependencies not installed. "
            "Install with: pip install opentelemetry-exporter-otlp-proto-http"
        )

    # Default endpoint
    if not endpoint:
        endpoint = "http://localhost:4318/v1/traces"

    logger.info(f"Creating OTLP HTTP exporter with endpoint: {endpoint}")

    exporter_kwargs = {"endpoint": endpoint}
    if headers:
        exporter_kwargs["headers"] = headers

    # Add any additional kwargs
    exporter_kwargs.update(kwargs)

    return OTLPHTTPSpanExporter(**exporter_kwargs)


def _create_otlp_grpc_exporter(
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
) -> SpanExporter:
    """Create an OTLP gRPC exporter."""
    if OTLPGRPCSpanExporter is None:
        raise ImportError(
            "OTLP gRPC exporter dependencies not installed. "
            "Install with: pip install opentelemetry-exporter-otlp-proto-grpc"
        )

    # Default endpoint
    if not endpoint:
        endpoint = "http://localhost:4317"

    logger.info(f"Creating OTLP gRPC exporter with endpoint: {endpoint}")

    exporter_kwargs = {"endpoint": endpoint}
    if headers:
        exporter_kwargs["headers"] = headers

    # Add any additional kwargs
    exporter_kwargs.update(kwargs)

    return OTLPGRPCSpanExporter(**exporter_kwargs)


def _create_multi_exporter(
        endpoint: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
) -> SpanExporter:
    """Create a multi-exporter that sends traces to multiple backends."""
    if MultiSpanExporter is None:
        raise ImportError("MultiSpanExporter not available in OpenTelemetry SDK")

    # Create default exporters: Jaeger + OTLP
    exporters = []
    
    # Add Jaeger exporter
    try:
        jaeger_exporter = _create_jaeger_exporter(endpoint=endpoint, headers=headers, **kwargs)
        exporters.append(jaeger_exporter)
        logger.info("Added Jaeger exporter to multi-exporter")
    except ImportError:
        logger.warning("Skipping Jaeger exporter - dependencies not installed")

    # Add OTLP HTTP exporter
    try:
        otlp_exporter = _create_otlp_http_exporter(endpoint=endpoint, headers=headers, **kwargs)
        exporters.append(otlp_exporter)
        logger.info("Added OTLP HTTP exporter to multi-exporter")
    except ImportError:
        logger.warning("Skipping OTLP HTTP exporter - dependencies not installed")

    if not exporters:
        # Fallback to console exporter
        logger.warning("No exporters available, falling back to console exporter")
        exporters.append(_create_console_exporter())

    logger.info(f"Creating multi-exporter with {len(exporters)} exporters")
    return MultiSpanExporter(exporters)


# Vendor-specific helper functions and configurations
class VendorConfigs:
    """Pre-configured settings for popular observability vendors."""

    @staticmethod
    def datadog(api_key: str, site: str = "datadoghq.com") -> Dict[str, Any]:
        """Configuration for Datadog."""
        if not isinstance(api_key, str):
            raise TypeError("Expected a string for API key")
        return {
            "exporter_type": ExporterType.OTLP_HTTP,
            "endpoint": f"https://trace-agent.{site}/v0.4/traces",
            "headers": {"DD-API-KEY": api_key},
        }

    @staticmethod
    def dynatrace(endpoint: str, token: str) -> Dict[str, Any]:
        """Configuration for Dynatrace."""
        return {
            "exporter_type": ExporterType.OTLP_HTTP,
            "endpoint": f"{endpoint}/v2/otlp",
            "headers": {"Authorization": f"Api-Token {token}"},
        }

    @staticmethod
    def new_relic(license_key: str) -> Dict[str, Any]:
        """Configuration for New Relic."""
        return {
            "exporter_type": ExporterType.OTLP_HTTP,
            "endpoint": "https://otlp.nr-data.net:4318/v1/traces",
            "headers": {"api-key": license_key},
        }

    @staticmethod
    def honeycomb(api_key: str, dataset: str = "unknown_service") -> Dict[str, Any]:
        """Configuration for Honeycomb."""
        return {
            "exporter_type": ExporterType.OTLP_HTTP,
            "endpoint": "https://api.honeycomb.io/v1/traces",
            "headers": {
                "x-honeycomb-team": api_key,
                "x-honeycomb-dataset": dataset,
            },
        }

    @staticmethod
    def aws_x_ray() -> Dict[str, Any]:
        """Configuration for AWS X-Ray (requires additional setup)."""
        return {
            "exporter_type": ExporterType.OTLP_GRPC,
            "endpoint": "http://localhost:4317",  # AWS X-Ray daemon
        }

    @staticmethod
    def google_cloud_trace(project_id: str) -> Dict[str, Any]:
        """Configuration for Google Cloud Trace."""
        return {
            "exporter_type": ExporterType.OTLP_GRPC,
            "endpoint": "https://cloudtrace.googleapis.com:443",
            "headers": {
                "x-goog-project-id": project_id,
            },
        }

    @staticmethod
    def elastic_apm(secret_token: str, server_url: str) -> Dict[str, Any]:
        """Configuration for Elastic APM."""
        return {
            "exporter_type": ExporterType.OTLP_HTTP,
            "endpoint": f"{server_url}/intake/v2/otlp",
            "headers": {
                "Authorization": f"Bearer {secret_token}",
            },
        }

    @staticmethod
    def jaeger_cloud(endpoint: str, username: str = None, password: str = None) -> Dict[str, Any]:
        """Configuration for Jaeger Cloud or self-hosted Jaeger."""
        config = {
            "exporter_type": ExporterType.JAEGER,
            "endpoint": endpoint,
        }
        if username and password:
            import base64
            auth_string = base64.b64encode(f"{username}:{password}".encode()).decode()
            config["headers"] = {"Authorization": f"Basic {auth_string}"}
        return config
