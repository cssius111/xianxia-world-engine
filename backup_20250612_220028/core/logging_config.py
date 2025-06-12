"""
日志配置
"""

import logging
import sys

def setup_logging(debug=True) -> None:
    """配置日志系统"""
    level = logging.DEBUG if debug else logging.INFO
    
    # 配置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)
    
    # 配置根日志器
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    
    # 特定模块的日志级别
    logging.getLogger('xwe.core.nlp').setLevel(logging.DEBUG)
    logging.getLogger('xwe.core.command_router').setLevel(logging.DEBUG)
    
    return root_logger
