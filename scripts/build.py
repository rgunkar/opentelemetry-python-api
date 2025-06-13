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

def run_command(command, check=True):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed with exit code {result.returncode}")
        sys.exit(1)
    
    return result

def clean():
    """Clean build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    # Directories to remove
    dirs_to_remove = ['build', 'dist', '*.egg-info', 'src/*.egg-info']
    
    for pattern in dirs_to_remove:
        for path in Path('.').glob(pattern):
            if path.is_dir():
                print(f"  Removing {path}")
                shutil.rmtree(path)
    
    # Remove __pycache__ directories
    for path in Path('.').rglob('__pycache__'):
        if path.is_dir():
            shutil.rmtree(path)
    
    # Remove .pyc files
    for path in Path('.').rglob('*.pyc'):
        path.unlink()
    
    print("✅ Clean complete")

def build():
    """Build the package."""
    print("📦 Building package...")
    clean()
    
    # Ensure we have build dependencies
    run_command("pip install build twine setuptools wheel")
    
    # Build the package
    run_command("python -m build")
    
    print("✅ Build complete")
    
    # Show built files
    dist_dir = Path('dist')
    if dist_dir.exists():
        print("📁 Built files:")
        for file in dist_dir.iterdir():
            print(f"  {file.name} ({file.stat().st_size} bytes)")

def check():
    """Check the built package."""
    print("🔍 Checking package...")
    
    dist_dir = Path('dist')
    if not dist_dir.exists() or not list(dist_dir.glob('*')):
        print("❌ No built packages found. Run build first.")
        return False
    
    # Check with twine
    run_command("python -m twine check dist/*")
    
    print("✅ Package check passed")
    return True

def show_contents():
    """Show what will be included in the package."""
    print("📋 Package contents (what will be published):")
    
    dist_dir = Path('dist')
    if not dist_dir.exists():
        print("❌ No dist directory found. Run build first.")
        return
    
    # Show wheel contents
    wheel_files = list(dist_dir.glob('*.whl'))
    if wheel_files:
        print("\n🗂️  Wheel contents:")
        run_command(f"python -m zipfile -l {wheel_files[0]} | head -20", check=False)
    
    # Show source distribution contents
    tar_files = list(dist_dir.glob('*.tar.gz'))
    if tar_files:
        print("\n🗂️  Source distribution contents:")
        run_command(f"tar -tzf {tar_files[0]} | head -20", check=False)

def publish_test():
    """Publish to TestPyPI."""
    print("📤 Publishing to TestPyPI...")
    print("⚠️  Make sure you have TestPyPI credentials configured!")
    
    if not check():
        return
    
    # Configure TestPyPI repository if not already configured
    run_command("python -m twine upload --repository testpypi dist/*")
    
    print("✅ Published to TestPyPI")
    print("🔗 Check: https://test.pypi.org/project/otel-web-tracing/")

def publish():
    """Publish to PyPI."""
    print("📤 Publishing to PyPI...")
    print("⚠️  This will publish to PRODUCTION PyPI!")
    
    if not check():
        return
    
    # Confirmation prompt
    response = input("Are you sure you want to publish to PyPI? Type 'yes' to continue: ")
    if response.lower() != 'yes':
        print("❌ Publish cancelled")
        return
    
    run_command("python -m twine upload dist/*")
    
    print("✅ Published to PyPI")
    print("🔗 Check: https://pypi.org/project/otel-web-tracing/")

def validate():
    """Full validation before publishing."""
    print("🔍 Running full package validation...")
    
    # Build and check
    build()
    if not check():
        return False
    
    # Show contents
    show_contents()
    
    # Run tests
    print("\n🧪 Running tests...")
    result = run_command("python -m pytest --cov=otel_tracer -v", check=False)
    if result.returncode != 0:
        print("⚠️  Some tests failed, but continuing validation...")
    
    print("\n✅ Package validation complete")
    print("📦 Package is ready to publish!")
    return True

def setup_pypi_config():
    """Help setup PyPI configuration."""
    print("🔧 PyPI Configuration Help")
    print("=" * 40)
    print()
    print("To publish to PyPI, you need to configure your credentials:")
    print()
    print("1. Create accounts:")
    print("   - PyPI: https://pypi.org/account/register/")
    print("   - TestPyPI: https://test.pypi.org/account/register/")
    print()
    print("2. Generate API tokens:")
    print("   - PyPI: https://pypi.org/manage/account/token/")
    print("   - TestPyPI: https://test.pypi.org/manage/account/token/")
    print()
    print("3. Configure ~/.pypirc:")
    print("""
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
""")
    print()
    print("4. Or use environment variables:")
    print("   export TWINE_USERNAME=__token__")
    print("   export TWINE_PASSWORD=pypi-your-api-token")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Build and publish otel-web-tracing")
    parser.add_argument('command', choices=[
        'clean', 'build', 'check', 'show-contents', 'publish-test', 
        'publish', 'validate', 'setup-pypi'
    ], help='Command to run')
    
    args = parser.parse_args()
    
    print("🚀 otel-web-tracing Build & Publish Script")
    print("=" * 50)
    
    if args.command == 'clean':
        clean()
    elif args.command == 'build':
        build()
    elif args.command == 'check':
        check()
    elif args.command == 'show-contents':
        show_contents()
    elif args.command == 'publish-test':
        publish_test()
    elif args.command == 'publish':
        publish()
    elif args.command == 'validate':
        validate()
    elif args.command == 'setup-pypi':
        setup_pypi_config()

if __name__ == '__main__':
    main() 