# main_enhanced_v3.py

"""
增强版主程序 - 使用AI和性能优化功能
"""

import asyncio
import os
import sys
import logging
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from xwe.core.game_core_enhanced import create_enhanced_game

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class EnhancedGameRunner:
    """增强版游戏运行器"""
    
    def __init__(self):
        self.game = None
        self.running = False
        
    async def initialize(self):
        """初始化游戏"""
        logger.info("=== 修仙世界引擎 v3.0 (增强版) ===")
        logger.info("正在初始化游戏系统...")
        
        try:
            # 创建增强版游戏实例
            self.game = create_enhanced_game()
            
            # 等待异步组件初始化完成
            await asyncio.sleep(0.1)
            
            logger.info("游戏初始化完成！")
            
            # 显示启用的功能
            self._show_enabled_features()
            
        except Exception as e:
            logger.error(f"游戏初始化失败：{e}")
            raise
            
    def _show_enabled_features(self):
        """显示启用的功能"""
        features = []
        
        if self.game.dialogue_manager:
            features.append("AI对话系统")
        if self.game.narrative_generator:
            features.append("动态叙事生成")
        if self.game.world_event_generator:
            features.append("AI世界事件")
        if self.game.jit_compiler:
            features.append("JIT表达式编译")
        if self.game.smart_cache:
            features.append("智能缓存")
        if self.game.async_events:
            features.append("异步事件系统")
        if self.game.plugin_manager:
            plugin_count = len(self.game.plugin_manager.plugins)
            features.append(f"插件系统 ({plugin_count}个插件)")
            
        if features:
            logger.info("已启用的增强功能：")
            for feature in features:
                logger.info(f"  ✓ {feature}")
        else:
            logger.warning("未启用任何增强功能，请检查配置文件。")
            
    async def run(self):
        """运行游戏主循环"""
        self.running = True
        
        print("\n" + "="*50)
        print("欢迎来到修仙世界！")
        print("="*50)
        print()
        
        # 显示初始状态
        status = self.game.process_command("状态")
        print(status)
        print()
        
        # 显示帮助
        print("输入 '帮助' 查看所有可用命令")
        print("输入 '退出' 结束游戏")
        print()
        
        # 主循环
        while self.running:
            try:
                # 获取用户输入
                user_input = await self._get_user_input()
                
                if not user_input:
                    continue
                    
                # 检查退出命令
                if user_input.lower() in ['退出', 'exit', 'quit']:
                    self.running = False
                    break
                    
                # 处理命令
                if self.game.ai_config.get('ai_features', {}).get('enabled'):
                    # 使用增强的AI处理
                    response = await self.game.process_enhanced_command(user_input)
                else:
                    # 使用普通处理
                    response = self.game.process_command(user_input)
                    
                # 显示响应
                if response:
                    print("\n" + response)
                    
                    # 如果有战斗或探索事件，生成叙事
                    await self._generate_narrative_if_needed(user_input, response)
                    
                print()
                
                # 处理异步事件
                await self._process_async_events()
                
            except KeyboardInterrupt:
                print("\n\n游戏被中断。")
                self.running = False
                break
            except Exception as e:
                logger.error(f"游戏循环错误：{e}")
                print(f"\n错误：{e}")
                print("请重试。\n")
                
    async def _get_user_input(self) -> str:
        """异步获取用户输入"""
        loop = asyncio.get_event_loop()
        
        # 在线程池中运行阻塞的input()
        user_input = await loop.run_in_executor(
            None, 
            lambda: input("> ")
        )
        
        return user_input.strip()
        
    async def _generate_narrative_if_needed(self, command: str, response: str):
        """根据需要生成叙事"""
        if not self.game.narrative_generator:
            return
            
        # 检查是否需要生成叙事
        if any(keyword in command for keyword in ['攻击', '使用', '防御']):
            # 可能是战斗
            if '伤害' in response or '生命值' in response:
                # 这里应该从游戏状态获取实际的战斗事件
                # 现在使用模拟数据
                narrative = await self.game.generate_narrative('combat', {
                    'events': [
                        {'type': 'attack', 'attacker': '玩家', 'damage': 50}
                    ]
                })
                if narrative:
                    print(f"\n[战斗描述]\n{narrative}")
                    
        elif '探索' in command:
            # 探索叙事
            discovery = None
            if '发现' in response:
                discovery = {'type': 'item', 'description': '一个神秘的物品'}
                
            narrative = await self.game.generate_narrative('exploration', {
                'action': '探索周围环境',
                'discovery': discovery
            })
            if narrative:
                print(f"\n[探索描述]\n{narrative}")
                
    async def _process_async_events(self):
        """处理异步事件"""
        # 给异步事件系统一些时间处理
        await asyncio.sleep(0.01)
        
        # 检查是否有世界事件需要触发
        if self.game.world_event_generator and self.game.turn_count % 50 == 0:
            # 每50回合可能触发一个世界事件
            import random
            if random.random() < 0.2:  # 20%概率
                event = await self.game.trigger_world_event(
                    "定期检查",
                    random.choice(['minor', 'minor', 'major'])
                )
                if event:
                    print(f"\n[世界事件] {event.get('name', '未知事件')}")
                    print(event.get('description', ''))
                    
    async def shutdown(self):
        """关闭游戏"""
        logger.info("正在关闭游戏...")
        
        if self.game:
            await self.game.shutdown()
            
        logger.info("游戏已安全关闭。")
        

async def main():
    """主函数"""
    runner = EnhancedGameRunner()
    
    try:
        # 初始化
        await runner.initialize()
        
        # 运行游戏
        await runner.run()
        
    except Exception as e:
        logger.error(f"游戏运行错误：{e}")
        
    finally:
        # 清理
        await runner.shutdown()
        
        # 显示性能统计
        if runner.game and runner.game.smart_cache:
            stats = runner.game.smart_cache.get_stats()
            logger.info(f"缓存统计：命中率={stats.get('hit_rate', 0):.2%}")
            
        if runner.game and runner.game.async_events:
            stats = runner.game.async_events.get_stats()
            logger.info(f"事件统计：已处理={stats.get('events_processed', 0)}")
            

def check_requirements():
    """检查运行要求"""
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        sys.exit(1)
        
    # 检查API密钥
    if not os.getenv('DEEPSEEK_API_KEY'):
        print("警告：未设置DEEPSEEK_API_KEY环境变量")
        print("AI功能将以降级模式运行")
        print()
        
    # 检查必要的目录
    required_dirs = ['saves', 'plugins', 'xwe/data']
    for dir_path in required_dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        

if __name__ == '__main__':
    # 检查要求
    check_requirements()
    
    # 运行游戏
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n再见，道友！期待您的下次光临！")
    except Exception as e:
        logger.error(f"程序异常退出：{e}")
        print(f"\n程序错误：{e}")
        print("请检查日志文件获取详细信息。")
