"""
玩家体验增强模块
提供友好的错误处理、智能命令处理、游戏提示等功能
"""

import difflib
import random
from datetime import datetime, timedelta
from typing import List, Optional, Set, Tuple


class FriendlyErrorHandler:
    """友好的错误处理器"""
    
    def __init__(self):
        self.error_messages = {
            "command_not_found": [
                "看起来你输入了一个未知的命令 '{cmd}'。",
                "'{cmd}' 不是一个有效的命令。",
                "我不太明白 '{cmd}' 是什么意思。"
            ],
            "insufficient_resources": [
                "你的{resource}不足，需要{required}，但你只有{current}。",
                "资源不足：缺少{lacking}个{resource}。",
                "{resource}不够用了，再去收集一些吧。"
            ],
            "invalid_target": [
                "找不到目标 '{target}'。",
                "'{target}' 似乎不在这里。",
                "没有发现叫 '{target}' 的东西。"
            ],
            "action_failed": [
                "这个操作失败了，可能是条件不满足。",
                "无法完成这个动作，请检查相关条件。",
                "操作未能成功，请稍后再试。"
            ]
        }
        
        self.suggestions = {
            "command_not_found": "你可以输入 'help' 查看所有可用命令。",
            "insufficient_resources": "试试使用 'inventory' 查看你的物品。",
            "invalid_target": "使用 'look' 查看周围的环境。",
            "action_failed": "查看 'status' 了解你的当前状态。"
        }
    
    def handle_error(self, error_type: str, **kwargs) -> str:
        """处理错误并返回友好的错误信息"""
        if error_type not in self.error_messages:
            return "发生了一个未知错误。"
        
        # 选择一个错误消息模板
        template = random.choice(self.error_messages[error_type])
        message = template.format(**kwargs)
        
        # 添加建议
        if error_type in self.suggestions:
            message += f"\n提示：{self.suggestions[error_type]}"
        
        return message
    
    def add_custom_error(self, error_type: str, messages: List[str], suggestion: str = ""):
        """添加自定义错误类型"""
        self.error_messages[error_type] = messages
        if suggestion:
            self.suggestions[error_type] = suggestion


class SmartCommandProcessor:
    """智能命令处理器"""
    
    def __init__(self):
        self.command_aliases = {
            # 移动相关
            "go": ["move", "walk", "走", "去", "前往"],
            "north": ["n", "北", "向北"],
            "south": ["s", "南", "向南"],
            "east": ["e", "东", "向东"],
            "west": ["w", "西", "向西"],
            # 物品相关
            "inventory": ["inv", "i", "物品", "背包", "包裹"],
            "get": ["take", "pick", "拿", "捡", "获取"],
            "drop": ["discard", "丢", "扔", "丢弃"],
            "use": ["用", "使用"],
            # 战斗相关
            "attack": ["fight", "hit", "攻击", "打", "战斗"],
            "defend": ["block", "防御", "格挡"],
            # 交互相关
            "talk": ["speak", "chat", "说话", "对话", "交谈"],
            "look": ["l", "examine", "查看", "观察", "看"],
            "help": ["?", "h", "帮助", "指令"]
        }
        
        self.command_history: List[str] = []
        self.common_typos = {
            "attakc": "attack",
            "moev": "move",
            "talkk": "talk",
            "statis": "status",
            "inventry": "inventory"
        }
    
    def process_command(self, raw_input: str) -> Tuple[str, List[str]]:
        """处理命令输入"""
        # 清理输入
        cleaned = raw_input.strip().lower()
        
        # 记录历史
        self.command_history.append(cleaned)
        if len(self.command_history) > 100:
            self.command_history.pop(0)
        
        # 分割命令和参数
        parts = cleaned.split()
        if not parts:
            return "", []
        
        command = parts[0]
        args = parts[1:]
        
        # 检查常见拼写错误
        if command in self.common_typos:
            command = self.common_typos[command]
        
        # 检查别名
        for base_cmd, aliases in self.command_aliases.items():
            if command in aliases:
                command = base_cmd
                break
        
        return command, args
    
    def suggest_command(self, invalid_command: str) -> Optional[str]:
        """建议相似的命令"""
        all_commands = list(self.command_aliases.keys())
        
        # 使用difflib找到最相似的命令
        matches = difflib.get_close_matches(invalid_command, all_commands, n=1, cutoff=0.6)
        
        if matches:
            return matches[0]
        
        # 检查是否是某个命令的别名
        for base_cmd, aliases in self.command_aliases.items():
            if invalid_command in [alias.lower() for alias in aliases]:
                return base_cmd
        
        return None
    
    def get_recent_commands(self, count: int = 5) -> List[str]:
        """获取最近使用的命令"""
        return self.command_history[-count:]


class GameTipsDisplay:
    """游戏提示显示器"""
    
    def __init__(self):
        self.tips = {
            "beginner": [
                "使用 'help' 命令可以查看所有可用指令。",
                "记得经常保存游戏进度，使用 'save' 命令。",
                "使用 'look' 可以观察周围环境。",
                "与NPC对话可能会获得有用的信息或任务。",
                "修炼是变强的关键，找一个安静的地方使用 'cultivate'。"
            ],
            "combat": [
                "战斗中要注意自己的血量和灵力。",
                "不同的技能有不同的效果，合理搭配使用。",
                "有时候撤退是更明智的选择。",
                "装备合适的武器和防具能大幅提升战斗力。"
            ],
            "exploration": [
                "地图上可能隐藏着秘密区域，仔细探索。",
                "某些地点只在特定时间开放。",
                "留意环境描述中的线索。",
                "与其他玩家交流可能会发现新的地点。"
            ],
            "cultivation": [
                "选择合适的功法对修炼速度影响很大。",
                "灵石可以加快修炼速度。",
                "突破境界需要满足特定条件。",
                "心魔是修炼路上的一大障碍。"
            ],
            "social": [
                "加入门派可以获得更多资源和指导。",
                "与其他玩家组队能更容易完成困难任务。",
                "声望会影响NPC对你的态度。",
                "某些任务需要特定的声望等级才能接取。"
            ]
        }
        
        self.displayed_tips: Set[str] = set()
        self.last_tip_time = None
        self.tip_interval = timedelta(minutes=10)
    
    def get_contextual_tip(self, context: str = "beginner") -> Optional[str]:
        """根据上下文获取提示"""
        if context not in self.tips:
            context = "beginner"
        
        available_tips = [
            tip for tip in self.tips[context] 
            if tip not in self.displayed_tips
        ]
        
        if not available_tips:
            # 如果该类别的提示都显示过了，重置
            for tip in self.tips[context]:
                self.displayed_tips.discard(tip)
            available_tips = self.tips[context]
        
        tip = random.choice(available_tips)
        self.displayed_tips.add(tip)
        self.last_tip_time = datetime.now()
        
        return f"💡 提示：{tip}"
    
    def should_show_tip(self) -> bool:
        """判断是否应该显示提示"""
        if self.last_tip_time is None:
            return True
        
        return datetime.now() - self.last_tip_time > self.tip_interval
    
    def add_custom_tips(self, category: str, tips: List[str]):
        """添加自定义提示"""
        if category not in self.tips:
            self.tips[category] = []
        self.tips[category].extend(tips)


class InputHelper:
    """输入辅助器"""
    
    def __init__(self):
        self.auto_complete_dict = {
            "attack": ["attack <target>", "attack with <skill>"],
            "go": ["go north", "go south", "go east", "go west"],
            "talk": ["talk to <npc>", "talk about <topic>"],
            "use": ["use <item>", "use <skill> on <target>"],
            "cultivate": ["cultivate", "cultivate with <method>"]
        }
        
        self.input_shortcuts = {
            "!!": "repeat_last_command",
            "!n": "go north",
            "!s": "go south",
            "!e": "go east",
            "!w": "go west",
            "!i": "inventory",
            "!l": "look"
        }
    
    def expand_shortcut(self, input_text: str) -> str:
        """展开快捷输入"""
        if input_text in self.input_shortcuts:
            return self.input_shortcuts[input_text]
        return input_text
    
    def get_completions(self, partial_input: str) -> List[str]:
        """获取自动补全建议"""
        completions = []
        
        for command, templates in self.auto_complete_dict.items():
            if command.startswith(partial_input.lower()):
                completions.extend(templates)
        
        return completions[:5]  # 最多返回5个建议
    
    def format_input_prompt(self, context: str = "normal") -> str:
        """格式化输入提示符"""
        prompts = {
            "normal": "》",
            "combat": "⚔️》",
            "dialogue": "💬》",
            "cultivation": "🧘》",
            "danger": "⚠️》"
        }
        
        return prompts.get(context, "》")


class PlayerGuidance:
    """玩家引导系统"""
    
    def __init__(self):
        self.tutorial_steps = {
            "first_login": [
                "欢迎来到修仙世界！我是你的引导精灵。",
                "首先，使用 'look' 命令观察周围环境。",
                "试试输入 'look' 看看周围有什么。"
            ],
            "first_move": [
                "很好！现在让我们学习如何移动。",
                "使用 'go <方向>' 来移动，比如 'go north'。",
                "方向可以是 north, south, east, west。"
            ],
            "first_item": [
                "看到物品了吗？使用 'get <物品名>' 来捡起它。",
                "捡起后可以用 'inventory' 查看背包。"
            ],
            "first_combat": [
                "遇到敌人了！别慌张。",
                "使用 'attack <目标>' 发起攻击。",
                "记得关注你的生命值，必要时使用 'flee' 逃跑。"
            ]
        }
        
        self.completed_tutorials: Set[str] = set()
        self.current_tutorial = None
        self.tutorial_step = 0
    
    def start_tutorial(self, tutorial_name: str) -> Optional[str]:
        """开始教程"""
        if tutorial_name in self.completed_tutorials:
            return None
        
        if tutorial_name not in self.tutorial_steps:
            return None
        
        self.current_tutorial = tutorial_name
        self.tutorial_step = 0
        
        return self._get_current_step()
    
    def _get_current_step(self) -> Optional[str]:
        """获取当前教程步骤"""
        if not self.current_tutorial:
            return None
        
        steps = self.tutorial_steps[self.current_tutorial]
        if self.tutorial_step < len(steps):
            return f"【引导】{steps[self.tutorial_step]}"
        
        return None
    
    def advance_tutorial(self) -> Optional[str]:
        """推进教程"""
        if not self.current_tutorial:
            return None
        
        self.tutorial_step += 1
        
        if self.tutorial_step >= len(self.tutorial_steps[self.current_tutorial]):
            # 教程完成
            self.completed_tutorials.add(self.current_tutorial)
            self.current_tutorial = None
            return "【引导】教程完成！你已经掌握了基本操作。"
        
        return self._get_current_step()
    
    def check_trigger(self, action: str) -> Optional[str]:
        """检查是否触发新教程"""
        triggers = {
            "first_login": lambda: len(self.completed_tutorials) == 0,
            "first_move": lambda: "first_login" in self.completed_tutorials and action == "look",
            "first_item": lambda: "first_move" in self.completed_tutorials and action.startswith("go"),
            "first_combat": lambda: len(self.completed_tutorials) >= 2 and action == "attack"
        }
        
        for tutorial, condition in triggers.items():
            if tutorial not in self.completed_tutorials and condition():
                return self.start_tutorial(tutorial)
        
        return None


# 全局实例
error_handler = FriendlyErrorHandler()
command_processor = SmartCommandProcessor()
tips_display = GameTipsDisplay()
input_helper = InputHelper()
player_guidance = PlayerGuidance()


def enhance_player_experience(game_core):
    """集成玩家体验增强功能"""
    # 包装原始的命令处理函数
    original_process = game_core.process_command if hasattr(game_core, 'process_command') else None
    
    def enhanced_process_command(raw_input: str):
        # 处理快捷输入
        expanded_input = input_helper.expand_shortcut(raw_input)
        
        # 智能命令处理
        command, args = command_processor.process_command(expanded_input)
        
        # 检查教程触发
        tutorial_msg = player_guidance.check_trigger(command)
        if tutorial_msg:
            print(tutorial_msg)
        
        # 调用原始处理函数
        if original_process:
            result = original_process(f"{command} {' '.join(args)}".strip())
            
            # 如果命令不存在，提供建议
            if "unknown command" in result.lower() or "invalid command" in result.lower():
                suggestion = command_processor.suggest_command(command)
                if suggestion:
                    result += f"\n你是否想输入 '{suggestion}'？"
            
            # 显示提示
            if tips_display.should_show_tip():
                tip = tips_display.get_contextual_tip()
                if tip:
                    result += f"\n\n{tip}"
            
            return result
        
        return f"已处理命令：{command} {args}"
    
    # 替换命令处理函数
    if hasattr(game_core, 'process_command'):
        game_core.process_command = enhanced_process_command
