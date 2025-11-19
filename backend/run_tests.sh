#!/bin/bash
# Backend test runner script for Weight Coach

set -e  # Exit on error

echo "🧪 Running Weight Coach Backend Tests..."
echo "========================================"
echo ""

# Check if we're in the backend directory
if [ ! -f "pytest.ini" ]; then
    echo "❌ Error: pytest.ini not found. Please run this script from the backend directory."
    exit 1
fi

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
elif [ -d "../venv" ]; then
    echo "📦 Activating virtual environment..."
    source ../venv/bin/activate
fi

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo "❌ Error: pytest not found. Please install dependencies:"
    echo "   pip install -r requirements.txt"
    exit 1
fi

echo "🔍 Running tests with coverage..."
echo ""

# Run tests with coverage
pytest tests/ \
    --cov=app \
    --cov-report=html \
    --cov-report=xml \
    --cov-report=term-missing \
    --cov-fail-under=80 \
    -v \
    "$@"  # Pass any additional arguments

# Check exit code
EXIT_CODE=$?

echo ""
echo "========================================"

if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ All tests passed!"
    echo "📊 Coverage reports generated:"
    echo "   - HTML: htmlcov/index.html"
    echo "   - XML:  coverage.xml"
    echo ""
    echo "💡 View HTML coverage report:"
    echo "   open htmlcov/index.html      # macOS"
    echo "   xdg-open htmlcov/index.html  # Linux"
else
    echo "❌ Tests failed!"
    echo "   Review the output above for details."
    exit 1
fi
