import argparse
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Mapping of old import paths to new ones using regex
REPLACEMENTS = {
    r"^from\s+create_enhanced_game\s+import\s+": "from xwe.features.create_enhanced_game import ",
    r"^from\s+AlPersonalization\s+import\s+": "from xwe.features.ai_personalization import ",
    r"^from\s+CommunitySystem\s+import\s+": "from xwe.features.community_system import ",
    r"^from\s+TechnicalOps\s+import\s+": "from xwe.features.technical_ops import ",
    r"^from\s+xwe\s+import\s+create_enhanced_game\b": "from xwe.features.create_enhanced_game import create_enhanced_game",
    r"^from\s+xwe\s+import\s+AlPersonalization\b": "from xwe.features.ai_personalization import AIPersonalization",
}

EXCLUDE_DIRS = {".git", "__pycache__", "archive", "_archive"}


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def fix_file(path: Path, *, backup: bool = False) -> bool:
    text = path.read_text()
    original = text
    for pattern, replacement in REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    if text != original:
        if backup:
            path.with_suffix(path.suffix + ".bak").write_text(original)
        path.write_text(text)
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Fix outdated import statements")
    parser.add_argument("--backup", action="store_true", help="Keep .bak backups of modified files")
    args = parser.parse_args()

    changed = []
    for py in PROJECT_ROOT.rglob("*.py"):
        if should_skip(py):
            continue
        if fix_file(py, backup=args.backup):
            changed.append(py)

    if changed:
        print("✅ Updated imports in:")
        for path in changed:
            print(" -", path.relative_to(PROJECT_ROOT))
    else:
        print("✨ No import statements updated.")


if __name__ == "__main__":
    main()
