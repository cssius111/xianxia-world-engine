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
        attrs = player.attributes
        self.status = {
            "名字": player.name,
            "境界": f"{attrs.realm_name} {attrs.cultivation_level}层",
            "生命": f"{int(attrs.current_health)}/{int(attrs.max_health)}",
            "法力": f"{int(attrs.current_mana)}/{int(attrs.max_mana)}",
            "攻击": int(attrs.get('attack_power')),
            "防御": int(attrs.get('defense')),
        }
        self._write_html()

    def add_log(self, text: str, category: str = "system"):
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
        log_lines = [
            f"<p class='log-line {c}'>{self._escape(t)}</p>" for t, c in self.logs
        ]
        log_html = "\n".join(log_lines)
        return f"""<!DOCTYPE html>
<html lang='zh'>
<head>
<meta charset='utf-8'>
<meta http-equiv='refresh' content='{self.refresh_interval}'>
<title>修仙世界日志</title>
<style>
body{{font-family:monospace;}}
#status{{width:200px;float:left;border-right:1px solid #ccc;padding:10px;}}
#log{{margin-left:220px;height:90vh;overflow-y:scroll;padding:10px;}}
.log-line{{margin:2px 0;}}
.system{{color:#666;font-style:italic;}}
.combat{{color:#c00;font-weight:bold;}}
.success{{color:#070;}}
.dialogue{{color:#039;}}
.error{{color:#c00;text-decoration:underline;}}
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

