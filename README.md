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

# Makefile
.PHONY: install test lint format clean build publish

# Development setup
install:
	pip install -e .[dev,all]

# Testing
test:
	pytest -v

test-cov:
	pytest --cov=otel_web_tracing --cov-report=html --cov-report=term

# Code quality
lint:
	flake8 otel_web_tracing tests
	mypy otel_web_tracing

format:
	black otel_web_tracing tests examples
	isort otel_web_tracing tests examples

# Build and publish
clean:
	rm -rf build/ dist/ *.egg-info/ .coverage htmlcov/

build: clean
	python -m build

publish-test: build
	python -m twine upload --repository testpypi dist/*

publish: build
	python -m twine upload dist/*

# Docker examples
docker-jaeger:
	docker run -d --name jaeger \
		-p 16686:16686 \
		-p 14268:14268 \
		-p 6831:6831/udp \
		jaegertracing/all-in-one:latest

docker-stop-jaeger:
	docker stop jaeger && docker rm jaeger

# MANIFEST.in
include README.md
include LICENSE
include Makefile
recursive-include examples *.py
recursive-include tests *.py
recursive-exclude * __pycache__
recursive-exclude * *.py[co]

# .gitignore
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class

# C extensions
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.nox/
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/
.pytest_cache/

# Translations
*.mo
*.pot

# Django stuff:
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal

# Flask stuff:
instance/
.webassets-cache

# Scrapy stuff:
.scrapy

# Sphinx documentation
docs/_build/

# PyBuilder
target/

# Jupyter Notebook
.ipynb_checkpoints

# IPython
profile_default/
ipython_config.py

# pyenv
.python-version

# pipenv
Pipfile.lock

# PEP 582
__pypackages__/

# Celery stuff
celerybeat-schedule
celerybeat.pid

# SageMath parsed files
*.sage.py

# Environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# Spyder project settings
.spyderproject
.spyproject

# Rope project settings
.ropeproject

# mkdocs documentation
/site

# mypy
.mypy_cache/
.dmypy.json
dmypy.json

# Pyre type checker
.pyre/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# docker-compose.yml
version: '3.8'

services:
  jaeger:
    image: jaegertracing/all-in-one:latest
    ports:
      - "16686:16686"  # Jaeger UI
      - "14268:14268"  # Jaeger collector HTTP
      - "6831:6831/udp"  # Jaeger agent UDP
    environment:
      - COLLECTOR_OTLP_ENABLED=true
    
  otel-collector:
    image: otel/opentelemetry-collector:latest
    command: ["--config=/etc/otel-collector-config.yaml"]
    volumes:
      - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
    ports:
      - "4317:4317"   # OTLP gRPC receiver
      - "4318:4318"   # OTLP HTTP receiver
    depends_on:
      - jaeger

  # Example Flask app
  flask-app:
    build:
      context: .
      dockerfile: examples/Dockerfile.flask
    ports:
      - "5000:5000"
    environment:
      - OTEL_SERVICE_NAME=flask-example
      - OTEL_EXPORTER_TYPE=otlp
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
    depends_on:
      - otel-collector

  # Example FastAPI app  
  fastapi-app:
    build:
      context: .
      dockerfile: examples/Dockerfile.fastapi
    ports:
      - "8000:8000"
    environment:
      - OTEL_SERVICE_NAME=fastapi-example
      - OTEL_EXPORTER_TYPE=otlp
      - OTEL_EXPORTER_OTLP_ENDPOINT=http://otel-collector:4317
    depends_on:
      - otel-collector

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
    timeout: 1s
    send_batch_size: 1024
  
  resource:
    attributes:
      - key: deployment.environment
        value: development
        action: upsert

exporters:
  jaeger:
    endpoint: jaeger:14250
    tls:
      insecure: true
  
  logging:
    loglevel: debug
  
  # Example: Datadog exporter (uncomment and configure)
  # datadog:
  #   api:
  #     key: "${DD_API_KEY}"
  #     site: datadoghq.com

service:
  pipelines:
    traces:
      receivers: [otlp]
      processors: [batch, resource]
      exporters: [jaeger, logging]

# examples/Dockerfile.flask
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY otel_web_tracing/ otel_web_tracing/
RUN pip install -e .[flask]

COPY examples/flask_example.py .

EXPOSE 5000

CMD ["python", "flask_example.py"]

# examples/Dockerfile.fastapi  
FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml .
COPY otel_web_tracing/ otel_web_tracing/
RUN pip install -e .[fastapi]

COPY examples/fastapi_example.py .

EXPOSE 8000

CMD ["python", "fastapi_example.py"]

# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10", "3.11", "3.12"]

    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e .[dev,all]
    
    - name: Lint with flake8
      run: |
        flake8 otel_web_tracing tests --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 otel_web_tracing tests --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
    
    - name: Test with pytest
      run: |
        pytest --cov=otel_web_tracing --cov-report=xml
    
    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  build:
    runs-on: ubuntu-latest
    needs: test
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.11"
    
    - name: Install build dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    
    - name: Build package
      run: python -m build
    
    - name: Check package
      run: twine check dist/*

# LICENSE
MIT License

Copyright (c) 2025 OpenTelemetry Web Tracing Library

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
