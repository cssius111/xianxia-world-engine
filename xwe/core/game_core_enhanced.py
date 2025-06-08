# xwe/core/game_core_enhanced.py

"""
增强版游戏核心 - 集成AI和性能优化功能
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from .game_core import GameCore
from .nlp.advanced import AdvancedPromptEngine, ResponseType, GameContext
from .optimizations import ExpressionJITCompiler, SmartCache, AsyncEventSystem
from .plugin_system import PluginManager
from ..features.ai_dialogue import AIDialogueManager
from ..features.narrative_generator import DynamicNarrativeGenerator
from ..features.ai_world_events import AIWorldEventGenerator

logger = logging.getLogger(__name__)


class EnhancedGameCore(GameCore):
    """增强版游戏核心"""
    
    def __init__(self):
        super().__init__()
        
        # 加载AI功能配置
        self.ai_config = self._load_ai_config()
        
        # 初始化增强组件
        self.prompt_engine = None
        self.dialogue_manager = None
        self.narrative_generator = None
        self.world_event_generator = None
        
        # 性能优化组件
        self.jit_compiler = None
        self.smart_cache = None
        self.async_events = None
        
        # 插件系统
        self.plugin_manager = None
        
        # 异步循环
        self.loop = None
        
    def _load_ai_config(self) -> Dict[str, Any]:
        """加载AI配置"""
        config_path = Path('xwe/data/ai_features_config.json')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
        
    async def async_init(self):
        """异步初始化"""
        logger.info("Initializing enhanced game core...")
        
        # 初始化基础组件
        self.init()
        
        # 初始化AI组件
        if self.ai_config.get('ai_features', {}).get('enabled'):
            await self._init_ai_components()
            
        # 初始化性能优化
        if self.ai_config.get('performance_optimizations'):
            await self._init_optimizations()
            
        # 初始化插件系统
        if self.ai_config.get('plugin_system', {}).get('enabled'):
            await self._init_plugin_system()
            
        logger.info("Enhanced game core initialized successfully")
        
    async def _init_ai_components(self):
        """初始化AI组件"""
        ai_config = self.ai_config.get('ai_features', {})
        
        # 初始化提示引擎
        self.prompt_engine = AdvancedPromptEngine()
        
        # 初始化对话管理器
        if ai_config.get('dialogue_system', {}).get('enabled'):
            from .nlp.llm_client import LLMClient
            llm_client = LLMClient()
            self.dialogue_manager = AIDialogueManager(llm_client, self.prompt_engine)
            logger.info("AI dialogue manager initialized")
            
        # 初始化叙事生成器
        if ai_config.get('narrative_generation', {}).get('enabled'):
            from .nlp.llm_client import LLMClient
            llm_client = LLMClient()
            self.narrative_generator = DynamicNarrativeGenerator(llm_client)
            logger.info("Dynamic narrative generator initialized")
            
        # 初始化世界事件生成器
        if ai_config.get('world_events', {}).get('enabled'):
            from .nlp.llm_client import LLMClient
            llm_client = LLMClient()
            world_state = self.get_world_state()
            self.world_event_generator = AIWorldEventGenerator(llm_client, world_state)
            logger.info("AI world event generator initialized")
            
    async def _init_optimizations(self):
        """初始化性能优化"""
        opt_config = self.ai_config.get('performance_optimizations', {})
        
        # 初始化JIT编译器
        if opt_config.get('expression_jit', {}).get('enabled'):
            self.jit_compiler = ExpressionJITCompiler()
            logger.info("Expression JIT compiler initialized")
            
        # 初始化智能缓存
        if opt_config.get('smart_cache', {}).get('enabled'):
            max_memory = opt_config.get('smart_cache', {}).get('max_memory_mb', 100)
            self.smart_cache = SmartCache(max_memory_mb=max_memory)
            logger.info(f"Smart cache initialized with {max_memory}MB")
            
        # 初始化异步事件系统
        if opt_config.get('async_events', {}).get('enabled'):
            worker_count = opt_config.get('async_events', {}).get('worker_count', 4)
            self.async_events = AsyncEventSystem(worker_count=worker_count)
            await self.async_events.start()
            
            # 迁移现有事件处理器
            self._migrate_to_async_events()
            logger.info(f"Async event system initialized with {worker_count} workers")
            
    async def _init_plugin_system(self):
        """初始化插件系统"""
        self.plugin_manager = PluginManager(self)
        
        plugin_config = self.ai_config.get('plugin_system', {})
        
        # 自动发现插件
        if plugin_config.get('auto_discover'):
            await self.plugin_manager.enable_all_plugins()
            
        logger.info(f"Plugin system initialized with {len(self.plugin_manager.plugins)} plugins")
        
    def _migrate_to_async_events(self):
        """将现有事件迁移到异步系统"""
        if hasattr(self, 'event_manager') and self.async_events:
            # 这里需要根据实际的事件系统实现迁移逻辑
            pass
            
    def get_world_state(self) -> Dict[str, Any]:
        """获取世界状态"""
        return {
            'player': self.player.__dict__ if hasattr(self, 'player') else {},
            'faction_relations': getattr(self, 'faction_relations', {}),
            'phenomena': getattr(self, 'world_phenomena', []),
            'resources': getattr(self, 'resource_distribution', {}),
            'time': getattr(self, 'game_time', 0)
        }
        
    async def process_enhanced_command(self, user_input: str) -> str:
        """处理增强命令（支持AI功能）"""
        
        # 构建游戏上下文
        context = self._build_game_context()
        
        # 使用增强的NLP处理
        if self.prompt_engine and hasattr(self.nlp_processor, 'llm_client'):
            # 解析命令
            parsed_command = self.nlp_processor.parse(user_input, context)
            
            # 如果是对话命令且启用了AI对话
            if (parsed_command.command_type.value == 'talk' and 
                self.dialogue_manager and 
                parsed_command.target):
                
                # 生成AI对话
                dialogue_result = await self.dialogue_manager.generate_npc_dialogue(
                    parsed_command.target,
                    user_input,
                    context
                )
                
                return self._format_dialogue_result(dialogue_result)
                
        # 否则使用原始处理方式
        return self.process_command(user_input)
        
    def _build_game_context(self) -> dict:
        """构建游戏上下文"""
        context = {
            'player': {
                'name': self.player.name,
                'realm': self.player.cultivation_realm,
                'health': self.player.health,
                'max_health': self.player.max_health,
                'level': self.player.level
            },
            'location': {
                'id': self.current_location,
                'name': self.get_location_name(self.current_location),
                'description': self.get_location_description(self.current_location)
            },
            'recent_events': self.get_recent_events(),
            'active_npcs': self.get_active_npcs(),
            'world': self.get_world_state()
        }
        
        return context
        
    async def generate_narrative(self, event_type: str, event_data: Dict) -> str:
        """生成叙事文本"""
        if not self.narrative_generator:
            return ""
            
        context = self._build_game_context()
        
        if event_type == 'combat':
            return await self.narrative_generator.generate_combat_narrative(
                event_data.get('events', []),
                context
            )
        elif event_type == 'exploration':
            return await self.narrative_generator.generate_exploration_narrative(
                event_data.get('action', ''),
                event_data.get('discovery'),
                context
            )
        elif event_type == 'cultivation':
            return await self.narrative_generator.generate_cultivation_narrative(
                event_data.get('duration', ''),
                event_data.get('results', {}),
                context
            )
            
        return ""
        
    async def trigger_world_event(self, trigger: str, severity: str = "minor") -> Dict:
        """触发世界事件"""
        if not self.world_event_generator:
            return {}
            
        return await self.world_event_generator.generate_world_event(trigger, severity)
        
    def compile_expression(self, expr_id: str, expression: Dict) -> Any:
        """编译表达式（JIT优化）"""
        if self.jit_compiler:
            compiled_func = self.jit_compiler.compile_expression(expr_id, expression)
            return lambda ctx: compiled_func(ctx)
        else:
            # 降级到解释执行
            return lambda ctx: self._evaluate_expression(expression, ctx)
            
    def cached_compute(self, key: str, compute_func, *args, **kwargs) -> Any:
        """缓存计算结果"""
        if self.smart_cache:
            return self.smart_cache.get_or_compute(key, compute_func, *args, **kwargs)
        else:
            # 直接计算
            return compute_func(*args, **kwargs)
            
    async def emit_async_event(self, event_type: str, data: Dict, priority: int = 0):
        """发送异步事件"""
        if self.async_events and self.async_events.running:
            await self.async_events.emit(event_type, data, priority)
        else:
            # 降级到同步处理
            self._emit_sync_event(event_type, data)
            
    def _emit_sync_event(self, event_type: str, data: Dict):
        """同步事件发送（降级方案）"""
        if hasattr(self, 'event_manager'):
            self.event_manager.emit(event_type, data)
            
    def _format_dialogue_result(self, dialogue_result: Dict) -> str:
        """格式化对话结果"""
        lines = []
        
        # NPC说话内容
        if dialogue_result.get('text'):
            emotion = dialogue_result.get('emotion', 'neutral')
            emotion_text = {
                'happy': '愉快地',
                'angry': '愤怒地',
                'sad': '悲伤地',
                'neutral': '',
                'mysterious': '神秘地'
            }.get(emotion, '')
            
            if emotion_text:
                lines.append(f"[NPC{emotion_text}说]：{dialogue_result['text']}")
            else:
                lines.append(f"[NPC]：{dialogue_result['text']}")
                
        # 选项
        if dialogue_result.get('choices'):
            lines.append("\n你可以选择：")
            for choice in dialogue_result['choices']:
                lines.append(f"{choice['id']}. {choice['text']}")
                
        # 效果
        if dialogue_result.get('effects'):
            lines.append("\n[效果]")
            for effect in dialogue_result['effects']:
                if effect['type'] == 'relationship':
                    lines.append(f"好感度{effect['value']:+d}")
                else:
                    lines.append(effect.get('description', ''))
                    
        return "\n".join(lines)
        
    def get_recent_events(self, limit: int = 10) -> list:
        """获取最近的事件"""
        # 这里需要根据实际实现获取事件历史
        return []
        
    def get_active_npcs(self) -> list:
        """获取当前激活的NPC"""
        # 这里需要根据实际实现获取NPC列表
        return []
        
    def get_location_name(self, location_id: str) -> str:
        """获取位置名称"""
        # 这里需要根据实际实现获取位置名称
        return location_id
        
    def get_location_description(self, location_id: str) -> str:
        """获取位置描述"""
        # 这里需要根据实际实现获取位置描述
        return ""
        
    def _evaluate_expression(self, expression: Any, context: Dict) -> Any:
        """简单的表达式求值（降级方案）"""
        # 这里实现一个简单的表达式求值器
        if isinstance(expression, dict):
            if 'constant' in expression:
                return expression['constant']
            elif 'attribute' in expression:
                path = expression['attribute'].split('.')
                value = context
                for part in path:
                    if isinstance(value, dict):
                        value = value.get(part, 0)
                    else:
                        return 0
                return value
        return expression
        
    async def shutdown(self):
        """关闭增强功能"""
        logger.info("Shutting down enhanced game core...")
        
        # 关闭异步事件系统
        if self.async_events:
            await self.async_events.stop()
            
        # 关闭插件
        if self.plugin_manager:
            for plugin_name in list(self.plugin_manager.plugins.keys()):
                try:
                    await self.plugin_manager.unload_plugin(plugin_name)
                except Exception as e:
                    logger.error(f"Error unloading plugin {plugin_name}: {e}")
                    
        # 保存缓存统计
        if self.smart_cache:
            stats = self.smart_cache.get_stats()
            logger.info(f"Cache stats: {stats}")
            
        logger.info("Enhanced game core shutdown complete")


# 向后兼容的别名，旧代码可能仍使用 GameCoreEnhanced
class GameCoreEnhanced(EnhancedGameCore):
    pass


def create_enhanced_game():
    """创建增强版游戏实例"""
    game = EnhancedGameCore()
    
    # 运行异步初始化
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(game.async_init())
        game.loop = loop
        return game
    except Exception as e:
        logger.error(f"Failed to initialize enhanced game: {e}")
        loop.close()
        raise
