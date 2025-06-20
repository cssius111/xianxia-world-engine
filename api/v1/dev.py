"""
开发调试API
提供系统状态监控和调试功能
"""

import json
import os
import platform
import sys
import time
from typing import Any, Dict

import psutil
from flask import Blueprint, jsonify, request

from api.errors import APIError
from api.utils.response import error_response, success_response
from xwe.metrics import metrics_registry
from xwe.services import ServiceContainer

# 创建蓝图
dev_bp = Blueprint("dev", __name__, url_prefix="/dev")


@dev_bp.route("/debug", methods=["GET"])
def debug_info() -> Dict[str, Any]:
    """
    获取系统调试信息

    返回：
    - 事件总线状态
    - 依赖注入容器状态
    - 系统资源使用情况
    - 服务状态
    """
    try:
        # 获取服务容器实例
        container = ServiceContainer.get_instance()

        debug_data = {
            "timestamp": time.time(),
            "system": _get_system_info(),
            "services": _get_services_info(container),
            "event_bus": _get_event_bus_info(container),
            "metrics": _get_metrics_summary(),
            "resources": _get_resource_usage(),
        }

        return success_response(data=debug_data, message="Debug information retrieved successfully")

    except Exception as e:
        return error_response(
            message=f"Failed to retrieve debug info: {str(e)}", code="DEBUG_ERROR", status_code=500
        )


@dev_bp.route("/debug/services", methods=["GET"])
def debug_services() -> Dict[str, Any]:
    """获取所有服务的详细状态"""
    try:
        container = ServiceContainer.get_instance()
        services_detail = {}

        for service_name, service_info in container._services.items():
            service_instance = service_info.get("instance")
            services_detail[service_name] = {
                "registered": True,
                "initialized": service_instance is not None,
                "singleton": service_info.get("singleton", False),
                "type": str(service_info.get("service_type", "Unknown")),
                "status": "active" if service_instance else "not_initialized",
            }

        return success_response(data=services_detail)

    except Exception as e:
        return error_response(
            message=f"Failed to retrieve services info: {str(e)}",
            code="SERVICES_ERROR",
            status_code=500,
        )


@dev_bp.route("/debug/events", methods=["GET"])
def debug_events() -> Dict[str, Any]:
    """获取事件总线详细信息"""
    try:
        container = ServiceContainer.get_instance()
        event_dispatcher = container.resolve("IEventDispatcher")

        if not event_dispatcher:
            return error_response(
                message="Event dispatcher not available",
                code="EVENT_DISPATCHER_NOT_FOUND",
                status_code=404,
            )

        # 获取事件监听器信息
        listeners_info = {}
        for event_name, listeners in event_dispatcher._listeners.items():
            listeners_info[event_name] = [
                {"handler": str(listener), "priority": getattr(listener, "priority", 0)}
                for listener in listeners
            ]

        event_data = {
            "total_event_types": len(event_dispatcher._listeners),
            "total_listeners": sum(len(l) for l in event_dispatcher._listeners.values()),
            "listeners_by_event": listeners_info,
            "event_queue_size": len(getattr(event_dispatcher, "_event_queue", [])),
        }

        return success_response(data=event_data)

    except Exception as e:
        return error_response(
            message=f"Failed to retrieve events info: {str(e)}",
            code="EVENTS_ERROR",
            status_code=500,
        )


@dev_bp.route("/debug/metrics", methods=["GET"])
def debug_metrics() -> Dict[str, Any]:
    """获取性能指标详情"""
    try:
        metrics_data = metrics_registry.get_stats()
        return success_response(data=metrics_data)

    except Exception as e:
        return error_response(
            message=f"Failed to retrieve metrics: {str(e)}", code="METRICS_ERROR", status_code=500
        )


@dev_bp.route("/debug/logs", methods=["GET"])
def debug_logs() -> Dict[str, Any]:
    """获取最近的日志条目"""
    try:
        container = ServiceContainer.get_instance()
        log_service = container.resolve("ILogService")

        if not log_service:
            return error_response(
                message="Log service not available", code="LOG_SERVICE_NOT_FOUND", status_code=404
            )

        # 获取最近50条日志
        recent_logs = log_service.get_recent_logs(limit=50)
        log_stats = log_service.get_log_statistics()

        logs_data = {"recent_logs": [log.to_dict() for log in recent_logs], "statistics": log_stats}

        return success_response(data=logs_data)

    except Exception as e:
        return error_response(
            message=f"Failed to retrieve logs: {str(e)}", code="LOGS_ERROR", status_code=500
        )


# 辅助函数
def _get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    return {
        "python_version": sys.version,
        "platform": platform.platform(),
        "processor": platform.processor(),
        "architecture": platform.machine(),
        "hostname": platform.node(),
    }


def _get_services_info(container: ServiceContainer) -> Dict[str, Any]:
    """获取服务信息摘要"""
    total_services = len(container._services)
    initialized_services = sum(
        1 for s in container._services.values() if s.get("instance") is not None
    )

    return {
        "total_registered": total_services,
        "total_initialized": initialized_services,
        "initialization_rate": (
            f"{(initialized_services/total_services*100):.1f}%" if total_services > 0 else "0%"
        ),
    }


def _get_event_bus_info(container: ServiceContainer) -> Dict[str, Any]:
    """获取事件总线信息摘要"""
    try:
        event_dispatcher = container.resolve("IEventDispatcher")
        if not event_dispatcher:
            return {"status": "not_available"}

        return {
            "status": "active",
            "total_event_types": len(event_dispatcher._listeners),
            "total_listeners": sum(len(l) for l in event_dispatcher._listeners.values()),
        }
    except:
        return {"status": "error"}


def _get_metrics_summary() -> Dict[str, Any]:
    """获取指标摘要"""
    stats = metrics_registry.get_stats()
    return {
        "total_metrics": stats.get("metrics_count", 0),
        "counters": len(stats.get("counters", {})),
        "gauges": len(stats.get("gauges", {})),
        "histograms": len(stats.get("histograms", {})),
    }


def _get_resource_usage() -> Dict[str, Any]:
    """获取资源使用情况"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()

        return {
            "cpu_percent": process.cpu_percent(interval=0.1),
            "memory_usage_mb": memory_info.rss / 1024 / 1024,
            "memory_percent": process.memory_percent(),
            "num_threads": process.num_threads(),
            "num_fds": process.num_fds() if hasattr(process, "num_fds") else None,
        }
    except:
        return {"error": "Unable to retrieve resource usage"}


# 注册到API
def register_dev_api(app):
    """注册开发调试API"""
    app.register_blueprint(dev_bp)
