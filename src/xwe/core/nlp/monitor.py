"""
NLP 性能监控
跟踪和分析 NLP 处理器的性能指标
"""

import time
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json

logger = logging.getLogger(__name__)


@dataclass
class RequestMetrics:
    """请求度量数据"""
    timestamp: float
    duration: float  # 秒
    success: bool
    command: str
    handler: str
    confidence: float
    use_cache: bool
    error: Optional[str] = None
    token_count: int = 0
    

class NLPMonitor:
    """NLP 性能监控器"""
    
    def __init__(self, max_history: int = 1000):
        """
        初始化监控器
        
        Args:
            max_history: 最大历史记录数
        """
        self.max_history = max_history
        self.request_history: deque = deque(maxlen=max_history)
        self.start_time = time.time()
        
        # 统计数据
        self.total_requests = 0
        self.total_success = 0
        self.total_failures = 0
        self.total_cache_hits = 0
        self.total_duration = 0.0
        self.total_tokens = 0
        
        # 命令统计
        self.command_stats: Dict[str, int] = {}
        self.handler_stats: Dict[str, int] = {}
        
    def record_request(self, 
                      command: str,
                      handler: str,
                      duration: float,
                      success: bool,
                      confidence: float = 1.0,
                      use_cache: bool = False,
                      error: Optional[str] = None,
                      token_count: int = 0) -> None:
        """
        记录请求
        
        Args:
            command: 原始命令
            handler: 处理器名称
            duration: 处理时长（秒）
            success: 是否成功
            confidence: 置信度
            use_cache: 是否使用缓存
            error: 错误信息
            token_count: token使用量
        """
        # 创建度量对象
        metric = RequestMetrics(
            timestamp=time.time(),
            duration=duration,
            success=success,
            command=command,
            handler=handler,
            confidence=confidence,
            use_cache=use_cache,
            error=error,
            token_count=token_count
        )
        
        # 添加到历史
        self.request_history.append(metric)
        
        # 更新统计
        self.total_requests += 1
        if success:
            self.total_success += 1
        else:
            self.total_failures += 1
            
        if use_cache:
            self.total_cache_hits += 1
            
        self.total_duration += duration
        self.total_tokens += token_count
        
        # 更新命令统计
        self.command_stats[command] = self.command_stats.get(command, 0) + 1
        self.handler_stats[handler] = self.handler_stats.get(handler, 0) + 1
        
        # 日志记录
        if not success:
            logger.warning(f"NLP请求失败: {command} -> {error}")
        elif duration > 5:  # 慢请求
            logger.warning(f"NLP慢请求: {command} 耗时 {duration:.2f}秒")
            
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        uptime = time.time() - self.start_time
        
        # 计算成功率
        success_rate = (self.total_success / self.total_requests * 100) if self.total_requests > 0 else 0
        
        # 计算平均响应时间
        avg_duration = (self.total_duration / self.total_requests) if self.total_requests > 0 else 0
        
        # 计算缓存命中率
        cache_hit_rate = (self.total_cache_hits / self.total_requests * 100) if self.total_requests > 0 else 0
        
        # 获取最近的性能数据
        recent_requests = self.get_recent_requests(minutes=5)
        recent_avg_duration = 0
        if recent_requests:
            recent_avg_duration = sum(r.duration for r in recent_requests) / len(recent_requests)
            
        # 获取热门命令
        top_commands = sorted(
            self.command_stats.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:10]
        
        # 获取处理器使用情况
        handler_usage = sorted(
            self.handler_stats.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return {
            "uptime_seconds": uptime,
            "uptime_readable": self._format_duration(uptime),
            "total_requests": self.total_requests,
            "total_success": self.total_success,
            "total_failures": self.total_failures,
            "success_rate": round(success_rate, 2),
            "total_cache_hits": self.total_cache_hits,
            "cache_hit_rate": round(cache_hit_rate, 2),
            "avg_duration_ms": round(avg_duration * 1000, 2),
            "recent_avg_duration_ms": round(recent_avg_duration * 1000, 2),
            "total_tokens": self.total_tokens,
            "estimated_cost": self._estimate_cost(self.total_tokens),
            "top_commands": top_commands,
            "handler_usage": handler_usage,
            "requests_per_minute": self._calculate_rpm(),
            "requests_per_hour": self._calculate_rph()
        }
        
    def get_recent_requests(self, minutes: int = 5) -> List[RequestMetrics]:
        """获取最近N分钟的请求"""
        cutoff_time = time.time() - (minutes * 60)
        return [r for r in self.request_history if r.timestamp > cutoff_time]
        
    def get_error_summary(self) -> Dict[str, int]:
        """获取错误摘要"""
        error_counts = {}
        for metric in self.request_history:
            if not metric.success and metric.error:
                error_type = metric.error.split(':')[0]  # 简化错误类型
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        return error_counts
        
    def get_performance_report(self) -> str:
        """生成性能报告"""
        stats = self.get_stats()
        
        report = f"""
=== NLP 性能报告 ===

运行时间: {stats['uptime_readable']}
总请求数: {stats['total_requests']}
成功率: {stats['success_rate']}%
缓存命中率: {stats['cache_hit_rate']}%

平均响应时间: {stats['avg_duration_ms']}ms
最近5分钟平均: {stats['recent_avg_duration_ms']}ms

Token使用量: {stats['total_tokens']}
预估成本: ${stats['estimated_cost']:.4f}

请求速率:
- 每分钟: {stats['requests_per_minute']:.1f}
- 每小时: {stats['requests_per_hour']:.1f}

热门命令 TOP 5:
"""
        
        for i, (cmd, count) in enumerate(stats['top_commands'][:5], 1):
            report += f"{i}. {cmd[:30]}... ({count}次)\n"
            
        return report
        
    def export_metrics(self, filepath: str) -> bool:
        """导出度量数据"""
        try:
            data = {
                "export_time": datetime.now().isoformat(),
                "stats": self.get_stats(),
                "error_summary": self.get_error_summary(),
                "recent_requests": [
                    {
                        "timestamp": r.timestamp,
                        "command": r.command,
                        "handler": r.handler,
                        "duration_ms": r.duration * 1000,
                        "success": r.success,
                        "confidence": r.confidence,
                        "use_cache": r.use_cache,
                        "error": r.error
                    }
                    for r in list(self.request_history)[-100:]  # 最近100条
                ]
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            logger.info(f"性能数据已导出到 {filepath}")
            return True
            
        except Exception as e:
            logger.error(f"导出性能数据失败: {e}")
            return False
            
    def _format_duration(self, seconds: float) -> str:
        """格式化时长"""
        td = timedelta(seconds=int(seconds))
        days = td.days
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        
        parts = []
        if days > 0:
            parts.append(f"{days}天")
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
            
        return " ".join(parts) or "刚刚启动"
        
    def _estimate_cost(self, tokens: int) -> float:
        """估算成本（基于DeepSeek定价）"""
        # DeepSeek 的大概定价（需要根据实际情况调整）
        # 假设每1000 tokens约0.002美元
        price_per_1k_tokens = 0.002
        return (tokens / 1000) * price_per_1k_tokens
        
    def _calculate_rpm(self) -> float:
        """计算每分钟请求数"""
        recent = self.get_recent_requests(minutes=1)
        return len(recent)
        
    def _calculate_rph(self) -> float:
        """计算每小时请求数"""
        recent = self.get_recent_requests(minutes=60)
        return len(recent)
        

# 全局监控实例
_global_monitor = None


def get_nlp_monitor() -> NLPMonitor:
    """获取全局监控实例"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = NLPMonitor()
    return _global_monitor


def reset_nlp_monitor() -> None:
    """重置全局监控实例"""
    global _global_monitor
    _global_monitor = None
