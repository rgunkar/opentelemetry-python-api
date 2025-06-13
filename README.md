# OpenTelemetry Web Framework Tracing Library

A **vendor-agnostic** OpenTelemetry tracing library for Python web frameworks including Flask, Django, and FastAPI. This library provides **idempotent setup**, **singleton pattern**, and **easy vendor switching** for observability backends.

## 🚀 Features

- **🔧 Idempotent Setup**: Safe to call setup functions multiple times without side effects
- **🏢 Vendor-Agnostic**: Built-in support for Jaeger, OTLP, and extensible to other vendors
- **🌐 Multi-Framework**: Support for Flask, Django, and FastAPI
- **⚙️ Environment-Driven**: Configure via environment variables
- **🔒 Thread-Safe**: Singleton pattern with proper locking
- **📊 Comprehensive**: Includes HTTP client instrumentation (requests, urllib3)

## 📦 Installation

### Basic Installation
```bash
pip install otel-web-tracing
```

### Framework-Specific Installation
```bash
# For Flask
pip install otel-web-tracing[flask]

# For Django  
pip install otel-web-tracing[django]

# For FastAPI
pip install otel-web-tracing[fastapi]

# For all frameworks
pip install otel-web-tracing[all]

# For development
pip install otel-web-tracing[dev]
```

## 🔧 Quick Start

### Flask Application

```python
from flask import Flask, jsonify
from otel_web_tracing import setup_flask_tracing

app = Flask(__name__)

# Setup tracing (idempotent - safe to call multiple times)
tracer = setup_flask_tracing(
    app, 
    service_name="my-flask-app",
    excluded_urls=["/health", "/metrics"]
)

@app.route("/")
def hello():
    return jsonify({"message": "Hello World!"})

if __name__ == "__main__":
    app.run()
```

### Django Application

```python
# In your Django settings.py
from otel_web_tracing import setup_django_tracing

# Setup tracing
tracer = setup_django_tracing(
    service_name="my-django-app",
    excluded_urls=["/admin/", "/health/"]
)
```

### FastAPI Application

```python
from fastapi import FastAPI
from otel_web_tracing import setup_fastapi_tracing

app = FastAPI()

# Setup tracing
tracer = setup_fastapi_tracing(
    app,
    service_name="my-fastapi-app",
    excluded_urls=["/health", "/docs"]
)

@app.get("/")
async def root():
    return {"message": "Hello World!"}
```

## ⚙️ Configuration

Configure the library using environment variables:

### Basic Configuration
```bash
export OTEL_SERVICE_NAME="my-web-service"
export OTEL_SERVICE_VERSION="1.0.0"
export OTEL_DEPLOYMENT_ENVIRONMENT="production"
```

### Exporter Configuration

#### Jaeger (Default)
```bash
export OTEL_EXPORTER_TYPE="jaeger"
export OTEL_EXPORTER_JAEGER_AGENT_HOST="localhost"
export OTEL_EXPORTER_JAEGER_AGENT_PORT="6831"
```

#### OTLP (OpenTelemetry Protocol)
```bash
export OTEL_EXPORTER_TYPE="otlp"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4317"
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"  # or "http/protobuf"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer your-token"
```

#### Console (Development)
```bash
export OTEL_EXPORTER_TYPE="console"
```

#### Multiple Exporters
```bash
export OTEL_EXPORTER_TYPE="multi"
# This will enable both Jaeger and OTLP exporters
```

## 🏢 Vendor-Specific Configurations

### Datadog
```bash
export OTEL_EXPORTER_TYPE="otlp"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://trace.agent.datadoghq.com"
export OTEL_EXPORTER_OTLP_HEADERS="DD-API-KEY=your-datadog-api-key"
```

### Dynatrace
```bash
export OTEL_EXPORTER_TYPE="otlp"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://your-environment.live.dynatrace.com/api/v2/otlp/v1/traces"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Api-Token your-dynatrace-token"
```

### New Relic
```bash
export OTEL_EXPORTER_TYPE="otlp"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp.nr-data.net:4317"
export OTEL_EXPORTER_OTLP_HEADERS="api-key=your-new-relic-license-key"
```

### Honeycomb
```bash
export OTEL_EXPORTER_TYPE="otlp"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://api.honeycomb.io"
export OTEL_EXPORTER_OTLP_HEADERS="x-honeycomb-team=your-api-key,x-honeycomb-dataset=your-dataset"
```

## 🐳 Running Jaeger Locally

### Using Docker
```bash
# Run Jaeger all-in-one
docker run -d --name jaeger \
  -p 16686:16686 \
  -p 14268:14268 \
  -p 6831:6831/udp \
  jaegertracing/all-in-one:latest

# Access Jaeger UI at http://localhost:16686
```

### Using Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"
      - "14268:14268"
      - "6831:6831/udp"
    environment:
      - COLLECTOR_OTLP_ENABLED=true
```

## 📊 OpenTelemetry Collector Configuration

### Basic OTLP Collector Config
```yaml
# otel-collector-config.yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

processors:
  batch:

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true
  
  # Add other exporters as needed
  datadog:
    api:
      key: "${DD_API_KEY}"
      site: datadoghq.com

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch]
      exporters: [jaeger, datadog]
```

### Running the Collector
```bash
docker run -p 4317:4317 -p 4318:4318 \
  -v $(pwd)/otel-collector-config.yaml:/etc/otel-collector-config.yaml \
  otel/opentelemetry-collector:latest \
  --config=/etc/otel-collector-config.yaml
```

## 🧪 Testing

Run the test suite:

```bash
# Install development dependencies
pip install -e .[dev]

# Run tests
pytest

# Run tests with coverage
pytest --cov=otel_web_tracing --cov-report=html

# Run specific test file
pytest tests/test_tracer.py -v
```

## 🏗️ Architecture

### Core Components

1. **OTelTracer**: Singleton tracer manager with vendor-agnostic exporter support
2. **Framework Modules**: Flask, Django, and FastAPI specific instrumentation
3. **Exporter Factory**: Dynamic exporter creation based on configuration
4. **Thread Safety**: Proper locking for singleton pattern

### Extension Points

Adding support for new vendors is straightforward:

```python
# In your application
import os
from otel_web_tracing.tracer import OTelTracer

# Custom exporter configuration
os.environ["OTEL_EXPORTER_TYPE"] = "custom"
os.environ["CUSTOM_EXPORTER_ENDPOINT"] = "https://your-vendor.com"

# Extend the OTelTracer class or contribute back to the library
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

## 📋 Requirements

- Python 3.8+
- OpenTelemetry SDK 1.20.0+
- Framework-specific dependencies (installed with extras)

## 🔄 Changelog

### v0.1.0
- Initial release
- Support for Flask, Django, FastAPI
- Jaeger and OTLP exporters
- Vendor-agnostic architecture
- Comprehensive test suite

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/rgunkar/otel-web-tracing/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rgunkar/otel-web-tracing/discussions)
- **Documentation**: [Full Documentation](https://rgunkar.github.io/otel-web-tracing/)

## 🌟 Acknowledgments
