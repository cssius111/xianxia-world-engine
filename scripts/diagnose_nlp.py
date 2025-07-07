#!/usr/bin/env python3
"""诊断 DeepSeek NLP 初始化问题"""
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

print("=== DeepSeek NLP 诊断 ===\n")

# 1. 检查 API Key
api_key = os.getenv('DEEPSEEK_API_KEY')
if api_key:
    print(f"1. API Key 已设置: {api_key[:10]}...")
else:
    print("1. API Key 未设置")

# 2. 尝试导入 NLP 模块
print("\n2. 测试 NLP 模块导入:")
try:
    from src.xwe.core.nlp.deepseek_nlp import DeepSeekNLPProcessor
    print("   ✅ 成功导入 DeepSeekNLPProcessor")
    
    # 尝试初始化
    print("\n3. 测试 NLP 初始化:")
    import time
    start_time = time.time()
    
    # 设置超时
    import signal
    def timeout_handler(signum, frame):
        raise TimeoutError("NLP 初始化超时")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(5)  # 5秒超时
    
    try:
        nlp = DeepSeekNLPProcessor()
        signal.alarm(0)  # 取消超时
        elapsed = time.time() - start_time
        print(f"   ✅ NLP 初始化成功 (耗时: {elapsed:.2f}秒)")
    except TimeoutError:
        print("   ❌ NLP 初始化超时（超过5秒）")
        print("   这可能是导致 Flask 启动阻塞的原因！")
    except Exception as e:
        signal.alarm(0)
        print(f"   ❌ NLP 初始化失败: {e}")
        
except ImportError as e:
    print(f"   ❌ 无法导入 NLP 模块: {e}")
except Exception as e:
    print(f"   ❌ 其他错误: {e}")

print("\n4. 建议:")
print("   如果 NLP 初始化超时或失败，可以：")
print("   a) 临时禁用 NLP: export DISABLE_NLP=true")
print("   b) 检查网络连接")
print("   c) 验证 API Key 是否有效")
