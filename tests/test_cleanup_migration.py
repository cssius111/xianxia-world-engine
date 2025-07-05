"""Test suite for Stage 1: Clean Up & Refactor"""

import pytest
import os
from pathlib import Path


def test_redundant_files_removed():
    """Verify that redundant files have been removed."""
    project_root = Path(__file__).parent.parent
    
    # Check api_fixes.py is removed (or backed up)
    assert not (project_root / "api_fixes.py").exists(), \
        "api_fixes.py should be removed"
    
    # Check deepseek/__init__.py is removed (or backed up)
    assert not (project_root / "deepseek" / "__init__.py").exists(), \
        "deepseek/__init__.py should be removed"
    
    # Verify backup files have been removed
    assert not (project_root / "api_fixes.py.backup").exists(), \
        "api_fixes.py.backup should be removed"
    assert not (project_root / "deepseek" / "__init__.py.backup").exists(), \
        "deepseek/__init__.py.backup should be removed"


def test_new_structure_exists():
    """Verify new file structure is in place."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    
    # Check AI module
    assert (src_dir / "ai" / "__init__.py").exists(), \
        "src/ai/__init__.py should exist"
    assert (src_dir / "ai" / "deepseek_client.py").exists(), \
        "src/ai/deepseek_client.py should exist"
    
    # Check API routes
    routes_dir = src_dir / "api" / "routes"
    required_routes = [
        "cultivation.py",
        "achievements.py",
        "map.py",
        "quests.py",
        "player.py",
        "intel_api.py"
    ]
    
    for route_file in required_routes:
        assert (routes_dir / route_file).exists(), \
            f"src/api/routes/{route_file} should exist"


def test_readme_updated():
    """Verify README contains migration notes."""
    project_root = Path(__file__).parent.parent
    readme_path = project_root / "README.md"
    
    assert readme_path.exists(), "README.md must exist"
    
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for architecture changes section
    assert "Recent Architecture Changes" in content, \
        "README should document architecture changes"
    assert "API Consolidation" in content, \
        "README should mention API consolidation"
    
    # Check that old instructions are removed
    assert "api_fixes.py" not in content or "Merged `api_fixes.py`" in content, \
        "README should not reference api_fixes.py except in migration notes"


def test_changelog_updated():
    """Verify CHANGELOG contains migration details."""
    project_root = Path(__file__).parent.parent
    changelog_path = project_root / "CHANGELOG.md"
    
    assert changelog_path.exists(), "CHANGELOG.md must exist"
    
    with open(changelog_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for version 0.3.0 entry
    assert "[0.3.0]" in content, \
        "CHANGELOG should have 0.3.0 entry"
    assert "Major Refactoring" in content, \
        "CHANGELOG should document refactoring"
    assert "api_fixes.py" in content, \
        "CHANGELOG should mention api_fixes.py removal"


def test_no_import_references():
    """Verify no remaining imports from deleted modules."""
    project_root = Path(__file__).parent.parent
    src_dir = project_root / "src"
    
    problematic_imports = []
    
    # Exclude backup files and test files
    exclude_patterns = ['.backup', '__pycache__', 'test_', '.pyc']
    
    for py_file in src_dir.rglob("*.py"):
        # Skip files matching exclude patterns
        if any(pattern in str(py_file) for pattern in exclude_patterns):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for imports from deleted modules
            if "from api_fixes import" in content or "import api_fixes" in content:
                problematic_imports.append((py_file, "api_fixes"))
            
            if "from deepseek import" in content and "deepseek_client" not in str(py_file):
                problematic_imports.append((py_file, "deepseek"))
        except Exception as e:
            print(f"Warning: Could not read {py_file}: {e}")
    
    assert not problematic_imports, \
        f"Found imports from deleted modules: {problematic_imports}"


def test_route_registration():
    """Verify route registration function exists and is properly structured."""
    project_root = Path(__file__).parent.parent
    routes_init = project_root / "src" / "api" / "routes" / "__init__.py"
    
    assert routes_init.exists(), "routes/__init__.py should exist"
    
    with open(routes_init, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for register_all_routes function
    assert "def register_all_routes" in content, \
        "routes/__init__.py should define register_all_routes function"
    
    # Check for blueprint imports
    required_blueprints = [
        "achievements_bp",
        "cultivation_bp",
        "map_bp",
        "player_bp",
        "quests_bp"
    ]
    
    for bp in required_blueprints:
        assert bp in content, f"routes/__init__.py should import {bp}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
