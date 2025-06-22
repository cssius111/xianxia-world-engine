"""
HTML输出模块
用于生成HTML格式的游戏日志和报告
"""

import os
from datetime import datetime
from typing import Dict, List, Optional


class HtmlGameLogger:
    """HTML游戏日志记录器"""
    
    def __init__(self, output_dir: str = "logs/html"):
        self.output_dir = output_dir
        self.current_session = None
        self.logs: List[Dict] = []
        self.template = self._get_template()
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
    
    def _get_template(self) -> str:
        """获取HTML模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>修仙世界引擎 - 游戏日志</title>
    <style>
        body {
            font-family: "Microsoft YaHei", Arial, sans-serif;
            background-color: #1a1a1a;
            color: #e0e0e0;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: linear-gradient(135deg, #2c3e50, #34495e);
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .log-entry {
            background-color: #2a2a2a;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
            transition: all 0.3s ease;
        }
        .log-entry:hover {
            transform: translateX(5px);
            box-shadow: 0 2px 5px rgba(52, 152, 219, 0.3);
        }
        .timestamp {
            color: #95a5a6;
            font-size: 0.9em;
        }
        .log-type {
            display: inline-block;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 0.85em;
            margin-right: 10px;
        }
        .type-info { background-color: #3498db; }
        .type-combat { background-color: #e74c3c; }
        .type-cultivation { background-color: #f39c12; }
        .type-quest { background-color: #2ecc71; }
        .type-system { background-color: #9b59b6; }
        .log-content {
            margin-top: 10px;
            line-height: 1.6;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }
        .stat-card {
            background-color: #2a2a2a;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
        }
        .stat-value {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
        }
        .stat-label {
            color: #95a5a6;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>修仙世界引擎 - 游戏日志</h1>
            <p>会话开始时间: {session_start}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{total_logs}</div>
                <div class="stat-label">总日志数</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{combat_logs}</div>
                <div class="stat-label">战斗日志</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{cultivation_logs}</div>
                <div class="stat-label">修炼日志</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{quest_logs}</div>
                <div class="stat-label">任务日志</div>
            </div>
        </div>
        
        <div class="logs">
            {log_entries}
        </div>
    </div>
</body>
</html>
        """
    
    def start_session(self, session_name: Optional[str] = None):
        """开始新会话"""
        timestamp = datetime.now()
        self.current_session = session_name or timestamp.strftime("%Y%m%d_%H%M%S")
        self.logs = []
        return self.current_session
    
    def log(self, content: str, log_type: str = "info", metadata: Optional[Dict] = None):
        """记录日志"""
        log_entry = {
            "timestamp": datetime.now(),
            "type": log_type,
            "content": content,
            "metadata": metadata or {}
        }
        self.logs.append(log_entry)
    
    def log_info(self, content: str, metadata: Optional[Dict] = None):
        """记录信息日志"""
        self.log(content, "info", metadata)
    
    def log_combat(self, content: str, metadata: Optional[Dict] = None):
        """记录战斗日志"""
        self.log(content, "combat", metadata)
    
    def log_cultivation(self, content: str, metadata: Optional[Dict] = None):
        """记录修炼日志"""
        self.log(content, "cultivation", metadata)
    
    def log_quest(self, content: str, metadata: Optional[Dict] = None):
        """记录任务日志"""
        self.log(content, "quest", metadata)
    
    def log_system(self, content: str, metadata: Optional[Dict] = None):
        """记录系统日志"""
        self.log(content, "system", metadata)
    
    def _format_log_entry(self, log: Dict) -> str:
        """格式化日志条目"""
        timestamp = log["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
        log_type = log["type"]
        content = log["content"]
        
        return f'''
        <div class="log-entry">
            <div>
                <span class="log-type type-{log_type}">{log_type.upper()}</span>
                <span class="timestamp">{timestamp}</span>
            </div>
            <div class="log-content">{content}</div>
        </div>
        '''
    
    def save(self, filename: Optional[str] = None):
        """保存日志到HTML文件"""
        if not self.current_session:
            return None
        
        # 统计日志类型
        stats = {
            "total": len(self.logs),
            "combat": sum(1 for log in self.logs if log["type"] == "combat"),
            "cultivation": sum(1 for log in self.logs if log["type"] == "cultivation"),
            "quest": sum(1 for log in self.logs if log["type"] == "quest")
        }
        
        # 生成日志条目HTML
        log_entries = "\n".join(self._format_log_entry(log) for log in self.logs)
        
        # 填充模板
        html_content = self.template.format(
            session_start=self.logs[0]["timestamp"].strftime("%Y-%m-%d %H:%M:%S") if self.logs else "N/A",
            total_logs=stats["total"],
            combat_logs=stats["combat"],
            cultivation_logs=stats["cultivation"],
            quest_logs=stats["quest"],
            log_entries=log_entries
        )
        
        # 保存文件
        filename = filename or f"game_log_{self.current_session}.html"
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath
    
    def clear(self):
        """清空当前日志"""
        self.logs = []
