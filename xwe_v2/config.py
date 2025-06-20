"""
XWE V2 Configuration and Feature Flags

Controls the gradual migration from v1 to v2.
"""

import os
from enum import Enum
from typing import Optional


class MigrationPhase(str, Enum):
    """Current migration phase."""

    PHASE_1_FOUNDATION = "phase_1"
    PHASE_2_SERVICES = "phase_2"
    PHASE_3_DATA = "phase_3"
    PHASE_4_DEPRECATION = "phase_4"


class FeatureFlags:
    """
    Feature flags for controlling v1/v2 behavior.

    Set environment variables to override defaults:
    - XWE_USE_V2=true
    - XWE_V2_IMPORTS=true
    - XWE_V2_SERVICES=false
    """

    def __init__(self):
        # Global v2 switch
        self.use_v2 = os.getenv("XWE_USE_V2", "false").lower() == "true"

        # Phase 1 flags
        self.v2_imports = os.getenv("XWE_V2_IMPORTS", "false").lower() == "true"
        self.v2_domain_models = os.getenv("XWE_V2_DOMAIN_MODELS", "false").lower() == "true"
        self.strict_mypy = os.getenv("XWE_STRICT_MYPY", "false").lower() == "true"

        # Phase 2 flags
        self.v2_services = os.getenv("XWE_V2_SERVICES", "false").lower() == "true"
        self.v2_repositories = os.getenv("XWE_V2_REPOSITORIES", "false").lower() == "true"
        self.v2_event_bus = os.getenv("XWE_V2_EVENT_BUS", "false").lower() == "true"

        # Phase 3 flags
        self.v2_data_layer = os.getenv("XWE_V2_DATA_LAYER", "false").lower() == "true"
        self.v2_migrations = os.getenv("XWE_V2_MIGRATIONS", "false").lower() == "true"

        # Phase 4 flags
        self.deprecate_v1 = os.getenv("XWE_DEPRECATE_V1", "false").lower() == "true"

        # Current phase
        phase_str = os.getenv("XWE_MIGRATION_PHASE", MigrationPhase.PHASE_1_FOUNDATION.value)
        self.current_phase = MigrationPhase(phase_str)

        # Monitoring
        self.enable_telemetry = os.getenv("XWE_TELEMETRY", "false").lower() == "true"
        self.log_v1_usage = os.getenv("XWE_LOG_V1_USAGE", "true").lower() == "true"


# Global instance
flags = FeatureFlags()


def is_v2_enabled(component: str) -> bool:
    """Check if a specific v2 component is enabled."""
    return getattr(flags, f"v2_{component}", False) or flags.use_v2


def get_import_path(module: str) -> str:
    """Get the correct import path based on feature flags."""
    if flags.v2_imports or flags.use_v2:
        return f"xwe_v2.{module}"
    return f"xwe.{module}"


def enable_phase(phase: MigrationPhase):
    """Enable all features for a given phase."""
    phase_flags = {
        MigrationPhase.PHASE_1_FOUNDATION: ["v2_imports", "v2_domain_models", "strict_mypy"],
        MigrationPhase.PHASE_2_SERVICES: ["v2_services", "v2_repositories", "v2_event_bus"],
        MigrationPhase.PHASE_3_DATA: ["v2_data_layer", "v2_migrations"],
        MigrationPhase.PHASE_4_DEPRECATION: ["deprecate_v1"],
    }

    # Enable all flags up to and including the current phase
    for p in MigrationPhase:
        if p.value <= phase.value:
            for flag in phase_flags.get(p, []):
                setattr(flags, flag, True)
        if p == phase:
            break

    flags.current_phase = phase


# Initialize from environment
if os.getenv("XWE_MIGRATION_PHASE"):
    enable_phase(MigrationPhase(os.getenv("XWE_MIGRATION_PHASE")))
