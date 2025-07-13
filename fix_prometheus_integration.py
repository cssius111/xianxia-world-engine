#!/usr/bin/env python3
"""
修复和完善 XWE 项目的 Prometheus 集成
"""

import os
import sys
import subprocess

def fix_app_py():
    """修复 app.py 中的导入路径问题"""
    print("📝 修复 app.py 中的 Prometheus 导入...")
    
    app_py_path = "app.py"
    
    # 读取当前内容
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复导入路径
    old_import = "from xwe.metrics.prometheus_metrics import"
    new_import = "from src.xwe.metrics.prometheus_metrics import"
    
    if old_import in content:
        content = content.replace(old_import, new_import)
        with open(app_py_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print("✅ 已修复导入路径")
    else:
        print("ℹ️ 导入路径可能已经正确或需要其他修复")
    
    # 确保 PYTHONPATH 包含 src 目录
    print("\n📝 创建启动脚本以确保正确的 PYTHONPATH...")
    
    startup_script = """#!/bin/bash
# XWE 启动脚本 - 确保正确的 Python 路径

export PYTHONPATH="${PYTHONPATH}:$(pwd):$(pwd)/src"
export ENABLE_PROMETHEUS=true

echo "🚀 启动 XianXia World Engine..."
echo "📊 Prometheus 监控已启用"
echo "📍 访问 http://localhost:5000/metrics 查看指标"

python app.py
"""
    
    with open("start_xwe.sh", 'w') as f:
        f.write(startup_script)
    
    os.chmod("start_xwe.sh", 0o755)
    print("✅ 创建启动脚本 start_xwe.sh")

def create_nlp_monitor_wrapper():
    """创建 NLP 监控包装器"""
    print("\n📝 创建 NLP 监控包装器...")
    
    nlp_monitor_code = '''"""
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
'''
    
    # 创建目录
    monitor_dir = "src/xwe/metrics/monitors"
    os.makedirs(monitor_dir, exist_ok=True)
    
    # 写入文件
    with open(os.path.join(monitor_dir, "__init__.py"), 'w') as f:
        f.write("")
    
    with open(os.path.join(monitor_dir, "nlp_monitor.py"), 'w', encoding='utf-8') as f:
        f.write(nlp_monitor_code)
    
    print("✅ 创建 NLP 监控包装器")

def update_requirements():
    """确保所有必要的依赖都在 requirements.txt 中"""
    print("\n📝 检查并更新 requirements.txt...")
    
    required_packages = [
        "prometheus-flask-exporter==0.23.0",
        "prometheus-client==0.19.0",
        "psutil==5.9.8"  # 用于系统指标
    ]
    
    with open("requirements.txt", 'r') as f:
        current_content = f.read()
    
    packages_to_add = []
    for package in required_packages:
        package_name = package.split('==')[0]
        if package_name not in current_content:
            packages_to_add.append(package)
    
    if packages_to_add:
        print(f"📦 添加缺失的包: {packages_to_add}")
        with open("requirements.txt", 'a') as f:
            f.write("\n# 监控相关依赖\n")
            for package in packages_to_add:
                f.write(f"{package}\n")
        print("✅ 更新 requirements.txt")
    else:
        print("✅ 所有必要的包都已存在")

def create_example_integration():
    """创建集成示例"""
    print("\n📝 创建集成示例...")
    
    example_code = '''"""
Prometheus 监控集成示例
展示如何在 XWE 中使用监控功能
"""

import time
from src.xwe.metrics.monitors.nlp_monitor import nlp_monitor

# 示例 1: 使用装饰器监控函数
@nlp_monitor.monitor_llm_call(model="deepseek-chat")
def call_deepseek_api(prompt: str) -> dict:
    """模拟 DeepSeek API 调用"""
    # 模拟 API 延迟
    time.sleep(0.5)
    
    # 模拟返回结果
    return {
        "choices": [{
            "message": {
                "content": "这是一个测试响应"
            }
        }],
        "usage": {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
    }

# 示例 2: 手动记录指标
def process_player_command(command: str):
    """处理玩家命令"""
    start_time = time.time()
    
    try:
        # 调用 NLP API
        response = call_deepseek_api(f"玩家说：{command}")
        
        # 处理响应...
        
        # 手动记录成功
        nlp_monitor.record_request(
            prompt=command,
            response=response,
            duration=time.time() - start_time,
            model="deepseek-chat"
        )
        
    except Exception as e:
        # 记录失败
        nlp_monitor.record_request(
            prompt=command,
            response=None,
            duration=time.time() - start_time,
            model="deepseek-chat",
            error=e
        )
        raise

if __name__ == "__main__":
    print("🧪 测试 Prometheus 监控集成...")
    
    # 测试装饰器方式
    result = call_deepseek_api("探索周围环境")
    print(f"✅ API 调用成功: {result}")
    
    # 测试手动记录方式
    process_player_command("开始修炼")
    print("✅ 命令处理成功")
    
    print("\\n📊 指标已记录，访问 http://localhost:5000/metrics 查看")
'''
    
    with open("examples/prometheus_integration_example.py", 'w', encoding='utf-8') as f:
        f.write(example_code)
    
    print("✅ 创建集成示例")

def main():
    """主函数"""
    print("🚀 开始修复和完善 Prometheus 集成...")
    
    # 1. 修复 app.py
    fix_app_py()
    
    # 2. 创建 NLP 监控包装器
    create_nlp_monitor_wrapper()
    
    # 3. 更新依赖
    update_requirements()
    
    # 4. 创建示例
    create_example_integration()
    
    print("\n✨ 完成！下一步：")
    print("1. 运行 'pip install -r requirements.txt' 安装依赖")
    print("2. 运行 './start_xwe.sh' 启动应用")
    print("3. 访问 http://localhost:5000/metrics 查看指标")
    print("4. 参考 examples/prometheus_integration_example.py 集成监控")

if __name__ == "__main__":
    main()
