"""
上下文摘要器
使用 LLM 生成对话历史的摘要
"""

import json
import logging
from typing import List, Optional, Dict, Any

from ..nlp.llm_client import LLMClient

logger = logging.getLogger(__name__)


class ContextSummarizer:
    """
    上下文摘要器 - 使用 LLM 生成简洁的对话摘要
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        """
        初始化摘要器
        
        Args:
            llm_client: LLM 客户端实例，如果不提供则创建新实例
        """
        self.llm_client = llm_client
        self._init_prompts()
        
    def _init_prompts(self):
        """初始化提示模板"""
        self.summary_prompt_template = """你是一个对话摘要助手。请将以下修仙世界游戏的对话历史压缩成一个简洁的摘要。

要求：
1. 保留关键事件和决策
2. 记录重要的游戏状态变化（境界提升、获得物品、位置变化等）
3. 保持时间顺序
4. 摘要长度不超过原文的 1/3
5. 使用第三人称叙述

对话历史：
{}

请直接输出摘要内容，不要有任何额外说明。"""

        self.structured_summary_prompt = """你是修仙世界游戏的上下文分析器。请分析以下对话并提取结构化信息。

对话历史：
{}

请以 JSON 格式输出以下信息：
{{
  "summary": "简要总结（不超过100字）",
  "key_events": ["事件1", "事件2"],
  "state_changes": {{
    "realm": "境界变化",
    "location": "位置变化",
    "items": ["获得/失去的物品"]
  }},
  "important_npcs": ["提到的重要NPC"],
  "player_goals": "玩家当前目标"
}}

只输出 JSON，不要有其他内容。"""
    
    def summarize(self, messages: List[str], 
                  structured: bool = False,
                  max_tokens: int = 200) -> str:
        """
        生成消息列表的摘要
        
        Args:
            messages: 消息列表
            structured: 是否生成结构化摘要
            max_tokens: 最大生成 token 数
            
        Returns:
            摘要文本或结构化摘要 JSON
        """
        if not messages:
            return ""
        
        # 合并消息
        combined_text = "\n".join(messages)
        
        # 限制输入长度（避免超过上下文窗口）
        max_input_chars = 2000
        if len(combined_text) > max_input_chars:
            # 保留开头和结尾
            head = combined_text[:max_input_chars//2]
            tail = combined_text[-max_input_chars//2:]
            combined_text = f"{head}\n...[中间部分已省略]...\n{tail}"
        
        try:
            # 选择提示模板
            if structured:
                prompt = self.structured_summary_prompt.format(combined_text)
            else:
                prompt = self.summary_prompt_template.format(combined_text)
            
            # 调用 LLM
            if self.llm_client:
                summary = self.llm_client.chat(
                    prompt=prompt,
                    temperature=0.3,  # 较低的温度以获得稳定输出
                    max_tokens=max_tokens
                )
                
                # 如果是结构化摘要，验证 JSON 格式
                if structured:
                    try:
                        json.loads(summary)
                    except json.JSONDecodeError:
                        logger.warning("LLM 返回的不是有效 JSON，使用降级方案")
                        summary = self._fallback_summary(messages)
                
                return summary
            else:
                # 没有 LLM 客户端时使用简单摘要
                return self._fallback_summary(messages)
                
        except Exception as e:
            logger.error(f"生成摘要失败: {e}")
            return self._fallback_summary(messages)
    
    def _fallback_summary(self, messages: List[str]) -> str:
        """
        降级摘要方案（不依赖 LLM）
        
        Args:
            messages: 消息列表
            
        Returns:
            简单的摘要文本
        """
        if not messages:
            return ""
        
        # 提取关键信息
        keywords = ["探索", "修炼", "战斗", "获得", "前往", "提升", "突破"]
        important_messages = []
        
        for msg in messages:
            # 检查是否包含关键词
            if any(keyword in msg for keyword in keywords):
                important_messages.append(msg)
        
        # 如果没有重要消息，取首尾
        if not important_messages:
            if len(messages) > 2:
                important_messages = [messages[0], messages[-1]]
            else:
                important_messages = messages
        
        # 限制数量
        important_messages = important_messages[:5]
        
        # 生成摘要
        summary_parts = [f"玩家进行了{len(messages)}次交互"]
        if important_messages:
            summary_parts.append("主要行动包括：" + "；".join(important_messages[:3]))
        
        return "。".join(summary_parts)
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """
        从文本中提取实体（NPC、地点、物品等）
        
        Args:
            text: 输入文本
            
        Returns:
            实体字典
        """
        # 简单的基于规则的实体提取
        entities = {
            "npcs": [],
            "locations": [],
            "items": []
        }
        
        # NPC 模式（XX道人、XX真人、XX散人等）
        npc_patterns = ["道人", "真人", "散人", "长老", "掌门", "弟子"]
        for pattern in npc_patterns:
            if pattern in text:
                # 简单提取，实际应用中可以使用更复杂的规则
                words = text.split()
                for i, word in enumerate(words):
                    if pattern in word and i > 0:
                        potential_npc = words[i-1] + word
                        if len(potential_npc) <= 6:  # 避免过长
                            entities["npcs"].append(potential_npc)
        
        # 地点模式
        location_patterns = ["城", "山", "谷", "洞", "府", "殿", "阁"]
        for pattern in location_patterns:
            if pattern in text:
                # 提取包含地点词的短语
                parts = text.split("前往")
                for part in parts[1:]:
                    words = part.split()
                    if words and pattern in words[0]:
                        entities["locations"].append(words[0])
        
        # 物品模式
        item_patterns = ["丹", "剑", "符", "玉", "石", "珠"]
        for pattern in item_patterns:
            if pattern in text:
                parts = text.split("获得")
                for part in parts[1:]:
                    words = part.split()
                    if words and pattern in words[0]:
                        entities["items"].append(words[0])
        
        # 去重
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def calculate_importance(self, messages: List[str]) -> float:
        """
        计算消息组的重要性得分
        
        Args:
            messages: 消息列表
            
        Returns:
            重要性得分 (0-1)
        """
        if not messages:
            return 0.0
        
        score = 0.5  # 基础分
        
        # 重要事件加分
        important_events = [
            ("突破", 0.2),
            ("获得", 0.1),
            ("战斗", 0.15),
            ("死亡", 0.25),
            ("任务完成", 0.2),
            ("境界提升", 0.25)
        ]
        
        combined_text = " ".join(messages)
        for event, weight in important_events:
            if event in combined_text:
                score += weight
        
        # 消息数量因素
        if len(messages) > 10:
            score += 0.1
        
        # 限制最大值
        return min(score, 1.0)
