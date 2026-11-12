#!/usr/bin/env python3
"""Validate lab evidence records (docs/lab-evidence/*.md) and the lab evidence template.

A lab evidence record documents one actual execution of a documented procedure. Tool entries
at status `lab-tested` or `production-validated` must link to at least one valid record
(enforced by check_quality.py, which uses this module).

Checks per record:
  - front matter: every required key, valid outcome and environment type, a real test date
    that is not in the future, `sanitised: true`, and an `entry` that exists and names the
    same tool;
  - every required section, in template order, with content, and no template placeholders;
  - privacy: no private (RFC 1918) or link-local IPv4 addresses, e-mail addresses, MAC
    addresses outside the documentation range, or private-looking hostnames;
  - discoverability: the record is linked from docs/lab-evidence/index.md.

Runs offline and is deterministic. Usage:
  python scripts/check_lab_evidence.py [records...]
Exit status: 0 = valid, 1 = errors found.
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from pathlib import Path

import yaml

import validate_entries as ve

ROOT = ve.ROOT
DOCS = ROOT / "docs"
LAB_DIR = DOCS / "lab-evidence"
TEMPLATE = ROOT / "templates" / "lab-evidence.md"

RECORD_KEYS = ("record_type", "tool", "tool_version", "entry", "test_date", "environment_type",
               "operating_system", "installation_method", "outcome", "tester", "sanitised")
RECORD_SECTIONS = ("Environment", "Hardware or virtual resources", "Installation method",
                   "Configuration summary", "Test objective", "Test procedure",
                   "Expected result", "Actual observed result", "Outcome",
                   "Deviations from the documented procedure", "Troubleshooting performed",
                   "Known limitations", "Supporting evidence")
OUTCOMES = ("pass", "fail", "partial")
SUPPORTING_OUTCOMES = {"pass", "partial"}
ENVIRONMENT_TYPES = ("lab", "production")
PLACEHOLDERS = ("Tool Name", "YYYY-MM-DD", "<category>", "<tool-slug>", "TODO", "TBD", "FIXME",
                "GitHub handle, or anonymous")

# Private data that must not appear in a published record. Documentation ranges (RFC 5737,
# RFC 3849, RFC 7042) and reserved names (.example, .test, .invalid) are allowed.
PRIVACY_RULES = (
    ("private IPv4 address",
     re.compile(r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168|169\.254)\.\d{1,3}\.\d{1,3}\b")),
    ("e-mail address", re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b")),
    ("MAC address outside the documentation range",
     re.compile(r"\b(?!00[:-]00[:-]5e[:-]00[:-]53)(?:[0-9a-f]{2}[:-]){5}[0-9a-f]{2}\b", re.I)),
    ("private-looking hostname",
     re.compile(r"\b[\w-]+\.(?:lan|local|localdomain|home|internal|corp|intranet)\b", re.I)),
)


def split(path: Path) -> tuple[dict, str]:
    return ve.split_front_matter(path.read_text(encoding="utf-8"))


def sections(body: str) -> dict[str, str]:
    parts = re.split(r"^## (.+?)\s*$", body, flags=re.M)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def check_structure(path: Path, meta: dict, body: str) -> list[str]:
    errs = [f"{path}: front matter missing '{k}'" for k in RECORD_KEYS if k not in meta]
    headings = re.findall(r"^## (.+?)\s*$", body, re.M)
    for s in RECORD_SECTIONS:
        if s not in headings:
            errs.append(f"{path}: missing section '## {s}'")
    order = [h for h in headings if h in RECORD_SECTIONS]
    if order != [s for s in RECORD_SECTIONS if s in order]:
        errs.append(f"{path}: sections out of template order")
    if not re.search(r"^# \S", body, re.M):
        errs.append(f"{path}: missing '# Lab evidence: ...' title")
    return errs


def validate_template(path: Path = TEMPLATE) -> list[str]:
    try:
        meta, body = split(path)
    except (ValueError, yaml.YAMLError, OSError) as exc:
        return [f"{path}: {exc}"]
    return check_structure(path, meta, body)


def validate_record(path: Path, *, today: dt.date | None = None, docs_root: Path = DOCS,
                    index: Path | None = None) -> list[str]:
    today = today or dt.date.today()
    try:
        meta, body = split(path)
    except (ValueError, yaml.YAMLError, OSError) as exc:
        return [f"{path}: {exc}"]
    errs = check_structure(path, meta, body)

    if meta.get("record_type") != "lab-evidence":
        errs.append(f"{path}: record_type must be 'lab-evidence'")
    if meta.get("outcome") not in OUTCOMES:
        errs.append(f"{path}: outcome '{meta.get('outcome')}' must be one of {', '.join(OUTCOMES)}")
    if meta.get("environment_type") not in ENVIRONMENT_TYPES:
        errs.append(f"{path}: environment_type must be one of {', '.join(ENVIRONMENT_TYPES)}")
    td = meta.get("test_date")
    if not isinstance(td, dt.date):
        errs.append(f"{path}: test_date must be an ISO date (YYYY-MM-DD)")
    elif td > today:
        errs.append(f"{path}: test_date is in the future")
    if meta.get("sanitised") is not True:
        errs.append(f"{path}: sanitised must be true; remove private details before publishing")
    for key in ("tool", "tool_version", "operating_system", "installation_method"):
        if key in meta and not str(meta.get(key) or "").strip():
            errs.append(f"{path}: '{key}' must not be empty")

    entry = str(meta.get("entry", ""))
    entry_path = docs_root / entry
    if entry and not entry_path.is_file():
        errs.append(f"{path}: entry '{entry}' does not exist")
    elif entry:
        try:
            entry_meta, _ = ve.split_front_matter(entry_path.read_text(encoding="utf-8"))
            if entry_meta.get("tool") != meta.get("tool"):
                errs.append(f"{path}: tool '{meta.get('tool')}' does not match the entry's "
                            f"tool '{entry_meta.get('tool')}'")
        except (ValueError, yaml.YAMLError) as exc:
            errs.append(f"{path}: entry '{entry}' unreadable: {exc}")

    secs = sections(body)
    for name in RECORD_SECTIONS:
        if name in secs and not re.search(r"[A-Za-z0-9]", secs[name]):
            errs.append(f"{path}: section '## {name}' is empty")
    if "Outcome" in secs and meta.get("outcome") in OUTCOMES and \
            not re.search(rf"\b{meta['outcome']}\b", secs["Outcome"], re.I):
        errs.append(f"{path}: '## Outcome' must state the recorded outcome "
                    f"'{meta.get('outcome')}'")

    text = path.read_text(encoding="utf-8")
    for ph in PLACEHOLDERS:
        if ph in text:
            errs.append(f"{path}: template placeholder '{ph}' left in record")
    for n, line in enumerate(text.splitlines(), 1):
        for label, rx in PRIVACY_RULES:
            m = rx.search(line)
            if m:
                errs.append(f"{path}:{n}: {label} '{m.group(0)}': use documentation values")

    idx = index if index is not None else path.parent / "index.md"
    if idx.exists() and f"({path.name})" not in idx.read_text(encoding="utf-8"):
        errs.append(f"{path}: not linked from {idx.name}")
    elif not idx.exists():
        errs.append(f"{path}: missing record index {idx}")
    return errs


def records(lab_dir: Path = LAB_DIR) -> list[Path]:
    return sorted(p for p in lab_dir.glob("*.md") if p.name != "index.md") if lab_dir.is_dir() else []


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]] or records()
    errs = [] if argv[1:] else validate_template()
    for p in targets:
        errs += validate_record(p)
    for e in errs:
        print(f"ERROR: {e}", file=sys.stderr)
    print(f"check_lab_evidence: template and {len(targets)} record(s) checked, "
          f"{len(errs)} error(s)")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
