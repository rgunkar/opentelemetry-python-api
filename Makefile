# Makefile for opentelemetry-python-api library
# Build and publish commands for PyPI

.PHONY: help install install-dev test test-all lint format type-check clean build publish publish-test docker-up docker-down poetry-install poetry-lock

# Default target
help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Targets:'
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-15s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Clean build artifacts
clean: ## Clean build artifacts
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf src/*.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Clean complete"

# Build the package
build: poetry-install ## Build package
	@echo "📦 Building package..."
	poetry build
	@echo "✅ Build complete"
	@echo "📁 Built files:"
	@ls -la dist/

# Check the built package
check: lint type-check test ## Run all checks (lint, type-check, test)
	@echo "✅ Package check passed"

# Publish to TestPyPI (for testing)
publish-test: build ## Publish to TestPyPI
	@echo "📤 Publishing to TestPyPI..."
	@echo "⚠️  Make sure you have TestPyPI credentials configured!"
	poetry config repositories.testpypi https://test.pypi.org/legacy/
	poetry publish --repository testpypi
	@echo "✅ Published to TestPyPI"
	@echo "🔗 Check: https://test.pypi.org/project/opentelemetry-python-api/"

# Publish to PyPI (production)
publish: build ## Publish to PyPI
	@echo "📤 Publishing to PyPI..."
	@echo "⚠️  This will publish to PRODUCTION PyPI!"
	@read -p "Are you sure? Type 'yes' to continue: " confirm && [ "$$confirm" = "yes" ]
	poetry publish
	@echo "✅ Published to PyPI"
	@echo "🔗 Check: https://pypi.org/project/opentelemetry-python-api/"

# Install package in development mode
install: poetry-install ## Install package in development mode
	@echo "🛠️  Installing package in development mode..."
	poetry install
	@echo "✅ Installation complete"

# Install with development dependencies
install-dev: poetry-install ## Install package with development dependencies
	@echo "🛠️  Installing with development dependencies..."
	poetry install --extras "dev all"
	@echo "✅ Development installation complete"

# Run tests
test: ## Run tests
	poetry run pytest tests/ -v --cov=otel_tracer --cov-report=term-missing

test-simple: ## Run tests without coverage
	poetry run pytest tests/ -v

# Run tests on all supported Python versions (requires Python 3.9+)
test-all: ## Run tests on all supported Python versions (requires Python 3.9+)
	@echo "Testing on Python 3.9..."
	@poetry env use python3.9 && poetry run pytest tests/ -v || echo "Python 3.9 tests failed"
	@echo "Testing on Python 3.10..."
	@poetry env use python3.10 && poetry run pytest tests/ -v || echo "Python 3.10 tests failed"
	@echo "Testing on Python 3.11..."
	@poetry env use python3.11 && poetry run pytest tests/ -v || echo "Python 3.11 tests failed"

# Run linting
lint: ## Run linting
	@echo "🔍 Running linting..."
	poetry run flake8 src/ tests/ --count --select=E9,F63,F7,F82 --show-source --statistics
	poetry run flake8 src/ tests/ --count --exit-zero --max-complexity=10 --max-line-length=88 --statistics

# Format code
format: ## Format code with black
	@echo "🎨 Formatting code..."
	poetry run black src/ tests/ --target-version py39
	@echo "✅ Formatting complete"

# Run type checking
type-check: ## Run type checking
	@echo "🔍 Running type checking..."
	poetry run mypy src/
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
docker-up: ## Start development environment with Docker
	@echo "🐳 Starting development environment with Docker..."
	docker-compose up -d

docker-down: ## Stop development environment
	@echo "🐳 Stopping development environment..."
	docker-compose down

# Development workflow targets
dev-setup: install-dev poetry-lock ## Set up development environment
	@echo "🚀 Development environment ready!"
	@echo ""
	@echo "Next steps:"
	@echo "  make test     # Run tests"
	@echo "  make docker-up  # Start observability stack"

# Poetry-specific commands
poetry-install: ## Install Poetry (if not already installed)
	@command -v poetry >/dev/null 2>&1 || { echo "Installing Poetry..."; curl -sSL https://install.python-poetry.org | python3 -; }
	@echo "✅ Poetry is installed"

poetry-lock: poetry-install ## Generate poetry.lock file
	poetry lock
	@echo "✅ poetry.lock generated"

poetry-shell: ## Activate Poetry shell
	poetry shell

poetry-show: ## Show installed packages
	poetry show

poetry-update: ## Update dependencies
	poetry update

poetry-add: ## Add a new dependency (usage: make poetry-add PACKAGE=package-name)
	poetry add $(PACKAGE)

poetry-add-dev: ## Add a new dev dependency (usage: make poetry-add-dev PACKAGE=package-name)
	poetry add --group dev $(PACKAGE) 