"""
请求验证工具
"""

from functools import wraps
from typing import Any, Callable, Dict

import jsonschema
from flask import request

from ..errors import InvalidRequestError


def validate_request(schema: Dict[str, Any]) -> Callable:
    """
    请求数据验证装饰器

    Args:
        schema: JSON Schema格式的验证规则

    Example:
        @validate_request({
            'type': 'object',
            'properties': {
                'command': {'type': 'string', 'minLength': 1},
                'target': {'type': 'string'}
            },
            'required': ['command']
        })
        def execute_command():
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 获取请求数据
            if request.method in ["POST", "PUT", "PATCH"]:
                data = request.get_json()

                if data is None:
                    raise InvalidRequestError(
                        "请求必须包含JSON数据", details={"content_type": request.content_type}
                    )
            else:
                data = dict(request.args)

            # 验证数据
            try:
                jsonschema.validate(data, schema)
            except jsonschema.ValidationError as e:
                raise InvalidRequestError(
                    f"请求数据验证失败: {e.message}",
                    details={
                        "field": ".".join(str(p) for p in e.path),
                        "value": e.instance,
                        "schema": e.schema,
                    },
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def validate_params(**param_schemas: Dict[str, Any]) -> Callable:
    """
    URL参数验证装饰器

    Args:
        **param_schemas: 参数名和对应的验证规则

    Example:
        @validate_params(
            page={'type': 'integer', 'minimum': 1},
            per_page={'type': 'integer', 'minimum': 1, 'maximum': 100}
        )
        def get_list(page=1, per_page=20):
            ...
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            errors = []

            for param_name, schema in param_schemas.items():
                value = request.args.get(param_name)

                # 处理类型转换
                if value is not None:
                    param_type = schema.get("type")
                    try:
                        if param_type == "integer":
                            value = int(value)
                        elif param_type == "number":
                            value = float(value)
                        elif param_type == "boolean":
                            value = value.lower() in ["true", "1", "yes"]
                    except ValueError:
                        errors.append(
                            {
                                "param": param_name,
                                "value": value,
                                "error": f"无法转换为{param_type}类型",
                            }
                        )
                        continue

                # 验证值
                try:
                    jsonschema.validate(value, schema)
                except jsonschema.ValidationError as e:
                    errors.append({"param": param_name, "value": value, "error": e.message})

            if errors:
                raise InvalidRequestError("URL参数验证失败", details={"errors": errors})

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def validate_json_body(required: bool = True) -> Callable:
    """
    验证请求必须包含JSON body

    Args:
        required: 是否必须包含body
    """

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method not in ["POST", "PUT", "PATCH"]:
                return f(*args, **kwargs)

            data = request.get_json()

            if required and data is None:
                raise InvalidRequestError(
                    "请求必须包含JSON数据",
                    details={"content_type": request.content_type, "method": request.method},
                )

            return f(*args, **kwargs)

        return decorated_function

    return decorator
