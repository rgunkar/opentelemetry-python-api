# Makefile for otel-web-tracing library
# Build and publish commands for PyPI

.PHONY: help clean build check publish publish-test install dev-install test lint format

# Default target
help:
	@echo "🚀 otel-web-tracing Build & Publish Commands"
	@echo "=============================================="
	@echo ""
	@echo "📦 Building:"
	@echo "  build         - Build the package (wheel and sdist)"
	@echo "  check         - Check the built package"
	@echo "  clean         - Clean build artifacts"
	@echo ""
	@echo "📤 Publishing:"
	@echo "  publish-test  - Publish to TestPyPI (for testing)"
	@echo "  publish       - Publish to PyPI (production)"
	@echo ""
	@echo "🛠️  Development:"
	@echo "  install       - Install package in development mode"
	@echo "  dev-install   - Install with all development dependencies"
	@echo "  test          - Run tests"
	@echo "  lint          - Run linting"
	@echo "  format        - Format code with black"
	@echo ""
	@echo "🔧 Usage Examples:"
	@echo "  make clean build check    # Build and verify package"
	@echo "  make publish-test         # Test on TestPyPI first"
	@echo "  make publish              # Publish to PyPI"

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
check: build
	@echo "🔍 Checking package..."
	python -m twine check dist/*
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
dev-install:
	@echo "🛠️  Installing with development dependencies..."
	pip install -e .[dev,build,all]
	@echo "✅ Development installation complete"

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest --cov=otel_tracer --cov-report=term-missing -v
	@echo "✅ Tests complete"

# Run linting
lint:
	@echo "🔍 Running linting..."
	flake8 src tests --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 src tests --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics
	mypy src
	@echo "✅ Linting complete"

# Format code
format:
	@echo "🎨 Formatting code..."
	black src tests examples
	@echo "✅ Formatting complete"

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
setup: dev-install
	@echo "🚀 Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  make test     # Run tests"
	@echo "  make build    # Build package"
	@echo "  make publish-test  # Test publish" 