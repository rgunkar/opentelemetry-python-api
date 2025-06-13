#!/usr/bin/env python3
"""
Example Flask application with OpenTelemetry tracing using otel-tracer.

This example demonstrates:
- Basic Flask app setup with tracing
- Custom spans and attributes
- Database tracing
- HTTP client instrumentation
- Error handling with tracing

Run with:
    python examples/flask_app.py

Or with custom configuration:
    OTEL_SERVICE_NAME="my-flask-app" \
    OTEL_EXPORTER_TYPE="jaeger" \
    OTEL_EXPORTER_JAEGER_AGENT_HOST="localhost" \
    python examples/flask_app.py
"""

import logging
import os
import time
from flask import Flask, jsonify, request
from otel_tracer import setup_flask_tracing

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Setup OpenTelemetry tracing
# This will automatically configure based on environment variables
tracer = setup_flask_tracing(
    app,
    service_name="flask-example-app",
    excluded_urls=["/health", "/metrics"]
)

@app.route("/")
def hello_world():
    """Simple hello world endpoint."""
    return jsonify({
        "message": "Hello from Flask with OpenTelemetry!",
        "service": "flask-example-app",
        "version": "1.0.0"
    })

@app.route("/health")
def health_check():
    """Health check endpoint (excluded from tracing)."""
    return jsonify({"status": "healthy"})

@app.route("/api/users/<int:user_id>")
def get_user(user_id):
    """Example endpoint with path parameters and custom spans."""
    
    # Create a custom span
    with tracer.start_as_current_span("get_user_details") as span:
        # Add custom attributes
        span.set_attribute("user.id", user_id)
        span.set_attribute("user.operation", "get_details")
        
        # Simulate some work
        time.sleep(0.1)
        
        # Simulate different user scenarios
        if user_id == 404:
            span.set_attribute("error", True)
            return jsonify({"error": "User not found"}), 404
        elif user_id == 500:
            span.set_attribute("error", True)
            span.record_exception(Exception("Database connection error"))
            return jsonify({"error": "Internal server error"}), 500
        
        # Return user data
        user_data = {
            "id": user_id,
            "name": f"User {user_id}",
            "email": f"user{user_id}@example.com",
            "active": True
        }
        
        span.set_attribute("user.name", user_data["name"])
        return jsonify(user_data)

@app.route("/api/slow")
def slow_endpoint():
    """Example of a slow endpoint for testing trace timing."""
    with tracer.start_as_current_span("slow_operation") as span:
        span.set_attribute("operation.type", "slow_computation")
        
        # Simulate slow work
        time.sleep(2)
        
        return jsonify({
            "message": "This endpoint is intentionally slow",
            "duration_seconds": 2
        })

@app.route("/api/external")
def call_external_api():
    """Example of calling external APIs (HTTP client instrumentation)."""
    import requests
    
    with tracer.start_as_current_span("external_api_call") as span:
        try:
            # This HTTP call will be automatically traced
            response = requests.get("https://httpbin.org/json", timeout=5)
            
            span.set_attribute("external.api", "httpbin.org")
            span.set_attribute("external.status_code", response.status_code)
            
            return jsonify({
                "message": "External API call successful",
                "status_code": response.status_code,
                "data": response.json()
            })
        except Exception as e:
            span.record_exception(e)
            span.set_attribute("error", True)
            return jsonify({"error": str(e)}), 500

@app.route("/api/batch")
def batch_operation():
    """Example of batch operations with multiple spans."""
    batch_results = []
    
    with tracer.start_as_current_span("batch_processing") as parent_span:
        parent_span.set_attribute("batch.size", 3)
        
        for i in range(3):
            with tracer.start_as_current_span(f"process_item_{i}") as item_span:
                item_span.set_attribute("item.index", i)
                
                # Simulate processing time
                time.sleep(0.2)
                
                result = {
                    "item": i,
                    "processed": True,
                    "timestamp": time.time()
                }
                batch_results.append(result)
        
        parent_span.set_attribute("batch.processed_count", len(batch_results))
    
    return jsonify({
        "message": "Batch processing completed",
        "results": batch_results
    })

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler that ensures errors are traced."""
    logger.exception("Unhandled exception occurred")
    
    # Add error information to current span if available
    from opentelemetry import trace
    current_span = trace.get_current_span()
    if current_span:
        current_span.record_exception(e)
        current_span.set_attribute("error", True)
    
    return jsonify({
        "error": "Internal server error",
        "message": str(e)
    }), 500

if __name__ == "__main__":
    # Print some helpful information
    print("\n🚀 Starting Flask application with OpenTelemetry tracing")
    print("="*60)
    print(f"Service Name: {os.getenv('OTEL_SERVICE_NAME', 'flask-example-app')}")
    print(f"Exporter Type: {os.getenv('OTEL_EXPORTER_TYPE', 'console')}")
    print(f"Environment: {os.getenv('OTEL_DEPLOYMENT_ENVIRONMENT', 'development')}")
    print("\n📍 Available endpoints:")
    print("  GET  /                 - Hello world")
    print("  GET  /health           - Health check (not traced)")
    print("  GET  /api/users/<id>   - Get user by ID")
    print("  GET  /api/slow         - Slow endpoint (2s)")
    print("  GET  /api/external     - External API call")
    print("  GET  /api/batch        - Batch processing")
    print("\n🔍 Try these examples:")
    print("  curl http://localhost:5000/")
    print("  curl http://localhost:5000/api/users/123")
    print("  curl http://localhost:5000/api/users/404  # Error case")
    print("  curl http://localhost:5000/api/slow")
    print("  curl http://localhost:5000/api/external")
    print("  curl http://localhost:5000/api/batch")
    print("\n" + "="*60)
    
    # Run the app
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
        use_reloader=False  # Disable reloader to avoid double instrumentation
    ) 