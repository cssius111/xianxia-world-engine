import argparse
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_DIR = PROJECT_ROOT / "templates"
KEEP_LIST_FILE = PROJECT_ROOT / "keep_list.txt"
ENTRYPOINT_FILE = PROJECT_ROOT / "entrypoints" / "run_web_ui_optimized.py"

TEMPLATE_REF_RE = re.compile(r"render_template\s*\(\s*['\"]([^'\"]+\.html)['\"]")
HTML_REF_RE = re.compile(r"{%%\s*(?:extends|include|import|from)\s+['\"]([^'\"]+\.html)['\"]")


def gather_from_python():
    keep = set()
    for py in PROJECT_ROOT.rglob("*.py"):
        if "venv" in py.parts or "site-packages" in py.parts:
            continue
        try:
            text = py.read_text(encoding="utf-8")
        except Exception:
            continue
        for match in TEMPLATE_REF_RE.findall(text):
            keep.add(match)
    return keep


def gather_from_html():
    keep = set()
    for html in TEMPLATE_DIR.rglob("*.html"):
        try:
            text = html.read_text(encoding="utf-8")
        except Exception:
            continue
        for match in HTML_REF_RE.findall(text):
            keep.add(match)
    return keep


def parse_allowed_modals():
    try:
        text = ENTRYPOINT_FILE.read_text(encoding="utf-8")
    except Exception:
        return set()
    m = re.search(r"allowed_modals\s*=\s*\[(.*?)\]", text, re.S)
    if not m:
        return set()
    names = re.findall(r"['\"]([^'\"]+)['\"]", m.group(1))
    return {f"modals/{n}.html" for n in names}


def build_keep_set():
    keep = gather_from_python()
    keep.update(gather_from_html())
    keep.update(parse_allowed_modals())
    return keep


def save_keep_list(keep):
    with KEEP_LIST_FILE.open("w", encoding="utf-8") as f:
        for name in sorted(keep):
            f.write(name + "\n")


def archive_unused(keep, apply=False):
    all_templates = {str(p.relative_to(TEMPLATE_DIR)) for p in TEMPLATE_DIR.rglob("*.html")}
    unused = sorted(all_templates - keep)
    if unused:
        print("\n未被引用的模板:")
        for t in unused:
            print(" -", t)
    else:
        print("所有模板均被引用。")
    if apply and unused:
        archive_dir = TEMPLATE_DIR / "archive"
        archive_dir.mkdir(exist_ok=True)
        for t in unused:
            src = TEMPLATE_DIR / t
            dst = archive_dir / t
            dst.parent.mkdir(parents=True, exist_ok=True)
            src.rename(dst)
        print(f"\n已移动 {len(unused)} 个模板到 {archive_dir.relative_to(PROJECT_ROOT)}")


def main():
    parser = argparse.ArgumentParser(description="归档未使用的模板")
    parser.add_argument("--apply", action="store_true", help="实际移动未使用的模板")
    args = parser.parse_args()

    keep = build_keep_set()
    save_keep_list(keep)
    print(f"已生成 keep_list.txt，共 {len(keep)} 个模板")
    archive_unused(keep, apply=args.apply)


if __name__ == "__main__":
    main()
