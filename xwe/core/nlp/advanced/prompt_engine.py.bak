# xwe/core/nlp/advanced/prompt_engine.py

from typing import Any, Dict, List, Optional
from dataclasses import dataclass
import json
from enum import Enum

class ResponseType(Enum):
    """AI响应类型"""
    NARRATIVE = "narrative"          # 叙事描述
    COMMAND_PARSE = "command_parse"  # 命令解析
    DIALOGUE = "dialogue"            # 对话生成
    WORLD_EVENT = "world_event"      # 世界事件
    COMBAT_NARRATION = "combat_narration"  # 战斗叙述

@dataclass
class GameContext:
    """游戏上下文"""
    player_state: Dict[str, Any]
    location: Dict[str, Any]
    recent_events: List[Dict[str, Any]]
    active_npcs: List[Dict[str, Any]]
    world_state: Dict[str, Any]
    
class AdvancedPromptEngine:
    """高级提示引擎"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.style_guides = self._load_style_guides()
        self.few_shot_examples = self._load_examples()
        
    def generate_prompt(self, 
                       response_type: ResponseType,
                       user_input: str,
                       context: GameContext,
                       constraints: Optional[Dict] = None) -> str:
        """生成优化的提示"""
        
        # 基础模板
        template = self.templates.get(response_type, self.templates[ResponseType.NARRATIVE])
        
        # 构建系统提示
        system_prompt = self._build_system_prompt(response_type, context)
        
        # 添加少样本示例
        examples = self._get_relevant_examples(response_type, user_input)
        
        # 构建约束条件
        constraints_text = self._format_constraints(constraints or {})
        
        # 组装完整提示
        prompt = f"""
{system_prompt}

{examples}

当前游戏状态：
- 玩家：{self._format_player_state(context.player_state)}
- 位置：{context.location['name']} - {context.location['description']}
- 最近事件：{self._format_recent_events(context.recent_events[-3:])}

{constraints_text}

玩家输入：{user_input}

请根据以上信息生成响应：
"""
        
        return prompt
        
    def _build_system_prompt(self, response_type: ResponseType, 
                            context: GameContext) -> str:
        """构建系统提示"""
        base_prompt = """
你是修仙世界的游戏引擎AI，负责生成沉浸式的游戏内容。

世界观设定：
- 这是一个东方玄幻修仙世界
- 修炼境界从低到高：炼气期、筑基期、金丹期、元婴期、化神期等
- 世界充满灵气，修士可以通过修炼提升境界
- 存在各种天材地宝、功法秘籍、法宝神器

写作风格要求：
- 使用古风仙侠文风，词藻优美但不过分华丽
- 保持神秘感和仙气飘飘的氛围
- 适当使用修仙术语，但要让玩家容易理解
- 重要数值变化用【】标注，如【灵力+10】
"""
        
        # 根据响应类型添加特定指令
        type_specific = {
            ResponseType.NARRATIVE: """
任务：根据玩家行动生成叙事描述
要求：
1. 描述要生动且符合当前场景
2. 包含感官细节（视觉、听觉、嗅觉等）
3. 如有数值变化，在描述后用【】标注
4. 保持100-200字的适中长度
""",
            ResponseType.COMMAND_PARSE: """
任务：将玩家的自然语言转换为游戏指令
输出格式：
{
    "command": "指令名称",
    "target": "目标ID（如果有）",
    "parameters": {参数字典}
}
注意：如果无法解析，返回最接近的指令并说明原因
""",
            ResponseType.DIALOGUE: f"""
任务：为NPC生成对话
当前NPC：{context.active_npcs[0]['name'] if context.active_npcs else '未知'}
性格设定：{context.active_npcs[0].get('personality', '中立') if context.active_npcs else ''}
要求：
1. 符合NPC的身份和性格
2. 推进剧情或提供有用信息
3. 可以包含选项供玩家选择
"""
        }
        
        return base_prompt + "\n" + type_specific.get(response_type, "")
        
    def _format_constraints(self, constraints: Dict[str, Any]) -> str:
        """格式化约束条件"""
        if not constraints:
            return ""
            
        lines = ["约束条件："]
        
        if 'max_damage' in constraints:
            lines.append(f"- 伤害不超过{constraints['max_damage']}")
        if 'forbidden_actions' in constraints:
            lines.append(f"- 禁止的行动：{', '.join(constraints['forbidden_actions'])}")
        if 'required_elements' in constraints:
            lines.append(f"- 必须包含：{', '.join(constraints['required_elements'])}")
            
        return "\n".join(lines)
        
    def parse_ai_response(self, response: str, 
                         response_type: ResponseType) -> Dict[str, Any]:
        """解析AI响应"""
        
        if response_type == ResponseType.COMMAND_PARSE:
            # 尝试解析JSON
            try:
                return json.loads(response)
            except:
                # 降级处理
                return self._fuzzy_parse_command(response)
                
        elif response_type == ResponseType.NARRATIVE:
            # 提取数值变化
            import re
            changes = re.findall(r'【([^】]+)】', response)
            narrative = re.sub(r'【[^】]+】', '', response).strip()
            
            return {
                'narrative': narrative,
                'changes': self._parse_changes(changes)
            }
            
        return {'raw_response': response}
        
    def _load_templates(self) -> Dict[ResponseType, str]:
        """加载提示模板"""
        return {
            ResponseType.NARRATIVE: "叙事模板",
            ResponseType.COMMAND_PARSE: "命令解析模板",
            ResponseType.DIALOGUE: "对话生成模板",
            ResponseType.WORLD_EVENT: "世界事件模板",
            ResponseType.COMBAT_NARRATION: "战斗叙述模板"
        }
        
    def _load_style_guides(self) -> Dict[str, str]:
        """加载风格指南"""
        return {
            "default": "标准仙侠风格",
            "ancient": "古风典雅",
            "modern": "现代网文风"
        }
        
    def _load_examples(self) -> Dict[ResponseType, List[str]]:
        """加载少样本示例"""
        return {
            ResponseType.NARRATIVE: [
                "示例1：你缓缓运转功法，周身灵气如潮水般涌入经脉...",
                "示例2：剑光如虹，斩破虚空，妖兽哀嚎一声倒下..."
            ],
            ResponseType.DIALOGUE: [
                "NPC：道友面生得很，可是初次来到天南坊市？",
                "NPC：此地灵气稀薄，不宜久留，还请道友另寻他处。"
            ]
        }
        
    def _format_player_state(self, player_state: Dict[str, Any]) -> str:
        """格式化玩家状态"""
        return f"{player_state.get('name', '无名')} - {player_state.get('realm', '炼气期')} - HP:{player_state.get('health', 100)}/{player_state.get('max_health', 100)}"
        
    def _format_recent_events(self, events: List[Dict[str, Any]]) -> str:
        """格式化最近事件"""
        if not events:
            return "无"
        return "; ".join([e.get('description', '') for e in events])
        
    def _parse_changes(self, changes: List[str]) -> List[Dict[str, Any]]:
        """解析数值变化"""
        parsed = []
        for change in changes:
            # 简单解析，如 "灵力+10" -> {"type": "灵力", "value": 10}
            parts = change.split('+')
            if len(parts) == 2:
                parsed.append({
                    "type": parts[0].strip(),
                    "value": int(parts[1].strip()) if parts[1].strip().isdigit() else parts[1].strip()
                })
        return parsed
        
    def _fuzzy_parse_command(self, response: str) -> Dict[str, Any]:
        """模糊解析命令"""
        # 简单的降级处理
        return {
            "command": "unknown",
            "confidence": 0.3,
            "raw_response": response
        }
