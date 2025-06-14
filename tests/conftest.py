"""
Pytest configuration and shared fixtures for otel-tracer tests.
"""

# Import all fixtures from __init__.py to make them available to pytest
from tests import (
    clean_environment,
    mock_exporter,
    sample_config,
    sample_env_config,
    TestEnvironment,
    MockExporter,
)

import pytest
from otel_tracer.tracer import reset_tracing


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
    
    # Reset after test - but be more careful to avoid conflicts
    try:
        reset_tracing()
    except Exception:
        # If reset fails (e.g., due to OpenTelemetry restrictions), just continue
        pass


# Re-export fixtures so they're available to all test modules
__all__ = [
    "reset_otel_state",
    "clean_environment", 
    "mock_exporter",
    "sample_config",
    "sample_env_config",
    "TestEnvironment",
    "MockExporter",
] 