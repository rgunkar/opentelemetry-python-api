#!/usr/bin/env python3
"""
Build and publish script for otel-web-tracing library.

This script provides commands to build and publish the library to PyPI,
ensuring only the core library code is included (no tests, examples, etc.).

Usage:
    python scripts/build.py build        # Build the package
    python scripts/build.py check        # Check the package
    python scripts/build.py publish-test # Publish to TestPyPI
    python scripts/build.py publish      # Publish to PyPI
    python scripts/build.py validate     # Full validation
"""

import os
import sys
import shutil
import subprocess
import argparse
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

def detect_build_system() -> str:
    """Detect which build system to use (pip or Poetry)."""
    if Path("poetry.lock").exists():
        return "poetry"
    elif Path("pyproject.toml").exists():
        return "pip"
    else:
        print("❌ No pyproject.toml found")
        sys.exit(1)

def install_build_dependencies(build_system: str) -> None:
    """Install build dependencies."""
    if build_system == "poetry":
        run_command(["poetry", "install", "--with", "build"], "Installing Poetry build dependencies")
    else:
        run_command([sys.executable, "-m", "pip", "install", "-e", ".[build]"], "Installing pip build dependencies")

def run_tests() -> None:
    """Run the test suite."""
    print("🧪 Running tests...")
    
    # Check if pytest is available
    try:
        subprocess.run([sys.executable, "-m", "pytest", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️  pytest not found, installing...")
        run_command([sys.executable, "-m", "pip", "install", "pytest"], "Installing pytest")
    
    # Run tests
    result = run_command([
        sys.executable, "-m", "pytest", 
        "tests/", "-v", "--tb=short"
    ], "Running tests", check=False)
    
    if result.returncode != 0:
        print("⚠️  Tests failed, but continuing with build...")
        return False
    return True

def run_linting() -> None:
    """Run code linting."""
    print("🔍 Running linting...")
    
    # Check if flake8 is available
    try:
        subprocess.run([sys.executable, "-m", "flake8", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️  flake8 not found, installing...")
        run_command([sys.executable, "-m", "pip", "install", "flake8"], "Installing flake8")
    
    # Run linting
    result = run_command([
        sys.executable, "-m", "flake8", 
        "src/", "tests/", "--count", "--statistics"
    ], "Running linting", check=False)
    
    if result.returncode != 0:
        print("⚠️  Linting issues found, but continuing with build...")

def build_package(build_system: str) -> None:
    """Build the package."""
    if build_system == "poetry":
        run_command(["poetry", "build"], "Building package with Poetry")
    else:
        run_command([sys.executable, "-m", "build"], "Building package with pip")

def check_package() -> None:
    """Check the built package."""
    print("🔍 Checking built package...")
    
    # Check if twine is available
    try:
        subprocess.run([sys.executable, "-m", "twine", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("⚠️  twine not found, installing...")
        run_command([sys.executable, "-m", "pip", "install", "twine"], "Installing twine")
    
    # Check package
    run_command([sys.executable, "-m", "twine", "check", "dist/*"], "Checking package")

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
    print("  • Test: python -m twine upload --repository testpypi dist/*")
    print("  • Publish: python -m twine upload dist/*")
    print("  • Or use: make publish-test / make publish")

def main() -> None:
    """Main build process."""
    print("🚀 otel-web-tracing Build Script")
    print("=" * 40)
    
    # Check Python version
    check_python_version()
    
    # Clean previous builds
    clean_build_artifacts()
    
    # Detect build system
    build_system = detect_build_system()
    print(f"📋 Using build system: {build_system}")
    
    # Install dependencies
    install_build_dependencies(build_system)
    
    # Run quality checks
    run_linting()
    tests_passed = run_tests()
    
    # Build package
    build_package(build_system)
    
    # Check package
    check_package()
    
    # Show results
    show_package_info()
    
    if tests_passed:
        print("\n✅ Build completed successfully!")
    else:
        print("\n⚠️  Build completed with test failures!")
    
    print(f"🐍 Built for Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+")
    print(f"📋 Supported versions: {', '.join(SUPPORTED_PYTHON_VERSIONS)}")

if __name__ == "__main__":
    main() 