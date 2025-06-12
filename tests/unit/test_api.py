"""
API测试脚本
用于测试新实现的RESTful API
"""

import requests  # type: ignore[import-untyped]
import json
import time
from typing import Dict, Any


class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.api_base = f"{base_url}/api/v1"
        self.session = requests.Session()
        
    def test_endpoint(self, method: str, endpoint: str, 
                     data: Dict[str, Any] = None,
                     expected_status: int = 200) -> Dict[str, Any]:
        """
        测试单个端点
        
        Args:
            method: HTTP方法
            endpoint: 端点路径
            data: 请求数据
            expected_status: 期望的状态码
            
        Returns:
            响应数据
        """
        url = f"{self.api_base}{endpoint}"
        
        print(f"\n{'='*50}")
        print(f"测试: {method} {endpoint}")
        
        if data:
            print(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
        
        # 发送请求
        try:
            if method == 'GET':
                response = self.session.get(url)
            elif method == 'POST':
                response = self.session.post(url, json=data)
            elif method == 'PUT':
                response = self.session.put(url, json=data)
            elif method == 'DELETE':
                response = self.session.delete(url)
            else:
                raise ValueError(f"不支持的方法: {method}")
            
            # 检查状态码
            print(f"状态码: {response.status_code}")
            
            if response.status_code != expected_status:
                print(f"❌ 期望状态码 {expected_status}, 实际 {response.status_code}")
            else:
                print(f"✅ 状态码正确")
            
            # 解析响应
            try:
                response_data = response.json()
                print(f"响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
                
                # 验证响应格式
                if 'success' in response_data:
                    if response_data['success']:
                        print("✅ 请求成功")
                    else:
                        print(f"❌ 请求失败: {response_data.get('error', {}).get('message', '未知错误')}")
                
                return response_data
                
            except json.JSONDecodeError:
                print(f"❌ 响应不是有效的JSON: {response.text}")
                return {}
                
        except Exception as e:
            print(f"❌ 请求失败: {str(e)}")
            return {}
    
    def run_all_tests(self):
        """运行所有测试"""
        print("开始API测试...")
        print(f"目标服务器: {self.base_url}")
        
        # 1. 测试系统API
        self.test_system_apis()
        
        # 2. 测试游戏API
        self.test_game_apis()
        
        # 3. 测试玩家API
        self.test_player_apis()
        
        # 4. 测试存档API
        self.test_save_apis()
        
        print("\n" + "="*50)
        print("API测试完成！")
    
    def test_system_apis(self):
        """测试系统相关API"""
        print("\n" + "="*70)
        print("测试系统API")
        print("="*70)
        
        # 系统信息
        self.test_endpoint('GET', '/system/info')
        
        # 命令列表
        self.test_endpoint('GET', '/system/commands')
        
        # 系统统计
        self.test_endpoint('GET', '/system/stats')
        
        # 健康检查
        self.test_endpoint('GET', '/system/health')
        
        # 游戏时间
        self.test_endpoint('GET', '/system/time')
    
    def test_game_apis(self):
        """测试游戏相关API"""
        print("\n" + "="*70)
        print("测试游戏API")
        print("="*70)
        
        # 初始化游戏
        self.test_endpoint('POST', '/game/initialize')
        
        # 获取状态
        self.test_endpoint('GET', '/game/status')
        
        # 执行命令
        self.test_endpoint('POST', '/game/command', 
                          data={'command': '帮助'})
        
        # 获取日志
        self.test_endpoint('GET', '/game/log?limit=10')
        
        # 获取事件
        self.test_endpoint('GET', '/game/events')
    
    def test_player_apis(self):
        """测试玩家相关API"""
        print("\n" + "="*70)
        print("测试玩家API")
        print("="*70)
        
        # 玩家信息
        self.test_endpoint('GET', '/player/info')
        
        # 技能列表
        self.test_endpoint('GET', '/player/skills')
        
        # 背包物品
        self.test_endpoint('GET', '/player/inventory')
        
        # 成就列表
        self.test_endpoint('GET', '/player/achievements')
        
        # 战斗统计
        self.test_endpoint('GET', '/player/stats/combat')
    
    def test_save_apis(self):
        """测试存档相关API"""
        print("\n" + "="*70)
        print("测试存档API")
        print("="*70)
        
        # 存档列表
        self.test_endpoint('GET', '/save/list')
        
        # 创建存档
        save_response = self.test_endpoint('POST', '/save/create',
                                         data={'name': '测试存档'})
        
        if save_response.get('success') and save_response.get('data'):
            save_id = save_response['data'].get('id')
            
            if save_id:
                # 获取存档详情
                self.test_endpoint('GET', f'/save/{save_id}')
                
                # 更新存档
                self.test_endpoint('PUT', f'/save/{save_id}',
                                 data={'name': '更新的存档名'})
                
                # 导出存档
                self.test_endpoint('GET', f'/save/export/{save_id}')
                
                # 删除存档
                self.test_endpoint('DELETE', f'/save/{save_id}')


def test_error_handling():
    """测试错误处理"""
    tester = APITester()
    
    print("\n" + "="*70)
    print("测试错误处理")
    print("="*70)
    
    # 测试无效的端点
    tester.test_endpoint('GET', '/invalid/endpoint', expected_status=404)
    
    # 测试无效的请求数据

    tester.test_endpoint(
        'POST',
        '/game/command',
        data={},  # 缺少required字段
        expected_status=400,
    )

    tester.test_endpoint('POST', '/game/command', data={}, expected_status=400)

    
    # 测试无效的命令
    tester.test_endpoint('POST', '/game/command',
                        data={'command': 'abcdefg'},
                        expected_status=400)


def test_concurrent_requests():
    """测试并发请求"""
    import threading
    
    print("\n" + "="*70)
    print("测试并发请求")
    print("="*70)
    
    def make_request(thread_id: int):
        tester = APITester()
        response = tester.test_endpoint('GET', '/system/info')
        print(f"线程 {thread_id} 完成")
    
    # 创建多个线程
    threads = []
    for i in range(5):
        thread = threading.Thread(target=make_request, args=(i,))
        threads.append(thread)
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("并发测试完成")


if __name__ == '__main__':
    # 主测试
    tester = APITester()
    
    # 运行所有测试
    tester.run_all_tests()
    
    # 测试错误处理
    test_error_handling()
    
    # 测试并发
    # test_concurrent_requests()
    
    print("\n提示：确保Flask应用正在运行在 http://localhost:5000")
