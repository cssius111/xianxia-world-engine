#!/bin/bash
# Enhanced E2E Test Runner Script for xianxia-world-engine
# This script sets up the environment and runs the E2E tests with better error handling

echo "🎮 Xianxia World Engine - E2E Test Runner (Enhanced)"
echo "===================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check command existence
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
echo "🔍 Checking prerequisites..."

# Check if Node.js is installed
if ! command_exists node; then
    print_error "Node.js is not installed. Please install Node.js first."
    echo "   Visit: https://nodejs.org/"
    exit 1
fi
print_success "Node.js found: $(node -v)"

# Check if Python is installed
if ! command_exists python3; then
    print_error "Python 3 is not installed."
    exit 1
fi
print_success "Python found: $(python3 --version)"

# Check if npm packages are installed
if [ ! -d "node_modules" ]; then
    print_warning "npm packages not installed. Installing..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "npm install failed"
        exit 1
    fi
fi
print_success "npm packages installed"

# Check if Playwright browsers are installed
if [ ! -d "$HOME/.cache/ms-playwright" ] && [ ! -d "$HOME/Library/Caches/ms-playwright" ]; then
    print_warning "Playwright browsers not installed. Installing..."
    npx playwright install
    if [ $? -ne 0 ]; then
        print_error "Playwright install failed"
        exit 1
    fi
fi
print_success "Playwright browsers installed"

# Create necessary directories
echo ""
echo "📁 Setting up directories..."
mkdir -p logs saves test-results/screenshots
print_success "Test directories created"

# Check if E2E routes are registered
echo ""
echo "🔧 Checking E2E route registration..."
if ! grep -q "register_e2e_routes" run.py 2>/dev/null; then
    print_warning "E2E routes not found in run.py"
    
    # Try to auto-add routes
    if [ -f "scripts/setup_e2e.py" ]; then
        print_info "Attempting to auto-register E2E routes..."
        python3 scripts/setup_e2e.py
    else
        print_error "Please manually add E2E routes to run.py"
        echo "Add this code after 'app = create_app()':"
        echo ""
        echo "if os.getenv('FLASK_ENV') in ['development', 'testing'] or os.getenv('ENABLE_E2E_API') == 'true':"
        echo "    try:"
        echo "        from routes.api_e2e import register_e2e_routes"
        echo "        register_e2e_routes(app)"
        echo "        logger.info('E2E test API endpoints enabled')"
        echo "    except ImportError as e:"
        echo "        logger.debug(f'E2E test routes not loaded: {e}')"
        exit 1
    fi
else
    print_success "E2E routes found in run.py"
fi

# Set environment variables
export FLASK_ENV=development
export ENABLE_E2E_API=true
export PORT=5001
export FLASK_DEBUG=False

# Parse command line arguments
MODE="headed"
PROJECT="all"
GREP=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --headless)
            MODE="headless"
            shift
            ;;
        --debug)
            MODE="debug"
            shift
            ;;
        --chromium)
            PROJECT="chromium"
            shift
            ;;
        --firefox)
            PROJECT="firefox"
            shift
            ;;
        --webkit)
            PROJECT="webkit"
            shift
            ;;
        --grep)
            GREP="$2"
            shift 2
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --headless    Run tests in headless mode"
            echo "  --debug       Run tests in debug mode"
            echo "  --chromium    Run tests only in Chromium"
            echo "  --firefox     Run tests only in Firefox"
            echo "  --webkit      Run tests only in WebKit/Safari"
            echo "  --grep TEXT   Run only tests matching TEXT"
            echo "  --help        Show this help message"
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            exit 1
            ;;
    esac
done

# Kill any existing process on port 5001
echo ""
echo "🧹 Cleaning up existing processes..."
if command_exists lsof; then
    lsof -ti:5001 | xargs kill -9 2>/dev/null || true
else
    # For Windows/other systems
    netstat -ano | grep :5001 | awk '{print $5}' | xargs kill -9 2>/dev/null || true
fi
print_success "Port 5001 cleared"

# Start the Flask server in background
echo ""
echo "🚀 Starting Flask server..."
echo "   Log file: logs/flask_test.log"

# Ensure log directory exists
mkdir -p logs

# Start server with proper output redirection
nohup python3 run.py > logs/flask_test.log 2>&1 &
FLASK_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    print_info "Cleaning up..."
    if [ ! -z "$FLASK_PID" ]; then
        kill $FLASK_PID 2>/dev/null || true
    fi
}
trap cleanup EXIT

# Wait for server to start
echo "⏳ Waiting for server to start..."
MAX_WAIT=30
WAITED=0

while [ $WAITED -lt $MAX_WAIT ]; do
    if curl -s http://localhost:5001 > /dev/null 2>&1; then
        print_success "Server is ready!"
        break
    fi
    
    # Check if process is still running
    if ! kill -0 $FLASK_PID 2>/dev/null; then
        print_error "Server process died. Check logs/flask_test.log for errors"
        echo ""
        echo "Last 20 lines of server log:"
        tail -20 logs/flask_test.log
        exit 1
    fi
    
    sleep 1
    WAITED=$((WAITED + 1))
    echo -ne "\r⏳ Waiting for server to start... ${WAITED}s"
done

echo ""

if [ $WAITED -eq $MAX_WAIT ]; then
    print_error "Server failed to start within ${MAX_WAIT} seconds"
    echo ""
    echo "Server log:"
    cat logs/flask_test.log
    exit 1
fi

# Build playwright command
PLAYWRIGHT_CMD="npx playwright test tests/e2e_full.spec.ts"

if [ "$PROJECT" != "all" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --project=$PROJECT"
fi

if [ ! -z "$GREP" ]; then
    PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --grep \"$GREP\""
fi

case $MODE in
    "headless")
        # Already headless by default
        ;;
    "debug")
        PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --debug"
        ;;
    *)
        PLAYWRIGHT_CMD="$PLAYWRIGHT_CMD --headed"
        ;;
esac

# Run the E2E tests
echo ""
print_info "Running E2E tests (${MODE} mode, project: ${PROJECT})..."
echo "📝 Command: $PLAYWRIGHT_CMD"
echo "===================================================="

# Execute tests
eval $PLAYWRIGHT_CMD
TEST_EXIT_CODE=$?

# Print test summary
echo ""
echo "===================================================="
if [ $TEST_EXIT_CODE -eq 0 ]; then
    print_success "All tests passed!"
else
    print_error "Some tests failed (exit code: $TEST_EXIT_CODE)"
fi

# Show server logs if tests failed
if [ $TEST_EXIT_CODE -ne 0 ]; then
    echo ""
    print_warning "Showing last 20 lines of server log:"
    tail -20 logs/flask_test.log
fi

# Offer to show report
if [ -d "playwright-report" ]; then
    echo ""
    echo "📊 View detailed test report? (y/n)"
    read -r response
    if [ "$response" == "y" ] || [ "$response" == "Y" ]; then
        npx playwright show-report
    fi
fi

# Show test artifacts location
if [ -d "test-results" ]; then
    echo ""
    print_info "Test artifacts saved in:"
    echo "   📁 test-results/"
    echo "   📸 test-results/screenshots/"
    echo "   📹 test-results/ (videos for failed tests)"
fi

exit $TEST_EXIT_CODE
