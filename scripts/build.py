#!/usr/bin/env python3
"""
Build script for opentelemetry-python-api package.

This script automates the build process with proper validation and cleanup.
Uses Poetry for better dependency resolution and management.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional

# Minimum Python version required
MIN_PYTHON_VERSION = (3, 9)
SUPPORTED_PYTHON_VERSIONS = ["3.9", "3.10", "3.11", "3.12"]

def check_python_version() -> None:
    """Check if Python version meets minimum requirements."""
    current_version = sys.version_info[:2]
    if current_version < MIN_PYTHON_VERSION:
        print(f"❌ Error: Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ required, got {current_version[0]}.{current_version[1]}")
        sys.exit(1)
    print(f"✅ Python {current_version[0]}.{current_version[1]} meets requirements")

def run_command(cmd: List[str], description: str, check: bool = True) -> subprocess.CompletedProcess:
    """Run a command with proper error handling."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} completed successfully")
        else:
            print(f"❌ {description} failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed with exit code {e.returncode}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        if check:
            sys.exit(1)
        return e

def clean_build_artifacts() -> None:
    """Clean previous build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    dirs_to_clean = [
        "build",
        "dist", 
        "*.egg-info",
        ".pytest_cache",
        "__pycache__"
    ]
    
    for pattern in dirs_to_clean:
        if "*" in pattern:
            # Handle glob patterns
            import glob
            for path in glob.glob(pattern):
                if os.path.isdir(path):
                    shutil.rmtree(path)
                    print(f"  Removed directory: {path}")
        else:
            if os.path.exists(pattern):
                if os.path.isdir(pattern):
                    shutil.rmtree(pattern)
                    print(f"  Removed directory: {pattern}")
                else:
                    os.remove(pattern)
                    print(f"  Removed file: {pattern}")
    
    print("✅ Build artifacts cleaned")

def check_poetry_installed() -> bool:
    """Check if Poetry is installed."""
    try:
        result = subprocess.run(["poetry", "--version"], 
                              check=True, capture_output=True, text=True)
        print(f"✅ Poetry found: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def install_poetry() -> None:
    """Install Poetry if not already installed."""
    if check_poetry_installed():
        return
    
    print("📦 Installing Poetry...")
    try:
        # Install Poetry using the official installer
        result = subprocess.run([
            "curl", "-sSL", "https://install.python-poetry.org", "|", "python3", "-"
        ], shell=True, check=True, capture_output=True, text=True)
        print("✅ Poetry installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install Poetry automatically")
        print("Please install Poetry manually: https://python-poetry.org/docs/#installation")
        sys.exit(1)

def detect_build_system() -> str:
    """Detect which build system to use (always Poetry now)."""
    if not Path("pyproject.toml").exists():
        print("❌ No pyproject.toml found")
        sys.exit(1)
    return "poetry"

def install_dependencies() -> None:
    """Install dependencies using Poetry."""
    print("📦 Installing dependencies with Poetry...")
    run_command(["poetry", "install", "--extras", "dev all"], "Installing dependencies")

def generate_lock_file() -> None:
    """Generate poetry.lock file if it doesn't exist."""
    if not Path("poetry.lock").exists():
        print("🔒 Generating poetry.lock file...")
        run_command(["poetry", "lock"], "Generating lock file")
    else:
        print("✅ poetry.lock file exists")

def run_tests() -> bool:
    """Run the test suite."""
    print("🧪 Running tests...")
    
    # Run tests
    result = run_command([
        "poetry", "run", "pytest", 
        "tests/", "-v", "--tb=short"
    ], "Running tests", check=False)
    
    if result.returncode != 0:
        print("⚠️  Tests failed, but continuing with build...")
        return False
    return True

def run_linting() -> None:
    """Run code linting."""
    print("🔍 Running linting...")
    
    # Run linting
    result = run_command([
        "poetry", "run", "flake8", 
        "src/", "tests/", "--count", "--statistics"
    ], "Running linting", check=False)
    
    if result.returncode != 0:
        print("⚠️  Linting issues found, but continuing with build...")

def run_type_checking() -> None:
    """Run type checking."""
    print("🔍 Running type checking...")
    
    result = run_command([
        "poetry", "run", "mypy", "src/"
    ], "Running type checking", check=False)
    
    if result.returncode != 0:
        print("⚠️  Type checking issues found, but continuing with build...")

def build_package() -> None:
    """Build the package using Poetry."""
    print("📦 Building package with Poetry...")
    run_command(["poetry", "build"], "Building package")

def check_package() -> None:
    """Check the built package."""
    print("🔍 Checking built package...")
    
    # Check package using Poetry
    run_command(["poetry", "run", "twine", "check", "dist/*"], "Checking package")

def show_package_info() -> None:
    """Show information about the built package."""
    print("\n📦 Package Information:")
    print("=" * 50)
    
    dist_dir = Path("dist")
    if dist_dir.exists():
        for file in dist_dir.iterdir():
            if file.is_file():
                size = file.stat().st_size
                size_mb = size / (1024 * 1024)
                print(f"  {file.name}: {size_mb:.2f} MB")
    
    print("\n🎯 Next Steps:")
    print("  • Test: poetry publish --repository testpypi")
    print("  • Publish: poetry publish")
    print("  • Or use Makefile: make publish-test / make publish")
    print("  • Generate lock: poetry lock")
    print("  • Install deps: poetry install --extras 'dev all'")

def show_poetry_info() -> None:
    """Show Poetry environment information."""
    print("\n🔧 Poetry Environment:")
    print("=" * 30)
    
    # Show Poetry version
    result = run_command(["poetry", "--version"], "Getting Poetry version", check=False)
    
    # Show virtual environment info
    result = run_command(["poetry", "env", "info"], "Getting environment info", check=False)
    
    # Show installed packages
    print("\n📦 Installed packages:")
    result = run_command(["poetry", "show", "--tree"], "Showing dependency tree", check=False)

def main() -> None:
    """Main build process."""
    print("🚀 opentelemetry-python-api Build Script (Poetry)")
    print("=" * 45)
    
    # Check Python version
    check_python_version()
    
    # Install Poetry if needed
    install_poetry()
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Detect build system (always Poetry now)
    build_system = detect_build_system()
    print(f"📋 Using build system: {build_system}")
    
    # Generate lock file if needed
    generate_lock_file()
    
    # Install dependencies
    install_dependencies()
    
    # Run quality checks
    run_linting()
    run_type_checking()
    tests_passed = run_tests()
    
    # Build package
    build_package()
    
    # Check package
    check_package()
    
    # Show results
    show_package_info()
    show_poetry_info()
    
    if tests_passed:
        print("\n✅ Build completed successfully!")
    else:
        print("\n⚠️  Build completed with test failures!")
    
    print(f"🐍 Built for Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+")
    print(f"📋 Supported versions: {', '.join(SUPPORTED_PYTHON_VERSIONS)}")
    print("🔧 Using Poetry for dependency management")
    
    print("\n💡 Quick Commands:")
    print("  poetry lock                    # Generate/update lock file")
    print("  poetry install                 # Install dependencies")
    print("  poetry install --extras 'all' # Install with all extras")
    print("  poetry run pytest             # Run tests")
    print("  poetry build                   # Build package")
    print("  poetry publish                 # Publish to PyPI")

if __name__ == "__main__":
    main()
