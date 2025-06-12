"""
NLP处理器 - 修复JSON解析问题
"""

import os
import json
import re
import requests  # type: ignore[import-untyped]
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from ..command_parser import ParsedCommand, CommandType

logger = logging.getLogger(__name__)


@dataclass
class NLPConfig:
    """NLP配置"""
    enable_llm: bool = True
    llm_provider: str = "deepseek"
    api_key: str = ""
    fallback_to_rules: bool = True
    confidence_threshold: float = 0.7


class NLPProcessor:
    """NLP处理器 - 修复JSON解析"""

    def __init__(self, command_parser=None, config: Optional[NLPConfig] = None):
        self.command_parser = command_parser
        self.config = config or NLPConfig()

        # 从环境变量获取API密钥
        if not self.config.api_key:
            self.config.api_key = os.getenv('DEEPSEEK_API_KEY', '')

        if not self.config.api_key:
            logger.warning("未设置DEEPSEEK_API_KEY，NLP功能将降级")
            self.config.enable_llm = False

        self.api_url = "https://api.deepseek.com/v1/chat/completions"

    def _parse_deepseek_json(self, raw_response: str) -> Optional[Dict[str, Any]]:
        """智能解析各种格式的JSON，处理markdown包裹的情况"""
        if not raw_response:
            return None
        
        # 1. 尝试直接解析
        try:
            return json.loads(raw_response)
        except:
            pass
        
        # 2. 去除markdown代码块标记
        patterns = [
            r"```json\s*\n([\s\S]*?)\n```",  # 匹配 ```json\n ... \n```
            r"```\s*\n([\s\S]*?)\n```"  # 匹配 ```\n ... \n```
        ]

        for pattern in patterns:
            match = re.search(pattern, raw_response, re.DOTALL)
            if match:
                try:
                    json_str = match.group(1)
                    return json.loads(json_str.strip())
                except:
                    continue
        
        # 3. 尝试提取JSON对象
        pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
        matches = re.findall(pattern, raw_response)
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
        
        # 4. 最后尝试：查找第一个{和最后一个}
        try:
            start = raw_response.find('{')
            end = raw_response.rfind('}')
            if start != -1 and end != -1 and start < end:
                json_str = raw_response[start:end+1]
                return json.loads(json_str)
        except:
            pass
        
        return None
    def parse(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> ParsedCommand:
        """解析用户输入 - 优先DeepSeek API"""
        
        if not user_input.strip():
            return ParsedCommand(
                command_type=CommandType.UNKNOWN,
                raw_text=user_input,
                confidence=0
            )
        
        # 1. 如果启用了LLM，优先使用DeepSeek
        if self.config.enable_llm and self.config.api_key:
            try:
                api_result = self._call_deepseek(user_input, context)
                if api_result and api_result.confidence > 0.3:
                    logger.info(f"DeepSeek解析成功: {api_result.command_type} (置信度:{api_result.confidence})")
                    return api_result
            except Exception as e:
                logger.error(f"DeepSeek API错误: {e}")
        
        # 2. 尝试本地解析
        if self.command_parser:
            local_result = self.command_parser.parse(user_input)
            if local_result.confidence > 0:
                return local_result
        
        # 3. 模糊匹配
        fuzzy_result = self._fuzzy_parse(user_input)
        if fuzzy_result.confidence > 0:
            return fuzzy_result
        
        # 4. 无法理解
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            raw_text=user_input,
            confidence=0,
            parameters={"suggestions": self._get_suggestions(user_input)}
        )
    
    def _call_deepseek(self, text: str, context: Optional[Dict[str, Any]] = None) -> Optional[ParsedCommand]:
        """调用DeepSeek API"""
        
        system_prompt = """你是一个文本冒险游戏的指令解析器。请将玩家输入转为一个结构化的游戏命令。

格式要求：
{
  "command": "命令类型（ATTACK, CULTIVATE, STATUS, USE_SKILL, DEFEND, FLEE, INVENTORY, SKILLS, MAP, EXPLORE, MOVE, TALK, BREAKTHROUGH）",
  "target": "可选目标",
  "parameters": { 键值对参数 },
  "confidence": 0.0-1.0,
  "reasoning": "简要解释你的判断"
}

示例：
- 输入"修炼100天" → {"command": "CULTIVATE", "parameters": {"duration": "100天"}, "confidence": 0.95}
- 输入"用剑气斩攻击妖兽" → {"command": "USE_SKILL", "target": "妖兽", "parameters": {"skill": "剑气斩"}, "confidence": 0.9}

不要返回代码块符号（```）。只输出 JSON。
Don't hold back. Give it your all. Be confident and concise."""
        
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.api_url,
            headers=headers,
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"解析玩家输入: {text}"}
                ],
                "temperature": 0.2,
                "max_tokens": 200
            },
            timeout=15
        )
        
        if response.status_code == 200:
            content = response.json()['choices'][0]['message']['content']
            logger.info(f"[NLP-INPUT] 玩家输入: {text}")
            logger.debug(f"[NLP-RESP] 原始响应: {content[:200]}...")
            logger.debug(f"DeepSeek原始返回: {content}")
            
            # 使用新的JSON解析方法
            parsed = self._parse_deepseek_json(content)
            
            if parsed:
                # 映射命令类型
                cmd_str = parsed.get("command", "UNKNOWN").upper()
                try:
                    command_type = CommandType(cmd_str.lower())
                except ValueError:
                    # 如果CommandType没有这个值，尝试映射
                    cmd_map = {
                        "ATTACK": CommandType.ATTACK,
                        "USE_SKILL": CommandType.USE_SKILL,
                        "CULTIVATE": getattr(CommandType, 'CULTIVATE', CommandType.UNKNOWN),
                        "STATUS": CommandType.STATUS,
                        "TALK": getattr(CommandType, 'TALK', CommandType.UNKNOWN),
                        "MOVE": getattr(CommandType, 'MOVE', CommandType.UNKNOWN),
                        "EXPLORE": getattr(CommandType, 'EXPLORE', CommandType.UNKNOWN),
                        "BREAKTHROUGH": getattr(CommandType, 'BREAKTHROUGH', CommandType.UNKNOWN)
                    }
                    command_type = cmd_map.get(cmd_str, CommandType.UNKNOWN)
                
                # 额外提取时长信息（如果命令是修炼）
                params = parsed.get("parameters", {})
                if cmd_str == "CULTIVATE" and "duration" not in params:
                    # 尝试从原文本提取时长
                    duration = self._extract_duration(text)
                    if duration:
                        params["duration"] = duration
                
                return ParsedCommand(
                    command_type=command_type,
                    target=parsed.get("target"),
                    parameters=params,
                    raw_text=text,
                    confidence=float(parsed.get("confidence", 0.7))
                )
            else:
                logger.error("无法解析DeepSeek返回的JSON")
                # 降级到文本解析
                return self._parse_text_response(content, text)
        
        return None
    
    def _parse_text_response(self, response_text: str, original_input: str) -> ParsedCommand:
        """从文本响应提取命令（降级方案）"""
        response_lower = response_text.lower()
        
        # 基于关键词匹配
        keyword_map = {
            ("attack", "攻击"): (CommandType.ATTACK, 0.7),
            ("skill", "技能", "剑气斩"): (CommandType.USE_SKILL, 0.7),
            ("cultivate", "修炼"): (getattr(CommandType, 'CULTIVATE', CommandType.UNKNOWN), 0.8),
            ("status", "状态"): (CommandType.STATUS, 0.9),
            ("talk", "对话", "聊天"): (getattr(CommandType, 'TALK', CommandType.UNKNOWN), 0.7),
            ("move", "移动", "去"): (getattr(CommandType, 'MOVE', CommandType.UNKNOWN), 0.7),
            ("breakthrough", "突破"): (getattr(CommandType, 'BREAKTHROUGH', CommandType.UNKNOWN), 0.8)
        }
        
        for keywords, (cmd_type, confidence) in keyword_map.items():
            if any(kw in response_lower for kw in keywords):
                params = {}
                
                # 尝试提取参数
                if cmd_type == CommandType.USE_SKILL and "剑气斩" in response_lower:
                    params["skill"] = "剑气斩"
                elif cmd_type == getattr(CommandType, 'TALK', CommandType.UNKNOWN):
                    # 提取NPC名字
                    if "王老板" in response_lower:
                        params["npc"] = "王老板"
                
                return ParsedCommand(
                    command_type=cmd_type,
                    target=self._extract_target_from_response(response_text),
                    parameters=params,
                    raw_text=original_input,
                    confidence=confidence
                )
        
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            raw_text=original_input,
            confidence=0
        )
    
    def _extract_target_from_response(self, response: str) -> Optional[str]:
        """从响应中提取目标"""
        targets = ["敌人", "妖兽", "怪物", "王老板", "坊市"]
        for target in targets:
            if target in response:
                return target
        return None

    def _extract_duration(self, text: str) -> Optional[str]:
        """从文本中提取时长，例如 '修炼3个月' → '3月'"""
        match = re.search(r'([0-9]+|[一二三四五六七八九十两]+)\s*(?:个)?\s*([年月天日时])', text)
        if match:
            num = match.group(1)
            if not num.isdigit():
                num_map = {
                    '一': '1', '二': '2', '三': '3', '四': '4', '五': '5',
                    '六': '6', '七': '7', '八': '8', '九': '9', '十': '10',
                    '两': '2'
                }
                num = num_map.get(num, '1')
            return f"{num}{match.group(2)}"
        return None
    
    def _fuzzy_parse(self, text: str) -> ParsedCommand:
        """增强的模糊匹配 - 支持更多自然语言"""
        text_lower = text.lower()
        
        # 修炼相关
        if any(w in text_lower for w in ["修炼", "修行", "打坐", "练功", "闭关"]):
            # 提取时长
            params = {}
            duration = self._extract_duration(text)
            if duration:
                params["duration"] = duration
            
            return ParsedCommand(
                command_type=getattr(CommandType, 'CULTIVATE', CommandType.UNKNOWN),
                parameters=params,
                raw_text=text,
                confidence=0.95
            )
        
        # 攻击相关
        elif any(w in text_lower for w in ["攻击", "打", "杀", "揍", "轰", "砍", "斩"]):
            # 提取目标
            target = None
            if "妖兽" in text:
                target = "妖兽"
            elif "敌人" in text:
                target = "敌人"
            elif "怪" in text:
                target = "怪物"
            
            return ParsedCommand(
                command_type=CommandType.ATTACK,
                target=target or "敌人",
                raw_text=text,
                confidence=0.85
            )
        
        # 使用技能
        elif any(w in text_lower for w in ["剑气斩", "火球术", "技能"]) or \
             ("用" in text_lower and any(w in text_lower for w in ["斩", "术", "技"])):
            # 识别技能名
            skill = None
            if "剑气斩" in text_lower:
                skill = "剑气斩"
            elif "火球" in text_lower:
                skill = "火球术"
            
            return ParsedCommand(
                command_type=CommandType.USE_SKILL,
                target="敌人",
                parameters={"skill": skill or "剑气斩"},
                raw_text=text,
                confidence=0.8
            )
        
        # 状态查看
        elif any(w in text_lower for w in ["状态", "属性", "面板", "查看", "我的", "角色"]):
            return ParsedCommand(
                command_type=CommandType.STATUS,
                raw_text=text,
                confidence=0.95
            )
        
        # 移动
        elif any(w in text_lower for w in ["去", "走", "前往", "移动", "回"]):
            # 提取地点
            location = None
            if "坊市" in text:
                location = "天南坊市"
            elif "城" in text:
                location = "青云城"
            elif "野外" in text:
                location = "荒野"
            
            return ParsedCommand(
                command_type=getattr(CommandType, 'MOVE', CommandType.UNKNOWN),
                parameters={"location": location} if location else {},
                raw_text=text,
                confidence=0.75
            )
        
        # 对话
        elif any(w in text_lower for w in ["聊", "说话", "对话", "交谈", "找"]):
            # 提取NPC
            npc = None
            if "王老板" in text:
                npc = "王老板"
            elif "李太虚" in text:
                npc = "李太虚"
            
            return ParsedCommand(
                command_type=getattr(CommandType, 'TALK', CommandType.UNKNOWN),
                target=npc,
                parameters={"npc": npc} if npc else {},
                raw_text=text,
                confidence=0.8
            )
        
        # 探索
        elif any(w in text_lower for w in ["探索", "搜索", "查看周围", "看看", "逛逛"]):
            return ParsedCommand(
                command_type=getattr(CommandType, 'EXPLORE', CommandType.UNKNOWN),
                raw_text=text,
                confidence=0.85
            )
        
        # 背包物品
        elif any(w in text_lower for w in ["背包", "物品", "装备", "道具"]):
            return ParsedCommand(
                command_type=CommandType.INVENTORY,
                raw_text=text,
                confidence=0.9
            )
        
        # 地图
        elif any(w in text_lower for w in ["地图", "位置", "在哪", "哪里"]):
            return ParsedCommand(
                command_type=CommandType.MAP,
                raw_text=text,
                confidence=0.9
            )
        
        # 生活类动作（吃饭、睡觉等）
        elif any(w in text_lower for w in ["吃", "喝", "睡", "休息"]):
            # 转换为修炼命令（游戏中休息等同于修炼恢复）
            return ParsedCommand(
                command_type=getattr(CommandType, 'CULTIVATE', CommandType.UNKNOWN),
                parameters={"action": "rest", "reason": "恢复体力"},
                raw_text=text,
                confidence=0.7
            )
        
        # 帮助
        elif any(w in text_lower for w in ["帮助", "命令", "怎么", "help", "?"]):
            return ParsedCommand(
                command_type=CommandType.HELP,
                raw_text=text,
                confidence=0.95
            )
        
        # 退出
        elif any(w in text_lower for w in ["退出", "离开", "再见", "拜拜", "quit", "exit"]):
            return ParsedCommand(
                command_type=CommandType.QUIT,
                raw_text=text,
                confidence=0.9
            )
        
        # 突破（如果存在）
        elif any(w in text_lower for w in ["突破", "进阶", "升级"]):
            return ParsedCommand(
                command_type=getattr(CommandType, 'BREAKTHROUGH', CommandType.UNKNOWN),
                raw_text=text,
                confidence=0.85
            )
        
        return ParsedCommand(
            command_type=CommandType.UNKNOWN,
            raw_text=text,
            confidence=0
        )
    
    def _get_suggestions(self, text: str) -> list:
        """获取更智能的建议"""
        suggestions = []
        text_lower = text.lower()
        
        # 基于输入给出相关建议
        if any(w in text_lower for w in ["修", "炼", "练"]):
            suggestions.extend(["修炼1天", "修炼1年", "闭关修炼"])
        elif any(w in text_lower for w in ["攻", "打", "战", "斗"]):
            suggestions.extend(["攻击敌人", "使用剑气斩", "防御"])
        elif any(w in text_lower for w in ["去", "走", "移"]):
            suggestions.extend(["去天南坊市", "去野外", "探索周围"])
        elif any(w in text_lower for w in ["聊", "说", "话"]):
            suggestions.extend(["和王老板聊天", "和李太虚对话"])
        elif any(w in text_lower for w in ["看", "查"]):
            suggestions.extend(["查看状态", "查看地图", "查看背包", "查看技能"])
        elif any(w in text_lower for w in ["吃", "喝", "休"]):
            suggestions.extend(["休息恢复", "修炼恢复体力", "使用丹药"])
        
        # 默认建议
        if not suggestions:
            suggestions = [
                "查看状态", 
                "查看地图", 
                "修炼", 
                "探索周围",
                "和附近的人聊天"
            ]
        
        return suggestions[:5]

    def get_suggestions(self, text: str = "", context: dict = None) -> list:
        """公有接口 - 获取命令建议"""
        return self._get_suggestions(text)

    def process(self, *args, **kwargs):
        """兼容旧接口"""
        import warnings
        warnings.warn("process()已废弃，请使用parse()", DeprecationWarning)
        if args:
            return self.parse(args[0], args[1] if len(args) > 1 else None)
        return self.parse(kwargs.get('user_input', ''), kwargs.get('context'))

    def explain_command(self, command):
        """解释命令对象"""
        if hasattr(command, 'command_type'):
            return f"命令类型: {command.command_type.value if hasattr(command.command_type, 'value') else command.command_type}"
        return "无法解释该命令"
