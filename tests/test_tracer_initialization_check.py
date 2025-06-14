"""
Tests for tracer initialization detection functionality.
"""

import pytest
from unittest.mock import patch, MagicMock

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.trace import NoOpTracerProvider

from otel_tracer.tracer import (
    is_tracer_already_initialized,
    setup_tracing,
    TracingConfig,
    reset_tracing
)


class TestTracerInitializationCheck:
    """Test tracer initialization detection."""

    def setup_method(self):
        """Reset tracing state before each test."""
        reset_tracing()

    def test_is_tracer_already_initialized_with_no_provider(self):
        """Test detection when no tracer provider is set."""
        # Reset to default state
        trace.set_tracer_provider(NoOpTracerProvider())
        
        result = is_tracer_already_initialized()
        assert result is False

    def test_is_tracer_already_initialized_with_sdk_provider(self):
        """Test detection when SDK TracerProvider is already set."""
        # Mock get_tracer_provider to return a TracerProvider instead of trying to set one
        provider = TracerProvider()
        with patch('otel_tracer.tracer.get_tracer_provider', return_value=provider):
            result = is_tracer_already_initialized()
            assert result is True

    def test_is_tracer_already_initialized_with_custom_provider(self):
        """Test detection with a custom (non-SDK) tracer provider."""
        # Mock a custom tracer provider that's not TracerProvider
        mock_provider = MagicMock()
        mock_provider.__class__.__name__ = "CustomTracerProvider"
        
        with patch('otel_tracer.tracer.get_tracer_provider', return_value=mock_provider):
            result = is_tracer_already_initialized()
            assert result is False

    def test_is_tracer_already_initialized_with_exception(self):
        """Test behavior when get_tracer_provider raises an exception."""
        with patch('otel_tracer.tracer.get_tracer_provider', side_effect=Exception("Test error")):
            result = is_tracer_already_initialized()
            assert result is False

    def test_setup_tracing_with_existing_provider_no_force(self):
        """Test setup_tracing when provider already exists without force_reinit."""
        # Set up existing provider
        existing_provider = TracerProvider()
        trace.set_tracer_provider(existing_provider)
        
        config = TracingConfig(service_name="test-service")
        
        # Should return tracer from existing provider without error
        tracer = setup_tracing(config, force_reinit=False)
        assert tracer is not None
        
        # Should still be using the existing provider
        assert trace.get_tracer_provider() is existing_provider

    def test_setup_tracing_with_existing_provider_force_reinit(self):
        """Test setup_tracing when provider exists with force_reinit=True."""
        # Set up existing provider
        existing_provider = TracerProvider()
        trace.set_tracer_provider(existing_provider)
        
        config = TracingConfig(service_name="test-service", exporter_type="console")
        
        # Should override existing provider
        tracer = setup_tracing(config, force_reinit=True)
        assert tracer is not None
        
        # Should have a new provider
        new_provider = trace.get_tracer_provider()
        assert new_provider is not existing_provider
        assert isinstance(new_provider, TracerProvider)

    def test_setup_tracing_no_existing_provider(self):
        """Test setup_tracing when no provider exists."""
        # Ensure no provider is set
        trace.set_tracer_provider(NoOpTracerProvider())
        
        config = TracingConfig(service_name="test-service", exporter_type="console")
        
        tracer = setup_tracing(config)
        assert tracer is not None
        
        # Should have created a new TracerProvider
        provider = trace.get_tracer_provider()
        assert isinstance(provider, TracerProvider)

    def test_multiple_setup_calls_idempotent(self):
        """Test that multiple setup calls are idempotent."""
        config = TracingConfig(service_name="test-service", exporter_type="console")
        
        # First call
        tracer1 = setup_tracing(config)
        provider1 = trace.get_tracer_provider()
        
        # Second call should return same tracer
        tracer2 = setup_tracing(config)
        provider2 = trace.get_tracer_provider()
        
        assert provider1 is provider2
        assert tracer1 is not None
        assert tracer2 is not None

    @patch('otel_tracer.tracer.logger')
    def test_warning_logged_for_existing_provider(self, mock_logger):
        """Test that warning is logged when existing provider is detected."""
        # Set up existing provider
        existing_provider = TracerProvider()
        trace.set_tracer_provider(existing_provider)
        
        config = TracingConfig(service_name="test-service")
        
        setup_tracing(config, force_reinit=False)
        
        # Check that warning was logged
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "already initialized by external code" in warning_call

    @patch('otel_tracer.tracer.logger')
    def test_force_reinit_warning_logged(self, mock_logger):
        """Test that warning is logged when force reinitializing."""
        # Set up existing provider
        existing_provider = TracerProvider()
        trace.set_tracer_provider(existing_provider)
        
        config = TracingConfig(service_name="test-service", exporter_type="console")
        
        setup_tracing(config, force_reinit=True)
        
        # Check that warning was logged
        mock_logger.warning.assert_called()
        warning_calls = [call[0][0] for call in mock_logger.warning.call_args_list]
        assert any("Force re-initializing tracing" in call for call in warning_calls)


class TestIntegrationWithFrameworks:
    """Test integration with framework setup functions."""

    def setup_method(self):
        """Reset tracing state before each test."""
        reset_tracing()

    def test_flask_setup_with_existing_provider(self):
        """Test Flask setup when provider already exists."""
        from otel_tracer import setup_flask_tracing
        from flask import Flask
        
        # Set up existing provider
        existing_provider = TracerProvider()
        trace.set_tracer_provider(existing_provider)
        
        app = Flask(__name__)
        
        # Should work without error
        tracer = setup_flask_tracing(app, service_name="test-flask")
        assert tracer is not None

    def test_django_setup_with_existing_provider(self):
        """Test Django setup when provider already exists."""
        from otel_tracer import setup_django_tracing
        
        # Set up existing provider
        existing_provider = TracerProvider()
        trace.set_tracer_provider(existing_provider)
        
        # Should work without error
        tracer = setup_django_tracing(service_name="test-django")
        assert tracer is not None

    def test_fastapi_setup_with_existing_provider(self):
        """Test FastAPI setup when provider already exists."""
        from otel_tracer import setup_fastapi_tracing
        from fastapi import FastAPI
        
        # Set up existing provider
        existing_provider = TracerProvider()
        trace.set_tracer_provider(existing_provider)
        
        app = FastAPI()
        
        # Should work without error
        tracer = setup_fastapi_tracing(app, service_name="test-fastapi")
        assert tracer is not None 