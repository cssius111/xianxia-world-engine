#!/bin/bash
# E2E Test Runner Script for xianxia-world-engine
# This script sets up the environment and runs the E2E tests

echo "🎮 Xianxia World Engine - E2E Test Runner"
echo "========================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js first.${NC}"
    exit 1
fi

# Check if npm packages are installed
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing npm packages...${NC}"
    npm install
fi

# Check if Playwright browsers are installed
if [ ! -d "$HOME/.cache/ms-playwright" ]; then
    echo -e "${YELLOW}🌐 Installing Playwright browsers...${NC}"
    npx playwright install
fi

# Create necessary directories
echo "📁 Creating test directories..."
mkdir -p logs saves test-results

# Set environment variables
export FLASK_ENV=development
export ENABLE_E2E_API=true
export PORT=5001

# Parse command line arguments
MODE="headed"
if [ "$1" == "--headless" ]; then
    MODE="headless"
elif [ "$1" == "--debug" ]; then
    MODE="debug"
fi

# Kill any existing process on port 5001
echo "🧹 Cleaning up existing processes..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Start the Flask server in background
echo -e "${GREEN}🚀 Starting Flask server...${NC}"
python run.py > logs/flask_test.log 2>&1 &
FLASK_PID=$!

# Wait for server to start
echo "⏳ Waiting for server to start..."
for i in {1..30}; do
    if curl -s http://localhost:5001 > /dev/null; then
        echo -e "${GREEN}✅ Server is ready!${NC}"
        break
    fi
    if [ $i -eq 30 ]; then
        echo -e "${RED}❌ Server failed to start. Check logs/flask_test.log${NC}"
        kill $FLASK_PID 2>/dev/null
        exit 1
    fi
    sleep 1
done

# Run the E2E tests
echo -e "${GREEN}🧪 Running E2E tests (${MODE} mode)...${NC}"
echo "========================================"

case $MODE in
    "headless")
        npx playwright test tests/e2e_full.spec.ts
        ;;
    "debug")
        npx playwright test tests/e2e_full.spec.ts --debug
        ;;
    *)
        npx playwright test tests/e2e_full.spec.ts --headed
        ;;
esac

TEST_EXIT_CODE=$?

# Kill the Flask server
echo "🛑 Stopping Flask server..."
kill $FLASK_PID 2>/dev/null

# Show test results
if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed!${NC}"
else
    echo -e "${RED}❌ Some tests failed. Check the report:${NC}"
    echo "   npx playwright show-report"
fi

# Offer to show report
if [ -d "playwright-report" ]; then
    echo ""
    echo "📊 View detailed test report? (y/n)"
    read -r response
    if [ "$response" == "y" ]; then
        npx playwright show-report
    fi
fi

exit $TEST_EXIT_CODE
