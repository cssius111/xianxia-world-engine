"""
修炼服务
负责修炼系统的逻辑处理
"""

from abc import ABC, abstractmethod
from typing import Any, Dict
import random

from xwe.services import ServiceBase, ServiceContainer


class ICultivationService(ABC):
    """修炼服务接口"""
    
    @abstractmethod
    def cultivate(self) -> Dict[str, Any]:
        """进行修炼"""
        pass
        
    @abstractmethod
    def breakthrough(self) -> Dict[str, Any]:
        """突破境界"""
        pass
        
    @abstractmethod
    def get_cultivation_info(self) -> Dict[str, Any]:
        """获取修炼信息"""
        pass


class CultivationService(ServiceBase[ICultivationService], ICultivationService):
    """修炼服务实现"""
    
    def __init__(self, container: ServiceContainer) -> None:
        super().__init__(container)
        self._cultivation_realms = [
            '炼气期', '筑基期', '金丹期', '元婴期', 
            '化神期', '炼虚期', '合体期', '大乘期', '渡劫期'
        ]
        
    def cultivate(self) -> Dict[str, Any]:
        """进行修炼"""
        # 获取玩家服务
        from xwe.services.interfaces.player_service import IPlayerService
        player_service = self.get_service(IPlayerService)
        
        player = player_service.get_current_player()
        if not player:
            return {
                'success': False,
                'message': '未找到玩家信息'
            }
            
        # 计算修炼收益
        base_exp = random.randint(10, 30)
        
        # 根据灵根加成
        if player.spiritual_root == '天灵根':
            base_exp = int(base_exp * 2)
        elif player.spiritual_root == '异灵根':
            base_exp = int(base_exp * 1.5)
            
        # 添加经验
        exp_result = player_service.add_experience(base_exp)
        
        # 恢复状态
        player_service.restore_mana(20)
        player_service.heal(10)
        
        # 随机事件
        event_chance = random.random()
        special_event = None
        
        if event_chance < 0.1:
            # 顿悟
            bonus_exp = random.randint(20, 50)
            player_service.add_experience(bonus_exp)
            special_event = f"你突然有所顿悟，额外获得{bonus_exp}点经验！"
        elif event_chance < 0.15:
            # 走火入魔
            damage = random.randint(10, 30)
            player_service.damage(damage)
            special_event = f"修炼时心神不稳，走火入魔受到{damage}点伤害！"
            
        message = f"修炼完成，{exp_result['message']}"
        if special_event:
            message += f"\n{special_event}"
            
        return {
            'success': True,
            'message': message,
            'experience_gained': base_exp,
            'special_event': special_event
        }
        
    def breakthrough(self) -> Dict[str, Any]:
        """突破境界"""
        # 获取玩家服务
        from xwe.services.interfaces.player_service import IPlayerService
        player_service = self.get_service(IPlayerService)
        
        player = player_service.get_current_player()
        if not player:
            return {
                'success': False,
                'message': '未找到玩家信息'
            }
            
        current_realm_index = self._cultivation_realms.index(player.realm)
        
        # 检查是否已经最高境界
        if current_realm_index >= len(self._cultivation_realms) - 1:
            return {
                'success': False,
                'message': '你已经达到最高境界！'
            }
            
        # 检查等级要求
        required_level = (current_realm_index + 1) * 10
        if player.level < required_level:
            return {
                'success': False,
                'message': f'突破到下一境界需要达到{required_level}级'
            }
            
        # 计算成功率
        success_rate = 0.5
        if player.spiritual_root == '天灵根':
            success_rate += 0.2
        elif player.spiritual_root == '异灵根':
            success_rate += 0.1
            
        # 尝试突破
        if random.random() < success_rate:
            # 突破成功
            new_realm = self._cultivation_realms[current_realm_index + 1]
            player_service.update_player(player.id, {'realm': new_realm})
            
            # 提升属性
            player_service.update_player(player.id, {
                'max_health': player.max_health + 100,
                'max_mana': player.max_mana + 50,
                'attack': player.attack + 20,
                'defense': player.defense + 15
            })
            
            return {
                'success': True,
                'message': f'恭喜！你成功突破到{new_realm}！',
                'new_realm': new_realm
            }
        else:
            # 突破失败
            damage = random.randint(20, 50)
            player_service.damage(damage)
            
            return {
                'success': False,
                'message': f'突破失败，受到{damage}点反噬伤害'
            }
            
    def get_cultivation_info(self) -> Dict[str, Any]:
        """获取修炼信息"""
        from xwe.services.interfaces.player_service import IPlayerService
        player_service = self.get_service(IPlayerService)
        
        player = player_service.get_current_player()
        if not player:
            return {}
            
        current_realm_index = self._cultivation_realms.index(player.realm)
        next_realm = None
        progress = 0
        
        if current_realm_index < len(self._cultivation_realms) - 1:
            next_realm = self._cultivation_realms[current_realm_index + 1]
            required_level = (current_realm_index + 1) * 10
            progress = min(100, int(player.level / required_level * 100))
            
        return {
            'current_realm': player.realm,
            'next_realm': next_realm,
            'progress': progress,
            'spiritual_root': player.spiritual_root,
            'cultivation_speed': self._get_cultivation_speed(player.spiritual_root)
        }
        
    def _get_cultivation_speed(self, spiritual_root: str) -> str:
        """获取修炼速度描述"""
        speeds = {
            '天灵根': '极快',
            '异灵根': '很快',
            '双灵根': '快',
            '三灵根': '普通',
            '四灵根': '慢',
            '五灵根': '很慢',
            '普通': '普通'
        }
        return speeds.get(spiritual_root, '普通')
