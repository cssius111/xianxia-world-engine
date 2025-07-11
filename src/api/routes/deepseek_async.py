"""DeepSeek API async routes for Xianxia World Engine."""

from flask import Blueprint, jsonify, request
import asyncio
from typing import Dict, Any
import logging

from src.ai.deepseek_client import DeepSeekClient, get_default_client

logger = logging.getLogger(__name__)

# Create blueprint
deepseek_bp = Blueprint('deepseek', __name__, url_prefix='/api/llm')


@deepseek_bp.route('/chat', methods=['POST'])
async def chat_async():
    """Async chat endpoint using DeepSeek API.
    
    Request body:
    {
        "prompt": "string",
        "async": true/false (optional, default: true)
    }
    
    Response:
    {
        "text": "response text",
        "mode": "async" or "sync"
    }
    """
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                "error": "Missing required field: prompt"
            }), 400
        
        prompt = data.get('prompt', '')
        use_async = data.get('async', True)
        
        # Get DeepSeek client
        client = get_default_client()
        
        if use_async:
            # Use async method
            response = await client.chat_async(prompt)
            response['mode'] = 'async'
        else:
            # Use sync method for comparison
            response = client.chat(prompt)
            response['mode'] = 'sync'
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return jsonify({
            "error": str(e)
        }), 500


@deepseek_bp.route('/chat/sync', methods=['POST'])
def chat_sync():
    """Sync chat endpoint (backward compatibility).
    
    Request body:
    {
        "prompt": "string"
    }
    
    Response:
    {
        "text": "response text"
    }
    """
    try:
        data = request.get_json()
        if not data or 'prompt' not in data:
            return jsonify({
                "error": "Missing required field: prompt"
            }), 400
        
        prompt = data.get('prompt', '')
        
        # Get DeepSeek client
        client = get_default_client()
        
        # Use sync method
        response = client.chat(prompt)
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Sync chat endpoint error: {e}")
        return jsonify({
            "error": str(e)
        }), 500


@deepseek_bp.route('/parse', methods=['POST'])
async def parse_async():
    """Async parse endpoint for game NLP.
    
    Request body:
    {
        "utterance": "string",
        "context": {
            "scene": "string",
            "player": {
                "realm": "string"
            },
            "target_realm": "string",
            "laws": [...]
        }
    }
    
    Response:
    {
        "intent": "string",
        "slots": {},
        "allowed": true/false,
        "reason": "string"
    }
    """
    try:
        data = request.get_json()
        if not data or 'utterance' not in data:
            return jsonify({
                "error": "Missing required field: utterance"
            }), 400
        
        utterance = data.get('utterance', '')
        context_data = data.get('context', {})
        
        # Create context object
        class Context:
            def __init__(self, data):
                self.scene = data.get('scene', '主城')
                
                # Player info
                player_data = data.get('player', {})
                self.player = type('Player', (), {
                    'realm': player_data.get('realm', '炼气期')
                })()
                
                self.target_realm = data.get('target_realm', '未知')
                
                # Laws
                laws_data = data.get('laws', [])
                self.laws = []
                for law in laws_data:
                    if isinstance(law, dict):
                        self.laws.append(type('Law', (), {
                            'enabled': law.get('enabled', True),
                            'code': law.get('code', '')
                        })())
        
        ctx = Context(context_data)
        
        # Get DeepSeek client
        client = get_default_client()
        
        # Use async parse
        result = await client.parse_async(utterance, ctx)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Parse endpoint error: {e}")
        return jsonify({
            "error": str(e)
        }), 500


@deepseek_bp.route('/parse/sync', methods=['POST'])
def parse_sync():
    """Sync parse endpoint for backward compatibility."""
    try:
        data = request.get_json()
        if not data or 'utterance' not in data:
            return jsonify({"error": "Missing required field: utterance"}), 400

        utterance = data.get('utterance', '')
        context_data = data.get('context', {})

        class Context:
            def __init__(self, data: Dict[str, Any]):
                self.scene = data.get('scene', '主城')
                player_data = data.get('player', {})
                self.player = type('Player', (), {
                    'realm': player_data.get('realm', '炼气期')
                })()
                self.target_realm = data.get('target_realm', '未知')
                laws_data = data.get('laws', [])
                self.laws = []
                for law in laws_data:
                    if isinstance(law, dict):
                        self.laws.append(type('Law', (), {
                            'enabled': law.get('enabled', True),
                            'code': law.get('code', '')
                        })())

        ctx = Context(context_data)

        client = get_default_client()
        result = client.parse(utterance, ctx)

        return jsonify(result)

    except Exception as e:
        logger.error(f"Parse sync endpoint error: {e}")
        return jsonify({"error": str(e)}), 500


@deepseek_bp.route('/batch', methods=['POST'])
async def batch_process():
    """Batch processing endpoint for multiple requests.
    
    Request body:
    {
        "requests": [
            {"prompt": "string"},
            {"prompt": "string"},
            ...
        ]
    }
    
    Response:
    {
        "results": [
            {"text": "response", "success": true},
            {"error": "error message", "success": false},
            ...
        ],
        "total": 10,
        "successful": 8,
        "failed": 2
    }
    """
    try:
        data = request.get_json()
        if not data or 'requests' not in data:
            return jsonify({
                "error": "Missing required field: requests"
            }), 400
        
        requests_data = data.get('requests', [])
        if not isinstance(requests_data, list):
            return jsonify({
                "error": "requests must be an array"
            }), 400
        
        # Get DeepSeek client
        client = get_default_client()
        
        # Process requests concurrently
        async def process_single(req_data):
            try:
                prompt = req_data.get('prompt', '')
                if not prompt:
                    return {"error": "Missing prompt", "success": False}
                
                response = await client.chat_async(prompt)
                return {**response, "success": True}
            except Exception as e:
                return {"error": str(e), "success": False}
        
        # Create tasks for all requests
        tasks = [process_single(req) for req in requests_data]
        
        # Run concurrently
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        # Calculate statistics
        successful = sum(1 for r in results if r.get('success', False))
        failed = len(results) - successful
        
        return jsonify({
            "results": results,
            "total": len(results),
            "successful": successful,
            "failed": failed
        })
        
    except Exception as e:
        logger.error(f"Batch endpoint error: {e}")
        return jsonify({
            "error": str(e)
        }), 500


@deepseek_bp.route('/status', methods=['GET'])
def get_status():
    """Get DeepSeek API status.
    
    Response:
    {
        "status": "ok" or "error",
        "api_key_configured": true/false,
        "endpoints": [...],
        "version": "1.0.0"
    }
    """
    try:
        client = get_default_client()
        
        return jsonify({
            "status": "ok",
            "api_key_configured": bool(client.api_key),
            "endpoints": [
                "/api/llm/chat",
                "/api/llm/chat/sync",
                "/api/llm/parse",
                "/api/llm/batch",
                "/api/llm/status"
            ],
            "version": "1.0.0",
            "async_enabled": True
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# Helper function to register blueprint
def register_deepseek_routes(app):
    """Register DeepSeek routes with Flask app.

    Args:
        app: Flask application instance
    """
    app.register_blueprint(deepseek_bp)
    logger.info("DeepSeek async routes registered")

    @app.teardown_appcontext
    async def cleanup_deepseek_client(error=None):
        """Cleanup DeepSeek async client on teardown."""
        client = get_default_client()
        if client._async_client:
            try:
                await client.close()
                logger.info("DeepSeek async client closed on teardown")
            except Exception as e:  # pragma: no cover - best effort cleanup
                logger.debug(f"DeepSeek cleanup error: {e}")
