"""
XWE V2 Configuration and Feature Flags

Controls the gradual migration from v1 to v2.
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseSettings, Field

class MigrationPhase(str, Enum):
    """Current migration phase."""
    PHASE_1_FOUNDATION = "phase_1"
    PHASE_2_SERVICES = "phase_2"
    PHASE_3_DATA = "phase_3"
    PHASE_4_DEPRECATION = "phase_4"

class FeatureFlags(BaseSettings):
    """
    Feature flags for controlling v1/v2 behavior.
    
    Set environment variables to override defaults:
    - XWE_USE_V2=true
    - XWE_V2_IMPORTS=true
    - XWE_V2_SERVICES=false
    """
    
    # Global v2 switch
    use_v2: bool = Field(default=False, env="XWE_USE_V2")
    
    # Phase 1 flags
    v2_imports: bool = Field(default=False, env="XWE_V2_IMPORTS")
    v2_domain_models: bool = Field(default=False, env="XWE_V2_DOMAIN_MODELS")
    strict_mypy: bool = Field(default=False, env="XWE_STRICT_MYPY")
    
    # Phase 2 flags  
    v2_services: bool = Field(default=False, env="XWE_V2_SERVICES")
    v2_repositories: bool = Field(default=False, env="XWE_V2_REPOSITORIES")
    v2_event_bus: bool = Field(default=False, env="XWE_V2_EVENT_BUS")
    
    # Phase 3 flags
    v2_data_layer: bool = Field(default=False, env="XWE_V2_DATA_LAYER")
    v2_migrations: bool = Field(default=False, env="XWE_V2_MIGRATIONS")
    
    # Phase 4 flags
    deprecate_v1: bool = Field(default=False, env="XWE_DEPRECATE_V1")
    
    # Current phase
    current_phase: MigrationPhase = Field(
        default=MigrationPhase.PHASE_1_FOUNDATION,
        env="XWE_MIGRATION_PHASE"
    )
    
    # Monitoring
    enable_telemetry: bool = Field(default=False, env="XWE_TELEMETRY")
    log_v1_usage: bool = Field(default=True, env="XWE_LOG_V1_USAGE")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

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
        MigrationPhase.PHASE_1_FOUNDATION: [
            "v2_imports", "v2_domain_models", "strict_mypy"
        ],
        MigrationPhase.PHASE_2_SERVICES: [
            "v2_services", "v2_repositories", "v2_event_bus"
        ],
        MigrationPhase.PHASE_3_DATA: [
            "v2_data_layer", "v2_migrations"
        ],
        MigrationPhase.PHASE_4_DEPRECATION: [
            "deprecate_v1"
        ]
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
