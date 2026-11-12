#!/usr/bin/env python3
"""Offline scan for credentials and secrets in repository files.

Usage:
  python scripts/scan_secrets.py            scan tracked + untracked (non-ignored) files
  python scripts/scan_secrets.py --staged   scan only content staged for commit

Matched values are never printed. Exit status: 0 = clean, 1 = findings, 2 = scan error.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP |ENCRYPTED )?PRIVATE KEY(?: BLOCK)?-----")),
    ("GitHub token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b")),
    ("GitHub fine-grained token", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{50,}\b")),
    ("AWS access key ID", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("Google API key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("Slack token", re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b")),
    ("Stripe live key", re.compile(r"\b[rs]k_live_[0-9A-Za-z]{16,}\b")),
    ("generic sk- API key", re.compile(r"\bsk-[A-Za-z0-9_-]{32,}\b")),
    ("JSON web token", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
    ("credential-bearing URL", re.compile(r"\b[a-z][a-z0-9+.-]*://[^/\s:@<>]+:[^/\s@<>]+@[^\s/]+", re.I)),
    ("hard-coded password assignment",
     re.compile(r"""(?i)\b(?:password|passwd|secret|api[_-]?key|token)\b\s*[:=]\s*["'][^"'\s<>{}$]{8,}["']""")),
]
SENSITIVE_FILENAMES = re.compile(r"(^|/)(\.env(\..+)?|id_(rsa|dsa|ecdsa|ed25519)|.*\.(pem|key|p12|pfx|kdbx))$")
ALLOWED_FILENAMES = {".env.example"}
# Placeholders that are explicitly fake and safe in documentation.
PLACEHOLDER = re.compile(r"(?i)(example|placeholder|your[_-]|<[^>]+>|changeme|x{6,}|\*{4,})")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                          check=True).stdout


def scan_text(name: str, text: str) -> list[str]:
    findings = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for label, rx in PATTERNS:
            m = rx.search(line)
            if m and not PLACEHOLDER.search(m.group(0)):
                findings.append(f"{name}:{lineno}: possible {label} (value redacted)")
    return findings


def main(argv: list[str]) -> int:
    staged = "--staged" in argv
    findings: list[str] = []
    try:
        if staged:
            names = git("diff", "--cached", "--name-only", "--diff-filter=ACMR").split()
            contents = {n: git("show", f":{n}") for n in names}
        else:
            names = git("ls-files", "-co", "--exclude-standard").split()
            contents = {}
            for n in names:
                p = ROOT / n
                if p.is_file():
                    try:
                        contents[n] = p.read_text(encoding="utf-8")
                    except UnicodeDecodeError:
                        contents[n] = ""   # binary: filename check only
    except (subprocess.CalledProcessError, FileNotFoundError, OSError) as exc:
        print(f"scan_secrets: ERROR — scan could not complete: {exc}", file=sys.stderr)
        return 2
    for n in names:
        if SENSITIVE_FILENAMES.search(n) and Path(n).name not in ALLOWED_FILENAMES:
            findings.append(f"{n}: sensitive filename should not be committed")
    for n, text in contents.items():
        if n == "scripts/scan_secrets.py":
            continue   # contains the detection patterns themselves
        findings += scan_text(n, text)
    for f in findings:
        print(f"FINDING: {f}", file=sys.stderr)
    print(f"scan_secrets: {len(names)} files scanned, {len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
