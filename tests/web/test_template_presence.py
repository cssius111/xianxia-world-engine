"""
Tests for web template presence and Flask configuration.
"""

from pathlib import Path
import pytest
from flask import Flask

from src.xwe.server.app_factory import create_app


class TestTemplatePresence:
    """Test cases for template file presence and Flask configuration."""

    def test_main_template_exists(self):
        """Test that the main game template exists in the correct location."""
        template_path = Path("src/web/templates/game_enhanced_optimized_v2.html")
        assert template_path.exists(), \
            "主模板缺失会导致 TemplateNotFound 错误"

    def test_intro_template_exists(self):
        """Test that the intro template exists."""
        template_path = Path("src/web/templates/intro_optimized.html")
        assert template_path.exists(), \
            "角色创建模板缺失"

    def test_base_template_exists(self):
        """Test that the base template exists."""
        template_path = Path("src/web/templates/base.html")
        assert template_path.exists(), \
            "基础模板缺失"

    def test_flask_app_template_folder_configured(self):
        """Test that Flask app is configured with correct template folder."""
        app = create_app()
        
        # Verify template folder is correctly set
        expected_template_folder = str(Path("src/web/templates").resolve())
        actual_template_folder = str(Path(app.template_folder).resolve())
        
        assert actual_template_folder.endswith("src/web/templates"), \
            f"Flask 模板文件夹配置错误: {actual_template_folder}"

    def test_flask_app_static_folder_configured(self):
        """Test that Flask app is configured with correct static folder."""
        app = create_app()
        
        # Verify static folder is correctly set
        expected_static_folder = str(Path("src/web/static").resolve())
        actual_static_folder = str(Path(app.static_folder).resolve())
        
        assert actual_static_folder.endswith("src/web/static"), \
            f"Flask 静态文件夹配置错误: {actual_static_folder}"

    def test_key_static_directories_exist(self):
        """Test that key static directories exist."""
        static_base = Path("src/web/static")
        
        assert static_base.exists(), "静态文件根目录不存在"
        assert (static_base / "css").exists(), "CSS 目录不存在"
        assert (static_base / "js").exists(), "JavaScript 目录不存在"

    def test_template_can_be_rendered(self):
        """Test that templates can be successfully rendered by Flask."""
        app = create_app()
        
        with app.app_context():
            # Test that Jinja2 can find and load the template
            from flask import render_template_string
            
            # Simple test to verify template loader works
            try:
                # This will raise TemplateNotFound if template folder is wrong
                result = app.jinja_loader.get_source(
                    app.jinja_env, 'base.html'
                )
                # get_source returns a 3-tuple: (source, filename, uptodate)
                template_source = result[0]
                template_filename = result[1]
                assert template_source is not None, "无法加载基础模板"
                assert 'base.html' in template_filename, "模板文件名不正确"
            except Exception as e:
                pytest.fail(f"模板加载失败: {e}")


class TestTemplateContent:
    """Test cases for template content validation."""

    def test_main_template_has_required_blocks(self):
        """Test that the main template has required template blocks."""
        template_path = Path("src/web/templates/game_enhanced_optimized_v2.html")
        
        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            
            # Check for Jinja2 template elements (this is an extending template)
            assert 'extends' in content.lower(), "模板缺少 extends 指令"
            assert 'block' in content.lower(), "模板缺少 block 定义"
            assert 'gamecontainer' in content.lower(), "模板缺少游戏容器"
        else:
            pytest.skip("主模板文件不存在，跳过内容测试")

    def test_intro_template_has_character_creation(self):
        """Test that intro template contains character creation elements."""
        template_path = Path("src/web/templates/intro_optimized.html")
        
        if template_path.exists():
            content = template_path.read_text(encoding='utf-8')
            
            # Check for character creation related content
            assert any(keyword in content.lower() for keyword in ['character', '角色', 'name', '姓名']), \
                "角色创建模板缺少相关元素"
        else:
            pytest.skip("角色创建模板文件不存在，跳过内容测试")
