"""
E2E Test API Registration Helper
Add this to your run.py after creating the Flask app
"""

def register_e2e_test_routes(app):
    """
    Register E2E test routes if in development/test mode
    
    Add this function call in run.py after app creation:
    
    # After: app = create_app()
    # Add:
    if os.getenv('FLASK_ENV') in ['development', 'testing'] or os.getenv('ENABLE_E2E_API') == 'true':
        try:
            from routes.api_e2e import register_e2e_routes
            register_e2e_routes(app)
        except ImportError:
            logger.warning("E2E test routes not available")
    """
    pass

# Example integration code for run.py:
INTEGRATION_CODE = """
# Add this after app = create_app() in run.py:

# Register E2E test routes in development/test mode
if os.getenv('FLASK_ENV') in ['development', 'testing'] or os.getenv('ENABLE_E2E_API') == 'true':
    try:
        from routes.api_e2e import register_e2e_routes
        register_e2e_routes(app)
        logger.info("E2E test API endpoints enabled")
    except ImportError as e:
        logger.debug(f"E2E test routes not loaded: {e}")
"""

print(INTEGRATION_CODE)
