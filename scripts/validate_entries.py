#!/usr/bin/env python3
"""Validate tool entries (docs/tools/<category>/<tool>.md) against the editorial template.

Usage: python scripts/validate_entries.py [paths...]
With no arguments, validates every tool entry and the template itself.
Exit status: 0 = valid, 1 = validation errors.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
TOOLS_DIR = ROOT / "docs" / "tools"
TEMPLATE = ROOT / "templates" / "tool-entry.md"

STATUSES = ("draft", "research-complete", "documentation-reviewed", "lab-tested",
            "production-validated")
FRONT_MATTER_KEYS = ("tool", "category", "status", "last_reviewed", "tested_versions")
GLANCE_FIELDS = ("Official website", "Source repository", "Licence",
                 "Supported operating systems", "Maintenance status", "Category",
                 "Personal suitability", "Enterprise suitability", "Tested versions",
                 "Verification status", "Last reviewed")
SECTIONS = ("At a glance", "Overview", "Features and capabilities", "System requirements",
            "Installation", "Initial configuration", "Security hardening",
            "Practical usage examples", "Enterprise deployment considerations",
            "Troubleshooting", "Alternatives and related tools", "References")
OFFENSIVE_CATEGORIES = {"penetration-testing", "osint"}


def split_front_matter(text: str) -> tuple[dict, str]:
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        raise ValueError("missing YAML front matter")
    data = yaml.safe_load(m.group(1))
    if not isinstance(data, dict):
        raise ValueError("front matter is not a mapping")
    return data, m.group(2)


def validate(path: Path, *, is_template: bool = False) -> list[str]:
    errs: list[str] = []
    try:
        meta, body = split_front_matter(path.read_text(encoding="utf-8"))
    except (ValueError, yaml.YAMLError, OSError) as exc:
        return [f"{path}: {exc}"]

    for key in FRONT_MATTER_KEYS:
        if key not in meta:
            errs.append(f"{path}: front matter missing '{key}'")
    headings = re.findall(r"^## (.+?)\s*$", body, re.M)
    for s in SECTIONS:
        if s not in headings:
            errs.append(f"{path}: missing section '## {s}'")
    order = [h for h in headings if h in SECTIONS]
    if order != [s for s in SECTIONS if s in order]:
        errs.append(f"{path}: sections out of template order")
    if not re.search(r"^# \S", body, re.M):
        errs.append(f"{path}: missing '# <Tool name>' title")
    for f in GLANCE_FIELDS:
        if not re.search(rf"^\|\s*{re.escape(f)}\s*\|", body, re.M):
            errs.append(f"{path}: 'At a glance' table missing row '{f}'")
    if is_template:
        return errs

    status = meta.get("status")
    if status not in STATUSES:
        errs.append(f"{path}: status '{status}' not one of {', '.join(STATUSES)}")
    category = meta.get("category")
    if category != path.parent.name:
        errs.append(f"{path}: category '{category}' does not match directory '{path.parent.name}'")
    lr = meta.get("last_reviewed")
    if not isinstance(lr, dt.date):
        errs.append(f"{path}: last_reviewed must be an ISO date (YYYY-MM-DD)")
    elif lr > dt.date.today():
        errs.append(f"{path}: last_reviewed is in the future")
    tv = meta.get("tested_versions")
    if not isinstance(tv, list):
        errs.append(f"{path}: tested_versions must be a list")
    elif status in ("lab-tested", "production-validated") and not tv:
        errs.append(f"{path}: status '{status}' requires at least one tested version")
    if category in OFFENSIVE_CATEGORIES and "Authorised use only" not in body:
        errs.append(f"{path}: offensive-category entry requires an 'Authorised use only' warning")
    return errs


def tool_entries() -> list[Path]:
    return sorted(p for p in TOOLS_DIR.glob("*/*.md") if p.name != "index.md")


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]] or tool_entries()
    errs = [] if argv[1:] else validate(TEMPLATE, is_template=True)
    for p in targets:
        errs += validate(p)
    for e in errs:
        print(f"ERROR: {e}", file=sys.stderr)
    print(f"validate_entries: {len(targets)} entr{'y' if len(targets) == 1 else 'ies'} checked, "
          f"{len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
