#!/bin/bash
# Quick test runner to verify E2E tests are working

echo "🧪 Running E2E tests for xianxia-world-engine"
echo "============================================"

# Set environment variables
export FLASK_ENV=development
export ENABLE_E2E_API=true
export PORT=5001

# Kill any existing processes on port 5001
echo "🧹 Cleaning up existing processes..."
lsof -ti:5001 | xargs kill -9 2>/dev/null || true

# Wait a moment
sleep 1

# Check if the routes are registered
echo "📝 Checking if E2E routes need to be added to run.py..."
if ! grep -q "api_e2e" run.py; then
    echo "⚠️  E2E routes not found in run.py"
    echo "Adding E2E routes registration..."
    
    # Create a backup
    cp run.py run.py.backup
    
    # Add the E2E routes registration after app creation
    sed -i.bak '/app = create_app()/a\
\
# Register E2E test routes in development/test mode\
if os.getenv("FLASK_ENV") in ["development", "testing"] or os.getenv("ENABLE_E2E_API") == "true":\
    try:\
        from routes.api_e2e import register_e2e_routes\
        register_e2e_routes(app)\
        logger.info("E2E test API endpoints enabled")\
    except ImportError as e:\
        logger.debug(f"E2E test routes not loaded: {e}")' run.py
    
    echo "✅ E2E routes added to run.py"
fi

# Run a single test to check if everything is working
echo ""
echo "🚀 Running a single test to verify setup..."
echo "============================================"

# Run just the first test
npx playwright test tests/e2e_full.spec.ts -g "1. Web UI 首屏正常渲染" --project=chromium --reporter=list

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Basic test passed! Ready to run full test suite."
    echo ""
    echo "Run full test suite with:"
    echo "  npx playwright test tests/e2e_full.spec.ts --headed"
else
    echo ""
    echo "❌ Basic test failed. Check the error messages above."
    echo ""
    echo "Common issues:"
    echo "  - Flask server not starting properly"
    echo "  - Template files not found"
    echo "  - Port 5001 already in use"
fi
