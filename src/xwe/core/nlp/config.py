"""
NLP 配置管理
管理 DeepSeek NLP 相关的配置
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class NLPConfig:
    """NLP 配置管理器"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        "enabled": True,                    # 是否启用NLP
        "provider": "deepseek",             # LLM提供商
        "model": "deepseek-chat",           # 模型名称
        "api_url": "https://api.deepseek.com/v1/chat/completions",
        "timeout": 30,                      # API超时时间（秒）
        "max_retries": 3,                   # 最大重试次数
        "cache_size": 128,                  # 缓存大小
        "temperature": 0.0,                 # 温度参数（0表示确定性输出）
        "max_tokens": 256,                  # 最大生成token数
        "fallback_enabled": True,           # 是否启用本地回退
        "log_level": "INFO",                # 日志级别
        "debug_mode": False,                # 调试模式
        "performance_monitoring": True,      # 性能监控
        "cost_tracking": True,              # 成本追踪
        "rate_limit": {
            "requests_per_minute": 20,      # 每分钟请求数限制
            "requests_per_hour": 500        # 每小时请求数限制
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()
        
    def _get_default_config_path(self) -> str:
        """获取默认配置文件路径"""
        return str(Path(__file__).parent.parent.parent / "config" / "nlp_config.json")
        
    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并用户配置和默认配置
                    config = self.DEFAULT_CONFIG.copy()
                    config.update(user_config)
                    logger.info(f"从 {self.config_path} 加载NLP配置")
                    return config
            except Exception as e:
                logger.error(f"加载配置文件失败: {e}")
                
        logger.info("使用默认NLP配置")
        return self.DEFAULT_CONFIG.copy()
        
    def save_config(self) -> bool:
        """保存配置"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
            logger.info(f"NLP配置已保存到 {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"保存配置文件失败: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        return self.config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        self.config[key] = value
        
    def update(self, updates: Dict[str, Any]) -> None:
        """批量更新配置"""
        self.config.update(updates)
        
    def is_enabled(self) -> bool:
        """检查NLP是否启用"""
        return self.config.get("enabled", False)
        
    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        # 优先从环境变量获取
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if api_key:
            return api_key
            
        # 从配置文件获取
        return self.config.get("api_key")
        
    def validate_config(self) -> bool:
        """验证配置是否有效"""
        if not self.is_enabled():
            return True  # 未启用时不需要验证
            
        # 检查API密钥
        if not self.get_api_key():
            logger.error("NLP已启用但未找到API密钥")
            return False
            
        # 检查必要字段
        required_fields = ["provider", "model", "api_url"]
        for field in required_fields:
            if not self.config.get(field):
                logger.error(f"缺少必要配置字段: {field}")
                return False
                
        return True
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return self.config.copy()
        
    def __repr__(self) -> str:
        """字符串表示"""
        return f"NLPConfig(enabled={self.is_enabled()}, provider={self.config.get('provider')})"


# 全局配置实例
_global_config = None


def get_nlp_config() -> NLPConfig:
    """获取全局NLP配置实例"""
    global _global_config
    if _global_config is None:
        _global_config = NLPConfig()
    return _global_config


def reset_nlp_config() -> None:
    """重置全局配置实例"""
    global _global_config
    _global_config = None
