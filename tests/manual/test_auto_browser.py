#!/usr/bin/env python3
"""Test automatic browser opening via ``run.py``."""

import sys
import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

RUN_PATH = PROJECT_ROOT / "scripts" / "run.py"


def _load_run_module():
    spec = importlib.util.spec_from_file_location("run_script", RUN_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore
    return module


class DummyApp:
    def run(self, host: str, port: int, debug: bool) -> None:  # pragma: no cover - dummy
        self.host = host
        self.port = port
        self.debug = debug


def test_open_browser(monkeypatch, capsys):
    run = _load_run_module()
    opened = []
    monkeypatch.setattr(run, "create_app", lambda: DummyApp())
    monkeypatch.setattr(run.threading, "Thread", lambda target, daemon=True: type("T", (), {"start": lambda self: target()})())
    monkeypatch.setattr(run, "sleep", lambda s: None)
    monkeypatch.setattr(run.webbrowser, "open", lambda url: opened.append(url))
    monkeypatch.setattr(sys, "argv", ["run.py"])
    run.main()
    assert opened == ["http://127.0.0.1:5001/"]
    captured = capsys.readouterr().out
    assert "已在浏览器打开" in captured


def test_no_browser_option(monkeypatch, capsys):
    run = _load_run_module()
    opened = []
    monkeypatch.setattr(run, "create_app", lambda: DummyApp())
    monkeypatch.setattr(run.threading, "Thread", lambda target, daemon=True: type("T", (), {"start": lambda self: target()})())
    monkeypatch.setattr(run, "sleep", lambda s: None)
    monkeypatch.setattr(run.webbrowser, "open", lambda url: opened.append(url))
    monkeypatch.setattr(sys, "argv", ["run.py", "--no-browser"])
    run.main()
    assert opened == []
    captured = capsys.readouterr().out
    assert "请手动打开" in captured
