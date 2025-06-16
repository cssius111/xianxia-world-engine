import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Patterns mapping old import forms to new absolute imports. Each tuple contains
# a regex pattern and its replacement string.
REPLACEMENTS = [
    # Standalone module imports
    (r'^from\s+create_enhanced_game\s+import\s+',
     'from xwe.features.create_enhanced_game import '),
    (r'^from\s+AlPersonalization\s+import\s+',
     'from xwe.features.ai_personalization import '),
    (r'^from\s+CommunitySystem\s+import\s+',
     'from xwe.features.community_system import '),
    (r'^from\s+TechnicalOps\s+import\s+',
     'from xwe.features.technical_ops import '),

    # Imports from the xwe package itself
    (r'^from\s+xwe\s+import\s+create_enhanced_game\b',
     'from xwe.features.create_enhanced_game import create_enhanced_game'),
    (r'^from\s+xwe\s+import\s+AlPersonalization\b',
     'from xwe.features.ai_personalization import AIPersonalization'),

    # Optional patterns for future layouts (commented out)
    # (r'^from\s+api\s+import\s+register_api\b', 'from xwe.api import register_api'),
    # (r'^from\s+routes\.core\s+import\s+', 'from xwe.routes.core import '),
]

EXCLUDE_DIRS = {'.git', '__pycache__', 'archive', '_archive'}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)


def fix_file(path: Path, *, backup: bool = False) -> bool:
    text = path.read_text()
    original = text
    for pattern, replacement in REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    if text != original:
        if backup:
            path.with_suffix(path.suffix + '.bak').write_text(original)
        path.write_text(text)
        return True
    return False


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Fix outdated import statements")
    parser.add_argument("--backup", action="store_true", help="Keep .bak backups of modified files")
    args = parser.parse_args()

    changed = []
    for py in PROJECT_ROOT.rglob('*.py'):
        if should_skip(py):
            continue
        if fix_file(py, backup=args.backup):
            changed.append(py)
    if changed:
        print('Updated imports in:')
        for path in changed:
            print(' -', path.relative_to(PROJECT_ROOT))
    else:
        print('No import statements updated.')


if __name__ == '__main__':
    main()
