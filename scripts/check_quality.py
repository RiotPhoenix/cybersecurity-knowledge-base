#!/usr/bin/env python3
"""Documentation quality checks for tool entries (automated parts of the quality gates).

Complements validate_entries.py (template structure). This script checks:

  Gate 1  structure:   placeholder text, fenced-code formatting, required subsections,
                       metadata/"At a glance" consistency, category-index and nav links.
  Gate 3  evidence:    official website and repository cited, reference subsections,
                       verification notes, testing claims consistent with the status.
  Gate 4  safety:      suspicious command patterns in code blocks, authorisation notice,
                       minimum depth of security, enterprise and troubleshooting sections.
  Review record:       every non-draft entry has a quality review row in the review log.

Gate 2 (technical accuracy) cannot be automated; it is recorded by a human reviewer in
docs/contributing/quality-review-log.md, which this script checks for completeness.

Runs offline and is deterministic. Usage:
  python scripts/check_quality.py [paths...]
Exit status: 0 = no errors (warnings allowed), 1 = errors found.

A flagged command can be accepted only with a justification placed on the line directly
before its code fence:
  <!-- quality-allow: rule-id[, rule-id] -- reason of at least ten characters -->
"""
from __future__ import annotations

import datetime as dt
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

import validate_entries as ve

ROOT = ve.ROOT
DOCS = ROOT / "docs"
REVIEW_LOG = DOCS / "contributing" / "quality-review-log.md"
MKDOCS = ROOT / "mkdocs.yml"

STATUS_LABELS = {
    "draft": "Draft",
    "research-complete": "Research complete",
    "documentation-reviewed": "Documentation reviewed",
    "lab-tested": "Lab tested",
    "production-validated": "Production validated",
}
TESTED_STATUSES = {"lab-tested", "production-validated"}
REVIEW_RESULTS = {"Pass", "Needs review", "Fail"}
REVIEW_MAX_AGE_DAYS = 365

# Text left over from the template, or obvious unfinished markers.
PLACEHOLDERS = [
    "YYYY-MM-DD", "Tool Name", "https://example.com/source", "SPDX identifier or licence name",
    "Exact versions and platforms, or", "High / Medium / Low", "Active / Maintenance only",
    "Lorem ipsum", "TODO", "TBD", "FIXME",
]

# (section, label, heading regex) — each section needs a level-3 heading matching the regex.
SUBSECTIONS = [
    ("Installation", "installation verification", r"verif"),
    ("Installation", "update procedure", r"updat|upgrad"),
    ("Practical usage examples", "personal use case", r"personal|home"),
    ("Practical usage examples", "enterprise use case", r"enterprise"),
    ("References", "official documentation", r"official documentation"),
    ("References", "installation references", r"install"),
    ("References", "security or deployment references", r"security|deployment|hardening"),
    ("References", "verification notes", r"^verification notes$"),
]
# Minimum words for sections whose absence would be a safety or usability gap.
MIN_WORDS = {
    "Security hardening": 120,
    "Enterprise deployment considerations": 120,
    "Troubleshooting": 80,
    "Installation": 120,
}


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    pattern: re.Pattern[str]


def _rx(p: str) -> re.Pattern[str]:
    return re.compile(p, re.I)


SAFETY_RULES = [
    Rule("pipe-to-shell", "downloaded script piped into a shell",
         _rx(r"\b(curl|wget)\b[^\n#]*\|\s*(sudo\s+)?(-\S+\s+)*(ba|z|da|k)?sh\b"
             r"|\b(iwr|irm|invoke-webrequest|invoke-restmethod)\b[^\n#]*\|\s*iex\b")),
    Rule("tls-verification-disabled", "TLS certificate verification disabled",
         _rx(r"\bcurl\b[^\n#]*\s(-k|--insecure)\b|--no-check-certificate|\bverify\s*=\s*false\b"
             r"|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*0|GIT_SSL_NO_VERIFY|sslverify\s*=\s*(0|false)"
             r"|--tls-verify[= ]false|PYTHONHTTPSVERIFY\s*=\s*0")),
    Rule("security-control-disabled", "firewall, SELinux, or malware protection disabled",
         _rx(r"\bsetenforce\s+0\b|SELINUX\s*=\s*disabled|\bsystemctl\s+(stop|disable|mask)\s+"
             r"(--now\s+)?firewalld\b|\bufw\s+disable\b|\biptables\s+-F\b"
             r"|\bnetsh\s+advfirewall\s+set\s+\w+\s+state\s+off\b"
             r"|Set-MpPreference\s+-DisableRealtimeMonitoring|\bspctl\s+--master-disable\b")),
    Rule("world-writable", "world-writable permissions", _rx(r"\bchmod\s+(-R\s+)?0?777\b")),
    Rule("hardcoded-credential", "literal credential in a command or configuration",
         _rx(r"(?:\b|_)(password|passwd|pass|token|secret|api[_-]?key)\b\s*[=:]\s*[\"']?"
             r"(?![<$%{])(?!(true|false)\b)[^\s\"'<>$]{4,}|\badmin:admin\b")),
    Rule("exposed-interface", "service bound to all interfaces or admin protection disabled",
         _rx(r"--listen[= ]0\.0\.0\.0\b|(?:-p|--publish)[ =]0\.0\.0\.0:"
             r"|(?:-p|--publish)[ =]\d{2,5}:\d{2,5}\b|^\s*-\s*[\"']?\d{2,5}:\d{2,5}[\"']?\s*$"
             r"|DISABLE_ADMIN_TOKEN\s*[=:]\s*[\"']?true")),
    Rule("intrusive-scan", "intrusive or destructive scan options",
         _rx(r"\bnmap\b[^\n#]*(-T5\b|--script[= ][\"']?[^\n]*\b(all|exploit|dos|brute|fuzzer|intrusive)\b)"
             r"|\bnuclei\b[^\n#]*(-itags|-include-tags)[= ]\S*\b(dos|fuzz|bruteforce)\b"
             r"|\bnuclei\b[^\n#]*\s-(dast|fuzz)\b")),
    Rule("privileged-gui", "packet-analysis GUI run as root", _rx(r"\bsudo\s+(-\S+\s+)*wireshark\b")),
]
RULE_IDS = {r.id for r in SAFETY_RULES}

FENCE_RE = re.compile(r"^(?P<indent>\s*)(?P<fence>```+|~~~+)(?P<info>[^\n`]*)$")
ALLOW_RE = re.compile(r"<!--\s*quality-allow:\s*(?P<ids>[\w\s,-]+?)\s+--\s+(?P<reason>.+?)\s*-->")
FIRST_PERSON_TEST = re.compile(
    r"\b(we|I)\s+(have\s+)?(tested|verified|confirmed|validated)\b", re.I)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)|<(https?://[^>\s]+)>")


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class CodeBlock:
    start: int                 # 1-based line number of the opening fence
    info: str
    lines: list[tuple[int, str]]
    allowed: set[str]


def sections(body: str) -> dict[str, str]:
    """Map each level-2 heading to its text (up to the next level-2 heading)."""
    parts = re.split(r"^## (.+?)\s*$", body, flags=re.M)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}


def subheadings(text: str) -> list[str]:
    return [h.strip() for h in re.findall(r"^### (.+?)\s*$", text, re.M)]


def subsection(text: str, heading_rx: str) -> str:
    parts = re.split(r"^### (.+?)\s*$", text, flags=re.M)
    for i in range(1, len(parts) - 1, 2):
        if re.search(heading_rx, parts[i].strip(), re.I):
            return parts[i + 1]
    return ""


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-z][A-Za-z'-]+", text))


def code_blocks(lines: list[str], path: Path, rep: Report) -> list[CodeBlock]:
    blocks: list[CodeBlock] = []
    open_block: CodeBlock | None = None
    fence = ""
    for n, line in enumerate(lines, 1):
        m = FENCE_RE.match(line)
        if open_block is None:
            if m:
                fence = m.group("fence")
                info = m.group("info").strip()
                allowed: set[str] = set()
                prev = next((lines[i] for i in range(n - 2, -1, -1) if lines[i].strip()), "")
                am = ALLOW_RE.search(prev)
                if am:
                    ids = {i.strip() for i in am.group("ids").split(",") if i.strip()}
                    unknown = ids - RULE_IDS
                    if unknown:
                        rep.errors.append(f"{path}:{n - 1}: unknown quality-allow rule(s) "
                                          f"{', '.join(sorted(unknown))}")
                    if len(am.group("reason")) < 10:
                        rep.errors.append(f"{path}:{n - 1}: quality-allow needs a reason")
                    else:
                        allowed = ids & RULE_IDS
                if m.group("indent"):
                    rep.errors.append(f"{path}:{n}: indented code fence (inside a list or "
                                      "admonition) does not render; start fences at column 0")
                if not info:
                    rep.errors.append(f"{path}:{n}: code block has no language "
                                      "(use bash, powershell, yaml, text, ...)")
                open_block = CodeBlock(n, info, [], allowed)
        elif m and m.group("fence").startswith(fence[0]) and len(m.group("fence")) >= len(fence) \
                and not m.group("info").strip():
            blocks.append(open_block)
            open_block = None
        else:
            open_block.lines.append((n, line))
    if open_block is not None:
        rep.errors.append(f"{path}:{open_block.start}: unclosed code block")
    return blocks


def check_safety(path: Path, blocks: list[CodeBlock], rep: Report) -> None:
    for b in blocks:
        for n, line in b.lines:
            for rule in SAFETY_RULES:
                if rule.id not in b.allowed and rule.pattern.search(line):
                    rep.errors.append(f"{path}:{n}: [{rule.id}] {rule.description}: "
                                      f"{line.strip()[:100]}")


def glance_value(body: str, field_name: str) -> str:
    m = re.search(rf"^\|\s*{re.escape(field_name)}\s*\|(.*)\|\s*$", body, re.M)
    return m.group(1).strip() if m else ""


def links(text: str) -> list[str]:
    return [a or b for a, b in LINK_RE.findall(text)]


def nav_files() -> set[str]:
    cfg = yaml.safe_load(MKDOCS.read_text(encoding="utf-8"))

    def walk(items):
        for item in items:
            if isinstance(item, str):
                yield item
            elif isinstance(item, dict):
                for v in item.values():
                    yield from (walk(v) if isinstance(v, list) else [v])
    return set(walk(cfg.get("nav", [])))


def review_rows(log: Path = REVIEW_LOG) -> dict[str, list[str]]:
    """Map entry path (relative to docs/) to the cells of its review-log row."""
    rows: dict[str, list[str]] = {}
    if not log.exists():
        return rows
    for line in log.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*\[[^\]]+\]\(\.\./(tools/[^)#]+\.md)\)\s*\|(.*)\|\s*$", line)
        if m:
            rows[m.group(1)] = [c.strip() for c in m.group(2).split("|")]
    return rows


def check_entry(path: Path, *, today: dt.date | None = None,
                nav: set[str] | None = None, reviews: dict[str, list[str]] | None = None,
                check_site_integration: bool = True) -> Report:
    rep = Report()
    today = today or dt.date.today()
    text = path.read_text(encoding="utf-8")
    try:
        meta, body = ve.split_front_matter(text)
    except (ValueError, yaml.YAMLError) as exc:
        rep.errors.append(f"{path}: {exc}")
        return rep
    status = meta.get("status")
    secs = sections(body)
    lines = text.splitlines()
    blocks = code_blocks(lines, path, rep)

    # Gate 4: command safety applies to every entry, including drafts.
    check_safety(path, blocks, rep)
    if meta.get("requires_authorisation") and "Authorised use only" not in body:
        rep.errors.append(f"{path}: requires_authorisation is true but the "
                          "'Authorised use only' warning is missing")
    if status == "draft":
        return rep

    # Gate 1: no template leftovers, consistent metadata.
    prose = re.sub(r"^(```|~~~).*?^\1", "", body, flags=re.M | re.S)
    for ph in PLACEHOLDERS:
        if re.search(rf"(?<![\w-]){re.escape(ph)}(?![\w-])", prose):
            rep.errors.append(f"{path}: placeholder text '{ph}' left in entry")
    if not glance_value(body, "Verification status").startswith(STATUS_LABELS.get(status, "?")):
        rep.errors.append(f"{path}: 'Verification status' row must start with "
                          f"'{STATUS_LABELS.get(status)}' to match status '{status}'")
    lr = meta.get("last_reviewed")
    if str(lr) not in glance_value(body, "Last reviewed"):
        rep.errors.append(f"{path}: 'Last reviewed' row does not match last_reviewed ({lr})")
    elif isinstance(lr, dt.date) and (today - lr).days > REVIEW_MAX_AGE_DAYS:
        rep.warnings.append(f"{path}: last reviewed {lr}, more than {REVIEW_MAX_AGE_DAYS} "
                            "days ago — re-check against official sources")
    for key, row in (("website", "Official website"), ("repository", "Source repository")):
        val = str(meta.get(key, ""))
        if val.startswith("https://") and val not in glance_value(body, row):
            rep.errors.append(f"{path}: '{row}' row does not contain {key} ({val})")

    for section, label, rx in SUBSECTIONS:
        if section in secs and not any(re.search(rx, h, re.I) for h in subheadings(secs[section])):
            rep.errors.append(f"{path}: '## {section}' needs a '### ...' subsection for {label}")
    for section, minimum in MIN_WORDS.items():
        if section in secs and word_count(secs[section]) < minimum:
            rep.errors.append(f"{path}: '## {section}' is too thin "
                              f"({word_count(secs[section])} words, minimum {minimum})")

    # Gate 3: sources.
    refs = secs.get("References", "")
    ref_links = links(refs)
    for key in ("website", "repository"):
        val = str(meta.get(key, ""))
        if val.startswith("https://") and not any(u.rstrip("/").startswith(val.rstrip("/"))
                                                   for u in ref_links):
            rep.errors.append(f"{path}: References must cite the {key} ({val})")
    external = [u for u in ref_links if u.startswith("http")]
    for u in external:
        if u.startswith("http://"):
            rep.errors.append(f"{path}: reference uses plain HTTP: {u}")
    if len(set(external)) < 5:
        rep.errors.append(f"{path}: References cite {len(set(external))} external sources "
                          "(minimum 5 for a non-draft entry)")
    notes = subsection(refs, r"^verification notes$")
    if notes and not re.search(r"\b\d{4}-\d{2}-\d{2}\b", notes):
        rep.errors.append(f"{path}: Verification notes must record the date sources were checked")

    tested = meta.get("tested_versions") or []
    if status not in TESTED_STATUSES:
        if tested:
            rep.errors.append(f"{path}: tested_versions must be empty for status '{status}' "
                              "(record spot checks in Verification notes instead)")
        outside_notes = refs.replace(notes, "") if notes else refs
        for name, sec_text in list(secs.items()):
            scope = outside_notes if name == "References" else sec_text
            m = FIRST_PERSON_TEST.search(scope)
            if m:
                rep.errors.append(f"{path}: testing claim '{m.group(0)}' in '## {name}' "
                                  f"is inconsistent with status '{status}'")
    else:
        evidence = subsection(refs, r"^lab evidence$")
        if not evidence or not re.search(r"\b\d{4}-\d{2}-\d{2}\b", evidence):
            rep.errors.append(f"{path}: status '{status}' requires a dated "
                              "'### Lab evidence' subsection under References")

    # Gate 4: authorisation context for active tools.
    if meta.get("requires_authorisation"):
        ent = secs.get("Enterprise deployment considerations", "")
        if not re.search(r"authoris|authoriz", ent, re.I) or not re.search(r"scope", ent, re.I):
            rep.errors.append(f"{path}: entries requiring authorisation must discuss "
                              "authorisation and scope in Enterprise deployment considerations")

    # Gate 1: discoverability.
    if check_site_integration:
        rel = path.resolve().relative_to(DOCS.resolve()).as_posix()
        if rel not in (nav if nav is not None else nav_files()):
            rep.errors.append(f"{path}: not listed in mkdocs.yml nav")
        index = path.parent / "index.md"
        if not index.exists() or f"({path.name})" not in index.read_text(encoding="utf-8"):
            rep.errors.append(f"{path}: not linked from its category index ({index.name})")
        row = (reviews if reviews is not None else review_rows()).get(rel)
        if row is None:
            rep.errors.append(f"{path}: no quality review record in "
                              f"{REVIEW_LOG.relative_to(ROOT)}")
        else:
            check_review_row(path, meta, row, rep)
    return rep


def check_review_row(path: Path, meta: dict, row: list[str], rep: Report) -> None:
    """Row cells: status | gate 1 | gate 2 | gate 3 | gate 4 | reviewed | notes."""
    if len(row) < 6:
        rep.errors.append(f"{path}: review-log row needs status, four gate results and a date")
        return
    status, gates, reviewed = row[0], row[1:5], row[5]
    if status.strip("`") != meta.get("status"):
        rep.errors.append(f"{path}: review-log status '{status}' differs from entry status")
    for i, g in enumerate(gates, 1):
        if g not in REVIEW_RESULTS:
            rep.errors.append(f"{path}: review-log gate {i} result '{g}' must be one of "
                              f"{', '.join(sorted(REVIEW_RESULTS))}")
        elif g == "Fail":
            rep.errors.append(f"{path}: gate {i} recorded as Fail — a failed entry must be "
                              "corrected or returned to draft")
    if reviewed != str(meta.get("last_reviewed")):
        rep.errors.append(f"{path}: review-log date {reviewed} differs from last_reviewed")


def main(argv: list[str]) -> int:
    targets = [Path(a) for a in argv[1:]] or ve.tool_entries()
    nav, reviews = nav_files(), review_rows()
    errors: list[str] = []
    warnings: list[str] = []
    for p in targets:
        r = check_entry(p, nav=nav, reviews=reviews)
        errors += r.errors
        warnings += r.warnings
    for w in warnings:
        print(f"WARNING: {w}", file=sys.stderr)
    for e in errors:
        print(f"ERROR: {e}", file=sys.stderr)
    print(f"check_quality: {len(targets)} entr{'y' if len(targets) == 1 else 'ies'} checked, "
          f"{len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
