#!/usr/bin/env python3
"""
Archive Legacy Files Script

This script moves all backup files, .bak files, and deprecated code
to a structured archive directory with timestamps.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

# Color codes for terminal output
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


def get_files_to_archive(root_dir: Path) -> Tuple[List[Path], List[Path]]:
    """Find all files that should be archived."""
    backup_files = []
    backup_dirs = []

    patterns = {
        "files": ["*.bak", "*.backup", "*.old", "*~"],
        "dirs": ["backup_*", "_archive", "_old", "deprecated"],
    }

    for root, dirs, files in os.walk(root_dir):
        root_path = Path(root)

        # Skip already archived content and v2
        if "archive" in root_path.parts or "xwe_v2" in root_path.parts:
            continue

        # Check files
        for file in files:
            for pattern in patterns["files"]:
                if Path(file).match(pattern):
                    backup_files.append(root_path / file)

        # Check directories
        for dir_name in dirs[:]:  # Use slice to modify during iteration
            for pattern in patterns["dirs"]:
                if Path(dir_name).match(pattern):
                    backup_dirs.append(root_path / dir_name)
                    dirs.remove(dir_name)  # Don't descend into backup dirs

    return backup_files, backup_dirs


def create_archive_structure(root_dir: Path) -> Path:
    """Create the archive directory structure."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_base = root_dir / "archive" / "legacy_2025" / f"archived_{timestamp}"

    subdirs = ["backup_files", "backup_directories", "bak_files", "deprecated_code"]

    for subdir in subdirs:
        (archive_base / subdir).mkdir(parents=True, exist_ok=True)

    return archive_base


def categorize_file(file_path: Path) -> str:
    """Determine which archive subdirectory a file belongs to."""
    if file_path.suffix == ".bak":
        return "bak_files"
    elif "backup" in file_path.name.lower():
        return "backup_files"
    elif "deprecated" in str(file_path).lower():
        return "deprecated_code"
    else:
        return "backup_files"


def archive_files(root_dir: Path, dry_run: bool = False):
    """Main archiving function."""
    print(f"{YELLOW}Scanning for files to archive...{RESET}")

    backup_files, backup_dirs = get_files_to_archive(root_dir)

    total_items = len(backup_files) + len(backup_dirs)
    if total_items == 0:
        print(f"{GREEN}No files found to archive!{RESET}")
        return

    print(f"Found {len(backup_files)} files and {len(backup_dirs)} directories to archive")

    if dry_run:
        print(f"\n{YELLOW}DRY RUN - No files will be moved{RESET}")
        print("\nFiles to archive:")
        for f in backup_files[:10]:  # Show first 10
            print(f"  - {f.relative_to(root_dir)}")
        if len(backup_files) > 10:
            print(f"  ... and {len(backup_files) - 10} more files")

        print("\nDirectories to archive:")
        for d in backup_dirs[:5]:  # Show first 5
            print(f"  - {d.relative_to(root_dir)}")
        if len(backup_dirs) > 5:
            print(f"  ... and {len(backup_dirs) - 5} more directories")
        return

    # Create archive structure
    archive_base = create_archive_structure(root_dir)
    print(f"\n{GREEN}Created archive at: {archive_base.relative_to(root_dir)}{RESET}")

    # Archive files
    print("\nArchiving files...")
    for i, file_path in enumerate(backup_files, 1):
        category = categorize_file(file_path)
        dest_dir = archive_base / category
        dest_path = dest_dir / file_path.relative_to(root_dir)

        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(file_path), str(dest_path))

        if i % 10 == 0:
            print(f"  Archived {i}/{len(backup_files)} files...")

    # Archive directories
    print("\nArchiving directories...")
    for i, dir_path in enumerate(backup_dirs, 1):
        dest_path = archive_base / "backup_directories" / dir_path.relative_to(root_dir)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(dir_path), str(dest_path))
        print(f"  Archived {dir_path.name}")

    # Create summary
    summary_path = archive_base / "ARCHIVE_SUMMARY.txt"
    with open(summary_path, "w") as f:
        f.write(f"Archive created on: {datetime.now().isoformat()}\n")
        f.write(f"Total files archived: {len(backup_files)}\n")
        f.write(f"Total directories archived: {len(backup_dirs)}\n")
        f.write(f"\nOriginal locations:\n")
        f.write("\nFiles:\n")
        for file_path in backup_files:
            f.write(f"  - {file_path.relative_to(root_dir)}\n")
        f.write("\nDirectories:\n")
        for dir_path in backup_dirs:
            f.write(f"  - {dir_path.relative_to(root_dir)}\n")

    print(f"\n{GREEN}✓ Archive complete!{RESET}")
    print(f"  - Files archived: {len(backup_files)}")
    print(f"  - Directories archived: {len(backup_dirs)}")
    print(f"  - Archive location: {archive_base.relative_to(root_dir)}")
    print(f"  - Summary saved to: ARCHIVE_SUMMARY.txt")


def main():
    """Entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Archive legacy XWE files")
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be archived without moving files"
    )
    parser.add_argument(
        "--root", type=Path, default=Path.cwd(), help="Root directory of the project"
    )

    args = parser.parse_args()

    if not args.root.exists():
        print(f"{RED}Error: Root directory {args.root} does not exist{RESET}")
        return 1

    try:
        archive_files(args.root, args.dry_run)
        return 0
    except Exception as e:
        print(f"{RED}Error during archiving: {e}{RESET}")
        return 1


if __name__ == "__main__":
    exit(main())
