"""
环境变量配置管理
提供集中的配置管理和验证
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging


@dataclass
class Config:
    """应用配置"""
    # Flask配置
    FLASK_ENV: str = "production"
    FLASK_DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-here"
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: Optional[str] = None
    LOG_MAX_SIZE: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # API配置
    ENABLE_DEV_API: bool = False
    API_RATE_LIMIT: str = "100/minute"
    
    # Prometheus配置
    METRICS_ENABLED: bool = True
    METRICS_PATH: str = "/api/v1/system/metrics"
    METRICS_MAX_LABELS: int = 1000
    
    # Docker/健康检查配置
    HEALTH_CHECK_INTERVAL: int = 30
    HEALTH_CHECK_TIMEOUT: int = 10
    
    # 数据库配置（未来使用）
    DATABASE_URL: Optional[str] = None
    DATABASE_POOL_SIZE: int = 10
    
    # 缓存配置（未来使用）
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 300  # 5分钟
    
    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量创建配置"""
        config = cls()
        
        # Flask配置
        config.FLASK_ENV = os.environ.get('FLASK_ENV', 'production')
        config.FLASK_DEBUG = os.environ.get('FLASK_DEBUG', '0') == '1'
        config.SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
        
        # 日志配置
        config.LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
        config.LOG_FORMAT = os.environ.get('LOG_FORMAT', 'json').lower()
        config.LOG_FILE = os.environ.get('LOG_FILE')
        
        # API配置
        config.ENABLE_DEV_API = os.environ.get('ENABLE_DEV_API', 'false').lower() in ('true', '1', 'yes')
        config.API_RATE_LIMIT = os.environ.get('API_RATE_LIMIT', '100/minute')
        
        # Prometheus配置
        config.METRICS_ENABLED = os.environ.get('METRICS_ENABLED', 'true').lower() in ('true', '1', 'yes')
        config.METRICS_MAX_LABELS = int(os.environ.get('METRICS_MAX_LABELS', '1000'))
        
        # 验证配置
        config.validate()
        
        return config
    
    def validate(self) -> None:
        """验证配置值"""
        # 验证日志级别
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.LOG_LEVEL not in valid_levels:
            raise ValueError(f"Invalid LOG_LEVEL: {self.LOG_LEVEL}. Must be one of {valid_levels}")
        
        # 验证日志格式
        if self.LOG_FORMAT not in ['json', 'text']:
            raise ValueError(f"Invalid LOG_FORMAT: {self.LOG_FORMAT}. Must be 'json' or 'text'")
        
        # 验证生产环境设置
        if self.FLASK_ENV == 'production':
            if self.FLASK_DEBUG:
                print("WARNING: Debug mode enabled in production!")
            if self.ENABLE_DEV_API:
                print("WARNING: Dev API enabled in production!")
            if self.LOG_LEVEL == 'DEBUG':
                print("WARNING: Debug logging enabled in production!")
    
    def get_log_level_int(self) -> int:
        """获取Python logging模块的日志级别"""
        return getattr(logging, self.LOG_LEVEL, logging.INFO)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（隐藏敏感信息）"""
        result = {}
        for key, value in self.__dict__.items():
            if key.upper() == key:  # 只包含大写字段
                if 'SECRET' in key or 'PASSWORD' in key:
                    result[key] = '***HIDDEN***'
                else:
                    result[key] = value
        return result


# 全局配置实例
config = Config.from_env()


def configure_logging(app=None):
    """配置日志系统"""
    import logging.config
    
    if config.LOG_FORMAT == 'json':
        # JSON格式日志配置
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'json': {
                    'class': 'xwe.services.log_service.StructuredLogger',
                    'service_name': 'xwe'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': config.LOG_LEVEL,
                    'formatter': 'json',
                    'stream': 'ext://sys.stdout'
                }
            },
            'root': {
                'level': config.LOG_LEVEL,
                'handlers': ['console']
            }
        }
    else:
        # 文本格式日志配置
        logging_config = {
            'version': 1,
            'disable_existing_loggers': False,
            'formatters': {
                'default': {
                    'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
                    'datefmt': '%Y-%m-%d %H:%M:%S'
                }
            },
            'handlers': {
                'console': {
                    'class': 'logging.StreamHandler',
                    'level': config.LOG_LEVEL,
                    'formatter': 'default',
                    'stream': 'ext://sys.stdout'
                }
            },
            'root': {
                'level': config.LOG_LEVEL,
                'handlers': ['console']
            }
        }
    
    # 添加文件处理器（如果配置了）
    if config.LOG_FILE:
        logging_config['handlers']['file'] = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': config.LOG_LEVEL,
            'formatter': 'json' if config.LOG_FORMAT == 'json' else 'default',
            'filename': config.LOG_FILE,
            'maxBytes': config.LOG_MAX_SIZE,
            'backupCount': config.LOG_BACKUP_COUNT
        }
        logging_config['root']['handlers'].append('file')
    
    logging.config.dictConfig(logging_config)
    
    # 设置Flask日志级别
    if app:
        app.logger.setLevel(config.get_log_level_int())
        
        # 生产环境禁用某些日志
        if config.FLASK_ENV == 'production':
            logging.getLogger('werkzeug').setLevel(logging.WARNING)
