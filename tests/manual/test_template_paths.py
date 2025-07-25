#!/usr/bin/env python3
"""Validate template and static path configuration for HF-002."""

import sys
import os
from pathlib import Path

# Set up proper path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

import pytest


def test_template_paths() -> None:
    """Ensure template and static paths exist and templates load correctly."""
    from src.xwe.server.app_factory import create_app

    app = create_app()

    template_path = Path(app.template_folder)
    static_path = Path(app.static_folder)

    assert template_path.exists()
    assert static_path.exists()

    main_template = template_path / "game.html"
    intro_template = template_path / "intro.html"
    base_template = template_path / "base.html"

    assert main_template.exists()
    assert intro_template.exists()
    assert base_template.exists()

    css_dir = static_path / "css"
    js_dir = static_path / "js"

    assert css_dir.exists()
    assert js_dir.exists()

    with app.app_context():
        try:
            app.jinja_env.get_template("base.html")
        except Exception as exc:
            pytest.fail(f"Template loading failed: {exc}")

def test_render_template() -> None:
    """Test that templates can be rendered without ``TemplateNotFound``."""

    from src.xwe.server.app_factory import create_app

    app = create_app()

    with app.app_context():
        try:
            app.jinja_env.get_template("base.html")
        except Exception as exc:
            pytest.fail(f"Template rendering failed: {exc}")

if __name__ == "__main__":
    import sys
    success1 = test_template_paths()
    success2 = test_render_template()

    if success1 is None and success2 is None:
        print("\n🚀 HF-002 verification: ALL PASSED")
        sys.exit(0)
    else:
        print("\n⚠️  HF-002 verification: SOME TESTS FAILED")
        sys.exit(1)
