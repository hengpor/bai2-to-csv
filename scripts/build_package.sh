#!/bin/bash

# Script to build and test the package locally
set -e

echo "Building BAI2 to CSV Package"
echo "============================="

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist/ build/ *.egg-info/
echo "✅ Previous builds cleaned"

# Run tests first
echo "Running test suite..."
python -m pytest tests/ -v \
    --cov=src/bai2_to_csv \
    --cov-report=term-missing \
    --cov-fail-under=80 || (echo "❌ Tests failed" && exit 1)
echo "✅ Tests passed"

# Run quality checks
echo "Running quality checks..."
python -m black --check src tests || (echo "❌ Black formatting check failed" && exit 1)
python -m isort --check-only src tests || (echo "❌ isort check failed" && exit 1)
python -m flake8 src tests || (echo "❌ flake8 linting failed" && exit 1)
python -m mypy src tests || (echo "❌ mypy type checking failed" && exit 1)
echo "✅ Quality checks passed"

# Build the package
echo "Building package..."
poetry build || (echo "❌ Package build failed" && exit 1)
echo "✅ Package built successfully"

# Check the built package
echo "Checking package..."
python -m twine check dist/* || (echo "❌ Package check failed" && exit 1)
echo "✅ Package check passed"

# Show build artifacts
echo ""
echo "Build artifacts:"
ls -la dist/

echo ""
echo "🎉 Package build completed successfully!"
echo ""
echo "To publish to Test PyPI:"
echo "  poetry config repositories.testpypi https://test.pypi.org/legacy/"
echo "  poetry publish --repository testpypi"
echo ""
echo "To publish to PyPI:"
echo "  poetry publish"