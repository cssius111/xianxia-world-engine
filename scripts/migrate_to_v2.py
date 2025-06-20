#!/usr/bin/env python3
"""
XWE V1 to V2 Migration Script

This script helps migrate code from the old xwe/ structure to the new xwe_v2/ clean architecture.
It includes:
1. Code analysis and mapping
2. Import path updates
3. Model conversions
4. Migration report generation
"""

import ast
import json
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


class ModuleMappingAnalyzer:
    """Analyzes v1 modules and suggests v2 mappings."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.v1_root = project_root / "xwe"
        self.v2_root = project_root / "xwe_v2"
        self.mappings = self._initialize_mappings()

    def _initialize_mappings(self) -> Dict[str, str]:
        """Initialize known module mappings from v1 to v2."""
        return {
            # Core -> Domain mappings
            "xwe.core.character": "xwe_v2.domain.character.models",
            "xwe.core.attributes": "xwe_v2.domain.character.attributes",
            "xwe.core.inventory": "xwe_v2.domain.inventory.models",
            "xwe.core.item_system": "xwe_v2.domain.items.models",
            "xwe.core.cultivation_system": "xwe_v2.domain.cultivation.models",
            "xwe.core.combat": "xwe_v2.domain.combat.models",
            "xwe.core.skills": "xwe_v2.domain.skills.models",
            "xwe.core.status": "xwe_v2.domain.character.status",
            # Core services -> Application layer
            "xwe.core.game_core": "xwe_v2.application.services.game_service",
            "xwe.core.command_processor": "xwe_v2.application.commands",
            "xwe.core.event_system": "xwe_v2.application.events",
            "xwe.core.data_manager": "xwe_v2.infrastructure.persistence.data_manager",
            # NPC system -> Domain + Application
            "xwe.npc.npc_manager": "xwe_v2.application.services.npc_service",
            "xwe.npc.dialogue_system": "xwe_v2.domain.npc.dialogue",
            # World system -> Domain
            "xwe.world.world_map": "xwe_v2.domain.world.map",
            "xwe.world.location_manager": "xwe_v2.domain.world.locations",
            "xwe.world.time_system": "xwe_v2.domain.world.time",
            # Features -> Plugins
            "xwe.features": "xwe_v2.plugins",
            # Services -> Infrastructure
            "xwe.services": "xwe_v2.infrastructure.services",
            # Utilities remain similar
            "xwe.utils": "xwe_v2.utils",
        }

    def analyze_imports(self, file_path: Path) -> List[Tuple[str, str]]:
        """Analyze imports in a Python file and suggest v2 replacements."""
        imports_to_update = []

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        try:
            tree = ast.parse(content)
        except SyntaxError:
            return imports_to_update

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("xwe"):
                    v2_module = self._get_v2_mapping(node.module)
                    if v2_module:
                        imports_to_update.append((node.module, v2_module))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith("xwe"):
                        v2_module = self._get_v2_mapping(alias.name)
                        if v2_module:
                            imports_to_update.append((alias.name, v2_module))

        return imports_to_update

    def _get_v2_mapping(self, v1_module: str) -> Optional[str]:
        """Get v2 mapping for a v1 module."""
        # Direct mapping
        if v1_module in self.mappings:
            return self.mappings[v1_module]

        # Try to find partial mapping
        for v1_prefix, v2_prefix in self.mappings.items():
            if v1_module.startswith(v1_prefix + "."):
                suffix = v1_module[len(v1_prefix) :]
                return v2_prefix + suffix

        # Generic mapping for unknown modules
        if v1_module.startswith("xwe."):
            return v1_module.replace("xwe.", "xwe_v2.")

        return None


class CodeMigrator:
    """Handles code migration from v1 to v2 patterns."""

    def __init__(self, analyzer: ModuleMappingAnalyzer):
        self.analyzer = analyzer
        self.migration_log = []

    def migrate_file(self, file_path: Path, dry_run: bool = False) -> Optional[Path]:
        """Migrate a single Python file to v2 patterns."""
        if not file_path.suffix == ".py":
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Update imports
        imports_to_update = self.analyzer.analyze_imports(file_path)
        for old_import, new_import in imports_to_update:
            # Update import statements
            content = re.sub(
                rf"\bfrom\s+{re.escape(old_import)}\s+import", f"from {new_import} import", content
            )
            content = re.sub(
                rf"\bimport\s+{re.escape(old_import)}\b", f"import {new_import}", content
            )

        # Update class patterns
        content = self._update_class_patterns(content)

        # Update method patterns
        content = self._update_method_patterns(content)

        if content != original_content:
            # Determine output path
            relative_path = file_path.relative_to(self.analyzer.v1_root)
            output_path = self._get_v2_output_path(relative_path)

            if not dry_run:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.migration_log.append(
                    {
                        "source": str(file_path),
                        "destination": str(output_path),
                        "imports_updated": len(imports_to_update),
                        "status": "success",
                    }
                )

                return output_path
            else:
                self.migration_log.append(
                    {
                        "source": str(file_path),
                        "destination": str(output_path),
                        "imports_updated": len(imports_to_update),
                        "status": "dry_run",
                    }
                )

        return None

    def _update_class_patterns(self, content: str) -> str:
        """Update class patterns to match v2 architecture."""
        # Example: Convert dataclasses to use proper domain models
        patterns = [
            # Update Character class references
            (r"class\s+Character\s*\(.*?\):", "class Character:"),
            # Update inheritance patterns
            (r"from\s+abc\s+import\s+ABC", "from abc import ABC, abstractmethod"),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content)

        return content

    def _update_method_patterns(self, content: str) -> str:
        """Update method patterns to match v2 conventions."""
        # Convert property methods to use v2 patterns
        patterns = [
            # Update getter/setter patterns
            (r"@property\s+def\s+(\w+)\(self\):", r"def get_\1(self):"),
            # Update async patterns
            (r"async\s+def\s+(\w+)\(", r"async def \1("),
        ]

        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)

        return content

    def _get_v2_output_path(self, relative_path: Path) -> Path:
        """Determine the v2 output path based on v1 structure."""
        parts = relative_path.parts

        if parts[0] == "core":
            # Core modules go to domain
            return self.analyzer.v2_root / "domain" / Path(*parts[1:])
        elif parts[0] == "services":
            # Services go to application/services
            return self.analyzer.v2_root / "application" / "services" / Path(*parts[1:])
        elif parts[0] == "features":
            # Features go to plugins
            return self.analyzer.v2_root / "plugins" / Path(*parts[1:])
        elif parts[0] in ["npc", "world"]:
            # These go to domain with their own subdirectories
            return self.analyzer.v2_root / "domain" / Path(*parts)
        else:
            # Default mapping
            return self.analyzer.v2_root / Path(*parts)


class DataMigrator:
    """Handles data migration from v1 to v2 formats."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.v1_data = project_root / "xwe" / "data"
        self.v2_data = project_root / "xwe_v2" / "data"

    def migrate_character_data(self, dry_run: bool = False):
        """Migrate character data to v2 format."""
        v1_char_file = self.v1_data / "character" / "character_creation.json"
        v2_char_file = self.v2_data / "character" / "templates.json"

        if not v1_char_file.exists():
            return

        with open(v1_char_file, "r", encoding="utf-8") as f:
            v1_data = json.load(f)

        # Transform to v2 format
        v2_data = self._transform_character_data(v1_data)

        if not dry_run:
            v2_char_file.parent.mkdir(parents=True, exist_ok=True)
            with open(v2_char_file, "w", encoding="utf-8") as f:
                json.dump(v2_data, f, indent=2, ensure_ascii=False)

    def _transform_character_data(self, v1_data: Dict) -> Dict:
        """Transform v1 character data to v2 format."""
        v2_data = {"version": "2.0", "templates": []}

        # Transform character templates
        if "templates" in v1_data:
            for template in v1_data["templates"]:
                v2_template = {
                    "id": template.get("id", ""),
                    "name": template.get("name", ""),
                    "type": template.get("type", "npc"),
                    "attributes": self._transform_attributes(template.get("attributes", {})),
                    "skills": template.get("skills", []),
                    "faction": template.get("faction", ""),
                }
                v2_data["templates"].append(v2_template)

        return v2_data

    def _transform_attributes(self, v1_attrs: Dict) -> List[Dict]:
        """Transform v1 attributes to v2 format."""
        v2_attrs = []

        for name, value in v1_attrs.items():
            v2_attrs.append({"name": name, "value": value})

        return v2_attrs


class MigrationReport:
    """Generates migration reports."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.report_dir = project_root / "migration_reports"
        self.report_dir.mkdir(exist_ok=True)

    def generate_report(self, migration_log: List[Dict], dry_run: bool = False):
        """Generate a comprehensive migration report."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_name = f"migration_report_{timestamp}.md"
        if dry_run:
            report_name = f"migration_preview_{timestamp}.md"

        report_path = self.report_dir / report_name

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# XWE V1 to V2 Migration Report\n\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n")
            f.write(f"Mode: {'DRY RUN' if dry_run else 'ACTUAL MIGRATION'}\n\n")

            # Summary
            f.write("## Summary\n\n")
            total_files = len(migration_log)
            successful = len([log for log in migration_log if log.get("status") == "success"])
            f.write(f"- Total files processed: {total_files}\n")
            f.write(f"- Successfully migrated: {successful}\n")
            f.write(f"- Failed: {total_files - successful}\n\n")

            # File migrations
            f.write("## File Migrations\n\n")
            for log in migration_log:
                status_icon = "✅" if log["status"] == "success" else "❌"
                f.write(f"{status_icon} `{log['source']}` → `{log['destination']}`\n")
                f.write(f"   - Imports updated: {log.get('imports_updated', 0)}\n")
                if log.get("errors"):
                    f.write(f"   - Errors: {log['errors']}\n")
                f.write("\n")

            # Next steps
            f.write("## Next Steps\n\n")
            f.write("1. Review migrated code for correctness\n")
            f.write("2. Run tests to ensure functionality\n")
            f.write("3. Update any manual references\n")
            f.write("4. Enable v2 feature flags in .env\n")

        return report_path


def main():
    """Main migration script."""
    import argparse

    parser = argparse.ArgumentParser(description="Migrate XWE from v1 to v2")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview migration without making changes"
    )
    parser.add_argument(
        "--include", nargs="+", help="Specific modules to migrate (e.g., core.character)"
    )
    parser.add_argument("--exclude", nargs="+", help="Modules to exclude from migration")
    parser.add_argument("--data-only", action="store_true", help="Only migrate data files")
    parser.add_argument("--code-only", action="store_true", help="Only migrate code files")

    args = parser.parse_args()

    # Initialize components
    project_root = Path.cwd()
    analyzer = ModuleMappingAnalyzer(project_root)
    code_migrator = CodeMigrator(analyzer)
    data_migrator = DataMigrator(project_root)
    report_generator = MigrationReport(project_root)

    print(f"{BLUE}XWE V1 to V2 Migration Tool{RESET}")
    print(f"{'='*50}\n")

    if args.dry_run:
        print(f"{YELLOW}Running in DRY RUN mode - no files will be modified{RESET}\n")

    migration_log = []

    # Migrate code
    if not args.data_only:
        print(f"{GREEN}Migrating code files...{RESET}")

        # Find all Python files in v1
        v1_files = list(analyzer.v1_root.rglob("*.py"))
        print(f"  Found {len(v1_files)} Python files in {analyzer.v1_root}")

        # Filter based on include/exclude
        if args.include:
            v1_files = [f for f in v1_files if any(inc in str(f) for inc in args.include)]
            print(f"  After include filter: {len(v1_files)} files")

        if args.exclude:
            v1_files = [f for f in v1_files if not any(exc in str(f) for exc in args.exclude)]
            print(f"  After exclude filter: {len(v1_files)} files")

        if not v1_files:
            print(f"  {YELLOW}No files to migrate!{RESET}")
        else:
            # Migrate each file
            for file_path in v1_files:
                print(f"  Processing: {file_path.relative_to(project_root)}")
                result = code_migrator.migrate_file(file_path, dry_run=args.dry_run)
                if result:
                    print(f"    → Migrated to: {result.relative_to(project_root)}")

        migration_log.extend(code_migrator.migration_log)

    # Migrate data
    if not args.code_only:
        print(f"\n{GREEN}Migrating data files...{RESET}")
        try:
            data_migrator.migrate_character_data(dry_run=args.dry_run)
            print(f"  ✅ Character data migrated")
        except Exception as e:
            print(f"  {RED}❌ Error migrating character data: {e}{RESET}")

    # Generate report
    print(f"\n{GREEN}Generating migration report...{RESET}")
    report_path = report_generator.generate_report(migration_log, dry_run=args.dry_run)
    print(f"  Report saved to: {report_path.relative_to(project_root)}")

    # Final instructions
    print(f"\n{BLUE}Migration {'Preview' if args.dry_run else 'Complete'}!{RESET}")
    if not args.dry_run:
        print(f"\nNext steps:")
        print(f"1. Review the migration report: {report_path.name}")
        print(f"2. Test the migrated code thoroughly")
        print(f"3. Enable v2 features in your .env file:")
        print(f"   XWE_USE_V2=true")
        print(f"   XWE_V2_IMPORTS=true")
        print(f"4. Run tests: pytest tests/v2/")
    else:
        print(f"\nTo perform the actual migration, run without --dry-run")


if __name__ == "__main__":
    main()
