from flask import make_response, request
from typing import Optional, Any

def setup_cors(app,
               origins: Optional[str] = None,
               methods: Optional[str] = None,
               headers: Optional[str] = None):

    if origins is None:
        origins = '*'
    
    if methods is None:
        methods = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
        
    if headers is None:
        headers = 'Content-Type, Authorization, X-Requested-With'
    
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = origins
        response.headers['Access-Control-Allow-Methods'] = methods
        response.headers['Access-Control-Allow-Headers'] = headers
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Access-Control-Max-Age'] = '3600'
        return response
    
    @app.before_request
    def handle_preflight():
        if request.method == 'OPTIONS':
            response = make_response()
            response.headers['Access-Control-Allow-Origin'] = origins
            response.headers['Access-Control-Allow-Methods'] = methods
            response.headers['Access-Control-Allow-Headers'] = headers
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Max-Age'] = '3600'
            return response