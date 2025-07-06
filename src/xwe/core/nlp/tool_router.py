from typing import Any, Callable, Dict

# Registered tools mapping
_TOOL_REGISTRY: Dict[str, Callable[[Dict[str, Any]], Any]] = {}


def register_tool(name: str) -> Callable[[Callable[[Dict[str, Any]], Any]], Callable[[Dict[str, Any]], Any]]:
    """Decorator to register a function as a tool."""

    def decorator(func: Callable[[Dict[str, Any]], Any]) -> Callable[[Dict[str, Any]], Any]:
        _TOOL_REGISTRY[name] = func
        return func

    return decorator


def dispatch(tool_name: str, payload: Dict[str, Any]) -> Any:
    """Dispatch a call to a registered tool.

    Args:
        tool_name: Name of the tool to invoke.
        payload: Parameters for the tool.

    Returns:
        The return value of the tool function.

    Raises:
        ValueError: If the tool is not registered.
    """
    if tool_name not in _TOOL_REGISTRY:
        raise ValueError(f"Invalid tool: {tool_name}")
    return _TOOL_REGISTRY[tool_name](payload)


@register_tool("start_cultivation")
def start_cultivation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder start_cultivation tool."""
    return {"action": "start_cultivation", "payload": payload}


@register_tool("consume_pill")
def consume_pill(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder consume_pill tool."""
    return {"action": "consume_pill", "payload": payload}


@register_tool("arrange_formation")
def arrange_formation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder arrange_formation tool."""
    return {"action": "arrange_formation", "payload": payload}


@register_tool("ask_player")
def ask_player(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder ask_player tool."""
    return {"action": "ask_player", "payload": payload}


@register_tool("chat")
def chat(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Placeholder chat tool."""
    return {"action": "chat", "payload": payload}

