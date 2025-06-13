#!/usr/bin/env python3
"""
Example demonstrating OpenTelemetry tracer initialization conflict detection.

This script shows how the library detects and handles cases where OpenTelemetry
is already initialized by other code in the system.
"""

from flask import Flask
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider

# Import our library functions
from otel_tracer import (
    setup_flask_tracing,
    is_tracer_already_initialized,
    setup_tracing,
    TracingConfig
)


def example_1_no_existing_tracer():
    """Example 1: Normal case - no existing tracer."""
    print("=== Example 1: No existing tracer ===")
    
    # Check if tracer is already initialized
    is_initialized = is_tracer_already_initialized()
    print(f"Tracer already initialized: {is_initialized}")
    
    # Set up Flask tracing
    app = Flask(__name__)
    tracer = setup_flask_tracing(app, service_name="example-app-1")
    
    print(f"Tracer created: {tracer}")
    print(f"Tracer provider: {trace.get_tracer_provider()}")
    print()


def example_2_existing_tracer_detected():
    """Example 2: External tracer already exists."""
    print("=== Example 2: External tracer already exists ===")
    
    # Simulate external code setting up OpenTelemetry
    print("External code sets up OpenTelemetry...")
    external_provider = TracerProvider()
    trace.set_tracer_provider(external_provider)
    
    # Check if tracer is already initialized
    is_initialized = is_tracer_already_initialized()
    print(f"Tracer already initialized: {is_initialized}")
    
    # Try to set up our tracing (should detect existing tracer)
    app = Flask(__name__)
    print("Setting up Flask tracing...")
    tracer = setup_flask_tracing(app, service_name="example-app-2")
    
    print(f"Tracer created: {tracer}")
    print(f"Tracer provider (should be same): {trace.get_tracer_provider() is external_provider}")
    print()


def example_3_force_override():
    """Example 3: Force override existing tracer."""
    print("=== Example 3: Force override existing tracer ===")
    
    # Set up external tracer
    print("External code sets up OpenTelemetry...")
    external_provider = TracerProvider()
    trace.set_tracer_provider(external_provider)
    
    # Check initial state
    is_initialized = is_tracer_already_initialized()
    print(f"Tracer already initialized: {is_initialized}")
    print(f"Current provider: {trace.get_tracer_provider()}")
    
    # Force override with our configuration
    print("Force overriding with our configuration...")
    config = TracingConfig(
        service_name="example-app-3",
        exporter_type="console"
    )
    tracer = setup_tracing(config, force_reinit=True)
    
    print(f"Tracer created: {tracer}")
    print(f"Provider changed: {trace.get_tracer_provider() is not external_provider}")
    print(f"New provider: {trace.get_tracer_provider()}")
    print()


def example_4_multiple_setups():
    """Example 4: Multiple setup calls (idempotent behavior)."""
    print("=== Example 4: Multiple setup calls ===")
    
    app = Flask(__name__)
    
    # First setup
    print("First setup call...")
    tracer1 = setup_flask_tracing(app, service_name="example-app-4")
    provider1 = trace.get_tracer_provider()
    
    # Second setup (should be idempotent)
    print("Second setup call...")
    tracer2 = setup_flask_tracing(app, service_name="example-app-4")
    provider2 = trace.get_tracer_provider()
    
    # Third setup (should still be idempotent)
    print("Third setup call...")
    tracer3 = setup_flask_tracing(app, service_name="example-app-4")
    provider3 = trace.get_tracer_provider()
    
    print(f"All providers are the same: {provider1 is provider2 is provider3}")
    print(f"Provider: {provider1}")
    print()


def example_5_real_world_scenario():
    """Example 5: Real-world scenario with multiple libraries."""
    print("=== Example 5: Real-world scenario ===")
    
    # Simulate another library setting up OpenTelemetry
    print("Library A sets up OpenTelemetry...")
    library_a_provider = TracerProvider()
    trace.set_tracer_provider(library_a_provider)
    
    # Our application tries to set up tracing
    print("Our application sets up tracing...")
    app = Flask(__name__)
    
    # Check before setup
    print(f"Before setup - is initialized: {is_tracer_already_initialized()}")
    
    # Set up tracing (should detect existing and work gracefully)
    tracer = setup_flask_tracing(
        app, 
        service_name="my-web-app",
        exporter_type="console"
    )
    
    print(f"After setup - tracer: {tracer}")
    print(f"Using original provider: {trace.get_tracer_provider() is library_a_provider}")
    
    # If we really need our own configuration, we can force it
    print("\nForcing our own configuration...")
    tracer_forced = setup_flask_tracing(
        app,
        service_name="my-web-app", 
        exporter_type="console",
        force_reinit=True
    )
    
    print(f"After force setup - tracer: {tracer_forced}")
    print(f"Provider changed: {trace.get_tracer_provider() is not library_a_provider}")
    print()


def reset_state():
    """Reset OpenTelemetry state between examples."""
    from otel_tracer.tracer import reset_tracing
    from opentelemetry.trace import NoOpTracerProvider
    
    reset_tracing()
    trace.set_tracer_provider(NoOpTracerProvider())


if __name__ == "__main__":
    print("OpenTelemetry Tracer Conflict Detection Examples")
    print("=" * 50)
    print()
    
    # Run examples
    example_1_no_existing_tracer()
    reset_state()
    
    example_2_existing_tracer_detected()
    reset_state()
    
    example_3_force_override()
    reset_state()
    
    example_4_multiple_setups()
    reset_state()
    
    example_5_real_world_scenario()
    
    print("All examples completed!")
    print("\nKey takeaways:")
    print("1. Use is_tracer_already_initialized() to check for existing setup")
    print("2. Library gracefully handles existing OpenTelemetry configuration")
    print("3. Use force_reinit=True only when you need to override existing setup")
    print("4. Multiple setup calls are safe and idempotent")
    print("5. Warnings are logged when conflicts are detected") 