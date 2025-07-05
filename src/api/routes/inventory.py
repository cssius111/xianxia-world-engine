"""Inventory API routes."""

from flask import Blueprint, jsonify, current_app, session
import logging

logger = logging.getLogger(__name__)
inventory_bp = Blueprint('inventory', __name__, url_prefix='/api/inventory')


@inventory_bp.route('', methods=['GET'])
@inventory_bp.route('/', methods=['GET'])
def get_inventory():
    """
    Get player inventory.
    ---
    responses:
      200:
        description: Success
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  quantity:
                    type: integer
                  type:
                    type: string
                  description:
                    type: string
    """
    try:
        # Try to get from game state if available
        if hasattr(current_app, 'game_instances') and 'session_id' in session:
            session_id = session.get('session_id')
            if session_id in current_app.game_instances:
                game = current_app.game_instances[session_id]['game']
                player = game.game_state.player
                if hasattr(player, 'inventory'):
                    inv = player.inventory
                    return jsonify([item.to_dict() for item in inv]), 200
    except Exception as e:
        logger.error(f"Error getting inventory from game state: {e}")
    
    # Try to get from inventory system
    try:
        from src.xwe.features import InventorySystem
        inventory_system = InventorySystem()
        player_id = session.get('player_id', 'default')
        inventory_data = inventory_system.get_inventory_data(player_id)
        
        # Convert to expected format
        items = []
        for item in inventory_data.get('items', []):
            items.append({
                'id': item.get('id', f"item_{len(items)}"),
                'name': item.get('name'),
                'quantity': item.get('quantity', 1),
                'type': item.get('type', 'misc'),
                'description': item.get('description', '')
            })
        
        return jsonify(items), 200
    except Exception as e:
        logger.error(f"Error getting inventory from inventory system: {e}")
    
    # Fallback to default inventory
    default_inventory = [
        {
            "id": "item_001",
            "name": "回血丹",
            "type": "consumable",
            "quantity": 3,
            "description": "恢复50点生命值"
        },
        {
            "id": "item_002",
            "name": "精铁剑",
            "type": "weapon",
            "quantity": 1,
            "description": "攻击力+5",
            "equipped": True
        }
    ]
    
    return jsonify(default_inventory), 200


@inventory_bp.post('/add')
def add_item():
    """
    Add item to inventory.
    ---
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              item_id:
                type: string
              quantity:
                type: integer
    responses:
      200:
        description: Success
    """
    # TODO: Implement add item logic
    return jsonify({"success": True, "message": "Item added"}), 200


@inventory_bp.post('/remove')
def remove_item():
    """
    Remove item from inventory.
    ---
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              item_id:
                type: string
              quantity:
                type: integer
    responses:
      200:
        description: Success
    """
    # TODO: Implement remove item logic
    return jsonify({"success": True, "message": "Item removed"}), 200
