"""Entry point wrapper for the optimized Web UI."""
import sys
from pathlib import Path

# Ensure repository root is on sys.path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from run_web_ui_optimized import app

if __name__ == "__main__":
    print("=== 修仙世界引擎 Web UI (优化版) ===")
    print("访问 http://localhost:5001 开始游戏")
    print("使用 Ctrl+C 停止服务器")
    print("=====================================")
    app.run(debug=True, host="0.0.0.0", port=5001)
