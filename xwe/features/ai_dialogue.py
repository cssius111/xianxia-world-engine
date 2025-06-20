# xwe/features/ai_dialogue.py

import asyncio
import re
from collections import defaultdict
from typing import Any, Dict, List, Optional


class AIDialogueManager:
    """AI驱动的对话管理器"""

    def __init__(self, llm_client, prompt_engine) -> None:
        self.llm = llm_client
        self.prompt_engine = prompt_engine
        self.conversation_memory = {}  # 对话记忆
        self.relationship_tracker = {}  # 关系追踪

    async def generate_npc_dialogue(self, npc_id: str, player_input: str, context: dict) -> Dict:
        """生成NPC对话"""

        # 获取对话历史
        history = self.conversation_memory.get(npc_id, [])

        # 构建增强上下文
        enhanced_context = self._enhance_context_with_history(context, npc_id, history)

        # 生成提示
        from xwe.core.nlp.advanced.prompt_engine import GameContext, ResponseType

        game_context = GameContext(
            player_state=context.get("player", {}),
            location=context.get("location", {}),
            recent_events=context.get("recent_events", []),
            active_npcs=[context.get("npc", {})],
            world_state=context.get("world", {}),
        )

        prompt = self.prompt_engine.generate_prompt(
            ResponseType.DIALOGUE,
            player_input,
            game_context,
            constraints={
                "maintain_consistency": True,
                "relationship_level": self.relationship_tracker.get(npc_id, 0),
            },
        )

        # 调用LLM
        response = await self.llm.generate(prompt, temperature=0.8)

        # 解析响应
        dialogue_data = self._parse_dialogue_response(response)

        # 更新记忆和关系
        self._update_conversation_memory(npc_id, player_input, dialogue_data)
        self._update_relationship(npc_id, dialogue_data)

        return dialogue_data

    def _parse_dialogue_response(self, response: str) -> Dict:
        """解析对话响应"""
        # 支持多种格式
        lines = response.strip().split("\n")

        dialogue = {"text": "", "emotion": "neutral", "choices": [], "effects": []}

        current_section = "text"

        for line in lines:
            if line.startswith("[情绪]"):
                dialogue["emotion"] = line.replace("[情绪]", "").strip()
            elif line.startswith("[选项"):
                current_section = "choices"
                choice_match = re.match(r"\[选项(\d+)\](.*)", line)
                if choice_match:
                    dialogue["choices"].append(
                        {"id": int(choice_match.group(1)), "text": choice_match.group(2).strip()}
                    )
            elif line.startswith("[效果]"):
                effect_text = line.replace("[效果]", "").strip()
                dialogue["effects"].append(self._parse_effect(effect_text))
            else:
                if current_section == "text":
                    dialogue["text"] += line + "\n"

        dialogue["text"] = dialogue["text"].strip()
        return dialogue

    def _enhance_context_with_history(self, context: dict, npc_id: str, history: List[Any]) -> dict:
        """用历史增强上下文"""
        enhanced = context.copy()

        # 添加对话历史摘要
        if history:
            recent_history = history[-5:]  # 最近5条
            enhanced["dialogue_history"] = [
                {"speaker": h["speaker"], "text": h["text"][:50] + "..."} for h in recent_history
            ]

        # 添加关系信息
        enhanced["relationship"] = {
            "level": self.relationship_tracker.get(npc_id, 0),
            "status": self._get_relationship_status(npc_id),
        }

        return enhanced

    def _update_conversation_memory(
        self, npc_id: str, player_input: str, dialogue_data: Dict[str, Any]
    ):
        """更新对话记忆"""
        if npc_id not in self.conversation_memory:
            self.conversation_memory[npc_id] = []

        # 记录玩家输入
        self.conversation_memory[npc_id].append(
            {
                "speaker": "player",
                "text": player_input,
                "timestamp": asyncio.get_event_loop().time(),
            }
        )

        # 记录NPC回复
        self.conversation_memory[npc_id].append(
            {
                "speaker": npc_id,
                "text": dialogue_data["text"],
                "emotion": dialogue_data["emotion"],
                "timestamp": asyncio.get_event_loop().time(),
            }
        )

        # 限制记忆长度
        if len(self.conversation_memory[npc_id]) > 100:
            self.conversation_memory[npc_id] = self.conversation_memory[npc_id][-50:]

    def _update_relationship(self, npc_id: str, dialogue_data: Dict[str, Any]) -> None:
        """更新关系值"""
        if npc_id not in self.relationship_tracker:
            self.relationship_tracker[npc_id] = 0

        # 根据对话效果更新关系
        for effect in dialogue_data.get("effects", []):
            if effect.get("type") == "relationship":
                self.relationship_tracker[npc_id] += effect.get("value", 0)

        # 确保关系值在合理范围
        self.relationship_tracker[npc_id] = max(-100, min(100, self.relationship_tracker[npc_id]))

    def _get_relationship_status(self, npc_id: str) -> str:
        """获取关系状态描述"""
        level = self.relationship_tracker.get(npc_id, 0)

        if level >= 80:
            return "挚友"
        elif level >= 60:
            return "友好"
        elif level >= 30:
            return "熟识"
        elif level >= 0:
            return "中立"
        elif level >= -30:
            return "冷淡"
        elif level >= -60:
            return "敌视"
        else:
            return "仇恨"

    def _parse_effect(self, effect_text: str) -> Dict[str, Any]:
        """解析效果文本"""
        # 简单的效果解析
        if "好感度" in effect_text:
            match = re.search(r"([+-]?\d+)", effect_text)
            if match:
                return {"type": "relationship", "value": int(match.group(1))}
        elif "物品" in effect_text:
            return {"type": "item", "description": effect_text}
        else:
            return {"type": "other", "description": effect_text}

    def get_npc_memory(self, npc_id: str) -> List[Dict]:
        """获取与NPC的对话记忆"""
        return self.conversation_memory.get(npc_id, [])

    def get_relationship_level(self, npc_id: str) -> int:
        """获取与NPC的关系值"""
        return self.relationship_tracker.get(npc_id, 0)

    def clear_memory(self, npc_id: Optional[str] = None) -> None:
        """清除对话记忆"""
        if npc_id:
            self.conversation_memory.pop(npc_id, None)
        else:
            self.conversation_memory.clear()
