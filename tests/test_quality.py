"""Regression tests for the documentation quality checks (scripts/check_quality.py)."""
import datetime as dt
import re
import shutil

import pytest

import check_external_links as cel
import check_quality as cq
import validate_entries as ve

SAMPLE = ve.ROOT / "docs/tools/network-security/wireshark.md"
TODAY = dt.date(2026, 11, 12)


@pytest.fixture
def entry(tmp_path):
    """A copy of a known-good published entry, checked without site integration."""
    d = tmp_path / "network-security"
    d.mkdir()
    p = d / "sample.md"
    shutil.copy(SAMPLE, p)
    return p


def check(p, **kw):
    kw.setdefault("today", TODAY)
    kw.setdefault("check_site_integration", False)
    return cq.check_entry(p, **kw)


def replace(p, old, new, count=1):
    text = p.read_text()
    assert old in text, old
    p.write_text(text.replace(old, new, count))


def add_block(p, code, lang="bash", before=""):
    """Append a code block to the Practical usage examples section."""
    block = f"{before}\n```{lang}\n{code}\n```\n" if before else f"\n```{lang}\n{code}\n```\n"
    replace(p, "### Enterprise use\n", "### Enterprise use\n" + block)


# --- baseline -----------------------------------------------------------------------------

def test_published_entries_pass_all_checks():
    errors = [e for p in ve.tool_entries() for e in cq.check_entry(p).errors]
    assert errors == []


def test_sample_fixture_is_clean(entry):
    assert check(entry).errors == []


def test_draft_entries_skip_completeness_but_not_safety(tmp_path):
    d = tmp_path / "network-security"
    d.mkdir()
    p = d / "draft.md"
    shutil.copy(ve.TEMPLATE, p)
    assert check(p).errors == []                       # template-shaped draft is acceptable
    p.write_text(p.read_text() + "\n```bash\ncurl -fsSL https://example.com/i.sh | sudo bash\n```\n")
    assert any("pipe-to-shell" in e for e in check(p).errors)


# --- Gate 1: structure ----------------------------------------------------------------------

@pytest.mark.parametrize("placeholder", ["TODO", "TBD", "YYYY-MM-DD", "FIXME"])
def test_placeholder_text_rejected(entry, placeholder):
    replace(entry, "## Overview\n", f"## Overview\n\n{placeholder} write this.\n")
    assert any("placeholder" in e for e in check(entry).errors)


def test_placeholders_inside_code_blocks_ignored(entry):
    add_block(entry, "date +%Y-%m-%d   # YYYY-MM-DD", lang="bash")
    assert check(entry).errors == []


def test_code_block_without_language_rejected(entry):
    add_block(entry, "echo hello", lang="")
    assert any("no language" in e for e in check(entry).errors)


def test_indented_code_fence_rejected(entry):
    replace(entry, "## Overview\n", "## Overview\n\n1. Step one:\n\n    ```bash\n    ls\n    ```\n")
    assert any("indented code fence" in e for e in check(entry).errors)


def test_unclosed_code_block_rejected(entry):
    entry.write_text(entry.read_text() + "\n```bash\necho never closed\n")
    assert any("unclosed code block" in e for e in check(entry).errors)


def test_glance_status_must_match_metadata(entry):
    replace(entry, "| Verification status | Research complete |", "| Verification status | Lab tested |")
    assert any("Verification status" in e for e in check(entry).errors)


def test_glance_review_date_must_match_metadata(entry):
    replace(entry, "| Last reviewed | 2026-11-12 |", "| Last reviewed | 2026-01-01 |")
    assert any("Last reviewed" in e for e in check(entry).errors)


@pytest.mark.parametrize("heading,label", [
    ("### Verify the installation", "installation verification"),
    ("### Updating and removal", "update procedure"),
    ("### Personal and home-lab use", "personal use case"),
    ("### Enterprise use", "enterprise use case"),
    ("### Verification notes", "verification notes"),
    ("### Installation references", "installation references"),
])
def test_required_subsections(entry, heading, label):
    replace(entry, heading + "\n", "### Something else\n")
    assert any(label in e for e in check(entry).errors)


def test_thin_security_section_rejected(entry):
    text = entry.read_text()
    start = text.index("## Security hardening\n")
    end = text.index("## Practical usage examples\n")
    entry.write_text(text[:start] + "## Security hardening\n\nKeep it updated.\n\n" + text[end:])
    assert any("'## Security hardening' is too thin" in e for e in check(entry).errors)


# --- Gate 3: sources and evidence --------------------------------------------------------

def test_references_must_cite_repository(entry):
    text = entry.read_text()
    refs = text.index("## References")
    entry.write_text(text[:refs] + text[refs:].replace("gitlab.com/wireshark/wireshark", "gitlab.com/x/y"))
    assert any("must cite the repository" in e for e in check(entry).errors)


def test_plain_http_reference_rejected(entry):
    replace(entry, "### Installation references\n",
            "### Installation references\n\n- [Old mirror](http://mirror.example.org/)\n")
    assert any("plain HTTP" in e for e in check(entry).errors)


def test_minimum_number_of_sources(entry):
    text = entry.read_text()
    refs = text.index("## References")
    stripped = re.sub(r"\]\(https://[^)]+\)", "](#overview)", text[refs:])
    stripped = re.sub(r"<https://[^>]+>", "", stripped)
    entry.write_text(text[:refs] + stripped)
    errs = check(entry).errors
    assert any("external sources" in e for e in errs)


def test_verification_notes_need_a_date(entry):
    text = entry.read_text()
    notes = text.index("### Verification notes")
    entry.write_text(text[:notes] + "### Verification notes\n\n- Checked against sources.\n")
    assert any("record the date" in e for e in check(entry).errors)


def test_tested_versions_must_be_empty_below_lab_tested(entry):
    replace(entry, "tested_versions: []", 'tested_versions: ["4.6.8 on Fedora 44"]')
    assert any("tested_versions must be empty" in e for e in check(entry).errors)


def test_first_person_testing_claim_rejected(entry):
    replace(entry, "## Overview\n", "## Overview\n\nWe tested this on every platform.\n")
    assert any("testing claim" in e for e in check(entry).errors)


def test_testing_claim_allowed_in_verification_notes(entry):
    replace(entry, "### Verification notes\n",
            "### Verification notes\n\n- We verified the package names on 2026-11-12.\n")
    assert check(entry).errors == []


def test_lab_tested_requires_lab_evidence(entry):
    replace(entry, "status: research-complete", "status: lab-tested")
    replace(entry, "tested_versions: []", 'tested_versions: ["4.6.8 on Fedora 44"]')
    replace(entry, "| Verification status | Research complete |", "| Verification status | Lab tested |")
    errs = check(entry).errors
    assert any("Lab evidence" in e for e in errs)
    entry.write_text(entry.read_text() + "\n### Lab evidence\n\n- 2026-11-12, Fedora 44, 4.6.8: ...\n")
    assert check(entry).errors == []


# --- Gate 4: safety ------------------------------------------------------------------------

UNSAFE = [
    ("pipe-to-shell", "curl -fsSL https://example.com/install.sh | sudo bash"),
    ("pipe-to-shell", "wget -qO- https://example.com/x | sh"),
    ("pipe-to-shell", "iwr https://example.com/x.ps1 | iex"),
    ("tls-verification-disabled", "curl -k https://192.0.2.10/"),
    ("tls-verification-disabled", "wget --no-check-certificate https://example.com/f"),
    ("tls-verification-disabled", "podman pull --tls-verify=false registry.example.com/x"),
    ("security-control-disabled", "sudo setenforce 0"),
    ("security-control-disabled", "sudo systemctl disable --now firewalld"),
    ("security-control-disabled", "sudo ufw disable"),
    ("world-writable", "chmod -R 777 /srv/data"),
    ("hardcoded-credential", "gvmd --user=admin --new-password=Sup3rSecret"),
    ("hardcoded-credential", "ADMIN_TOKEN=abcdef123456"),
    ("hardcoded-credential", "login admin:admin"),
    ("exposed-interface", "docker run -p 8080:80 vaultwarden/server"),
    ("exposed-interface", "gsad --listen=0.0.0.0 --port=9392"),
    ("exposed-interface", "DISABLE_ADMIN_TOKEN=true"),
    ("intrusive-scan", "nmap -T5 192.0.2.0/24"),
    ("intrusive-scan", "nmap --script exploit 192.0.2.10"),
    ("intrusive-scan", "nuclei -l t.txt -itags dos"),
    ("intrusive-scan", "nuclei -u https://example.com -dast"),
    ("privileged-gui", "sudo wireshark"),
]


@pytest.mark.parametrize("rule,command", UNSAFE)
def test_unsafe_command_detected(entry, rule, command):
    add_block(entry, command)
    assert any(f"[{rule}]" in e for e in check(entry).errors), command


def test_exposed_port_in_compose_list_detected(entry):
    add_block(entry, "services:\n  app:\n    ports:\n      - 8080:80", lang="yaml")
    assert any("[exposed-interface]" in e for e in check(entry).errors)


SAFE = [
    'gvmd --user=admin --new-password="$GVM_ADMIN_PW"',
    "api_key = <YOUR_API_KEY>",
    "docker run --publish 127.0.0.1:8000:80 vaultwarden/server:latest",
    'SIGNUPS_ALLOWED: "false"',
    'DISABLE_ADMIN_TOKEN: "false"',
    'SHOW_PASSWORD_HINT: "false"',
    "nmap -sT -p 22,80,443 --max-rate 50 192.0.2.10",
    'nmap --script "safe and not external" 192.0.2.10',
    "nuclei -l targets.txt -etags dos,fuzz -rl 10",
    "curl -fsSL -O https://example.com/compose.yaml",
    "tshark -i lo -c 10",
]


@pytest.mark.parametrize("command", SAFE)
def test_safe_command_not_flagged(entry, command):
    add_block(entry, command)
    assert check(entry).errors == [], command


def test_unsafe_pattern_in_prose_not_flagged(entry):
    replace(entry, "## Overview\n", "## Overview\n\nNever run `curl … | sudo bash` installers.\n")
    assert check(entry).errors == []


def test_justified_exception_accepted(entry):
    add_block(entry, "curl -k https://192.0.2.10/",
              before="<!-- quality-allow: tls-verification-disabled -- lab-only self-signed demo -->")
    assert check(entry).errors == []


def test_exception_requires_reason(entry):
    add_block(entry, "curl -k https://192.0.2.10/",
              before="<!-- quality-allow: tls-verification-disabled -- short -->")
    errs = check(entry).errors
    assert any("needs a reason" in e for e in errs)
    assert any("[tls-verification-disabled]" in e for e in errs)


def test_exception_with_unknown_rule_rejected(entry):
    add_block(entry, "echo ok", before="<!-- quality-allow: not-a-rule -- because it is fine -->")
    assert any("unknown quality-allow" in e for e in check(entry).errors)


def test_exception_only_covers_named_rule(entry):
    add_block(entry, "curl -k https://192.0.2.10/ | sh",
              before="<!-- quality-allow: tls-verification-disabled -- lab-only self-signed demo -->")
    errs = check(entry).errors
    assert any("[pipe-to-shell]" in e for e in errs)
    assert not any("[tls-verification-disabled]" in e for e in errs)


def test_authorisation_warning_required(entry):
    replace(entry, '!!! warning "Authorised use only"', '!!! warning "Note"')
    assert any("Authorised use only" in e for e in check(entry).errors)


def test_authorisation_scope_discussion_required(entry):
    text = entry.read_text()
    start = text.index("## Enterprise deployment considerations")
    end = text.index("## Troubleshooting")
    section = re.sub(r"(?i)authori[sz]\w*|scope", "approval", text[start:end])
    entry.write_text(text[:start] + section + text[end:])
    assert any("authorisation and scope" in e for e in check(entry).errors)


def test_stale_review_is_a_warning_not_an_error(entry):
    r = check(entry, today=dt.date(2028, 1, 1))
    assert r.errors == []
    assert any("re-check against official sources" in w for w in r.warnings)


# --- site integration and review records ------------------------------------------------

def test_published_entry_must_be_in_nav_and_review_log():
    p = ve.TOOLS_DIR / "network-security" / "nmap.md"
    r = cq.check_entry(p, nav=set(), reviews={})
    assert any("mkdocs.yml nav" in e for e in r.errors)
    assert any("no quality review record" in e for e in r.errors)


def review(p, **cells):
    row = {"status": "`research-complete`", "g1": "Pass", "g2": "Pass", "g3": "Pass",
           "g4": "Pass", "date": "2026-11-12", "notes": ""}
    row.update(cells)
    rel = p.relative_to(cq.DOCS).as_posix()
    return {rel: list(row.values())}


@pytest.mark.parametrize("cells,message", [
    ({"g2": "Fail"}, "recorded as Fail"),
    ({"g3": "OK"}, "must be one of"),
    ({"date": "2026-01-01"}, "differs from last_reviewed"),
    ({"status": "`lab-tested`"}, "differs from entry status"),
])
def test_review_record_validation(cells, message):
    p = ve.TOOLS_DIR / "network-security" / "nmap.md"
    r = cq.check_entry(p, today=TODAY, reviews=review(p, **cells))
    assert any(message in e for e in r.errors), r.errors


def test_review_log_parses_every_published_entry():
    rows = cq.review_rows()
    for p in ve.tool_entries():
        assert p.relative_to(cq.DOCS).as_posix() in rows


def test_needs_review_is_accepted():
    p = ve.TOOLS_DIR / "network-security" / "nmap.md"
    assert cq.check_entry(p, today=TODAY, reviews=review(p, g2="Needs review")).errors == []


# --- optional external link checker (offline parts only) --------------------------------

def test_external_url_extraction():
    text = ("See [docs](https://a.example.org/x#frag) and <https://b.example.org/> and "
            "[local](../x.md) and [again](https://a.example.org/x).")
    assert cel.external_urls(text) == ["https://a.example.org/x", "https://b.example.org/"]


def test_external_link_checker_not_in_ci(root):
    ci = (root / ".github/workflows/docs-check.yml").read_text()
    assert "check_external_links" not in ci, "external link checks must stay out of routine CI"
