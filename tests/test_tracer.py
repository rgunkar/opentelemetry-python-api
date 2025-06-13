"""
Tests for the core tracer functionality.
"""

import pytest
import os
from unittest.mock import patch, MagicMock

from otel_tracer.tracer import TracingConfig, setup_tracing, is_initialized, reset_tracing
from otel_tracer.exporters import ExporterType


@pytest.fixture(autouse=True)
def reset_tracer_state():
    """Reset tracer state before each test."""
    reset_tracing()
    yield
    reset_tracing()


class TestTracingConfig:
    def test_default_config(self):
        """Test default TracingConfig values."""
        config = TracingConfig(service_name="test-service")

        assert config.service_name == "test-service"
        assert config.service_version == "1.0.0"
        assert config.exporter_type == ExporterType.CONSOLE
        assert config.sample_rate == 1.0
        assert config.environment == "development"

    def test_from_env_with_defaults(self):
        """Test TracingConfig.from_env with default values."""
        with patch.dict(os.environ, {}, clear=True):
            config = TracingConfig.from_env("my-service")

            assert config.service_name == "my-service"
            assert config.service_version == "1.0.0"
            assert config.exporter_type == "console"

    def test_from_env_with_values(self):
        """Test TracingConfig.from_env with environment variables."""
        env_vars = {
            "OTEL_SERVICE_NAME": "env-service",
            "OTEL_SERVICE_VERSION": "2.0.0",
            "OTEL_EXPORTER_TYPE": "jaeger",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4318",
            "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer token",
            "OTEL_SAMPLE_RATE": "0.5",
            "OTEL_ENVIRONMENT": "production",
            "OTEL_RESOURCE_ATTRIBUTES": "team=backend,version=1.0",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = TracingConfig.from_env()

            assert config.service_name == "env-service"
            assert config.service_version == "2.0.0"
            assert config.exporter_type == "jaeger"
            assert config.exporter_endpoint == "http://localhost:4318"
            assert config.exporter_headers == {"Authorization": "Bearer token"}
            assert config.sample_rate == 0.5
            assert config.environment == "production"
            assert config.additional_resource_attributes == {
                "team": "backend",
                "version": "1.0"
            }


class TestSetupTracing:
    @patch('otel_tracer.tracer.trace.set_tracer_provider')
    @patch('otel_tracer.tracer.create_exporter')
    def test_setup_tracing_basic(self, mock_create_exporter, mock_set_provider):
        """Test basic tracing setup."""
        mock_exporter = MagicMock()
        mock_create_exporter.return_value = mock_exporter

        config = TracingConfig(service_name="test-service")
        tracer = setup_tracing(config)

        assert tracer is not None
        assert is_initialized()
        mock_create_exporter.assert_called_once()
        mock_set_provider.assert_called_once()

    @patch('otel_tracer.tracer.trace.set_tracer_provider')
    @patch('otel_tracer.tracer.create_exporter')
    def test_setup_tracing_idempotent(self, mock_create_exporter, mock_set_provider):
        """Test that setup_tracing is idempotent."""
        mock_exporter = MagicMock()
        mock_create_exporter.return_value = mock_exporter

        config = TracingConfig(service_name="test-service")

        # First call
        tracer1 = setup_tracing(config)
        assert is_initialized()

        # Second call should not reinitialize
        tracer2 = setup_tracing(config)
        assert tracer1 is not None
        assert tracer2 is not None

        # Should only be called once due to idempotent behavior
        assert mock_create_exporter.call_count == 1
        assert mock_set_provider.call_count == 1

    @patch('otel_tracer.tracer.trace.set_tracer_provider')
    @patch('otel_tracer.tracer.create_exporter')
    def test_setup_tracing_force_reinit(self, mock_create_exporter, mock_set_provider):
        """Test forced re-initialization."""
        mock_exporter = MagicMock()
        mock_create_exporter.return_value = mock_exporter

        config = TracingConfig(service_name="test-service")

        # First call
        setup_tracing(config)

        # Second call with force_reinit=True
        setup_tracing(config, force_reinit=True)

        # Should be called twice due to forced re-initialization
        assert mock_create_exporter.call_count == 2
        assert mock_set_provider.call_count == 2

    def test_setup_tracing_from_env(self):
        """Test setup_tracing with config from environment."""
        env_vars = {
            "OTEL_SERVICE_NAME": "env-test-service",
            "OTEL_EXPORTER_TYPE": "console",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch('otel_tracer.tracer.create_exporter') as mock_create_exporter:
                mock_exporter = MagicMock()
                mock_create_exporter.return_value = mock_exporter

                tracer = setup_tracing()

                assert tracer is not None
                assert is_initialized()
                mock_create_exporter.assert_called_once()

    @patch('otel_tracer.tracer.create_exporter')
    def test_setup_tracing_exporter_error(self, mock_create_exporter):
        """Test setup_tracing handles exporter creation errors."""
        mock_create_exporter.side_effect = Exception("Exporter creation failed")

        config = TracingConfig(service_name="test-service")

        with pytest.raises(ValueError, match="Invalid exporter configuration"):
            setup_tracing(config)


class TestInstrumentation:
    @patch('otel_tracer.tracer.RequestsInstrumentor')
    @patch('otel_tracer.tracer.URLLib3Instrumentor')
    def test_http_libraries_instrumentation(self, mock_urllib3, mock_requests):
        """Test that HTTP libraries are instrumented."""
        # Setup mocks
        mock_requests_instance = MagicMock()
        mock_requests_instance.is_instrumented_by_opentelemetry = False
        mock_requests.return_value = mock_requests_instance

        mock_urllib3_instance = MagicMock()
        mock_urllib3_instance.is_instrumented_by_opentelemetry = False
        mock_urllib3.return_value = mock_urllib3_instance

        with patch('otel_tracer.tracer.create_exporter') as mock_create_exporter:
            mock_exporter = MagicMock()
            mock_create_exporter.return_value = mock_exporter

            config = TracingConfig(service_name="test-service")
            setup_tracing(config)

            # Verify HTTP libraries were instrumented
            mock_requests_instance.instrument.assert_called_once()
            mock_urllib3_instance.instrument.assert_called_once()