"""DeepSeek API routes with async support for Xianxia World Engine."""

from flask import Blueprint, request, jsonify
from typing import Dict, Any
import asyncio
import logging
import os
from src.ai.deepseek_client import DeepSeekClient

logger = logging.getLogger(__name__)

# Create blueprint
deepseek_bp = Blueprint('deepseek', __name__, url_prefix='/api/v1/deepseek')

# Initialize DeepSeek client (shared instance)
deepseek_client = DeepSeekClient()


@deepseek_bp.route('/chat', methods=['POST'])
async def chat_async():
    """Async chat endpoint for DeepSeek API.
    
    This endpoint uses Flask's async support (Flask 2.3+) to handle
    DeepSeek API calls asynchronously, improving concurrency.
    
    Request JSON:
        {
            "prompt": "string - The prompt to send to DeepSeek"
        }
    
    Response JSON:
        {
            "text": "string - The response from DeepSeek",
            "status": "success|error",
            "error": "string - Error message if any"
        }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400
        
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({
                "status": "error",
                "error": "Prompt is required"
            }), 400
        
        # Log request
        logger.info(f"Async chat request received: {prompt[:50]}...")
        
        # Call async method
        response = await deepseek_client.chat_async(prompt)
        
        # Check response
        if response.get("text"):
            return jsonify({
                "status": "success",
                "text": response["text"]
            })
        else:
            return jsonify({
                "status": "error",
                "error": "Empty response from DeepSeek"
            }), 500
            
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@deepseek_bp.route('/chat/sync', methods=['POST'])
def chat_sync():
    """Synchronous chat endpoint (backward compatibility).
    
    This endpoint maintains backward compatibility by providing
    a synchronous version of the chat API.
    
    Request/Response format same as /chat endpoint.
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400
        
        prompt = data.get("prompt", "")
        if not prompt:
            return jsonify({
                "status": "error",
                "error": "Prompt is required"
            }), 400
        
        # Log request
        logger.info(f"Sync chat request received: {prompt[:50]}...")
        
        # Call sync method
        response = deepseek_client.chat(prompt)
        
        # Check response
        if response.get("text"):
            return jsonify({
                "status": "success",
                "text": response["text"]
            })
        else:
            return jsonify({
                "status": "error",
                "error": "Empty response from DeepSeek"
            }), 500
            
    except Exception as e:
        logger.error(f"Sync chat endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@deepseek_bp.route('/parse', methods=['POST'])
async def parse_intent_async():
    """Async parse user intent with game context.
    
    This endpoint analyzes player input considering the current
    game state and active world laws.
    
    Request JSON:
        {
            "utterance": "string - Player input",
            "context": {
                "scene": "string - Current scene",
                "player": {
                    "realm": "string - Player's cultivation realm"
                },
                "target_realm": "string - Target realm if applicable",
                "laws": [
                    {
                        "enabled": boolean,
                        "code": "string - Law code"
                    }
                ]
            }
        }
    
    Response JSON:
        {
            "intent": "string - Detected intent type",
            "slots": object - Extracted parameters,
            "allowed": boolean - Whether action is allowed,
            "reason": "string - Reason if not allowed",
            "status": "success|error"
        }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400
        
        utterance = data.get("utterance", "")
        if not utterance:
            return jsonify({
                "status": "error",
                "error": "Utterance is required"
            }), 400
        
        # Build context object
        context_data = data.get("context", {})
        
        # Create a mock context object that matches expected structure
        class MockContext:
            def __init__(self, data):
                self.scene = data.get("scene", "主城")
                player_data = data.get("player", {})
                self.player = type('Player', (), {
                    'realm': player_data.get('realm', '炼气期')
                })()
                self.target_realm = data.get("target_realm", "未知")
                self.laws = []
                for law_data in data.get("laws", []):
                    law = type('Law', (), {
                        'enabled': law_data.get('enabled', False),
                        'code': law_data.get('code', '')
                    })()
                    self.laws.append(law)
        
        ctx = MockContext(context_data)
        
        # Log request
        logger.info(f"Parse request: {utterance} in scene {ctx.scene}")
        
        # Call async parse method
        result = await deepseek_client.parse_async(utterance, ctx)
        
        # Add status to response
        result["status"] = "success"
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Parse endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e),
            "intent": "unknown",
            "slots": {},
            "allowed": True,
            "reason": ""
        }), 500


@deepseek_bp.route('/parse/sync', methods=['POST'])
def parse_intent_sync():
    """Synchronous parse endpoint (backward compatibility).
    
    Request/Response format same as /parse endpoint.
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400
        
        utterance = data.get("utterance", "")
        if not utterance:
            return jsonify({
                "status": "error",
                "error": "Utterance is required"
            }), 400
        
        # Build context object (same as async version)
        context_data = data.get("context", {})
        
        class MockContext:
            def __init__(self, data):
                self.scene = data.get("scene", "主城")
                player_data = data.get("player", {})
                self.player = type('Player', (), {
                    'realm': player_data.get('realm', '炼气期')
                })()
                self.target_realm = data.get("target_realm", "未知")
                self.laws = []
                for law_data in data.get("laws", []):
                    law = type('Law', (), {
                        'enabled': law_data.get('enabled', False),
                        'code': law_data.get('code', '')
                    })()
                    self.laws.append(law)
        
        ctx = MockContext(context_data)
        
        # Log request
        logger.info(f"Sync parse request: {utterance} in scene {ctx.scene}")
        
        # Call sync parse method
        result = deepseek_client.parse(utterance, ctx)
        
        # Add status to response
        result["status"] = "success"
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Sync parse endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e),
            "intent": "unknown",
            "slots": {},
            "allowed": True,
            "reason": ""
        }), 500


@deepseek_bp.route('/batch', methods=['POST'])
async def batch_chat_async():
    """Batch async chat endpoint for multiple prompts.
    
    This endpoint demonstrates handling multiple concurrent
    DeepSeek API calls efficiently.
    
    Request JSON:
        {
            "prompts": ["prompt1", "prompt2", ...],
            "max_concurrent": 5  // Optional, default 5
        }
    
    Response JSON:
        {
            "status": "success|error",
            "results": [
                {
                    "prompt": "original prompt",
                    "text": "response text",
                    "error": "error if any"
                },
                ...
            ]
        }
    """
    try:
        # Get request data
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error",
                "error": "No JSON data provided"
            }), 400
        
        prompts = data.get("prompts", [])
        if not prompts:
            return jsonify({
                "status": "error",
                "error": "Prompts array is required"
            }), 400
        
        max_concurrent = data.get("max_concurrent", 5)
        
        # Log request
        logger.info(f"Batch request for {len(prompts)} prompts")
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_prompt(prompt):
            """Process single prompt with semaphore."""
            async with semaphore:
                try:
                    response = await deepseek_client.chat_async(prompt)
                    return {
                        "prompt": prompt,
                        "text": response.get("text", ""),
                        "error": None
                    }
                except Exception as e:
                    logger.error(f"Batch item error: {e}")
                    return {
                        "prompt": prompt,
                        "text": "",
                        "error": str(e)
                    }
        
        # Process all prompts concurrently
        tasks = [process_prompt(prompt) for prompt in prompts]
        results = await asyncio.gather(*tasks)
        
        # Count successes
        success_count = sum(1 for r in results if not r["error"])
        logger.info(f"Batch completed: {success_count}/{len(prompts)} successful")
        
        return jsonify({
            "status": "success",
            "results": results,
            "summary": {
                "total": len(prompts),
                "successful": success_count,
                "failed": len(prompts) - success_count
            }
        })
        
    except Exception as e:
        logger.error(f"Batch endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@deepseek_bp.route('/status', methods=['GET'])
def get_status():
    """Get DeepSeek client status.
    
    Returns information about the current DeepSeek client configuration
    and async support status.
    """
    try:
        status = {
            "status": "success",
            "async_enabled": deepseek_client.async_enabled,
            "httpx_available": deepseek_client.async_enabled,
            "api_key_configured": bool(deepseek_client.api_key),
            "model": deepseek_client.model,
            "base_url": deepseek_client.base_url,
            "environment": {
                "USE_ASYNC_DEEPSEEK": os.environ.get("USE_ASYNC_DEEPSEEK", "1"),
                "DEEPSEEK_VERBOSE": os.environ.get("DEEPSEEK_VERBOSE", "0")
            }
        }
        
        return jsonify(status)
        
    except Exception as e:
        logger.error(f"Status endpoint error: {e}", exc_info=True)
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


# Error handlers
@deepseek_bp.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return jsonify({
        "status": "error",
        "error": "Endpoint not found"
    }), 404


@deepseek_bp.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    logger.error(f"Internal error: {e}", exc_info=True)
    return jsonify({
        "status": "error",
        "error": "Internal server error"
    }), 500


# Register cleanup on app teardown
def register_cleanup(app):
    """Register cleanup function for app teardown."""
    @app.teardown_appcontext
    async def cleanup_deepseek_client(error=None):
        """Cleanup DeepSeek client on app teardown."""
        if error:
            logger.error(f"App teardown with error: {error}")
        
        # Close async client if needed
        if deepseek_client._async_client:
            await deepseek_client.close()
            logger.info("DeepSeek async client closed on teardown")


# Import for convenience
__all__ = ['deepseek_bp', 'register_cleanup']
