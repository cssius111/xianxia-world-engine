#!/usr/bin/env python3
"""
DeepSeek NLP 集成测试脚本
快速验证 NLP 功能是否正常工作
"""

import os
import sys
import logging
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_environment():
    """检查环境配置"""
    print("=== 环境检查 ===")
    
    # 检查 API 密钥
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if api_key:
        print("✅ DEEPSEEK_API_KEY 已设置")
    else:
        print("❌ DEEPSEEK_API_KEY 未设置")
        print("   请在 .env 文件中设置或使用:")
        print("   export DEEPSEEK_API_KEY='your-api-key'")
        return False
        
    # 检查依赖
    try:
        import requests
        print("✅ requests 已安装")
    except ImportError:
        print("❌ requests 未安装")
        return False
        
    try:
        import backoff
        print("✅ backoff 已安装")
    except ImportError:
        print("❌ backoff 未安装")
        return False
        
    return True


def run_nlp_processor():
    """测试 NLP 处理器"""
    print("\n=== 测试 NLP 处理器 ===")
    
    try:
        from xwe.core.nlp import DeepSeekNLPProcessor
        
        # 创建处理器
        processor = DeepSeekNLPProcessor()
        print("✅ NLP 处理器初始化成功")
        
        # 测试解析
        test_commands = [
            "四处看看",
            "休息一个时辰",
            "去丹药铺",
            "使用回春丹"
        ]
        
        print("\n测试命令解析:")
        for cmd in test_commands:
            print(f"\n输入: {cmd}")
            try:
                result = processor.parse(cmd, use_cache=False)
                print(f"  命令: {result.normalized_command}")
                print(f"  意图: {result.intent}")
                print(f"  参数: {result.args}")
                print(f"  说明: {result.explanation}")
            except Exception as e:
                print(f"  ❌ 解析失败: {e}")
                
        # 显示缓存信息
        cache_info = processor.get_cache_info()
        print(f"\n缓存信息:")
        print(f"  命中率: {cache_info['hit_rate']:.1%}")
        print(f"  当前大小: {cache_info['currsize']}/{cache_info['maxsize']}")
        
        return True
        
    except Exception as e:
        print(f"❌ NLP 处理器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_nlp_processor():
    assert run_nlp_processor()


def run_command_router():
    """测试命令路由器"""
    print("\n=== 测试命令路由器 ===")
    
    try:
        from xwe.core.command_router import CommandRouter
        
        # 创建路由器
        router = CommandRouter(use_nlp=True)
        print("✅ 命令路由器初始化成功")
        
        # 测试路由
        test_inputs = [
            "随便走走看看",
            "打坐修炼一会儿",
            "查看我的背包"
        ]
        
        print("\n测试命令路由:")
        for inp in test_inputs:
            print(f"\n输入: {inp}")
            handler, params = router.route_command(inp)
            print(f"  处理器: {handler}")
            print(f"  参数: {params}")
            
        return True
        
    except Exception as e:
        print(f"❌ 命令路由器测试失败: {e}")
        return False

def test_command_router():
    assert run_command_router()


def run_monitor():
    """测试性能监控"""
    print("\n=== 测试性能监控 ===")
    
    try:
        from xwe.core.nlp.monitor import get_nlp_monitor
        
        monitor = get_nlp_monitor()
        print("✅ 性能监控器初始化成功")
        
        # 记录一些测试数据
        monitor.record_request(
            command="测试命令",
            handler="test",
            duration=0.5,
            success=True,
            confidence=0.95,
            use_cache=False,
            token_count=50
        )
        
        # 获取统计
        stats = monitor.get_stats()
        print("\n性能统计:")
        print(f"  总请求数: {stats['total_requests']}")
        print(f"  成功率: {stats['success_rate']}%")
        print(f"  平均响应时间: {stats['avg_duration_ms']}ms")
        
        return True
        
    except Exception as e:
        print(f"❌ 性能监控测试失败: {e}")
        return False

def test_monitor():
    assert run_monitor()


def run_flask_integration():
    """测试 Flask 集成"""
    print("\n=== 测试 Flask 集成 ===")
    
    try:
        from run import app
        
        # 创建测试客户端
        client = app.test_client()
        
        # 测试命令接口
        response = client.post('/command', 
            json={'text': '探索周围', 'command': '探索周围'},
            content_type='application/json'
        )
        
        if response.status_code == 200:
            data = response.get_json()
            print("✅ Flask 集成测试成功")
            print(f"  响应: {data.get('result', '无结果')[:50]}...")
        else:
            print(f"❌ Flask 集成测试失败: {response.status_code}")
            
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ Flask 集成测试失败: {e}")
        return False

def test_flask_integration():
    assert run_flask_integration()


def main():
    """主测试流程"""
    print("🚀 DeepSeek NLP 集成测试")
    print("=" * 50)
    
    # 加载环境变量
    from dotenv import load_dotenv
    load_dotenv()
    
    # 执行测试
    tests = [
        ("环境检查", check_environment),
        ("NLP处理器", run_nlp_processor),
        ("命令路由", run_command_router),
        ("性能监控", run_monitor),
        ("Flask集成", run_flask_integration)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            logger.error(f"{name}测试异常: {e}")
            results.append((name, False))
            
    # 总结
    print("\n" + "=" * 50)
    print("📊 测试总结")
    print("=" * 50)
    
    total = len(results)
    passed = sum(1 for _, success in results if success)
    
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{name}: {status}")
        
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！NLP 功能已准备就绪。")
        print("\n下一步:")
        print("1. 运行 python start_web.py 启动游戏")
        print("2. 访问 http://localhost:5001")
        print("3. 在游戏中尝试自然语言命令")
        print("4. 访问 http://localhost:5001/nlp_monitor 查看性能")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
        

if __name__ == "__main__":
    main()
