#!/usr/bin/env python3
"""
Quick Start Guide for otel-web-tracing

This script demonstrates how to quickly get started with each framework.
Run different examples based on command line arguments.

Usage:
    python examples/quickstart.py flask
    python examples/quickstart.py fastapi  
    python examples/quickstart.py django
    python examples/quickstart.py all
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the src directory to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def setup_environment():
    """Set up basic environment variables for demo."""
    os.environ.setdefault('OTEL_SERVICE_NAME', 'quickstart-demo')
    os.environ.setdefault('OTEL_EXPORTER_TYPE', 'console')
    os.environ.setdefault('OTEL_DEPLOYMENT_ENVIRONMENT', 'development')


def flask_example():
    """Quick Flask example."""
    print("\n🌶️  Flask Example")
    print("=" * 50)
    
    try:
        from flask import Flask, jsonify
        from otel_tracer import setup_flask_tracing
        
        app = Flask(__name__)
        
        # Setup tracing - this is all you need!
        tracer = setup_flask_tracing(app, service_name="flask-quickstart")
        
        @app.route("/")
        def hello():
            return jsonify({"message": "Hello from Flask!", "framework": "flask"})
        
        @app.route("/api/test")
        def test():
            # Create a custom span
            with tracer.start_as_current_span("custom_operation") as span:
                span.set_attribute("operation", "test")
                return jsonify({"status": "success", "traced": True})
        
        print("✅ Flask app created with OpenTelemetry tracing!")
        print("📍 Available endpoints:")
        print("   GET /         - Hello endpoint")
        print("   GET /api/test - Test endpoint with custom span")
        print("\n🚀 To run: python examples/flask_app.py")
        
    except ImportError as e:
        print(f"❌ Flask not available: {e}")
        print("💡 Install with: pip install flask")


async def fastapi_example():
    """Quick FastAPI example."""
    print("\n⚡ FastAPI Example")
    print("=" * 50)
    
    try:
        from fastapi import FastAPI
        from otel_tracer import setup_fastapi_tracing
        
        app = FastAPI(title="FastAPI Quickstart")
        
        # Setup tracing - this is all you need!
        tracer = setup_fastapi_tracing(app, service_name="fastapi-quickstart")
        
        @app.get("/")
        async def hello():
            return {"message": "Hello from FastAPI!", "framework": "fastapi"}
        
        @app.get("/api/test")
        async def test():
            # Create a custom span
            with tracer.start_as_current_span("async_custom_operation") as span:
                span.set_attribute("operation", "async_test")
                await asyncio.sleep(0.1)  # Simulate async work
                return {"status": "success", "traced": True, "async": True}
        
        print("✅ FastAPI app created with OpenTelemetry tracing!")
        print("📍 Available endpoints:")
        print("   GET /         - Hello endpoint")
        print("   GET /api/test - Async test endpoint with custom span")
        print("   GET /docs     - API documentation")
        print("\n🚀 To run: python examples/fastapi_app.py")
        
    except ImportError as e:
        print(f"❌ FastAPI not available: {e}")
        print("💡 Install with: pip install fastapi uvicorn")


def django_example():
    """Quick Django example."""
    print("\n🎸 Django Example")
    print("=" * 50)
    
    try:
        # Django setup is more complex, so we just show the basic pattern
        print("📝 Django setup requires configuration in settings.py:")
        print()
        print("```python")
        print("# In your Django settings.py")
        print("from otel_tracer import setup_django_tracing")
        print()
        print("# Setup tracing - add this to your settings.py")
        print("tracer = setup_django_tracing(")
        print("    service_name='my-django-app',")
        print("    excluded_urls=['/admin/', '/health/']")
        print(")")
        print("```")
        print()
        print("✅ Django integration ready!")
        print("📍 This will automatically trace:")
        print("   • All HTTP requests")
        print("   • Database queries")
        print("   • Template rendering")
        print("\n🚀 To see full example: examples/django_app/")
        
    except Exception as e:
        print(f"ℹ️  Django example is conceptual: {e}")


def vendor_examples():
    """Show vendor configuration examples."""
    print("\n🏢 Vendor Configuration Examples")
    print("=" * 50)
    
    print("🔹 Datadog:")
    print("export OTEL_EXPORTER_TYPE=otlp")
    print("export OTEL_EXPORTER_OTLP_ENDPOINT=https://trace.agent.datadoghq.com")
    print("export OTEL_EXPORTER_OTLP_HEADERS='DD-API-KEY=your-key'")
    print()
    
    print("🔹 Jaeger (local):")
    print("export OTEL_EXPORTER_TYPE=jaeger")
    print("export OTEL_EXPORTER_JAEGER_AGENT_HOST=localhost")
    print()
    
    print("🔹 New Relic:")
    print("export OTEL_EXPORTER_TYPE=otlp")
    print("export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp.nr-data.net:4317")
    print("export OTEL_EXPORTER_OTLP_HEADERS='api-key=your-license-key'")
    print()
    
    print("🔹 Multi-exporter (send to multiple backends):")
    print("export OTEL_EXPORTER_TYPE=multi")
    print()


def main():
    """Main function to run different examples."""
    setup_environment()
    
    if len(sys.argv) < 2:
        print("🚀 otel-web-tracing Quickstart Guide")
        print("=" * 50)
        print("Usage: python examples/quickstart.py <framework>")
        print()
        print("Available frameworks:")
        print("  flask    - Show Flask integration example")
        print("  fastapi  - Show FastAPI integration example")
        print("  django   - Show Django integration example")
        print("  vendors  - Show vendor configuration examples")
        print("  all      - Show all examples")
        print()
        return
    
    framework = sys.argv[1].lower()
    
    print("🚀 otel-web-tracing Quickstart Guide")
    print("=" * 50)
    print(f"Environment: {os.getenv('OTEL_DEPLOYMENT_ENVIRONMENT')}")
    print(f"Exporter: {os.getenv('OTEL_EXPORTER_TYPE')}")
    print(f"Service: {os.getenv('OTEL_SERVICE_NAME')}")
    
    if framework == "flask":
        flask_example()
    elif framework == "fastapi":
        asyncio.run(fastapi_example())
    elif framework == "django":
        django_example()
    elif framework == "vendors":
        vendor_examples()
    elif framework == "all":
        flask_example()
        asyncio.run(fastapi_example())
        django_example()
        vendor_examples()
    else:
        print(f"❌ Unknown framework: {framework}")
        print("Available: flask, fastapi, django, vendors, all")
        return
    
    print("\n📚 Next Steps:")
    print("1. Install your framework dependencies")
    print("2. Run the full examples in examples/")
    print("3. Check out docker-compose.yml for Jaeger setup")
    print("4. Configure your preferred observability backend")
    print("5. Read the README.md for full documentation")
    print("\n🎉 Happy tracing!")


if __name__ == "__main__":
    main() 