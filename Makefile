# Makefile for otel-web-tracing library
# Build and publish commands for PyPI

.PHONY: help install install-dev test test-all lint format type-check clean build publish publish-test docker-up docker-down

# Default target
help:
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

# Build the package
build: clean
	@echo "📦 Building package..."
	python -m build
	@echo "✅ Build complete"
	@echo "📁 Built files:"
	@ls -la dist/

# Check the built package
check: lint type-check test
	@echo "✅ Package check passed"

# Publish to TestPyPI (for testing)
publish-test: check
	@echo "📤 Publishing to TestPyPI..."
	@echo "⚠️  Make sure you have TestPyPI credentials configured!"
	python -m twine upload --repository testpypi dist/*
	@echo "✅ Published to TestPyPI"
	@echo "🔗 Check: https://test.pypi.org/project/otel-web-tracing/"

# Publish to PyPI (production)
publish: check
	@echo "📤 Publishing to PyPI..."
	@echo "⚠️  This will publish to PRODUCTION PyPI!"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	python -m twine upload dist/*
	@echo "✅ Published to PyPI"
	@echo "🔗 Check: https://pypi.org/project/otel-web-tracing/"

# Install package in development mode
install:
	@echo "🛠️  Installing package in development mode..."
	pip install -e .
	@echo "✅ Installation complete"

# Install with development dependencies
install-dev:
	@echo "🛠️  Installing with development dependencies..."
	pip install -e ".[dev,all]"
	@echo "✅ Development installation complete"

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest tests/ -v --cov=otel_tracer --cov-report=term-missing
	@echo "✅ Tests complete"

# Run tests on all supported Python versions (requires Python 3.9+)
test-all:
	@echo "Testing on Python 3.9..."
	@python3.9 -m pytest tests/ -v || echo "Python 3.9 tests failed"
	@echo "Testing on Python 3.10..."
	@python3.10 -m pytest tests/ -v || echo "Python 3.10 tests failed"
	@echo "Testing on Python 3.11..."
	@python3.11 -m pytest tests/ -v || echo "Python 3.11 tests failed"

# Run linting
lint:
	@echo "🔍 Running linting..."
	flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Format code
format:
	@echo "🎨 Formatting code..."
	black src/ tests/ --target-version py39
	@echo "✅ Formatting complete"

# Run type checking
type-check:
	@echo "🔍 Running type checking..."
	mypy src/
	@echo "✅ Type checking complete"

# Show package contents (what will be published)
show-contents: build
	@echo "📋 Package contents (what will be published):"
	@echo ""
	@echo "🗂️  Wheel contents:"
	python -m zipfile -l dist/*.whl | grep -v "^Archive:" | head -20
	@echo ""
	@echo "🗂️  Source distribution contents:"
	tar -tzf dist/*.tar.gz | head -20

# Validate package before publishing
validate: clean build check show-contents
	@echo "✅ Package validation complete"
	@echo "📦 Ready to publish!"

# Quick development setup
setup: install-dev
	@echo "🚀 Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  make test     # Run tests"
	@echo "  make build    # Build package"
	@echo "  make publish-test  # Test publish"

# Run all checks (lint, type-check, test)
ci: check build
	@echo "✅ CI pipeline complete"

# Docker development environment targets
docker-up:
	@echo "🐳 Starting development environment with Docker..."
	docker-compose up -d

docker-down:
	@echo "🐳 Stopping development environment..."
	docker-compose down

# Development workflow targets
dev-setup: install-dev
	@echo "🚀 Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  make test     # Run tests"
	@echo "  make docker-up  # Start observability stack" 