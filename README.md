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

## 🔄 CI/CD Pipeline Explained

Our project uses **GitHub Actions** for automated testing, building, and publishing. Here's a beginner-friendly explanation of what happens when you push code:

### 📁 Pipeline Configuration
**Location**: `.github/workflows/ci.yml`

### 🎯 Pipeline Overview
```mermaid
graph TD
    A[Push Code] --> B[Test All Python Versions]
    A --> C[Core Tests 3.8-3.11]
    A --> D[Python 3.12 Experimental]
    
    C --> E[Integration Tests]
    C --> F[Example Tests]
    C --> G[Security Scan]
    
    E --> H[Build Package]
    F --> H
    G --> H
    
    H --> I[Publish to PyPI]
    
    B --> J[Test Summary]
    C --> J
    D --> J
```

### 🧪 **Test Jobs Explained**

#### 1. **Main Test Job** (`test`)
**Purpose**: Tests all Python versions (3.8, 3.9, 3.10, 3.11, 3.12)

**What happens**:
```bash
# 1. Install dependencies
pip install -e .[dev,all]

# 2. Code quality checks
flake8 src tests          # Check code style and syntax
black --check src tests   # Verify code formatting
mypy src                  # Type checking

# 3. Run comprehensive tests
pytest --cov=otel_tracer --cov-report=xml -v
```

**Key Features**:
- `fail-fast: false` - If Python 3.9 fails, Python 3.10 still runs
- `continue-on-error: true` for Python 3.12 - Can fail without breaking pipeline
- Uploads coverage reports to Codecov for tracking

#### 2. **Core Test Job** (`core-test`)
**Purpose**: Tests stable Python versions (3.8-3.11) that deployment depends on

**Why separate**: Python 3.12 issues won't block your releases

**Dependencies**: Other critical jobs wait for this to pass

#### 3. **Python 3.12 Test** (`test-python312`)
**Purpose**: Test experimental Python 3.12 support

**Special behavior**: 
- Can fail without affecting other jobs
- Logs failures for future compatibility work
- Doesn't block deployment

### 🔗 **Integration Tests**
**Purpose**: Test with real services (not mocks)

**Services started**:
```yaml
services:
  jaeger:
    image: jaegertracing/all-in-one:1.51
    ports:
      - 16686:16686  # Jaeger UI
      - 14268:14268  # Jaeger collector
      - 6831:6831/udp # Jaeger agent
```

**What it tests**:
```bash
# Wait for Jaeger to be ready
timeout 60 bash -c 'until curl -f http://localhost:16686; do sleep 2; done'

# Test real tracing pipeline
OTEL_EXPORTER_TYPE=jaeger pytest tests/integration/ -v
```

### 📝 **Example Tests**
**Purpose**: Verify example applications work correctly

**Flask example test**:
```bash
# Start Flask app in background
timeout 30 python examples/flask_app.py &
sleep 5

# Test endpoints
curl -f http://localhost:5000/
curl -f http://localhost:5000/api/users/1

# Clean up
pkill -f flask_app.py
```

**FastAPI example test**:
```bash
# Start FastAPI app
timeout 30 python examples/fastapi_app.py &
sleep 5

# Test endpoints
curl -f http://localhost:8000/
curl -f http://localhost:8000/api/users

# Clean up
pkill -f fastapi_app.py
```

### 🔒 **Security Scanning**
**Tools used**:
- **Safety**: Checks dependencies for known vulnerabilities
- **Bandit**: Static security analysis of Python code

**Commands**:
```bash
# Check for vulnerable dependencies
safety check --json

# Scan source code for security issues
bandit -r src/ -f json
```

### 📦 **Build & Publish**

#### **Build Job**
```bash
# Install build tools
pip install build twine

# Create wheel and source distribution
python -m build

# Validate the package
twine check dist/*

# Upload as artifact for publishing
```

#### **Publish Job** (Only on releases)
**Trigger**: When you create a GitHub release
**What it does**: Automatically publishes to PyPI
**Security**: Uses encrypted `PYPI_API_TOKEN` secret

### 🎮 **How to Trigger CI/CD**

1. **Push to main/develop**: Runs all tests
   ```bash
   git push origin main
   ```

2. **Create Pull Request**: Runs all tests
   ```bash
   git checkout -b feature/my-feature
   git push origin feature/my-feature
   # Create PR on GitHub
   ```

3. **Create Release**: Runs tests + publishes to PyPI
   ```bash
   git tag v0.2.0
   git push origin v0.2.0
   # Create release on GitHub
   ```

### 📊 **Monitoring CI/CD**

**View Results**:
1. Go to your GitHub repository
2. Click "Actions" tab
3. See all workflow runs and their status

**Coverage Reports**:
- Automatically uploaded to Codecov
- View detailed coverage at: `https://codecov.io/gh/rgunkar/otel-web-tracing`

## 🐳 Docker & Development Environment Explained

### 📁 **Docker Files Overview**

Our project includes a complete observability stack for development and testing.

#### 1. **docker-compose.yml** - Complete Development Stack

**Purpose**: Sets up a full observability environment with one command

**Services included**:

```yaml
# 🔍 Jaeger - Distributed Tracing Backend
jaeger:
  image: jaegertracing/all-in-one:1.51
  ports:
    - "16686:16686"  # 🌐 Jaeger UI (web interface)
    - "14268:14268"  # 📡 HTTP collector endpoint
    - "6831:6831/udp" # 📡 UDP agent endpoint
  environment:
    - COLLECTOR_OTLP_ENABLED=true

# 🔄 OpenTelemetry Collector - Data Processing Hub
otel-collector:
  image: otel/opentelemetry-collector-contrib:0.89.0
  ports:
    - "4317:4317"   # 📡 OTLP gRPC endpoint
    - "4318:4318"   # 📡 OTLP HTTP endpoint
    - "8889:8889"   # 📊 Metrics endpoint
  volumes:
    - ./otel-collector-config.yaml:/etc/otel-collector-config.yaml
  command: ["--config=/etc/otel-collector-config.yaml"]

# 📊 Prometheus - Metrics Storage
prometheus:
  image: prom/prometheus:v2.47.0
  ports:
    - "9090:9090"   # 🌐 Prometheus UI
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml

# 📈 Grafana - Data Visualization
grafana:
  image: grafana/grafana:10.1.0
  ports:
    - "3000:3000"   # 🌐 Grafana UI
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

#### 2. **otel-collector-config.yaml** - Data Pipeline Configuration

**Purpose**: Configures how telemetry data flows through the system

**Pipeline Structure**:
```yaml
# 📥 RECEIVERS - How data comes in
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317  # Accept gRPC connections
      http:
        endpoint: 0.0.0.0:4318  # Accept HTTP connections

# ⚙️ PROCESSORS - How data is processed
processors:
  batch:
    timeout: 1s              # Batch data for efficiency
    send_batch_size: 1024    # Send in batches of 1024

# 📤 EXPORTERS - Where data goes
exporters:
  jaeger:
    endpoint: jaeger:14250   # Send to Jaeger
    tls:
      insecure: true
  prometheus:
    endpoint: "0.0.0.0:8889" # Expose metrics for Prometheus

# 🔄 SERVICE - Connect everything together
service:
  pipelines:
    traces:
      receivers: [otlp]      # Receive from OTLP
      processors: [batch]    # Process in batches
      exporters: [jaeger]    # Send to Jaeger
    metrics:
      receivers: [otlp]
      processors: [batch]
      exporters: [prometheus]
```

#### 3. **prometheus.yml** - Metrics Collection Configuration

**Purpose**: Tells Prometheus where to collect metrics from

```yaml
global:
  scrape_interval: 15s     # How often to collect metrics

scrape_configs:
  - job_name: 'otel-collector'
    static_configs:
      - targets: ['otel-collector:8889']  # Collect from collector
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']       # Self-monitoring
```

### 🚀 **Using the Development Environment**

#### **Start Everything**
```bash
# Start all services in background
docker-compose up -d

# View logs from all services
docker-compose logs -f

# View logs from specific service
docker-compose logs -f jaeger
```

#### **Access the Services**

| Service | URL | Purpose | Login |
|---------|-----|---------|-------|
| 🔍 Jaeger UI | http://localhost:16686 | View distributed traces | None |
| 📊 Prometheus | http://localhost:9090 | Query metrics and alerts | None |
| 📈 Grafana | http://localhost:3000 | Create dashboards | admin/admin |
| 📡 OTLP Collector | http://localhost:4318 | Send telemetry data | None |

#### **Complete Development Workflow**

1. **Start the observability stack**:
   ```bash
   docker-compose up -d
   ```

2. **Install your project in development mode**:
   ```bash
   pip install -e .[dev,all]
   ```

3. **Create a test application**:
   ```python
   # test_app.py
   from flask import Flask
   from otel_web_tracing import setup_flask_tracing
   
   app = Flask(__name__)
   tracer = setup_flask_tracing(
       app,
       service_name="my-test-app",
       exporter_type="otlp",
       otlp_endpoint="http://localhost:4318"
   )
   
   @app.route("/")
   def hello():
       return "Hello, World!"
   
   if __name__ == "__main__":
       app.run(debug=True)
   ```

4. **Run your application**:
   ```bash
   python test_app.py
   ```

5. **Generate some traffic**:
   ```bash
   # Make some requests
   curl http://localhost:5000/
   curl http://localhost:5000/
   curl http://localhost:5000/
   ```

6. **View the results**:
   - **Traces**: Open http://localhost:16686
     - Select "my-test-app" from service dropdown
     - Click "Find Traces"
     - Click on a trace to see details
   
   - **Metrics**: Open http://localhost:9090
     - Try query: `http_requests_total`
   
   - **Dashboards**: Open http://localhost:3000
     - Login: admin/admin
     - Create custom dashboards

7. **Stop everything when done**:
   ```bash
   docker-compose down
   ```

### 🔧 **Development Commands**

```bash
# Start services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f [service-name]

# Restart a service
docker-compose restart jaeger

# Stop services
docker-compose stop

# Remove everything (including volumes)
docker-compose down -v

# Rebuild services (if you change config)
docker-compose up -d --build
```

### 🐛 **Troubleshooting Docker**

**Common Issues**:

1. **Port already in use**:
   ```bash
   # Check what's using the port
   lsof -i :16686
   
   # Kill the process or change ports in docker-compose.yml
   ```

2. **Services not starting**:
   ```bash
   # Check logs for errors
   docker-compose logs jaeger
   docker-compose logs otel-collector
   
   # Check if containers are running
   docker-compose ps
   ```

3. **Can't connect to services**:
   ```bash
   # Make sure services are up
   curl http://localhost:16686
   
   # Check Docker network
   docker network ls
   docker network inspect otel-web-tracing_default
   ```

4. **Reset everything**:
   ```bash
   # Nuclear option - remove everything
   docker-compose down -v
   docker system prune -f
   docker-compose up -d
   ```

### 🎯 **What Each Service Does**

- **🔍 Jaeger**: Stores and visualizes distributed traces
- **🔄 OTLP Collector**: Receives, processes, and routes telemetry data
- **📊 Prometheus**: Stores and queries metrics data
- **📈 Grafana**: Creates beautiful dashboards and alerts

This setup gives you a **production-like observability environment** on your local machine!

## 📋 Requirements

- Python 3.8+
- OpenTelemetry SDK 1.20.0+
- Framework-specific dependencies (installed with extras)
- Docker & Docker Compose (for development environment)

## 🔄 Changelog

### v0.1.0
- Initial release
- Support for Flask, Django, FastAPI
- Jaeger and OTLP exporters
- Vendor-agnostic architecture
- Comprehensive test suite
- Complete CI/CD pipeline
- Docker development environment

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/rgunkar/otel-web-tracing/issues)
- **Discussions**: [GitHub Discussions](https://github.com/rgunkar/otel-web-tracing/discussions)
- **Documentation**: [Full Documentation](https://rgunkar.github.io/otel-web-tracing/)

## 🌟 Acknowledgments
