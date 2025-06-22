# xwe/__init__.py
"""
仙侠世界引擎 (XianXia World Engine)

一个基于文本的仙侠世界模拟器。

This module now includes a compatibility layer for gradual migration to v2.
When XWE_USE_V2 environment variable is set, imports will be redirected to xwe_v2.
"""

__version__ = "2.0.0"
__author__ = "XWE Team"

import importlib.util
import os
import sys
import warnings
from typing import Any

# Check if we should use v2
_USE_V2 = os.getenv("XWE_USE_V2", "").lower() in ("true", "1", "yes")
_V2_AVAILABLE = False

if _USE_V2:
    try:
        # Redirect imports to v2
        import xwe_v2
        _V2_AVAILABLE = True
    except ModuleNotFoundError:
        warnings.warn(
            "XWE_USE_V2 is set but xwe_v2 is not available. Falling back to v1.",
            RuntimeWarning,
            stacklevel=2,
        )

if _V2_AVAILABLE:
    # Copy v2 attributes to this namespace
    for attr in dir(xwe_v2):
        if not attr.startswith("_"):
            globals()[attr] = getattr(xwe_v2, attr)

    # Show migration warning
    warnings.warn(
        "XWE is running in v2 mode. This is a migration path - "
        "please update your imports to use 'xwe_v2' directly.",
        DeprecationWarning,
        stacklevel=2,
    )


# Import hook for transparent v1/v2 switching
class _XWEImportHook:
    """Import hook to redirect xwe.* imports to xwe_v2.* when v2 is enabled."""

    def find_module(self, fullname: str, path=None):
        if _USE_V2 and _V2_AVAILABLE and fullname.startswith("xwe."):
            return self
        return None

    def load_module(self, fullname: str):
        if fullname in sys.modules:
            return sys.modules[fullname]

        # Convert xwe.module to xwe_v2.module
        v2_name = fullname.replace("xwe.", "xwe_v2.", 1)

        try:
            # Try to import from v2
            module = importlib.import_module(v2_name)
            sys.modules[fullname] = module

            # Log the redirection for monitoring
            if os.getenv("XWE_LOG_V1_USAGE", "true").lower() == "true":
                import logging

                logging.info(f"Redirected import: {fullname} -> {v2_name}")

            return module
        except ImportError:
            # Fall back to v1 if v2 module doesn't exist yet
            parts = fullname.split(".")
            path = None
            for part in parts[1:]:
                if path is None:
                    path = __import__(parts[0]).__path__
                else:
                    path = [
                        getattr(sys.modules[".".join(parts[:i])], part).__path__[0]
                        for i in range(2, len(parts))
                    ]

            # Import the v1 module normally
            return importlib.import_module(fullname)


# Install the import hook only when v2 is available
if _USE_V2 and _V2_AVAILABLE:
    sys.meta_path.insert(0, _XWEImportHook())
