"""
Test V2 Infrastructure Setup

Verifies that the v2 module structure is properly set up and that
the import redirection works correctly.
"""

import os
import sys
import pytest
import importlib
from pathlib import Path

class TestV2Infrastructure:
    """Test the v2 infrastructure setup."""
    
    def test_v2_directory_structure_exists(self):
        """Verify all v2 directories are created."""
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        v2_root = project_root / "xwe_v2"
        
        expected_dirs = [
            "domain",
            "domain/world",
            "application",
            "infrastructure",
            "infrastructure/persistence",
            "infrastructure/ai",
            "presentation",
            "presentation/cli",
            "presentation/api", 
            "presentation/web",
            "plugins"
        ]
        
        for dir_name in expected_dirs:
            dir_path = v2_root / dir_name
            assert dir_path.exists(), f"Directory {dir_name} does not exist"
            assert dir_path.is_dir(), f"{dir_name} is not a directory"
    
    def test_v2_init_files_exist(self):
        """Verify all __init__.py files are in place."""
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        v2_root = project_root / "xwe_v2"
        
        init_locations = [
            "",  # root
            "domain",
            "application",
            "infrastructure",
            "presentation"
        ]
        
        for location in init_locations:
            init_path = v2_root / location / "__init__.py"
            assert init_path.exists(), f"__init__.py missing in {location or 'root'}"
    
    def test_v2_imports_work(self):
        """Test that v2 modules can be imported."""
        try:
            import xwe_v2
            assert hasattr(xwe_v2, '__version__')
            assert xwe_v2.__version__ == "2.0.0-alpha"
        except ImportError as e:
            pytest.fail(f"Failed to import xwe_v2: {e}")
    
    def test_config_module(self):
        """Test the configuration module."""
        try:
            from xwe_v2.config import FeatureFlags, MigrationPhase, is_v2_enabled
            
            # Test default flags
            flags = FeatureFlags()
            assert not flags.use_v2
            assert not flags.v2_imports
            assert flags.current_phase == MigrationPhase.PHASE_1_FOUNDATION
            
            # Test helper functions
            assert not is_v2_enabled("imports")
            
        except ImportError as e:
            pytest.fail(f"Failed to import config module: {e}")


class TestImportRedirection:
    """Test the import redirection mechanism."""
    
    def setup_method(self):
        """Set up test environment."""
        # Store original env var
        self.original_use_v2 = os.environ.get('XWE_USE_V2')
        # Clear module cache
        modules_to_clear = [m for m in sys.modules if m.startswith('xwe')]
        for module in modules_to_clear:
            del sys.modules[module]
    
    def teardown_method(self):
        """Restore environment."""
        if self.original_use_v2 is not None:
            os.environ['XWE_USE_V2'] = self.original_use_v2
        else:
            os.environ.pop('XWE_USE_V2', None)
            
        # Clear module cache again
        modules_to_clear = [m for m in sys.modules if m.startswith('xwe')]
        for module in modules_to_clear:
            del sys.modules[module]
    
    def test_v1_imports_by_default(self):
        """Test that v1 imports work when v2 is not enabled."""
        os.environ['XWE_USE_V2'] = 'false'
        
        # Reimport xwe
        import xwe
        assert xwe.__version__ == '2.0.0'
        
        # Should not have v2 attributes
        assert not hasattr(xwe, '_USE_V2') or not xwe._USE_V2
    
    @pytest.mark.skip(reason="Import hook implementation needs v2 modules to exist")
    def test_v2_redirection_when_enabled(self):
        """Test that imports redirect to v2 when enabled."""
        os.environ['XWE_USE_V2'] = 'true'
        
        # This would need actual v2 modules to exist
        # For now, we skip this test
        pass


class TestArchiveScript:
    """Test the archive script functionality."""
    
    def test_archive_script_exists(self):
        """Verify the archive script is created."""
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        script_path = project_root / "scripts" / "archive_legacy.py"
        
        assert script_path.exists(), "Archive script does not exist"
        assert script_path.is_file(), "Archive script is not a file"
        
        # Check it's executable (has shebang)
        with open(script_path, 'r') as f:
            first_line = f.readline()
            assert first_line.startswith('#!/usr/bin/env python'), \
                "Archive script missing shebang"


class TestProjectConfiguration:
    """Test project configuration files."""
    
    def test_pyproject_toml_exists(self):
        """Verify pyproject.toml is properly configured."""
        project_root = Path(__file__).resolve().parent.parent.parent.parent
        pyproject_path = project_root / "pyproject.toml"
        
        assert pyproject_path.exists(), "pyproject.toml does not exist"
        
        # Basic validation of content
        content = pyproject_path.read_text()
        assert "[tool.mypy]" in content, "Missing mypy configuration"
        assert "[tool.poetry]" in content, "Missing poetry configuration"
        assert 'strict = true' in content, "Mypy strict mode not enabled for v2"
        assert 'xwe_v2' in content, "v2 package not referenced in pyproject.toml"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
