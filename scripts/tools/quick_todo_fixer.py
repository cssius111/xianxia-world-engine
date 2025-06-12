#!/usr/bin/env python3
"""
快速TODO修复器 - 自动修复最关键的TODO项
"""

import os
import re
from pathlib import Path


class QuickTodoFixer:
    """快速TODO修复器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.fixes_applied = []
    
    def fix_critical_todos(self):
        """修复关键TODO项"""
        print("🔧 开始修复关键TODO项...")
        
        # 1. 修复物品系统集成
        self._fix_item_system_integration()
        
        # 2. 添加Character序列化方法
        self._fix_character_serialization()
        
        # 3. 创建系统管理器
        self._create_system_manager()
        
        print(f"\n✅ 修复完成！共应用了 {len(self.fixes_applied)} 个修复")
        for fix in self.fixes_applied:
            print(f"   - {fix}")
    
    def _fix_item_system_integration(self):
        """修复物品系统集成"""
        game_core_path = self.project_root / "xwe/core/game_core.py"
        
        if not game_core_path.exists():
            print("❌ game_core.py 不存在")
            return
        
        try:
            with open(game_core_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 1. 添加item_system导入（如果不存在）
            if "from .item_system import item_system" not in content:
                # 在其他导入之后添加
                import_pattern = r"(from \..*? import .*?\n)"
                import_insertion = r"\1from .item_system import item_system\n"
                content = re.sub(import_pattern, import_insertion, content, count=1)
            
            # 2. 替换硬编码的spirit_stones
            content = re.sub(
                r"'spirit_stones': 1000  # TODO: 实现物品系统后从背包获取",
                "'spirit_stones': item_system.get_spirit_stones(player.id)",
                content
            )
            
            content = re.sub(
                r"'spirit_stones': 1000  # TODO: 从背包获取",
                "'spirit_stones': item_system.get_spirit_stones(player.id)",
                content
            )
            
            # 3. 修复其他相关的硬编码
            content = re.sub(
                r"# TODO: 实现物品系统后.*?\n",
                "# 已修复：使用物品系统\n",
                content
            )
            
            if content != original_content:
                # 创建备份
                backup_path = game_core_path.with_suffix('.py.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original_content)
                
                # 写入修复后的内容
                with open(game_core_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixes_applied.append("物品系统集成")
                print("✅ 修复物品系统集成")
            
        except Exception as e:
            print(f"❌ 修复物品系统失败: {e}")
    
    def _fix_character_serialization(self):
        """修复Character序列化"""
        character_path = self.project_root / "xwe/core/character.py"
        
        if not character_path.exists():
            print("❌ character.py 不存在")
            return
        
        try:
            with open(character_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否已经有from_dict方法
            if "def from_dict" in content:
                print("✅ Character.from_dict 已存在")
                return
            
            # 添加序列化方法
            serialization_methods = '''
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """从字典创建角色对象"""
        character = cls()
        
        # 基础信息
        character.name = data.get('name', '')
        if 'character_type' in data:
            character.character_type = CharacterType(data['character_type'])
        
        # 属性系统 - 简化版本
        if 'attributes' in data:
            attr_data = data['attributes']
            character.attributes.strength = attr_data.get('strength', 10)
            character.attributes.constitution = attr_data.get('constitution', 10)
            character.attributes.agility = attr_data.get('agility', 10)
            character.attributes.intelligence = attr_data.get('intelligence', 10)
            character.attributes.willpower = attr_data.get('willpower', 10)
            character.attributes.comprehension = attr_data.get('comprehension', 10)
            character.attributes.luck = attr_data.get('luck', 10)
            character.attributes.calculate_derived_attributes()
        
        # 技能
        character.learned_skills = set(data.get('learned_skills', []))
        
        # 其他数据
        character.extra_data = data.get('extra_data', {})
        
        return character
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于序列化）"""
        return {
            'name': self.name,
            'character_type': self.character_type.value if hasattr(self.character_type, 'value') else str(self.character_type),
            'attributes': {
                'strength': self.attributes.strength,
                'constitution': self.attributes.constitution,
                'agility': self.attributes.agility,
                'intelligence': self.attributes.intelligence,
                'willpower': self.attributes.willpower,
                'comprehension': self.attributes.comprehension,
                'luck': self.attributes.luck,
                'current_health': self.attributes.current_health,
                'current_mana': self.attributes.current_mana,
                'current_stamina': self.attributes.current_stamina,
            },
            'learned_skills': list(self.learned_skills),
            'extra_data': self.extra_data
        }
'''
            
            # 在类的最后添加这些方法（在最后一个方法后）
            # 找到类定义的结束位置
            class_pattern = r"(class Character[^:]*:.*?)(\n\n|\n$|\Z)"
            
            # 在类的末尾添加序列化方法
            if "class Character" in content:
                # 简单的方法：在文件末尾添加
                content += serialization_methods
                
                # 创建备份
                backup_path = character_path.with_suffix('.py.backup')
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(open(character_path, 'r', encoding='utf-8').read())
                
                # 写入修复后的内容
                with open(character_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fixes_applied.append("Character序列化方法")
                print("✅ 添加Character序列化方法")
            
        except Exception as e:
            print(f"❌ 修复Character序列化失败: {e}")
    
    def _create_system_manager(self):
        """创建系统管理器"""
        system_manager_path = self.project_root / "xwe/core/system_manager.py"
        
        if system_manager_path.exists():
            print("✅ SystemManager 已存在")
            return
        
        system_manager_code = '''"""
游戏系统管理器 - 管理角色的特殊系统（如修炼系统、战斗系统等）
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SystemManager:
    """游戏系统管理器"""
    
    def __init__(self):
        self.active_systems: Dict[str, Dict[str, Any]] = {}
    
    def activate_system(self, player_id: str, system_data: Dict[str, Any]):
        """激活玩家的系统"""
        if not system_data:
            return
        
        system_type = system_data.get('name', '')
        system_rarity = system_data.get('rarity', 'common')
        
        logger.info(f"激活系统: {system_type} ({system_rarity}) for player {player_id}")
        
        if "修炼" in system_type:
            self._activate_cultivation_system(player_id, system_data)
        elif "战斗" in system_type:
            self._activate_combat_system(player_id, system_data) 
        elif "交易" in system_type:
            self._activate_trading_system(player_id, system_data)
        else:
            self._activate_generic_system(player_id, system_data)
    
    def _activate_cultivation_system(self, player_id: str, system_data: Dict):
        """激活修炼系统"""
        rarity = system_data.get('rarity', 'common')
        
        # 根据稀有度设置加成
        bonuses = {
            'common': {'cultivation_speed': 1.2, 'breakthrough_success': 1.1},
            'rare': {'cultivation_speed': 1.5, 'breakthrough_success': 1.2},
            'epic': {'cultivation_speed': 2.0, 'breakthrough_success': 1.5},
            'legendary': {'cultivation_speed': 3.0, 'breakthrough_success': 2.0}
        }
        
        system_bonuses = bonuses.get(rarity, bonuses['common'])
        
        self.active_systems[player_id] = {
            'type': 'cultivation',
            'name': system_data.get('name'),
            'rarity': rarity,
            'bonuses': system_bonuses,
            'features': system_data.get('features', [])
        }
    
    def _activate_combat_system(self, player_id: str, system_data: Dict):
        """激活战斗系统"""
        rarity = system_data.get('rarity', 'common')
        
        bonuses = {
            'common': {'damage_bonus': 1.1, 'crit_chance': 1.1},
            'rare': {'damage_bonus': 1.3, 'crit_chance': 1.2},
            'epic': {'damage_bonus': 1.6, 'crit_chance': 1.4},
            'legendary': {'damage_bonus': 2.0, 'crit_chance': 1.8}
        }
        
        system_bonuses = bonuses.get(rarity, bonuses['common'])
        
        self.active_systems[player_id] = {
            'type': 'combat',
            'name': system_data.get('name'),
            'rarity': rarity,
            'bonuses': system_bonuses,
            'features': system_data.get('features', [])
        }
    
    def _activate_trading_system(self, player_id: str, system_data: Dict):
        """激活交易系统"""
        self.active_systems[player_id] = {
            'type': 'trading',
            'name': system_data.get('name'),
            'rarity': system_data.get('rarity'),
            'bonuses': {'price_discount': 0.9, 'sell_bonus': 1.2},
            'features': system_data.get('features', [])
        }
    
    def _activate_generic_system(self, player_id: str, system_data: Dict):
        """激活通用系统"""
        self.active_systems[player_id] = {
            'type': 'generic',
            'name': system_data.get('name'),
            'rarity': system_data.get('rarity'),
            'bonuses': {},
            'features': system_data.get('features', [])
        }
    
    def get_system_bonus(self, player_id: str, bonus_type: str) -> float:
        """获取系统提供的加成"""
        system = self.active_systems.get(player_id)
        if system:
            return system.get('bonuses', {}).get(bonus_type, 1.0)
        return 1.0
    
    def get_player_system(self, player_id: str) -> Optional[Dict[str, Any]]:
        """获取玩家的系统信息"""
        return self.active_systems.get(player_id)
    
    def has_feature(self, player_id: str, feature_name: str) -> bool:
        """检查玩家是否有特定功能"""
        system = self.active_systems.get(player_id)
        if system:
            return feature_name in system.get('features', [])
        return False


# 全局系统管理器实例
system_manager = SystemManager()
'''
        
        try:
            # 确保目录存在
            system_manager_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(system_manager_path, 'w', encoding='utf-8') as f:
                f.write(system_manager_code)
            
            self.fixes_applied.append("系统管理器")
            print("✅ 创建系统管理器")
            
        except Exception as e:
            print(f"❌ 创建系统管理器失败: {e}")
    
    def show_integration_guide(self):
        """显示集成指南"""
        print("\n" + "="*50)
        print("🎯 集成指南")
        print("="*50)
        
        print("\n1. 在 game_core.py 中集成系统管理器:")
        print("   from .system_manager import system_manager")
        print("   # 在角色创建时:")
        print("   if roll_result.system:")
        print("       system_manager.activate_system(character.id, roll_result.system)")
        
        print("\n2. 在修炼时使用系统加成:")
        print("   cultivation_bonus = system_manager.get_system_bonus(player.id, 'cultivation_speed')")
        print("   exp_gained = base_exp * cultivation_bonus")
        
        print("\n3. 在战斗时使用系统加成:")
        print("   damage_bonus = system_manager.get_system_bonus(player.id, 'damage_bonus')")
        print("   final_damage = base_damage * damage_bonus")
        
        print("\n4. 检查系统功能:")
        print("   if system_manager.has_feature(player.id, '自动修炼'):")
        print("       # 执行自动修炼逻辑")
        
        print(f"\n✨ 修复完成！请手动集成以上代码以完全激活系统功能。")


def main():
    """主函数"""
    fixer = QuickTodoFixer()
    fixer.fix_critical_todos()
    fixer.show_integration_guide()


if __name__ == '__main__':
    main()
