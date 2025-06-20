"""
XWE V2 Data Manager

Infrastructure service for managing game data files.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class DataManager:
    """
    Manages loading and caching of game data files.

    This is an infrastructure service that handles file I/O
    and data caching.
    """

    def __init__(self, data_root: Optional[Path] = None):
        if data_root is None:
            # Default to xwe_v2/data directory
            self.data_root = Path(__file__).parent.parent.parent / "data"
        else:
            self.data_root = data_root

        self._cache: Dict[str, Any] = {}

    def load_json(self, filepath: str, use_cache: bool = True) -> Dict[str, Any]:
        """Load a JSON file."""
        # Check cache first
        if use_cache and filepath in self._cache:
            return self._cache[filepath]

        full_path = self.data_root / filepath

        if not full_path.exists():
            # Try without .json extension
            full_path = self.data_root / f"{filepath}.json"

        if not full_path.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")

        with open(full_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Cache the data
        if use_cache:
            self._cache[filepath] = data

        return data

    def save_json(self, filepath: str, data: Dict[str, Any]) -> None:
        """Save data to a JSON file."""
        full_path = self.data_root / filepath

        # Ensure directory exists
        full_path.parent.mkdir(parents=True, exist_ok=True)

        with open(full_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        # Update cache
        self._cache[filepath] = data

    def clear_cache(self) -> None:
        """Clear the data cache."""
        self._cache.clear()

    def get_config(self, config_name: str) -> Dict[str, Any]:
        """Get a configuration file."""
        return self.load_json(f"config/{config_name}")

    def get_template(self, template_type: str, template_name: str) -> Dict[str, Any]:
        """Get a template file."""
        return self.load_json(f"templates/{template_type}/{template_name}")

    def list_files(self, directory: str, extension: str = ".json") -> list[str]:
        """List all files in a directory."""
        dir_path = self.data_root / directory

        if not dir_path.exists():
            return []

        files = []
        for file_path in dir_path.glob(f"*{extension}"):
            if file_path.is_file():
                files.append(file_path.stem)

        return files


# Global instance
_data_manager = DataManager()


# Compatibility functions
def load_game_data(filepath: str) -> Dict[str, Any]:
    """Load game data from file (v1 compatibility)."""
    return _data_manager.load_json(filepath)


def get_config(config_name: str) -> Dict[str, Any]:
    """Get configuration (v1 compatibility)."""
    return _data_manager.get_config(config_name)


__all__ = ["DataManager", "load_game_data", "get_config"]
