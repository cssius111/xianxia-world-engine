"""
确认机制管理器 - 处理需要用户确认的操作
"""

from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass, field
import uuid


@dataclass
class PendingConfirmation:
    """待确认的操作"""
    id: str
    action: str
    description: str
    callback: Callable
    data: Dict[str, Any] = field(default_factory=dict)


class ConfirmationManager:
    """确认机制管理器"""
    
    def __init__(self) -> None:
        self.pending_confirmations: Dict[str, PendingConfirmation] = {}
    
    def request_confirmation(
        self, 
        action: str, 
        description: str,
        callback: Callable,
        data: Optional[Dict[str, Any]] = None
    ) -> str:
        """请求用户确认操作"""
        confirmation_id = str(uuid.uuid4())[:8]
        
        self.pending_confirmations[confirmation_id] = PendingConfirmation(
            id=confirmation_id,
            action=action,
            description=description,
            callback=callback,
            data=data or {}
        )
        
        return confirmation_id
    
    def confirm(self, confirmation_id: str, confirmed: bool = True) -> bool:
        """确认或取消操作"""
        if confirmation_id not in self.pending_confirmations:
            return False
        
        confirmation = self.pending_confirmations.pop(confirmation_id)
        
        if confirmed:
            try:
                confirmation.callback(confirmation.data)
                return True
            except Exception as e:
                print(f"确认操作执行失败: {e}")
                return False
        
        return True
    
    def get_pending_confirmations(self) -> Dict[str, PendingConfirmation]:
        """获取所有待确认操作"""
        return self.pending_confirmations.copy()


# 全局确认管理器实例
confirmation_manager = ConfirmationManager()
