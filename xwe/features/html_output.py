class HtmlGameLogger:
    """简单的HTML日志和状态显示器"""

    def __init__(self, filepath: str = "game_log.html", refresh_interval: int = 2):
        self.filepath = filepath
        self.refresh_interval = refresh_interval
        self.logs = []
        self.status = {}
        self._write_html()

    def update_status(self, player):
        """更新角色状态"""
        if not player:
            return
        # 支持传入字典或拥有 attributes 属性的对象
        if isinstance(player, dict):
            self.status = {
                "名字": player.get("name", ""),
                "境界": f"{player.get('realm', '')}第{player.get('level', 1)}层",
                "气血": f"{player.get('health', 0)}/{player.get('max_health', 0)}",
                "法力": f"{player.get('mana', 0)}/{player.get('max_mana', 0)}",
                "攻击": player.get('attack', 0),
                "防御": player.get('defense', 0),
            }
        else:
            attrs = player.attributes
            self.status = {
                "名字": player.name,
                "境界": f"{attrs.realm_name} {attrs.cultivation_level}层",
                "气血": f"{int(attrs.current_health)}/{int(attrs.max_health)}",
                "灵力": f"{int(attrs.current_mana)}/{int(attrs.max_mana)}",
                "攻击": int(attrs.get('attack_power')),
                "防御": int(attrs.get('defense')),
            }
        self._write_html()

    def add_log(self, text: str, category: str = "system", is_continuation: bool = False):
        """添加日志，支持续行"""
        if is_continuation and self.logs:
            # 如果是续行，将文本添加到上一条日志
            last_text, last_category = self.logs[-1]
            self.logs[-1] = (last_text + "\n" + text, last_category)
        else:
            self.logs.append((text, category))
        
        if len(self.logs) > 200:
            self.logs = self.logs[-200:]
        self._write_html()

    def _write_html(self):
        html = self._generate_html()
        with open(self.filepath, "w", encoding="utf-8") as f:
            f.write(html)

    def _generate_html(self) -> str:
        status_lines = [f"<li><strong>{k}</strong>: {v}</li>" for k, v in self.status.items()]
        status_html = "\n".join(status_lines)
        # 将连续的多行输出组合在一起
        log_blocks = []
        for text, category in self.logs:
            # 如果文本包含换行，保留换行显示
            if '\n' in text:
                # 多行文本放在一个块内
                escaped_text = self._escape(text).replace('\n', '<br>')
                log_blocks.append(f"<div class='log-block {category}'>{escaped_text}</div>")
            else:
                # 单行文本
                log_blocks.append(f"<p class='log-line {category}'>{self._escape(text)}</p>")
        
        log_html = "\n".join(log_blocks)
        return f"""<!DOCTYPE html>
<html lang='zh'>
<head>
<meta charset='utf-8'>
<meta http-equiv='refresh' content='{self.refresh_interval}'>
<title>修仙世界日志</title>
<style>
body{{font-family:monospace;background:#f5f5f5;}}
#status{{width:250px;float:left;border-right:1px solid #ccc;padding:15px;background:#fff;box-shadow:2px 0 5px rgba(0,0,0,0.1);}}
#status ul{{list-style:none;padding:0;}}
#status li{{padding:5px 0;border-bottom:1px solid #eee;}}
#log{{margin-left:270px;height:90vh;overflow-y:scroll;padding:15px;}}
.log-line{{margin:5px 0;padding:8px 12px;background:#fff;border-radius:4px;box-shadow:0 1px 3px rgba(0,0,0,0.1);}}
.log-block{{margin:10px 0;padding:15px;background:#fff;border-radius:6px;box-shadow:0 2px 5px rgba(0,0,0,0.1);border-left:4px solid #4a90e2;}}
.system{{color:#666;font-style:italic;border-left-color:#999;}}
.combat{{color:#c00;font-weight:bold;border-left-color:#e74c3c;}}
.success{{color:#070;border-left-color:#27ae60;}}
.dialogue{{color:#039;border-left-color:#3498db;}}
.error{{color:#c00;text-decoration:underline;border-left-color:#c0392b;}}
.log-block.system{{background:#f9f9f9;}}
.log-block.combat{{background:#fff5f5;}}
.log-block.success{{background:#f0fff4;}}
.log-block.dialogue{{background:#f0f8ff;}}
.log-block br{{line-height:1.5;}}
</style>
</head>
<body>
<div id='status'>
<ul>
{status_html}
</ul>
</div>
<div id='log'>
{log_html}
</div>
<script>document.getElementById('log').scrollTop=document.getElementById('log').scrollHeight;</script>
</body>
</html>"""

    @staticmethod
    def _escape(text: str) -> str:
        return (text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;"))

