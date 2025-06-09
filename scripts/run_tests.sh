#!/bin/bash

# Script to run all tests locally similar to CI
set -e

echo "Running BAI2 to CSV Test Suite"
echo "==============================="

# Check formatting
echo "Checking code formatting with black..."
python -m black --check src tests || (echo "❌ Black formatting check failed" && exit 1)
echo "✅ Black formatting check passed"

# Check imports
echo "Checking import sorting with isort..."
python -m isort --check-only src tests || (echo "❌ isort check failed" && exit 1)
echo "✅ isort check passed"

# Lint code
echo "Linting code with flake8..."
python -m flake8 src tests || (echo "❌ flake8 linting failed" && exit 1)
echo "✅ flake8 linting passed"

# Type checking
echo "Type checking with mypy..."
python -m mypy src tests || (echo "❌ mypy type checking failed" && exit 1)
echo "✅ mypy type checking passed"

# Run unit tests
echo "Running unit tests with pytest..."
python -m pytest tests/ -v \
    --cov=src/bai2_to_csv \
    --cov-report=term-missing \
    --cov-report=xml \
    --cov-report=html \
    --junit-xml=pytest-results.xml \
    --maxfail=10 || (echo "❌ Unit tests failed" && exit 1)

echo "✅ All tests passed!"
echo ""
echo "Coverage report:"
echo "- XML report: coverage.xml"
echo "- HTML report: htmlcov/index.html"
echo "- JUnit report: pytest-results.xml"
echo ""
echo "🎉 Test suite completed successfully!"