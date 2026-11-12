#!/usr/bin/env python3
"""Check relative links and anchors in tracked Markdown files.

`mkdocs build --strict` validates links inside docs/. This script additionally covers
repository Markdown outside docs/ (README, CONTRIBUTING, templates, ADRs, .github) and
re-checks docs/ independently of MkDocs. External (http/https/mailto) links are skipped:
the check runs offline.

Exit status: 0 = all links resolve, 1 = broken links found.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {".git", ".venv", "site", "node_modules"}
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
IMG_RE = re.compile(r"!\[[^\]]*\]\(\s*<?([^)\s>]+)>?")
FENCE_RE = re.compile(r"^(```|~~~).*?^\1", re.M | re.S)
INLINE_CODE_RE = re.compile(r"`[^`\n]*`")


def markdown_files() -> list[Path]:
    try:
        out = subprocess.run(["git", "ls-files", "-co", "--exclude-standard", "*.md"],
                             cwd=ROOT, capture_output=True, text=True, check=True).stdout
        files = [ROOT / p for p in out.split()]
    except (subprocess.CalledProcessError, FileNotFoundError):
        files = list(ROOT.rglob("*.md"))
    return sorted(p for p in files
                  if p.is_file() and not SKIP_DIRS.intersection(p.relative_to(ROOT).parts))


def slugify(heading: str) -> str:
    """Approximate Python-Markdown's default toc slugify."""
    text = re.sub(r"<[^>]+>", "", heading)
    text = re.sub(r"[`*_]", "", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[-\s]+", "-", text)


def anchors(path: Path) -> set[str]:
    text = FENCE_RE.sub("", path.read_text(encoding="utf-8"))
    return {slugify(h) for h in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, re.M)}


def check(path: Path) -> list[str]:
    errors = []
    text = INLINE_CODE_RE.sub("", FENCE_RE.sub("", path.read_text(encoding="utf-8")))
    for target in LINK_RE.findall(text) + IMG_RE.findall(text):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):   # http:, https:, mailto:
            continue
        file_part, _, frag = target.partition("#")
        file_part = unquote(file_part)
        dest = path if not file_part else (path.parent / file_part).resolve()
        rel = path.relative_to(ROOT)
        if not file_part and not frag:
            continue
        if not dest.exists():
            errors.append(f"{rel}: broken link -> {target}")
            continue
        if dest.is_dir():
            if (dest / "index.md").exists():
                dest = dest / "index.md"
            else:
                continue
        if frag and dest.suffix == ".md" and frag not in anchors(dest):
            errors.append(f"{rel}: missing anchor -> {target}")
    return errors


def main() -> int:
    files = markdown_files()
    errors = [e for f in files for e in check(f)]
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    print(f"check_links: {len(files)} files checked, {len(errors)} broken link(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
