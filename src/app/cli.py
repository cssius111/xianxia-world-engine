"""CLI helpers for running the Flask app."""

from __future__ import annotations

import os
from pathlib import Path

from . import create_app, command_router


def main() -> None:
    app = create_app()
    port = int(os.getenv("PORT", 5001))
    debug = os.getenv("DEBUG", "true").lower() == "true"

    print("=" * 60)
    print("🎮 修仙世界引擎")
    print("=" * 60)
    print(f"🌐 访问地址: http://localhost:{port}")
    print(f"🔧 调试模式: {'开启' if debug else '关闭'}")
    print(f"📝 日志目录: {Path('logs').absolute()}")
    print(f"💾 存档目录: {Path('saves').absolute()}")
    if hasattr(command_router, 'use_nlp') and command_router.use_nlp:
        print("🤖 DeepSeek NLP: 已启用")
    else:
        print("🤖 DeepSeek NLP: 未启用（使用传统解析）")
    print("=" * 60)
    print("使用 Ctrl+C 停止服务器")
    print("=" * 60)

    app.run(host="0.0.0.0", port=port, debug=debug)


if __name__ == "__main__":  # pragma: no cover
    main()
