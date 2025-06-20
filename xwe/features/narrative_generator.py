# xwe/features/narrative_generator.py

import asyncio
from collections import defaultdict
from typing import Any, Dict, List, Optional


class DynamicNarrativeGenerator:
    """动态叙事生成器"""

    def __init__(self, llm_client, style_manager=None) -> None:
        self.llm = llm_client
        self.style_manager = style_manager or DefaultStyleManager()
        self.narrative_cache = {}  # 缓存常见场景

    async def generate_combat_narrative(self, combat_events: List[Dict], context: dict) -> str:
        """生成战斗叙事"""

        # 分析战斗事件
        key_moments = self._extract_key_moments(combat_events)

        # 构建叙事提示
        prompt = f"""
将以下战斗事件转化为精彩的仙侠战斗描写：

战斗概况：
- 参战方：{self._format_combatants(combat_events)}
- 环境：{context.get('location', {}).get('name', '未知之地')}
- 持续回合：{len(combat_events)}

关键时刻：
{self._format_key_moments(key_moments)}

要求：
1. 描写要有画面感，突出仙侠特色
2. 使用招式名称，如"青莲剑歌"、"天雷引"等
3. 体现战斗的激烈程度和转折点
4. 结尾总结战斗结果
5. 全文200-300字

风格参考：{self.style_manager.get_combat_style()}
"""

        # 生成叙事
        narrative = await self.llm.generate(prompt, temperature=0.9)

        # 后处理
        return self._post_process_narrative(narrative, combat_events)

    async def generate_exploration_narrative(
        self, action: str, discovery: Optional[Dict], context: dict
    ) -> str:
        """生成探索叙事"""

        # 检查缓存
        cache_key = f"{context.get('location', {}).get('id', 'unknown')}_{action}_{discovery.get('type') if discovery else 'none'}"
        if cache_key in self.narrative_cache:
            return self._personalize_cached_narrative(self.narrative_cache[cache_key], context)

        # 构建提示
        prompt = self._build_exploration_prompt(action, discovery, context)

        # 生成叙事
        narrative = await self.llm.generate(prompt, temperature=0.85)

        # 缓存通用部分
        if discovery is None:  # 只缓存无发现的情况
            self.narrative_cache[cache_key] = self._extract_template(narrative)

        return narrative

    def _extract_key_moments(self, combat_events: List[Dict]) -> List[Dict]:
        """提取关键战斗时刻"""
        key_moments = []

        for event in combat_events:
            # 暴击
            if event.get("critical"):
                key_moments.append(
                    {
                        "type": "critical",
                        "attacker": event["attacker"],
                        "skill": event.get("skill", "普通攻击"),
                        "damage": event["damage"],
                    }
                )
            # 技能释放
            elif event.get("skill_used"):
                key_moments.append(
                    {
                        "type": "skill",
                        "caster": event["caster"],
                        "skill": event["skill_name"],
                        "effect": event.get("effect", "造成伤害"),
                    }
                )
            # 血量临界
            elif event.get("health_critical"):
                key_moments.append(
                    {
                        "type": "near_death",
                        "entity": event["entity"],
                        "health_percent": event["health_percent"],
                    }
                )

        return key_moments

    def _format_combatants(self, combat_events: List[Dict]) -> str:
        """格式化参战方信息"""
        combatants = set()
        for event in combat_events:
            if "attacker" in event:
                combatants.add(event["attacker"])
            if "defender" in event:
                combatants.add(event["defender"])
            if "caster" in event:
                combatants.add(event["caster"])

        return "、".join(list(combatants)[:5])  # 最多显示5个

    def _format_key_moments(self, key_moments: List[Dict]) -> str:
        """格式化关键时刻"""
        lines = []
        for i, moment in enumerate(key_moments[:5]):  # 最多5个关键时刻
            if moment["type"] == "critical":
                lines.append(
                    f"{i+1}. {moment['attacker']}使用{moment['skill']}打出暴击，造成{moment['damage']}点伤害"
                )
            elif moment["type"] == "skill":
                lines.append(f"{i+1}. {moment['caster']}释放{moment['skill']}，{moment['effect']}")
            elif moment["type"] == "near_death":
                lines.append(
                    f"{i+1}. {moment['entity']}生命值降至{moment['health_percent']}%，濒临败北"
                )

        return "\n".join(lines)

    def _build_exploration_prompt(
        self, action: str, discovery: Optional[Dict], context: dict
    ) -> str:
        """构建探索提示"""
        location = context.get("location", {})
        player = context.get("player", {})

        base_prompt = f"""
玩家在{location.get('name', '未知之地')}进行探索。

地点描述：{location.get('description', '一个神秘的地方')}
玩家动作：{action}
"""

        if discovery:
            base_prompt += f"""
发现内容：
- 类型：{discovery.get('type', '未知')}
- 描述：{discovery.get('description', '有所发现')}
- 价值：{discovery.get('value', '普通')}
"""
        else:
            base_prompt += "\n结果：没有特别的发现"

        base_prompt += f"""

请生成100-150字的探索叙事，要求：
1. 描写玩家的探索过程
2. 营造场景氛围
3. 如有发现，描述发现过程和玩家反应
4. 使用第二人称"你"
5. 风格：{self.style_manager.get_exploration_style()}
"""

        return base_prompt

    def _post_process_narrative(self, narrative: str, events: List[Dict]) -> str:
        """后处理叙事文本"""
        # 确保长度合适
        if len(narrative) > 500:
            # 找到最后一个句号截断
            last_period = narrative[:500].rfind("。")
            if last_period > 300:
                narrative = narrative[: last_period + 1]

        # 添加战斗结果总结（如果原文没有）
        if events and not any(word in narrative[-50:] for word in ["胜利", "败北", "结束", "完"]):
            winner = self._determine_winner(events)
            if winner:
                narrative += f"\n\n最终，{winner}取得了胜利。"

        return narrative.strip()

    def _determine_winner(self, events: List[Dict]) -> Optional[str]:
        """根据战斗事件判断胜者"""
        # 简单的判断逻辑
        for event in reversed(events):
            if event.get("type") == "defeat":
                return event.get("winner")
        return None

    def _personalize_cached_narrative(self, template: str, context: dict) -> str:
        """个性化缓存的叙事模板"""
        # 替换模板中的占位符
        player_name = context.get("player", {}).get("name", "你")
        location_name = context.get("location", {}).get("name", "此地")

        narrative = template.replace("[玩家]", player_name)
        narrative = narrative.replace("[地点]", location_name)

        return narrative

    def _extract_template(self, narrative: str) -> str:
        """从叙事中提取可重用的模板"""
        # 将具体名称替换为占位符
        template = narrative
        # 这里可以使用更复杂的NER来识别和替换实体
        # 简单示例：
        template = template.replace("你", "[玩家]")

        return template

    async def generate_cultivation_narrative(
        self, duration: str, results: Dict[str, Any], context: dict
    ) -> str:
        """生成修炼叙事"""
        prompt = f"""
描述修炼过程：

修炼者：{context.get('player', {}).get('name', '你')}
当前境界：{context.get('player', {}).get('realm', '炼气期')}
修炼时长：{duration}
修炼地点：{context.get('location', {}).get('name', '洞府')}

修炼结果：
- 经验获得：{results.get('exp_gained', 0)}
- 境界变化：{results.get('realm_change', '无')}
- 特殊感悟：{results.get('enlightenment', '无')}

请生成150-200字的修炼描述，要求：
1. 描写修炼的过程和感受
2. 如有突破，重点描写突破时刻
3. 体现修仙世界的特色（灵气、经脉、天地感应等）
4. 使用第二人称
"""

        narrative = await self.llm.generate(prompt, temperature=0.8)
        return narrative


class DefaultStyleManager:
    """默认风格管理器"""

    def get_combat_style(self) -> str:
        return "热血激烈，招式华丽，注重画面感"

    def get_exploration_style(self) -> str:
        return "细腻神秘，充满未知感和期待"

    def get_cultivation_style(self) -> str:
        return "玄妙深邃，强调内在感悟和天人合一"
