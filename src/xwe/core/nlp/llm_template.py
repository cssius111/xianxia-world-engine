#!/usr/bin/env python
"""
LLM集成模板 - 为后续接入DeepSeek/OpenAI做准备
"""

class LLMIntegrationTemplate:
    """LLM集成模板类"""
    
    def __init__(self, api_key=None, provider="deepseek") -> None:
        self.api_key = api_key
        self.provider = provider
        
    def parse_with_llm(self, text: str, context=None) -> dict:
        """
        使用LLM解析文本
        
        注意：返回格式必须与简单规则解析保持一致！
        """
        # TODO: 实现实际的LLM调用
        # 1. 构建prompt
        # 2. 调用API
        # 3. 解析返回结果
        # 4. 转换为标准格式
        
        # 临时返回
        return {
            "action": "unknown",
            "detail": "LLM集成待实现",
            "confidence": 0.0
        }
    
    def build_prompt(self, text: str, context=None) -> str:
        """构建LLM提示词"""
        prompt = f"""将下面的自然语言转换为游戏命令。

用户输入: {text}

可用的命令类型:
- attack: 攻击
- use_skill: 使用技能
- defend: 防御
- flee: 逃跑
- cultivate: 修炼
- status: 查看状态
- move: 移动
- explore: 探索

请返回JSON格式:
{{
    "action": "命令类型",
    "target": "目标（如果有）",
    "parameters": {{额外参数}},
    "confidence": 0.0-1.0
}}
"""
        return prompt
