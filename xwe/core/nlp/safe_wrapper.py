#!/usr/bin/env python
"""
NLP安全包装器 - 提供降级保护
"""

from typing import Any, Dict, Optional

class SafeNLPWrapper:
    """安全的NLP包装器，防止崩溃"""
    
    def __init__(self, nlp_processor=None) -> None:
        self.nlp = nlp_processor
        
    def parse(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """安全的解析方法，带降级保护"""
        try:
            if self.nlp and hasattr(self.nlp, 'parse'):
                return self.nlp.parse(user_input, context)
            elif self.nlp and hasattr(self.nlp, 'process'):
                # 兼容旧版本
                return self.nlp.parse(user_input, context)
            else:
                raise AttributeError("NLP处理器没有parse或process方法")
                
        except Exception as e:
            print(f"【NLP警告】解析失败: {e}")
            print("【NLP降级】使用简单规则匹配...")
            
            # 降级到简单规则
            return self._simple_parse(user_input)
    
    def _simple_parse(self, text: str) -> Dict[str, Any]:
        """简单的规则解析"""
        text_lower = text.lower()
        
        # 基础规则匹配
        if any(word in text_lower for word in ['攻击', '打', '杀']):
            return {"action": "attack", "target": "敌人", "confidence": 0.5}
        elif any(word in text_lower for word in ['修炼', '打坐', '冥想']):
            return {"action": "cultivate", "confidence": 0.6}
        elif any(word in text_lower for word in ['状态', '属性', '面板']):
            return {"action": "status", "confidence": 0.7}
        elif any(word in text_lower for word in ['逃', '跑', '撤退']):
            return {"action": "flee", "confidence": 0.6}
        elif any(word in text_lower for word in ['地图', '位置', '哪里']):
            return {"action": "map", "confidence": 0.6}
        else:
            return {"action": "unknown", "detail": f"无法理解: {text}", "confidence": 0.0}
