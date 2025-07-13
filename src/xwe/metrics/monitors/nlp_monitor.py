"""
NLP 监控包装器 - 用于记录 DeepSeek API 调用指标
"""

import time
import logging
from typing import Dict, Any, Optional, Callable
from functools import wraps

logger = logging.getLogger(__name__)

try:
    from src.xwe.metrics.prometheus_metrics import metrics_collector
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False
    logger.warning("Prometheus metrics not available")

class NLPMonitor:
    """NLP API 调用监控器"""
    
    def __init__(self):
        self.enabled = METRICS_AVAILABLE
        
    def monitor_llm_call(self, model: str = "deepseek-chat"):
        """
        装饰器：监控 LLM API 调用
        
        使用示例:
            @nlp_monitor.monitor_llm_call(model="deepseek-chat")
            def call_deepseek_api(prompt: str) -> Dict[str, Any]:
                # 调用 API 的代码
                pass
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                
                start_time = time.time()
                success = False
                token_count = 0
                error_type = None
                
                try:
                    result = func(*args, **kwargs)
                    success = True
                    
                    # 尝试从结果中提取 token 计数
                    if isinstance(result, dict):
                        usage = result.get('usage', {})
                        token_count = usage.get('total_tokens', 0)
                    
                    return result
                    
                except Exception as e:
                    error_type = type(e).__name__
                    logger.error(f"LLM API call failed: {e}")
                    raise
                    
                finally:
                    duration = time.time() - start_time
                    
                    if METRICS_AVAILABLE:
                        try:
                            # 推断命令类型
                            command_type = "unknown"
                            if args and isinstance(args[0], str):
                                # 简单的命令类型推断
                                prompt = args[0].lower()
                                if "探索" in prompt or "explore" in prompt:
                                    command_type = "explore"
                                elif "战斗" in prompt or "fight" in prompt:
                                    command_type = "combat"
                                elif "修炼" in prompt or "cultivate" in prompt:
                                    command_type = "cultivate"
                                elif "交谈" in prompt or "talk" in prompt:
                                    command_type = "dialogue"
                            
                            metrics_collector.record_nlp_request(
                                command_type=command_type,
                                duration=duration,
                                success=success,
                                token_count=token_count,
                                model=model,
                                error_type=error_type
                            )
                            
                            # 记录 API 调用延迟
                            metrics_collector.record_api_call(
                                api_name="deepseek",
                                endpoint="/v1/chat/completions",
                                duration=duration
                            )
                        except Exception as e:
                            logger.error(f"Failed to record metrics: {e}")
            
            return wrapper
        return decorator
    
    def record_request(self, 
                      prompt: str,
                      response: Dict[str, Any],
                      duration: float,
                      model: str = "deepseek-chat",
                      error: Optional[Exception] = None):
        """
        手动记录 NLP 请求
        
        Args:
            prompt: 输入提示
            response: API 响应
            duration: 请求耗时（秒）
            model: 使用的模型
            error: 发生的错误（如果有）
        """
        if not self.enabled or not METRICS_AVAILABLE:
            return
        
        try:
            # 提取信息
            success = error is None
            token_count = 0
            command_type = "unknown"
            
            if response and isinstance(response, dict):
                usage = response.get('usage', {})
                token_count = usage.get('total_tokens', 0)
            
            # 简单的命令类型推断
            if prompt:
                prompt_lower = prompt.lower()
                if "探索" in prompt_lower:
                    command_type = "explore"
                elif "战斗" in prompt_lower:
                    command_type = "combat"
                elif "修炼" in prompt_lower:
                    command_type = "cultivate"
            
            # 记录指标
            metrics_collector.record_nlp_request(
                command_type=command_type,
                duration=duration,
                success=success,
                token_count=token_count,
                model=model,
                error_type=type(error).__name__ if error else None
            )
            
        except Exception as e:
            logger.error(f"Failed to record NLP metrics: {e}")

# 全局实例
nlp_monitor = NLPMonitor()
