"""
Tests for the exporter configuration functionality.
"""

import pytest
from unittest.mock import patch, MagicMock
from otel_tracer.exporters import VendorConfigs

from otel_tracer.exporters import (
    ExporterType,
    create_exporter,
    VendorConfigs,
)


class TestCreateExporter:
    def test_console_exporter(self):
        """Test console exporter creation."""
        exporter = create_exporter(ExporterType.CONSOLE)

        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        assert isinstance(exporter, ConsoleSpanExporter)

    def test_console_exporter_string(self):
        """Test console exporter creation with string type."""
        exporter = create_exporter("console")

        from opentelemetry.sdk.trace.export import ConsoleSpanExporter
        assert isinstance(exporter, ConsoleSpanExporter)

    @patch('otel_tracer.exporters.JaegerExporter')
    def test_jaeger_exporter_default(self, mock_jaeger):
        """Test Jaeger exporter with default settings."""
        mock_instance = MagicMock()
        mock_jaeger.return_value = mock_instance

        exporter = create_exporter(ExporterType.JAEGER)

        assert exporter == mock_instance
        mock_jaeger.assert_called_once_with(
            agent_host_name="localhost",
            agent_port=6831,
        )

    @patch('otel_tracer.exporters.JaegerExporter')
    def test_jaeger_exporter_with_endpoint(self, mock_jaeger):
        """Test Jaeger exporter with custom endpoint."""
        mock_instance = MagicMock()
        mock_jaeger.return_value = mock_instance

        exporter = create_exporter(
            ExporterType.JAEGER,
            endpoint="http://jaeger:14268/api/traces"
        )

        assert exporter == mock_instance
        mock_jaeger.assert_called_once_with(
            collector_endpoint="http://jaeger:14268/api/traces"
        )

    @patch('otel_tracer.exporters.JaegerExporter')
    def test_jaeger_exporter_with_host_port(self, mock_jaeger):
        """Test Jaeger exporter with host:port endpoint."""
        mock_instance = MagicMock()
        mock_jaeger.return_value = mock_instance

        exporter = create_exporter(
            ExporterType.JAEGER,
            endpoint="jaeger-host:6831"
        )

        assert exporter == mock_instance
        mock_jaeger.assert_called_once_with(
            agent_host_name="jaeger-host",
            agent_port=6831,
        )

    def test_jaeger_import_error(self):
        """Test Jaeger exporter import error handling."""
        with patch.dict('sys.modules', {'opentelemetry.exporter.jaeger.thrift': None}):
            with pytest.raises(ImportError, match="Jaeger exporter dependencies not installed"):
                create_exporter(ExporterType.JAEGER)

    @patch('otel_tracer.exporters.OTLPHTTPSpanExporter')
    def test_otlp_http_exporter_default(self, mock_otlp):
        """Test OTLP HTTP exporter with default settings."""
        mock_instance = MagicMock()
        mock_otlp.return_value = mock_instance

        exporter = create_exporter(ExporterType.OTLP_HTTP)

        assert exporter == mock_instance
        mock_otlp.assert_called_once_with(
            endpoint="http://localhost:4318/v1/traces"
        )

    @patch('otel_tracer.exporters.OTLPHTTPSpanExporter')
    def test_otlp_http_exporter_with_config(self, mock_otlp):
        """Test OTLP HTTP exporter with custom configuration."""
        mock_instance = MagicMock()
        mock_otlp.return_value = mock_instance

        headers = {"Authorization": "Bearer token"}
        endpoint = "https://api.vendor.com/v1/traces"

        exporter = create_exporter(
            ExporterType.OTLP_HTTP,
            endpoint=endpoint,
            headers=headers
        )

        assert exporter == mock_instance
        mock_otlp.assert_called_once_with(
            endpoint=endpoint,
            headers=headers
        )

    def test_otlp_http_import_error(self):
        """Test OTLP HTTP exporter import error handling."""
        with patch('otel_tracer.exporters.OTLPHTTPSpanExporter', None):
            with pytest.raises(ImportError, match="OTLP HTTP exporter dependencies not installed"):
                create_exporter(ExporterType.OTLP_HTTP)

    @patch('otel_tracer.exporters.OTLPGRPCSpanExporter')
    def test_otlp_grpc_exporter_default(self, mock_otlp):
        """Test OTLP gRPC exporter with default settings."""
        mock_instance = MagicMock()
        mock_otlp.return_value = mock_instance

        exporter = create_exporter(ExporterType.OTLP_GRPC)

        assert exporter == mock_instance
        mock_otlp.assert_called_once_with(
            endpoint="http://localhost:4317"
        )

    def test_unsupported_exporter_type(self):
        """Test error handling for unsupported exporter type."""
        with pytest.raises(ValueError, match="Unsupported exporter type"):
            create_exporter("unsupported_type")


class TestVendorConfigs:
    def test_datadog_config(self):
        """Test Datadog vendor configuration."""
        config = VendorConfigs.datadog("test-api-key")

        expected = {
            "exporter_type": ExporterType.OTLP_HTTP,
            "endpoint": "https://trace-agent.datadoghq.com/v0.4/traces",
            "headers": {"DD-API-KEY": "test-api-key"},
        }

        assert config == expected

    def test_datadog_config_custom_site(self):
        """Test Datadog vendor configuration with custom site."""
        config = VendorConfigs.datadog("test-api-key", "datadoghq.eu")

        expected = {
            "exporter_type": ExporterType.OTLP_HTTP,
            "endpoint": "https://trace-agent.datadoghq.eu/v0.4/traces",
            "headers": {"DD-API-KEY": "test-api-key"},
        }

        assert config == expected

    def test_dynatrace_config(self):
        """Test Dynatrace vendor configuration."""
        endpoint = "https://tenant.live.dynatrace.com"
        token = "dt0c01.test-token"

        config = VendorConfigs.dynatrace(endpoint, token)

        expected = {
            "exporter_type": ExporterType.OTLP_HTTP,
            "endpoint": f"{endpoint}/v2/otlp",
            "headers": {"Authorization": f"Api-Token {token}"},
        }
        assert config == expected

    def test_vendor_configs_invalid_type(self):
        """Test error handling for invalid vendor configuration type."""
        with pytest.raises(TypeError, match="Expected a string for API key"):
            VendorConfigs.datadog(12345)
