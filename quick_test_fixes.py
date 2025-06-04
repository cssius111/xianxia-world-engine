#!/usr/bin/env python3
"""快速测试所有修复"""

from xwe.core.nlp.nlp_processor import NLPProcessor, NLPConfig
from xwe.core.command_parser import CommandType

# 测试NLP
config = NLPConfig(enable_llm=False)
nlp = NLPProcessor(config=config)

result = nlp.parse("修炼一年")
print(f"命令类型: {result.command_type}")
print(f"参数: {result.parameters}")

if "duration" in result.parameters:
    print(f"✅ Duration提取成功: {result.parameters['duration']}")
else:
    print("❌ Duration提取失败")

# 测试EmotionState
from xwe.npc.emotion_system import EmotionState
state = EmotionState()
print(f"\n✅ EmotionState.current_emotion: {state.current_emotion}")
