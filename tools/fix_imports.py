import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Patterns mapping old import forms to new absolute imports
REPLACEMENTS = {
    r'^from\s+create_enhanced_game\s+import\s+': 'from xwe.features.create_enhanced_game import ',
    r'^from\s+AlPersonalization\s+import\s+': 'from xwe.features.ai_personalization import ',
    r'^from\s+CommunitySystem\s+import\s+': 'from xwe.features.community_system import ',
    r'^from\s+TechnicalOps\s+import\s+': 'from xwe.features.technical_ops import ',
}

EXCLUDE_DIRS = {'.git', '__pycache__', 'archive', '_archive'}


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & EXCLUDE_DIRS)


def fix_file(path: Path) -> bool:
    text = path.read_text()
    original = text
    for pattern, replacement in REPLACEMENTS.items():
        text = re.sub(pattern, replacement, text, flags=re.MULTILINE)
    if text != original:
        path.write_text(text)
        return True
    return False


def main() -> None:
    changed = []
    for py in PROJECT_ROOT.rglob('*.py'):
        if should_skip(py):
            continue
        if fix_file(py):
            changed.append(py)
    if changed:
        print('Updated imports in:')
        for path in changed:
            print(' -', path.relative_to(PROJECT_ROOT))
    else:
        print('No import statements updated.')


if __name__ == '__main__':
    main()
