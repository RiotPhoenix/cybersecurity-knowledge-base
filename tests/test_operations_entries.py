"""Security operations entries, the home-lab reference architecture, and compatibility."""
import re

import pytest

import check_quality as cq
import validate_entries as ve

DOCS = ve.ROOT / "docs"

NEW_ENTRIES = {
    "tools/network-security/suricata.md": ("Suricata", "network-security", True, "docs.suricata.io"),
    "tools/network-security/zeek.md": ("Zeek", "network-security", True, "docs.zeek.org"),
    "tools/siem/wazuh.md": ("Wazuh", "siem", False, "documentation.wazuh.com"),
    "tools/penetration-testing/zap.md": ("ZAP", "penetration-testing", True, "www.zaproxy.org/docs"),
    "tools/password-management/openbao.md": ("OpenBao", "password-management", False, "openbao.org/docs"),
}
EARLIER_ENTRIES = [
    "tools/network-security/nmap.md", "tools/network-security/wireshark.md",
    "tools/vulnerability-management/greenbone-community-edition.md",
    "tools/vulnerability-management/nuclei.md", "tools/password-management/keepassxc.md",
    "tools/password-management/vaultwarden.md",
]
ARCHITECTURE = DOCS / "environments/personal/security-monitoring-lab.md"
ARCH_SECTIONS = ["Purpose", "Intended audience", "Hardware assumptions", "Network topology",
                 "Security zones", "Monitoring interfaces", "Data flows", "Tool responsibilities",
                 "Deployment sequence", "Resource considerations", "Security hardening",
                 "Backup and recovery", "Maintenance", "Troubleshooting", "Limitations",
                 "Expansion options"]


def meta_body(rel):
    return ve.split_front_matter((DOCS / rel).read_text())


def references(body):
    return cq.sections(body).get("References", "")


@pytest.mark.parametrize("rel", NEW_ENTRIES)
def test_new_entry_metadata(rel):
    tool, category, auth, _ = NEW_ENTRIES[rel]
    meta, _ = meta_body(rel)
    assert meta["tool"] == tool
    assert meta["category"] == category
    assert meta["requires_authorisation"] is auth
    assert meta["status"] == "research-complete"
    assert meta["tested_versions"] == []
    assert str(meta["last_reviewed"]) == "2026-11-12"


@pytest.mark.parametrize("rel", NEW_ENTRIES)
def test_new_entry_passes_structure_and_quality(rel):
    assert ve.validate(DOCS / rel) == []
    assert cq.check_entry(DOCS / rel).errors == []


@pytest.mark.parametrize("rel", NEW_ENTRIES)
def test_new_entry_cites_official_sources(rel):
    meta, body = meta_body(rel)
    refs = references(body)
    domain = NEW_ENTRIES[rel][3]
    assert f"https://{domain}" in refs, f"{rel}: official documentation not cited"
    assert meta["website"].rstrip("/") in refs and meta["repository"] in refs
    notes = cq.subsection(refs, r"^verification notes$")
    assert "2026-11-12" in notes and "Not executed" in notes


@pytest.mark.parametrize("rel", NEW_ENTRIES)
def test_new_entry_has_required_template_content(rel):
    _, body = meta_body(rel)
    secs = cq.sections(body)
    for s in ve.SECTIONS:
        assert s in secs, s
    assert re.search(r"^### .*(personal|home)", secs["Practical usage examples"], re.I | re.M)
    assert re.search(r"^### .*enterprise", secs["Practical usage examples"], re.I | re.M)


@pytest.mark.parametrize("rel,phrases", [
    ("tools/network-security/suricata.md",
     ["Passive IDS", "Inline IPS", "not recommended as a beginner", "mirror", "TAP"]),
    ("tools/network-security/zeek.md",
     ["How Zeek differs from Suricata", "not a drop-in replacement for a signature IDS",
      "LogExpireInterval"]),
    ("tools/siem/wazuh.md",
     ["Endpoint monitoring is not network monitoring", "does not automatically",
      "default values that are published", "use_password"]),
    ("tools/penetration-testing/zap.md",
     ["Passive analysis", "Active testing", "explicit written authorisation",
      "Spidering is not passive", "Protected"]),
    ("tools/password-management/openbao.md",
     ["Never, ever, ever run", "removed in 2.7.0", "unseal", "Revoke the initial root token"]),
])
def test_new_entry_safety_distinctions(rel, phrases):
    text = re.sub(r"\s+", " ", (DOCS / rel).read_text())
    for phrase in phrases:
        assert phrase in text, f"{rel}: missing '{phrase}'"


def test_active_scans_and_dev_mode_carry_justifications():
    """Every flagged command in the new entries is explicitly justified."""
    for rel in ("tools/penetration-testing/zap.md", "tools/password-management/openbao.md"):
        text = (DOCS / rel).read_text()
        assert re.search(r"quality-allow: (active-web-scan|dev-mode-server) -- ", text), rel


@pytest.mark.parametrize("rel", NEW_ENTRIES)
def test_new_entry_reviewed_and_linked(rel):
    meta, _ = meta_body(rel)
    row = cq.review_rows().get(rel)
    assert row and row[0].strip("`") == meta["status"]
    assert all(g in cq.REVIEW_RESULTS for g in row[1:5])
    index = (DOCS / rel).parent / "index.md"
    assert f"({(DOCS / rel).name})" in index.read_text()
    assert rel in cq.nav_files()


@pytest.mark.parametrize("page", ["index.md", "tools/index.md",
                                  "environments/personal/index.md",
                                  "environments/enterprise/index.md"])
def test_overview_pages_link_new_entries(page):
    text = (DOCS / page).read_text()
    for rel in NEW_ENTRIES:
        assert rel.split("/")[-1] in text, f"{page} does not link {rel}"


@pytest.mark.parametrize("rel", EARLIER_ENTRIES)
def test_earlier_entries_still_valid(rel):
    assert (DOCS / rel).is_file()
    assert ve.validate(DOCS / rel) == []
    assert cq.check_entry(DOCS / rel).errors == []
    assert rel in cq.review_rows()


# --- reference architecture -----------------------------------------------------------

def test_architecture_has_required_sections_in_order():
    headings = re.findall(r"^## \d+\. (.+?)\s*$", ARCHITECTURE.read_text(), re.M)
    assert headings == ARCH_SECTIONS


def test_architecture_links_every_component():
    text = ARCHITECTURE.read_text()
    for target in ("network-security/suricata.md", "network-security/zeek.md", "siem/wazuh.md",
                   "network-security/nmap.md",
                   "vulnerability-management/greenbone-community-edition.md",
                   "password-management/openbao.md"):
        assert target in text, target
    for link in re.findall(r"\]\(([^)#\s]+\.md)", text):
        if not link.startswith("http"):
            assert (ARCHITECTURE.parent / link).resolve().is_file(), link


def test_architecture_diagram_is_text_and_self_hosted():
    text = ARCHITECTURE.read_text()
    assert "```text" in text
    assert not re.search(r"mermaid|plantuml|kroki|draw\.io|lucid", text, re.I)


def test_architecture_uses_documentation_addresses_only():
    text = ARCHITECTURE.read_text()
    private = re.compile(r"\b(?:10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01])|192\.168)\.\d{1,3}\.\d{1,3}\b")
    assert not private.search(text)
    assert "192.0.2.0/24" in text and "198.51.100.0/24" in text


def test_architecture_separates_documented_from_conceptual_flows():
    text = ARCHITECTURE.read_text()
    flows = cq.sections(text).get("7. Data flows", "")
    assert "**Documented**" in flows and "**Conceptual**" in flows
    assert "not** been" in text or "has **not**" in text


def test_architecture_states_visibility_and_resource_limits():
    text = ARCHITECTURE.read_text()
    for phrase in ("port mirroring", "TAP", "cannot realistically run the complete stack",
                   "Minimum viable lab", "Recommended expanded lab",
                   "Enterprise-oriented extensions", "assumption"):
        assert phrase.lower() in text.lower(), phrase


def test_architecture_linked_from_tracks_and_nav(mkdocs_config):
    assert "environments/personal/security-monitoring-lab.md" in str(mkdocs_config["nav"])
    for page in ("index.md", "environments/personal/index.md", "environments/enterprise/index.md",
                 "tools/index.md"):
        assert "security-monitoring-lab.md" in (DOCS / page).read_text(), page


def test_no_numbered_list_starts_after_one():
    """Python-Markdown ignores start numbers: a list split by a code block restarts at 1."""
    for page in sorted(DOCS.rglob("*.md")):
        in_code, prev_item = False, False
        for n, line in enumerate(page.read_text().splitlines(), 1):
            if line.startswith(("```", "~~~")):
                in_code, prev_item = not in_code, False
                continue
            if in_code:
                continue
            m = re.match(r"^(\d+)\. ", line)
            if m:
                assert prev_item or m.group(1) == "1", f"{page}:{n}: list starts at {m.group(1)}"
                prev_item = True
            elif line.strip() and not line.startswith((" ", "\t")):
                prev_item = False
