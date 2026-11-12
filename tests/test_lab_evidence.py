"""Lab evidence template, record validation, and verification-status enforcement."""
import datetime as dt
import re
import shutil

import pytest

import check_lab_evidence as cle
import check_quality as cq
import validate_entries as ve

TODAY = dt.date(2026, 11, 12)
SAMPLE = ve.ROOT / "docs/tools/network-security/wireshark.md"


@pytest.fixture
def docs(tmp_path):
    """A temporary docs root holding one known-good entry at network-security/sample.md."""
    d = tmp_path / "network-security"
    d.mkdir()
    shutil.copy(SAMPLE, d / "sample.md")
    return tmp_path


def validate(record, docs_root):
    return cle.validate_record(record, today=TODAY, docs_root=docs_root)


# --- template --------------------------------------------------------------------------

def test_template_is_structurally_complete():
    assert cle.validate_template() == []


def test_template_contains_every_required_field_and_section():
    meta, body = ve.split_front_matter(cle.TEMPLATE.read_text())
    assert set(cle.RECORD_KEYS) <= set(meta)
    for s in cle.RECORD_SECTIONS:
        assert f"## {s}" in body


def test_template_documents_allowed_values():
    text = cle.TEMPLATE.read_text()
    for value in (*cle.OUTCOMES, *cle.ENVIRONMENT_TYPES):
        assert value in text


def test_template_uses_only_documentation_values():
    text = cle.TEMPLATE.read_text()
    for label, rx in cle.PRIVACY_RULES:
        assert not rx.search(text), label


def test_required_fields_cover_the_evidence_policy():
    """Every field the lab validation policy requires has a home in the record."""
    fields = " ".join(cle.RECORD_KEYS + cle.RECORD_SECTIONS).lower()
    for required in ("tool", "tool_version", "test_date", "operating_system", "environment",
                     "hardware", "installation", "configuration", "objective", "procedure",
                     "expected", "observed", "outcome", "troubleshooting", "limitations",
                     "evidence", "tester", "deviations"):
        assert required in fields, required


def test_contributor_guide_documents_every_field(root):
    page = (root / "docs/contributing/lab-validation.md").read_text()
    for key in cle.RECORD_KEYS:
        assert f"`{key}`" in page, key


# --- valid records ----------------------------------------------------------------------

def test_valid_record_passes(docs, lab_record):
    assert validate(lab_record(docs), docs) == []


@pytest.mark.parametrize("outcome", cle.OUTCOMES)
def test_all_outcomes_accepted(docs, lab_record, outcome):
    assert validate(lab_record(docs, outcome=outcome), docs) == []


def test_documentation_addresses_allowed(docs, lab_record):
    p = lab_record(docs)
    p.write_text(p.read_text() + "\nAddresses 192.0.2.10, 198.51.100.7, 203.0.113.9, "
                 "MAC 00:00:5e:00:53:01, host sensor.lab.example.\n")
    assert validate(p, docs) == []


def test_published_records_are_valid():
    for record in cle.records():
        assert cle.validate_record(record) == []


def test_record_index_exists_and_is_in_nav(root, mkdocs_config):
    assert (root / "docs/lab-evidence/index.md").is_file()
    assert "lab-evidence/index.md" in str(mkdocs_config["nav"])


# --- invalid records --------------------------------------------------------------------

@pytest.mark.parametrize("key", cle.RECORD_KEYS)
def test_missing_key_rejected(docs, lab_record, key):
    p = lab_record(docs, **{key: None})
    assert any(f"missing '{key}'" in e for e in validate(p, docs))


@pytest.mark.parametrize("field,value,message", [
    ("outcome", "passed", "outcome"),
    ("environment_type", "staging", "environment_type"),
    ("record_type", "notes", "record_type"),
    ("sanitised", False, "sanitised must be true"),
    ("tool_version", "", "'tool_version' must not be empty"),
])
def test_invalid_values_rejected(docs, lab_record, field, value, message):
    p = lab_record(docs, **{field: value})
    assert any(message in e for e in validate(p, docs))


def test_future_test_date_rejected(docs, lab_record):
    p = lab_record(docs, test_date="2026-12-01")
    assert any("future" in e for e in validate(p, docs))


def test_entry_must_exist(docs, lab_record):
    p = lab_record(docs, entry="network-security/missing.md")
    assert any("does not exist" in e for e in validate(p, docs))


def test_tool_must_match_entry(docs, lab_record):
    p = lab_record(docs, tool="Nmap")
    assert any("does not match the entry's tool" in e for e in validate(p, docs))


@pytest.mark.parametrize("section", cle.RECORD_SECTIONS)
def test_missing_section_rejected(docs, lab_record, section):
    p = lab_record(docs)
    text = re.sub(rf"^## {re.escape(section)}\n", "## Something else\n", p.read_text(), flags=re.M)
    p.write_text(text)
    assert any(f"missing section '## {section}'" in e for e in validate(p, docs))


def test_empty_section_rejected(docs, lab_record):
    p = lab_record(docs)
    p.write_text(p.read_text().replace("None.\n\n## Troubleshooting", "\n## Troubleshooting"))
    assert any("is empty" in e for e in validate(p, docs))


def test_sections_out_of_order_rejected(docs, lab_record):
    p = lab_record(docs)
    t = p.read_text()
    t = t.replace("## Expected result", "## TMP").replace("## Actual observed result",
                                                          "## Expected result")
    p.write_text(t.replace("## TMP", "## Actual observed result"))
    assert any("out of template order" in e for e in validate(p, docs))


def test_outcome_section_must_match(docs, lab_record):
    p = lab_record(docs, outcome="fail")
    p.write_text(p.read_text().replace("fail: the documented", "The documented"))
    assert any("must state the recorded outcome" in e for e in validate(p, docs))


def test_template_placeholder_rejected(docs, lab_record):
    p = lab_record(docs)
    p.write_text(p.read_text() + "\nTested on YYYY-MM-DD.\n")
    assert any("placeholder" in e for e in validate(p, docs))


@pytest.mark.parametrize("leak,label", [
    ("10.20.30.40", "private IPv4"),
    ("172.16.5.4", "private IPv4"),
    ("192.168.1.10", "private IPv4"),
    ("169.254.10.1", "private IPv4"),
    ("someone@gmail.example.org", "e-mail"),
    ("aa:bb:cc:dd:ee:ff", "MAC address"),
    ("nas01.lan", "hostname"),
    ("printer.home", "hostname"),
    ("db.corp", "hostname"),
])
def test_private_details_rejected(docs, lab_record, leak, label):
    p = lab_record(docs)
    p.write_text(p.read_text() + f"\nObserved traffic from {leak}.\n")
    assert any(label in e for e in validate(p, docs)), leak


def test_record_must_be_indexed(docs, lab_record):
    p = lab_record(docs, index=False)
    assert any("not linked from index.md" in e for e in validate(p, docs))


# --- status enforcement in check_quality ----------------------------------------------

def _make_tested(docs, status="lab-tested", label="Lab tested", link="sample-2026-11-12.md"):
    entry = docs / "network-security/sample.md"
    t = entry.read_text()
    t = t.replace("status: research-complete", f"status: {status}")
    t = t.replace("tested_versions: []", 'tested_versions: ["4.6.8 on Fedora 44"]')
    t = t.replace("| Verification status | Research complete |", f"| Verification status | {label} |")
    t += f"\n### Lab evidence\n\n- 2026-11-12, Fedora 44, 4.6.8: [record](../lab-evidence/{link})\n"
    entry.write_text(t)
    return entry


def check(entry, docs):
    return cq.check_entry(entry, today=TODAY, check_site_integration=False, docs_root=docs).errors


def test_lab_tested_with_valid_record_passes(docs, lab_record):
    lab_record(docs)
    assert check(_make_tested(docs), docs) == []


def test_lab_tested_without_record_link_rejected(docs):
    entry = _make_tested(docs)
    entry.write_text(entry.read_text().replace("[record](../lab-evidence/sample-2026-11-12.md)", "done"))
    assert any("must link to at least one record" in e for e in check(entry, docs))


def test_lab_tested_with_missing_record_rejected(docs):
    assert any("record not found" in e for e in check(_make_tested(docs), docs))


def test_invalid_linked_record_rejected(docs, lab_record):
    lab_record(docs, sanitised=False)
    assert any("invalid lab evidence record" in e for e in check(_make_tested(docs), docs))


def test_failed_record_does_not_support_status(docs, lab_record):
    lab_record(docs, outcome="fail")
    assert any("outcome 'pass' or 'partial'" in e for e in check(_make_tested(docs), docs))


def test_partial_record_supports_status(docs, lab_record):
    lab_record(docs, outcome="partial")
    assert check(_make_tested(docs), docs) == []


def test_record_for_another_entry_rejected(docs, lab_record):
    other = docs / "network-security/other.md"
    shutil.copy(SAMPLE, other)
    lab_record(docs, entry="network-security/other.md")
    assert any("not this entry" in e for e in check(_make_tested(docs), docs))


def test_record_version_must_be_in_tested_versions(docs, lab_record):
    lab_record(docs, version="4.6.9")
    assert any("not in tested_versions" in e for e in check(_make_tested(docs), docs))


def test_production_validated_needs_production_record(docs, lab_record):
    lab_record(docs)
    entry = _make_tested(docs, status="production-validated", label="Production validated")
    assert any("environment_type 'production'" in e for e in check(entry, docs))


def test_production_validated_with_production_record_passes(docs, lab_record):
    lab_record(docs, environment_type="production")
    entry = _make_tested(docs, status="production-validated", label="Production validated")
    assert check(entry, docs) == []


def test_no_published_entry_claims_testing_without_records():
    for p in ve.tool_entries():
        meta, _ = ve.split_front_matter(p.read_text())
        if meta["status"] in cq.TESTED_STATUSES:
            assert cq.check_entry(p).errors == [], p
        else:
            assert meta["tested_versions"] == [], p
