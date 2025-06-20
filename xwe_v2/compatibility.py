"""
XWE V1/V2 Compatibility Layer

This module provides compatibility between v1 and v2 code during migration.
It allows gradual migration by providing adapters and wrappers.
"""

import os
import sys
from typing import Any, Dict, Optional, Type, TypeVar

from xwe_v2.config import flags

T = TypeVar("T")


class ImportAdapter:
    """Handles dynamic imports based on feature flags."""

    def __init__(self):
        self.v1_to_v2_mapping = {
            "xwe.core.character": "xwe_v2.domain.character.models",
            "xwe.core.attributes": "xwe_v2.domain.character.attributes",
            "xwe.core.combat": "xwe_v2.domain.combat.models",
            "xwe.core.game_core": "xwe_v2.application.services.game_service",
            "xwe.services.game_service": "xwe_v2.application.services.game_service",
        }

    def get_module(self, module_name: str) -> Any:
        """Dynamically import the correct module based on flags."""
        if flags.use_v2 or flags.v2_imports:
            v2_module = self.v1_to_v2_mapping.get(module_name, module_name)
            if v2_module != module_name:
                return __import__(v2_module, fromlist=[""])

        return __import__(module_name, fromlist=[""])


class CharacterAdapter:
    """Adapter to convert between v1 and v2 Character models."""

    @staticmethod
    def v1_to_v2(v1_character: Any) -> Any:
        """Convert v1 Character to v2 format."""
        from xwe_v2.domain.character.models import Attribute, Character

        # Extract attributes
        attributes = []
        if hasattr(v1_character, "attributes") and isinstance(v1_character.attributes, dict):
            for name, value in v1_character.attributes.items():
                attributes.append(Attribute(name=name, value=value))
        elif hasattr(v1_character, "attributes"):
            # Handle CharacterAttributes object
            for attr_name in ["strength", "agility", "intelligence", "constitution"]:
                value = getattr(v1_character.attributes, attr_name, 0)
                attributes.append(Attribute(name=attr_name, value=value))

        return Character(
            name=v1_character.name,
            level=getattr(v1_character, "level", 1),
            attributes=attributes,
            faction=getattr(v1_character, "faction", None),
        )

    @staticmethod
    def v2_to_v1(v2_character: Any) -> Any:
        """Convert v2 Character to v1 format."""
        from xwe.core.attributes import CharacterAttributes
        from xwe.core.character import Character as V1Character

        # Create v1 attributes
        attrs = CharacterAttributes()
        for attribute in v2_character.attributes:
            if hasattr(attrs, attribute.name):
                setattr(attrs, attribute.name, attribute.value)

        v1_char = V1Character(
            name=v2_character.name,
            attributes=attrs,
            level=v2_character.level,
            faction=v2_character.faction or "",
        )

        return v1_char


class ServiceProxy:
    """Proxy for services that can switch between v1 and v2 implementations."""

    def __init__(self, v1_class: Type[T], v2_class: Type[T]):
        self.v1_class = v1_class
        self.v2_class = v2_class
        self._instance: Optional[T] = None

    def get_instance(self) -> T:
        """Get the appropriate service instance based on flags."""
        if self._instance is None:
            if flags.v2_services:
                self._instance = self.v2_class()
            else:
                self._instance = self.v1_class()
        return self._instance


class DataCompatibilityLayer:
    """Handles data format conversions between v1 and v2."""

    @staticmethod
    def convert_save_data(save_data: Dict[str, Any], to_version: str = "v2") -> Dict[str, Any]:
        """Convert save data between v1 and v2 formats."""
        if to_version == "v2":
            return DataCompatibilityLayer._v1_to_v2_save(save_data)
        else:
            return DataCompatibilityLayer._v2_to_v1_save(save_data)

    @staticmethod
    def _v1_to_v2_save(v1_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v1 save format to v2."""
        v2_data = {
            "version": "2.0",
            "timestamp": v1_data.get("timestamp", ""),
            "player": None,
            "world_state": v1_data.get("world_state", {}),
            "metadata": {"migrated_from": "v1", "original_version": v1_data.get("version", "1.0")},
        }

        # Convert player data
        if "player" in v1_data:
            v1_player = v1_data["player"]
            v2_data["player"] = {
                "id": v1_player.get("id", ""),
                "name": v1_player.get("name", ""),
                "level": v1_player.get("level", 1),
                "attributes": DataCompatibilityLayer._convert_attributes(
                    v1_player.get("attributes", {})
                ),
                "faction": v1_player.get("faction", ""),
            }

        return v2_data

    @staticmethod
    def _v2_to_v1_save(v2_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert v2 save format to v1."""
        v1_data = {
            "version": "1.0",
            "timestamp": v2_data.get("timestamp", ""),
            "player": None,
            "world_state": v2_data.get("world_state", {}),
        }

        # Convert player data
        if "player" in v2_data:
            v2_player = v2_data["player"]
            v1_data["player"] = {
                "id": v2_player.get("id", ""),
                "name": v2_player.get("name", ""),
                "level": v2_player.get("level", 1),
                "attributes": DataCompatibilityLayer._convert_attributes_to_dict(
                    v2_player.get("attributes", [])
                ),
                "faction": v2_player.get("faction", ""),
            }

        return v1_data

    @staticmethod
    def _convert_attributes(v1_attrs: Dict[str, Any]) -> list:
        """Convert v1 attribute dict to v2 attribute list."""
        if isinstance(v1_attrs, dict):
            return [{"name": k, "value": v} for k, v in v1_attrs.items()]
        return []

    @staticmethod
    def _convert_attributes_to_dict(v2_attrs: list) -> Dict[str, Any]:
        """Convert v2 attribute list to v1 attribute dict."""
        result = {}
        for attr in v2_attrs:
            if isinstance(attr, dict):
                result[attr["name"]] = attr["value"]
        return result


# Import hooks for compatibility
class CompatibilityImportHook:
    """Import hook that redirects v1 imports to v2 when enabled."""

    def __init__(self):
        self.adapter = ImportAdapter()

    def find_module(self, fullname: str, path=None):
        """Check if this is a module we should redirect."""
        if fullname.startswith("xwe.") and (flags.use_v2 or flags.v2_imports):
            return self
        return None

    def load_module(self, fullname: str):
        """Load the redirected module."""
        if fullname in sys.modules:
            return sys.modules[fullname]

        # Get the v2 module name
        v2_name = self.adapter.v1_to_v2_mapping.get(fullname)
        if v2_name:
            try:
                # Import the v2 module
                module = __import__(v2_name, fromlist=[""])
                # Register it under the v1 name
                sys.modules[fullname] = module
                return module
            except ImportError:
                pass

        # Fall back to normal import
        return __import__(fullname, fromlist=[""])


# Install the import hook if compatibility mode is enabled
if os.getenv("XWE_COMPATIBILITY_MODE", "false").lower() == "true":
    sys.meta_path.insert(0, CompatibilityImportHook())


# Convenience functions
def get_character_class():
    """Get the appropriate Character class based on configuration."""
    if flags.v2_domain_models:
        from xwe_v2.domain.character.models import Character

        return Character
    else:
        from xwe.core.character import Character

        return Character


def create_game_service():
    """Create the appropriate game service based on configuration."""
    if flags.v2_services:
        from xwe_v2.application.services.game_service import GameService

        return GameService()
    else:
        from xwe.services.game_service import GameService

        return GameService()


def load_save_file(filepath: str) -> Dict[str, Any]:
    """Load a save file with automatic version detection and conversion."""
    import json

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Detect version
    version = data.get("version", "1.0")
    target_version = "v2" if flags.use_v2 else "v1"

    # Convert if necessary
    if version.startswith("1.") and target_version == "v2":
        return DataCompatibilityLayer.convert_save_data(data, "v2")
    elif version.startswith("2.") and target_version == "v1":
        return DataCompatibilityLayer.convert_save_data(data, "v1")

    return data


# Decorators for gradual migration
def v2_ready(func):
    """Decorator to mark functions that are ready for v2."""
    func._v2_ready = True
    return func


def requires_v1(func):
    """Decorator to mark functions that still require v1."""
    func._requires_v1 = True
    return func
