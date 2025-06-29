#!/bin/bash
# Complete E2E Test Runner with Server Management

echo "🎮 Xianxia World Engine - Complete E2E Test Suite"
echo "================================================="

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
export FLASK_ENV=development
export ENABLE_E2E_API=true
export PORT=5001
export FLASK_DEBUG=False

# Function to cleanup
cleanup() {
    echo -e "\n${YELLOW}🧹 Cleaning up...${NC}"
    
    # Kill Flask server
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null
        echo "Flask server stopped"
    fi
    
    # Kill any orphaned processes
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true
}

# Set trap to cleanup on exit
trap cleanup EXIT

# Check dependencies
echo -e "${BLUE}📋 Checking dependencies...${NC}"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not installed${NC}"
    exit 1
fi

# Check Python
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not installed${NC}"
    exit 1
fi

# Install Node dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing Node.js dependencies...${NC}"
    npm install
fi

# Install Playwright browsers if needed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo -e "${YELLOW}🌐 Installing Playwright browsers...${NC}"
    npx playwright install
fi

# Create necessary directories
mkdir -p logs saves test-results

# Clean up any existing processes
echo -e "${BLUE}🧹 Cleaning existing processes...${NC}"
lsof -ti:5001 | xargs kill -9 2>/dev/null || true
sleep 1

# Start Flask server
echo -e "${GREEN}🚀 Starting Flask server...${NC}"
python run.py > logs/flask_server.log 2>&1 &
FLASK_PID=$!

# Wait for server to start
echo -e "${BLUE}⏳ Waiting for server to start...${NC}"
MAX_WAIT=30
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:5001 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is ready!${NC}"
        break
    fi
    
    if [ $WAITED -eq $MAX_WAIT ]; then
        echo -e "${RED}❌ Server failed to start${NC}"
        echo "Check logs/flask_server.log for errors"
        exit 1
    fi
    
    sleep 1
    WAITED=$((WAITED + 1))
    echo -n "."
done
echo ""

# Quick verification
echo -e "\n${BLUE}🔍 Running quick verification...${NC}"
python verify_e2e.py

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Verification failed${NC}"
    exit 1
fi

# Run E2E tests
echo -e "\n${GREEN}🧪 Running E2E Test Suite...${NC}"
echo "================================================="

# Parse command line options
TEST_MODE="headed"
SPECIFIC_TEST=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --headless)
            TEST_MODE="headless"
            shift
            ;;
        --debug)
            TEST_MODE="debug"
            shift
            ;;
        --test)
            SPECIFIC_TEST="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --headless    Run tests without browser UI"
            echo "  --debug       Run tests in debug mode"
            echo "  --test NAME   Run specific test by name"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Build test command
if [ -n "$SPECIFIC_TEST" ]; then
    TEST_CMD="npx playwright test -g \"$SPECIFIC_TEST\""
else
    TEST_CMD="npx playwright test tests/e2e_full.spec.ts tests/e2e_extended.spec.ts"
fi

# Add mode options
case $TEST_MODE in
    "headless")
        TEST_CMD="$TEST_CMD --reporter=list"
        ;;
    "debug")
        TEST_CMD="$TEST_CMD --debug"
        ;;
    *)
        TEST_CMD="$TEST_CMD --headed --reporter=list"
        ;;
esac

# Run tests
echo -e "${BLUE}Executing: $TEST_CMD${NC}\n"
eval $TEST_CMD
TEST_EXIT_CODE=$?

# Summary
echo -e "\n${BLUE}📊 Test Summary${NC}"
echo "================================================="

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed${NC}"
fi

# Count test results
if [ -f "test-results/results.json" ]; then
    echo -e "\n${BLUE}📈 Test Statistics:${NC}"
    # Simple parsing of results (would need jq for proper parsing)
    cat test-results/results.json | grep -E '"(passed|failed|skipped)"' | head -10
fi

# Show performance metrics if available
if [ -f "test-results/performance-metrics.json" ]; then
    echo -e "\n${BLUE}⚡ Performance Metrics:${NC}"
    cat test-results/performance-metrics.json
fi

# List generated files
echo -e "\n${BLUE}📁 Generated Files:${NC}"
ls -la test-results/ 2>/dev/null | grep -E '\.(png|webm|json)$' | head -10

# Offer to show report
if [ -d "playwright-report" ]; then
    echo -e "\n${YELLOW}📊 HTML report available${NC}"
    echo "View with: npx playwright show-report"
    
    if [ $TEST_MODE != "headless" ]; then
        echo -n "Open report now? (y/n): "
        read -r response
        if [ "$response" = "y" ]; then
            npx playwright show-report
        fi
    fi
fi

exit $TEST_EXIT_CODE
