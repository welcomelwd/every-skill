#!/bin/bash
# Script to run the MCP EU AI Act test suite

echo "=========================================="
echo "  MCP EU AI Act - Test Suite Runner"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Change to server root directory
cd "$(dirname "$0")/.."

# Verify pytest is available
if ! python3 -m pytest --version &> /dev/null; then
    echo -e "${RED}❌ pytest is not installed${NC}"
    echo "Install with: pip install pytest pytest-cov"
    exit 1
fi

echo -e "${YELLOW}📋 Configuration:${NC}"
echo "  - Directory: $(pwd)"
echo "  - Python: $(python3 --version)"
echo "  - pytest: $(python3 -m pytest --version)"
echo ""

# Full test run with coverage
echo "=========================================="
echo -e "${YELLOW}🎯 Running all tests with coverage${NC}"
echo "=========================================="

if python3 -m pytest tests/ -v --tb=short --cov=. --cov-report=term-missing; then
    echo ""
    echo -e "${GREEN}✅ ALL TESTS PASSED${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    exit 1
fi
