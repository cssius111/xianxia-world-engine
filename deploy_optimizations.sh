#!/bin/bash
# deploy_optimizations.sh
# 仙侠世界引擎优化部署脚本

set -e  # 遇到错误时退出

echo "=========================================="
echo "仙侠世界引擎优化部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查Python版本
check_python_version() {
    log_info "检查Python版本..."
    
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    log_info "Python版本: $PYTHON_VERSION"
    
    # 检查版本是否 >= 3.8
    if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
        log_success "Python版本符合要求 (>= 3.8)"
    else
        log_error "Python版本过低，需要 >= 3.8"
        exit 1
    fi
}

# 备份现有文件
backup_existing_files() {
    log_info "备份现有文件..."
    
    BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份核心文件
    if [ -f "xwe/core/game_core.py" ]; then
        cp xwe/core/game_core.py "$BACKUP_DIR/"
        log_success "已备份 game_core.py"
    fi
    
    if [ -f "main.py" ]; then
        cp main.py "$BACKUP_DIR/"
        log_success "已备份 main.py"
    fi
    
    if [ -f "requirements.txt" ]; then
        cp requirements.txt "$BACKUP_DIR/"
        log_success "已备份 requirements.txt"
    fi
    
    if [ -f ".env" ]; then
        cp .env "$BACKUP_DIR/"
        log_success "已备份 .env"
    fi
    
    log_success "备份完成，备份目录: $BACKUP_DIR"
}

# 创建优化目录结构
create_optimization_structure() {
    log_info "创建优化目录结构..."
    
    # 创建必要目录
    mkdir -p xwe/core/optimizations
    mkdir -p logs
    mkdir -p saves
    mkdir -p tests/unit
    mkdir -p tests/integration
    mkdir -p scripts
    
    # 创建__init__.py文件
    touch xwe/core/optimizations/__init__.py
    
    log_success "目录结构创建完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖包..."
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3 未安装"
        exit 1
    fi
    
    # 升级pip
    pip3 install --upgrade pip
    
    # 安装基础依赖
    if [ -f "requirements.txt" ]; then
        pip3 install -r requirements.txt
    fi
    
    # 安装优化相关依赖
    pip3 install psutil>=5.9.0
    pip3 install python-dotenv>=1.0.0
    
    log_success "依赖安装完成"
}

# 创建配置文件
create_config_files() {
    log_info "创建配置文件..."
    
    # 创建.env文件（如果不存在）
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# 仙侠世界引擎配置文件

# 游戏核心配置
USE_ENHANCED_CORE=true
ENABLE_PERFORMANCE_MONITORING=true

# 缓存配置
CACHE_MAX_SIZE=2000
CACHE_TTL=600
CACHE_MAX_MEMORY_MB=100

# 异步事件处理配置
ASYNC_MAX_WORKERS=4
ASYNC_QUEUE_SIZE=1000
ASYNC_ENABLE_STATS=true

# 性能优化配置
ENABLE_JIT_COMPILATION=true
ASYNC_EVENT_PROCESSING=true
MAX_CONCURRENT_EVENTS=10

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/xwe.log
ENABLE_DEBUG_LOGGING=false

# 调试配置
DEBUG_PERFORMANCE=false
LOG_CACHE_STATS=false
ENABLE_PROFILING=false

# LLM配置
LLM_PROVIDER=deepseek
# DEEPSEEK_API_KEY=your-api-key
# OPENAI_API_KEY=your-api-key

# 游戏设置
AUTO_SAVE_INTERVAL=300
MAX_SAVE_FILES=10
ENABLE_VISUAL_ENHANCEMENTS=true
EOF
        log_success "创建了.env配置文件"
    else
        log_warning ".env文件已存在，跳过创建"
    fi
}

# 创建基础的优化组件
create_basic_optimizations() {
    log_info "创建基础优化组件..."
    
    # 创建智能缓存系统
    cat > xwe/core/optimizations/smart_cache.py << 'EOF'
"""
智能缓存系统 - 简化版
"""
import time
import threading
from typing import Any, Optional, Dict
from collections import OrderedDict

class SmartCache:
    def __init__(self, max_size: int = 1000, ttl: float = 300.0):
        self.max_size = max_size
        self.ttl = ttl
        self._cache = OrderedDict()
        self._lock = threading.RLock()
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key: str) -> Optional[Any]:
        with self._lock:
            if key not in self._cache:
                self.miss_count += 1
                return None
            
            entry = self._cache[key]
            timestamp, value = entry['timestamp'], entry['value']
            
            # 检查是否过期
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                self.miss_count += 1
                return None
            
            # 移动到末尾（LRU）
            self._cache.move_to_end(key)
            self.hit_count += 1
            return value
    
    def set(self, key: str, value: Any):
        with self._lock:
            # 如果达到最大大小，删除最旧的
            if len(self._cache) >= self.max_size and key not in self._cache:
                self._cache.popitem(last=False)
            
            self._cache[key] = {
                'value': value,
                'timestamp': time.time()
            }
    
    @property
    def hit_rate(self) -> float:
        total = self.hit_count + self.miss_count
        return self.hit_count / total if total > 0 else 0.0
    
    def get_stats(self):
        return {
            'hit_count': self.hit_count,
            'miss_count': self.miss_count,
            'hit_rate': self.hit_rate,
            'cache_size': len(self._cache),
            'max_size': self.max_size
        }
    
    def clear(self):
        with self._lock:
            self._cache.clear()

# 全局缓存实例
_global_cache = SmartCache()

def get_global_cache():
    return _global_cache
EOF
    
    # 创建异步事件系统（简化版）
    cat > xwe/core/optimizations/async_event_system.py << 'EOF'
"""
异步事件处理系统 - 简化版
"""
import threading
import time
from typing import Dict, Any, List, Callable, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

class AsyncEventHandler:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.event_queue = deque()
        self.handlers = {}
        self.running = False
        self.workers = []
        self._lock = threading.Lock()
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        self.running = False
        for worker in self.workers:
            worker.join(timeout=1.0)
        self.workers.clear()
    
    def register_handler(self, event_type: str, handler: Callable):
        self.handlers[event_type] = handler
    
    def trigger_event_sync(self, event_type: str, data: Dict[str, Any]) -> str:
        event_id = f"{event_type}_{int(time.time() * 1000)}"
        event = {
            'id': event_id,
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        
        with self._lock:
            self.event_queue.append(event)
        
        return event_id
    
    def _worker_loop(self):
        while self.running:
            try:
                event = None
                with self._lock:
                    if self.event_queue:
                        event = self.event_queue.popleft()
                
                if event:
                    self._process_event(event)
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def _process_event(self, event):
        try:
            handler = self.handlers.get(event['type'])
            if handler:
                handler(event['data'])
        except Exception as e:
            logger.error(f"Event processing error: {e}")
    
    def process_pending_events(self):
        """同步处理挂起的事件"""
        processed = 0
        while processed < 10:  # 限制单次处理数量
            event = None
            with self._lock:
                if self.event_queue:
                    event = self.event_queue.popleft()
            
            if event:
                self._process_event(event)
                processed += 1
            else:
                break

# 全局事件处理器
_global_handler = None

def get_global_event_handler():
    global _global_handler
    if _global_handler is None:
        _global_handler = AsyncEventHandler()
        _global_handler.start()
    return _global_handler
EOF
    
    log_success "基础优化组件创建完成"
}

# 创建测试脚本
create_test_script() {
    log_info "创建测试脚本..."
    
    cat > test_basic_optimizations.py << 'EOF'
#!/usr/bin/env python3
"""
基础优化功能测试
"""
import sys
import time
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_cache():
    logger.info("测试缓存系统...")
    try:
        from xwe.core.optimizations.smart_cache import SmartCache
        
        cache = SmartCache(max_size=5, ttl=1.0)
        
        # 测试基本操作
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # 测试TTL
        time.sleep(1.1)
        assert cache.get("key1") is None
        
        # 测试统计
        stats = cache.get_stats()
        assert 'hit_rate' in stats
        
        logger.info("✓ 缓存系统测试通过")
        return True
    except Exception as e:
        logger.error(f"✗ 缓存系统测试失败: {e}")
        return False

def test_events():
    logger.info("测试事件系统...")
    try:
        from xwe.core.optimizations.async_event_system import AsyncEventHandler
        
        handler = AsyncEventHandler(max_workers=1)
        handler.start()
        
        # 注册处理器
        results = []
        def test_handler(data):
            results.append(data['message'])
        
        handler.register_handler("test", test_handler)
        
        # 触发事件
        handler.trigger_event_sync("test", {"message": "hello"})
        
        # 处理事件
        handler.process_pending_events()
        time.sleep(0.1)
        
        handler.stop()
        
        # 验证结果
        assert len(results) > 0
        assert results[0] == "hello"
        
        logger.info("✓ 事件系统测试通过")
        return True
    except Exception as e:
        logger.error(f"✗ 事件系统测试失败: {e}")
        return False

def main():
    logger.info("开始测试基础优化功能...")
    
    tests = [test_cache, test_events]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    logger.info(f"测试完成: {passed}/{len(tests)} 通过")
    return passed == len(tests)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
EOF
    
    chmod +x test_basic_optimizations.py
    log_success "测试脚本创建完成"
}

# 创建启动脚本
create_startup_script() {
    log_info "创建启动脚本..."
    
    cat > run_optimized_game.py << 'EOF'
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
EOF
    
    chmod +x run_optimized_game.py
    
    # 创建便捷脚本
    cat > start_game.sh << 'EOF'
#!/bin/bash
echo "启动仙侠世界引擎（优化版）..."
python3 run_optimized_game.py
EOF
    
    chmod +x start_game.sh
    log_success "启动脚本创建完成"
}

# 主函数
main() {
    echo "开始部署基础优化..."
    
    # 检查当前目录
    if [ ! -f "main.py" ] || [ ! -d "xwe" ]; then
        log_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行部署步骤
    check_python_version
    backup_existing_files
    create_optimization_structure
    install_dependencies
    create_config_files
    create_basic_optimizations
    create_test_script
    create_startup_script
    
    echo ""
    log_success "基础优化部署完成！"
    echo ""
    echo "下一步："
    echo "1. 运行测试: python3 test_basic_optimizations.py"
    echo "2. 启动游戏: ./start_game.sh"
    echo "3. 编辑 .env 文件调整配置"
    echo ""
}

# 脚本入口
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi
