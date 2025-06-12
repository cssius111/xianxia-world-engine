"""
Metrics module for monitoring and observability
"""
from .prometheus import PrometheusMetrics, metrics_registry


from .prometheus import (
    PrometheusMetrics,
    metrics_registry,
    inc_counter,
    time_histogram
)

__all__ = [
    "PrometheusMetrics",
    "metrics_registry",
    "inc_counter",
    "time_histogram"
]
