#!/usr/bin/env python3
"""Optional, network-dependent check of external links in tool entries.

NOT part of the routine offline checks or CI: results depend on third-party servers.
Run it manually when reviewing entries, for example before raising an entry's status.

Usage: python scripts/check_external_links.py [paths...] [--timeout SECONDS]

Limitations (see docs/contributing/quality-framework.md):
- A successful response proves only that a URL answers, not that it still supports the
  claim it is cited for. Content must still be re-read by a reviewer.
- Some sites reject automated clients (HTTP 403/429) or require JavaScript; these are
  reported as "unverified", not as broken.
- Redirects are followed and reported, because a moved page often signals moved content.

Exit status: 0 = no definite failures, 1 = at least one URL returned 404/410 or failed DNS.
"""
from __future__ import annotations

import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

import validate_entries as ve

URL_RE = re.compile(r"\]\((https://[^)\s]+)\)|<(https://[^>\s]+)>")
USER_AGENT = "cybersecurity-knowledge-base-link-check/1.0"
DEFINITE_FAILURES = {404, 410}


def external_urls(text: str) -> list[str]:
    """Unique https URLs from Markdown links and autolinks, in order of appearance."""
    seen: dict[str, None] = {}
    for a, b in URL_RE.findall(text):
        seen.setdefault((a or b).split("#", 1)[0], None)
    return list(seen)


def probe(url: str, timeout: float) -> tuple[str, str]:
    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                final = resp.geturl()
                return ("ok" if final == url else "redirected", final)
        except urllib.error.HTTPError as exc:
            # Some servers answer HEAD with 404/405 while serving GET normally, so a HEAD
            # error is never conclusive: only a GET 404/410 counts as a definite failure.
            if method == "GET":
                if exc.code in DEFINITE_FAILURES:
                    return ("broken", f"HTTP {exc.code}")
                return ("unverified", f"HTTP {exc.code}")
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            if method == "GET":
                reason = getattr(exc, "reason", exc)
                kind = "broken" if "Name or service not known" in str(reason) else "unverified"
                return (kind, str(reason))
    return ("unverified", "no response")


def main(argv: list[str]) -> int:
    timeout = 15.0
    args = argv[1:]
    if "--timeout" in args:
        i = args.index("--timeout")
        timeout = float(args[i + 1])
        del args[i:i + 2]
    files = [Path(a) for a in args] or ve.tool_entries()
    broken = 0
    for f in files:
        for url in external_urls(f.read_text(encoding="utf-8")):
            state, detail = probe(url, timeout)
            broken += state == "broken"
            if state != "ok":
                print(f"{state.upper():10} {f.name}: {url} ({detail})")
    print(f"check_external_links: {len(files)} file(s), {broken} definite failure(s)")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
