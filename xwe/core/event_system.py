"""
沉浸式分步事件系统
支持分支选择、打字机效果、逐步展示
"""
import time
import random
from typing import Dict, List, Optional, Callable, Any
from enum import Enum

class EventType(Enum):
    """事件类型"""
    STORY = "story"          # 剧情事件
    COMBAT = "combat"        # 战斗事件
    CHOICE = "choice"        # 选择事件
    REWARD = "reward"        # 奖励事件
    SPECIAL = "special"      # 特殊事件
    ROLL = "roll"           # Roll事件

class EventChoice:
    """事件选择项"""
    def __init__(self, text: str, next_event_id: Optional[str] = None, 
                 condition: Optional[Callable] = None, effect: Optional[Callable] = None):
        self.text = text
        self.next_event_id = next_event_id
        self.condition = condition  # 显示条件
        self.effect = effect        # 选择效果

class GameEvent:
    """游戏事件"""
    def __init__(self, event_id: str, event_type: EventType, title: str, 
                 description: str, choices: Optional[List[EventChoice]] = None):
        self.event_id = event_id
        self.event_type = event_type
        self.title = title
        self.description = description
        self.choices = choices or []
        self.is_completed = False

class ImmersiveEventSystem:
    """沉浸式事件系统"""
    
    def __init__(self, output_func: Callable):
        self.output = output_func
        self.events: Dict[str, GameEvent] = {}
        self.current_event: Optional[GameEvent] = None
        self.event_history: List[str] = []
        self.typing_speed = 0.03  # 打字机效果速度
        self._load_events()
    
    def _load_events(self):
        """加载预定义事件"""
        # 开局事件
        self.add_event(GameEvent(
            "start_journey",
            EventType.STORY,
            "踏入修仙之路",
            "你站在青云山脚下，仰望着云雾缭绕的山峰。传说中，这里是修仙者的圣地...",
            [
                EventChoice("直接上山", "climb_mountain"),
                EventChoice("先到山脚村庄打听消息", "visit_village"),
                EventChoice("在山脚调息准备", "prepare_first")
            ]
        ))
        
        # 山脚村庄事件
        self.add_event(GameEvent(
            "visit_village",
            EventType.CHOICE,
            "山脚村庄",
            "村庄里炊烟袅袅，一位老者坐在村口的大树下...",
            [
                EventChoice("向老者请教", "talk_elder"),
                EventChoice("到茶馆打听消息", "visit_teahouse"),
                EventChoice("直接离开上山", "climb_mountain")
            ]
        ))
        
        # 特殊遭遇事件
        self.add_event(GameEvent(
            "mysterious_encounter",
            EventType.SPECIAL,
            "神秘遭遇",
            "一道身影从你面前飘过，留下一阵清香...",
            [
                EventChoice("追上去查看", "follow_figure", 
                           condition=lambda p: p.speed > 50),
                EventChoice("原地观察", "observe_spot"),
                EventChoice("不予理会", "ignore_it")
            ]
        ))
        
        # Roll事件示例
        self.add_event(GameEvent(
            "talent_awakening",
            EventType.ROLL,
            "天赋觉醒",
            "一股神秘的力量在你体内涌动，你感觉到某种天赋正在觉醒...",
            [
                EventChoice("专注感受这股力量", "roll_talent"),
                EventChoice("压制这股力量", "suppress_power"),
                EventChoice("顺其自然", "natural_flow")
            ]
        ))
    
    def add_event(self, event: GameEvent):
        """添加事件"""
        self.events[event.event_id] = event
    
    def start_event(self, event_id: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """开始事件"""
        if event_id not in self.events:
            return False
        
        event = self.events[event_id]
        if event.is_completed and event.event_type != EventType.COMBAT:
            # 非战斗事件只能触发一次
            return False
        
        self.current_event = event
        self.event_history.append(event_id)
        
        # 显示事件
        self._display_event(event, context)
        return True
    
    def _display_event(self, event: GameEvent, context: Optional[Dict[str, Any]] = None):
        """显示事件内容"""
        # 清屏效果
        self.output("\n" * 2)
        
        # 显示事件标题
        self._type_text(f"【{event.title}】", delay=0.05)
        self.output("")
        
        # 打字机效果显示描述
        self._type_text(event.description)
        self.output("")
        
        # 显示选择项
        if event.choices:
            self._display_choices(event, context)
    
    def _display_choices(self, event: GameEvent, context: Optional[Dict[str, Any]] = None):
        """显示选择项"""
        time.sleep(0.5)  # 短暂停顿增强节奏感
        
        self.output("你的选择：")
        valid_choices = []
        
        for i, choice in enumerate(event.choices):
            # 检查显示条件
            if choice.condition is None or (context and choice.condition(context)):
                valid_choices.append((i, choice))
                self.output(f"  {len(valid_choices)}. {choice.text}")
        
        if not valid_choices:
            self.output("  [没有可用选择，按回车继续]")
        
        return valid_choices
    
    def handle_choice(self, choice_index: int, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """处理玩家选择"""
        if not self.current_event:
            return None
        
        if 0 <= choice_index < len(self.current_event.choices):
            choice = self.current_event.choices[choice_index]
            
            # 执行选择效果
            if choice.effect and context:
                self._type_text("\n效果：", delay=0.05)
                result = choice.effect(context)
                if result:
                    self._type_text(str(result))
            
            # 标记事件完成
            self.current_event.is_completed = True
            
            # 返回下一个事件ID
            return choice.next_event_id
        
        return None
    
    def _type_text(self, text: str, delay: Optional[float] = None):
        """打字机效果输出文本"""
        delay = delay or self.typing_speed
        
        for char in text:
            print(char, end='', flush=True)
            time.sleep(delay)
        print()  # 换行
    
    def process_event_chain(self, start_event_id: str, context: Optional[Dict[str, Any]] = None):
        """处理事件链"""
        current_id = start_event_id
        
        while current_id:
            if not self.start_event(current_id, context):
                break
            
            # 等待玩家输入
            if self.current_event and self.current_event.choices:
                valid_choices = self._display_choices(self.current_event, context)
                
                if valid_choices:
                    while True:
                        try:
                            choice_str = input("\n请选择 (输入数字): ").strip()
                            choice_num = int(choice_str) - 1
                            
                            if 0 <= choice_num < len(valid_choices):
                                actual_index = valid_choices[choice_num][0]
                                current_id = self.handle_choice(actual_index, context)
                                break
                            else:
                                self.output("无效选择，请重新输入")
                        except ValueError:
                            self.output("请输入有效数字")
                else:
                    input("\n按回车继续...")
                    current_id = None
            else:
                current_id = None
            
            # 事件间隔
            time.sleep(0.5)
    
    def trigger_random_event(self, event_type: Optional[EventType] = None, 
                           context: Optional[Dict[str, Any]] = None) -> bool:
        """触发随机事件"""
        # 筛选可用事件
        available_events = [
            event for event in self.events.values()
            if not event.is_completed and 
               (event_type is None or event.event_type == event_type)
        ]
        
        if available_events:
            event = random.choice(available_events)
            return self.start_event(event.event_id, context)
        
        return False
    
    def create_dynamic_event(self, title: str, description: str, 
                           choices: List[tuple]) -> GameEvent:
        """创建动态事件"""
        event_id = f"dynamic_{int(time.time() * 1000)}"
        event_choices = [
            EventChoice(text, next_id) for text, next_id in choices
        ]
        
        event = GameEvent(
            event_id,
            EventType.SPECIAL,
            title,
            description,
            event_choices
        )
        
        self.add_event(event)
        return event

# 特殊事件处理器
class SpecialEventHandler:
    """处理特殊事件逻辑"""
    
    @staticmethod
    def handle_roll_event(event_system: ImmersiveEventSystem, player_data: Dict[str, Any]):
        """处理Roll事件"""
        event_system._type_text("\n开始觉醒天赋...", delay=0.1)
        time.sleep(1)
        
        # 模拟Roll过程
        talents = ["剑心通明", "丹田异变", "神识过人", "五行亲和", "气运加身"]
        
        for _ in range(5):  # 滚动效果
            talent = random.choice(talents)
            print(f"\r正在觉醒: {talent}", end='', flush=True)
            time.sleep(0.2)
        
        final_talent = random.choice(talents)
        event_system.output(f"\n\n恭喜！你觉醒了天赋【{final_talent}】！")
        
        # 更新玩家数据
        if 'talents' not in player_data:
            player_data['talents'] = []
        player_data['talents'].append(final_talent)
        
        return f"获得天赋：{final_talent}"
    
    @staticmethod
    def handle_cultivation_event(event_system: ImmersiveEventSystem, 
                               player_data: Dict[str, Any], duration: int):
        """处理修炼事件"""
        event_system._type_text(f"\n你开始闭关修炼，计划修炼{duration}天...", delay=0.05)
        
        # 分段显示修炼过程
        segments = min(5, duration // 10 + 1)
        for i in range(segments):
            time.sleep(0.5)
            days = duration * (i + 1) // segments
            
            # 随机修炼事件
            events = [
                f"第{days}天：你感觉丹田微热，真气运转加快。",
                f"第{days}天：一缕明悟涌上心头，你对功法的理解更深了。",
                f"第{days}天：突然心魔来袭，你咬牙坚持，终于度过难关。",
                f"第{days}天：真气如潮水般涌动，你感觉快要突破了！"
            ]
            
            event_system._type_text(random.choice(events), delay=0.02)
        
        # 计算收获
        exp_gained = duration * random.randint(10, 30)
        event_system.output(f"\n修炼结束！获得经验值：{exp_gained}")
        
        return exp_gained
