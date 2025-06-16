#!/usr/bin/env python3
"""
优化版游戏启动脚本
"""
import os
import sys
import logging
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 加载环境变量
try:
    from xwe.utils.dotenv_helper import load_dotenv
    load_dotenv()
except ImportError:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("启动优化版仙侠世界引擎...")
    
    try:
        # 检查是否使用优化功能
        use_cache = os.getenv('USE_ENHANCED_CORE', 'false').lower() == 'true'
        
        if use_cache:
            logger.info("启用缓存和优化功能")
            from xwe.core.optimizations.smart_cache import get_global_cache
            cache = get_global_cache()
            logger.info(f"缓存系统已就绪: max_size={cache.max_size}")
        
        # 启动原有游戏
        from main import main as original_main
        original_main()
        
    except ImportError as e:
        logger.error(f"导入错误: {e}")
        logger.info("回退到标准版本...")
        from main import main as original_main
        original_main()
    except Exception as e:
        logger.error(f"启动失败: {e}")

if __name__ == "__main__":
    main()
