"""
异步事件处理系统 - 简化版
"""
import threading
import time
from typing import Dict, Any, List, Callable, Optional
from collections import deque
import logging

logger = logging.getLogger(__name__)

class AsyncEventHandler:
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
        self.event_queue = deque()
        self.handlers: Dict[str, Callable[[Dict[str, Any]], None]] = {}
        self.running = False
        self.workers: List[threading.Thread] = []
        self._lock = threading.Lock()
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        for i in range(self.max_workers):
            worker = threading.Thread(target=self._worker_loop, daemon=True)
            worker.start()
            self.workers.append(worker)
    
    def stop(self):
        self.running = False
        for worker in self.workers:
            worker.join(timeout=1.0)
        self.workers.clear()
    
    def register_handler(self, event_type: str, handler: Callable):
        self.handlers[event_type] = handler
    
    def trigger_event_sync(self, event_type: str, data: Dict[str, Any]) -> str:
        event_id = f"{event_type}_{int(time.time() * 1000)}"
        event = {
            'id': event_id,
            'type': event_type,
            'data': data,
            'timestamp': time.time()
        }
        
        with self._lock:
            self.event_queue.append(event)
        
        return event_id
    
    def _worker_loop(self):
        while self.running:
            try:
                event = None
                with self._lock:
                    if self.event_queue:
                        event = self.event_queue.popleft()
                
                if event:
                    self._process_event(event)
                else:
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Worker error: {e}")
    
    def _process_event(self, event):
        try:
            handler = self.handlers.get(event['type'])
            if handler:
                handler(event['data'])
        except Exception as e:
            logger.error(f"Event processing error: {e}")
    
    def process_pending_events(self):
        """同步处理挂起的事件"""
        processed = 0
        while processed < 10:  # 限制单次处理数量
            event = None
            with self._lock:
                if self.event_queue:
                    event = self.event_queue.popleft()
            
            if event:
                self._process_event(event)
                processed += 1
            else:
                break

# 全局事件处理器
_global_handler = None

def get_global_event_handler():
    global _global_handler
    if _global_handler is None:
        _global_handler = AsyncEventHandler()
        _global_handler.start()
    return _global_handler
