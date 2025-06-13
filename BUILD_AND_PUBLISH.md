# Building and Publishing otel-web-tracing

This guide explains how to build and publish the `otel-web-tracing` library to PyPI.

## 🎯 What Gets Published

The package is configured to include **only the core library code**:

✅ **Included:**
- `src/otel_tracer/` - Main library code
- `README.md` - Package documentation
- `LICENSE` - License file
- `pyproject.toml` - Package metadata

❌ **Excluded:**
- `tests/` - Test files
- `examples/` - Example applications
- `docs/` - Documentation files
- `.github/` - CI/CD workflows
- `docker-compose.yml` - Development setup
- `Makefile` - Build scripts
- Any other development files

## 🛠️ Prerequisites

1. **Install build dependencies:**
   ```bash
   pip install -e .[build]
   # or
   pip install build twine setuptools wheel
   ```

### Using Poetry (Optional)
If you prefer Poetry for dependency management:
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
# or
pip install poetry

# Install dependencies
poetry install

# Build with Poetry
poetry build
```

2. **Configure PyPI credentials:**
   ```bash
   # Option 1: Configure ~/.pypirc
   cat > ~/.pypirc << EOF
   [distutils]
   index-servers =
       pypi
       testpypi

   [pypi]
   username = __token__
   password = pypi-your-api-token-here

   [testpypi]
   repository = https://test.pypi.org/legacy/
   username = __token__
   password = pypi-your-test-api-token-here
   EOF

   # Option 2: Use environment variables
   export TWINE_USERNAME=__token__
   export TWINE_PASSWORD=pypi-your-api-token
   ```

## 🚀 Building and Publishing

### Method 1: Using Make (Recommended)

```bash
# Show available commands
make help

# Build and validate package
make clean build check

# Show what will be published
make show-contents

# Test publish to TestPyPI first
make publish-test

# Publish to PyPI (production)
make publish
```

### Method 2: Using Python Script

```bash
# Build package
python scripts/build.py build

# Check package
python scripts/build.py check

# Show contents
python scripts/build.py show-contents

# Test publish
python scripts/build.py publish-test

# Publish to PyPI
python scripts/build.py publish
```

### Method 3: Manual Commands

```bash
# Clean previous builds
rm -rf build/ dist/ *.egg-info/

# Build package
python -m build

# Check package
python -m twine check dist/*

# Test upload
python -m twine upload --repository testpypi dist/*

# Production upload
python -m twine upload dist/*
```

### Method 4: Using Poetry (Optional)

```bash
# Build with Poetry
poetry build

# Check package
poetry run twine check dist/*

# Test publish
poetry publish --repository testpypi

# Publish to PyPI
poetry publish
```

## 🔍 Validation

Before publishing, always run validation:

```bash
# Full validation (recommended)
make validate
# or
python scripts/build.py validate

# This will:
# 1. Clean build artifacts
# 2. Build the package
# 3. Check package with twine
# 4. Show package contents
# 5. Run tests
```

## 📦 Package Structure

The built package will contain:

```
otel-web-tracing-0.1.0/
├── otel_tracer/
│   ├── __init__.py
│   ├── tracer.py
│   ├── exporters.py
│   ├── database.py
│   ├── py.typed
│   └── frameworks/
│       ├── __init__.py
│       ├── flask.py
│       ├── django.py
│       └── fastapi.py
├── README.md
├── LICENSE
└── PKG-INFO
```

## 🎯 Publishing Workflow

1. **Test locally:**
   ```bash
   make dev-install
   make test
   ```

2. **Build and validate:**
   ```bash
   make validate
   ```

3. **Test publish:**
   ```bash
   make publish-test
   ```

4. **Test installation from TestPyPI:**
   ```bash
   pip install -i https://test.pypi.org/simple/ otel-web-tracing
   ```

5. **Publish to PyPI:**
   ```bash
   make publish
   ```

6. **Test installation from PyPI:**
   ```bash
   pip install otel-web-tracing
   ```

## 🤖 Automated Publishing

The library includes GitHub Actions for automated publishing:

- **On push to main:** Runs tests and builds package
- **On release creation:** Automatically publishes to PyPI

To create a release:
1. Tag the commit: `git tag v0.1.0`
2. Push tag: `git push origin v0.1.0`
3. Create GitHub release from the tag
4. CI will automatically publish to PyPI



## 🆘 Troubleshooting

**Build fails:**
- Ensure all dependencies are installed: `pip install -e .[build]`
- Check Python version compatibility (3.8+)

**Upload fails:**
- Verify PyPI credentials are configured correctly
- Check if package version already exists on PyPI
- Ensure package passes `twine check`

**Package too large:**
- Check `make show-contents` to see what's included
- Verify `MANIFEST.in` and `pyproject.toml` exclude rules

**Import errors after installation:**
- Test in a clean virtual environment
- Check package structure with `make show-contents`
- Verify all required dependencies are in `pyproject.toml` 