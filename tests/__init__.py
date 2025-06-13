"""
Test suite for otel-tracer library.

This module provides common test utilities, fixtures, and setup for testing
the otel-tracer OpenTelemetry integration library.
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any, Generator

import pytest
from unittest.mock import patch, MagicMock

# Add src directory to Python path for imports
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

# Import main library modules
from otel_tracer import (
    TracingConfig,
    setup_tracing,
    ExporterType,
    create_exporter,
    setup_database_tracing,
)
from otel_tracer.tracer import reset_tracing, is_initialized
from otel_tracer.exporters import VendorConfigs


class TestEnvironment:
    """Test environment utilities."""
    
    @staticmethod
    def clean_env() -> Dict[str, str]:
        """Get a clean environment dict without OTEL variables."""
        return {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("OTEL_")
        }
    
    @staticmethod
    def otel_env(**kwargs) -> Dict[str, str]:
        """Create environment dict with OTEL variables."""
        base_env = TestEnvironment.clean_env()
        base_env.update(kwargs)
        return base_env


class MockExporter:
    """Mock exporter for testing."""
    
    def __init__(self, name: str = "mock"):
        self.name = name
        self.spans = []
        self.shutdown_called = False
        self.force_flush_called = False
    
    def export(self, spans):
        """Mock export method."""
        self.spans.extend(spans)
    
    def shutdown(self):
        """Mock shutdown method."""
        self.shutdown_called = True
    
    def force_flush(self, timeout_millis: int = 30000):
        """Mock force_flush method."""
        self.force_flush_called = True
        return True


@pytest.fixture(autouse=True)
def reset_otel_state():
    """
    Automatically reset OpenTelemetry state before and after each test.
    
    This fixture ensures that each test runs with a clean OpenTelemetry state,
    preventing tests from interfering with each other.
    """
    # Reset before test
    reset_tracing()
    
    yield
    
    # Reset after test
    reset_tracing()


@pytest.fixture
def clean_environment():
    """Provide a clean test environment without OTEL variables."""
    with patch.dict(os.environ, TestEnvironment.clean_env(), clear=True):
        yield


@pytest.fixture
def mock_exporter():
    """Provide a mock exporter for testing."""
    return MockExporter()


@pytest.fixture
def sample_config():
    """Provide a sample TracingConfig for testing."""
    return TracingConfig(
        service_name="test-service",
        service_version="1.0.0",
        exporter_type=ExporterType.CONSOLE,
        sample_rate=1.0,
        environment="test"
    )


@pytest.fixture
def sample_env_config():
    """Provide environment variables for testing TracingConfig.from_env()."""
    return {
        "OTEL_SERVICE_NAME": "env-test-service",
        "OTEL_SERVICE_VERSION": "2.0.0",
        "OTEL_EXPORTER_TYPE": "jaeger",
        "OTEL_EXPORTER_OTLP_ENDPOINT": "http://localhost:4318",
        "OTEL_EXPORTER_OTLP_HEADERS": "Authorization=Bearer token",
        "OTEL_SAMPLE_RATE": "0.5",
        "OTEL_ENVIRONMENT": "production",
        "OTEL_RESOURCE_ATTRIBUTES": "team=backend,version=1.0",
    }


# Export commonly used test utilities
__all__ = [
    "TestEnvironment",
    "MockExporter",
    "TracingConfig",
    "setup_tracing",
    "ExporterType",
    "create_exporter",
    "setup_database_tracing",
    "VendorConfigs",
    "reset_tracing",
    "is_initialized",
]
