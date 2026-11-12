"""Tool entry template and validator behaviour."""
import textwrap

import validate_entries as ve


def test_template_is_complete(root):
    assert ve.validate(ve.TEMPLATE, is_template=True) == []


def test_template_page_documents_every_section(root):
    page = (root / "docs/contributing/tool-template.md").read_text()
    for s in ve.SECTIONS[1:]:
        assert s in page, f"tool-template.md does not document '{s}'"
    for f in ve.GLANCE_FIELDS:
        assert f in page, f"tool-template.md does not document field '{f}'"
    for k in ve.FRONT_MATTER_KEYS:
        assert f"`{k}`" in page


def test_statuses_documented(root):
    page = (root / "docs/contributing/verification-statuses.md").read_text()
    for s in ve.STATUSES:
        assert f"`{s}`" in page


def _entry(tmp_path, category="network-security", **meta):
    fm = {"tool": "Example", "category": category, "status": "draft",
          "last_reviewed": "2026-01-01", "tested_versions": "[]"}
    fm.update(meta)
    body = ve.TEMPLATE.read_text().split("\n---\n", 1)[1]
    d = tmp_path / category
    d.mkdir()
    p = d / "example.md"
    p.write_text("---\n" + "\n".join(f"{k}: {v}" for k, v in fm.items()) + "\n---\n" + body)
    return p


def test_valid_entry_passes(tmp_path):
    assert ve.validate(_entry(tmp_path)) == []


def test_invalid_status_rejected(tmp_path):
    errs = ve.validate(_entry(tmp_path, status="verified"))
    assert any("status" in e for e in errs)


def test_category_mismatch_rejected(tmp_path):
    p = _entry(tmp_path)
    p.write_text(p.read_text().replace("category: network-security", "category: osint"))
    assert any("does not match directory" in e for e in ve.validate(p))


def test_lab_tested_requires_versions(tmp_path):
    errs = ve.validate(_entry(tmp_path, status="lab-tested"))
    assert any("requires at least one tested version" in e for e in errs)


def test_future_review_date_rejected(tmp_path):
    errs = ve.validate(_entry(tmp_path, last_reviewed="2999-01-01"))
    assert any("future" in e for e in errs)


def test_missing_section_rejected(tmp_path):
    p = _entry(tmp_path)
    p.write_text(p.read_text().replace("## Security hardening", "## Hardening"))
    assert any("Security hardening" in e for e in ve.validate(p))


def test_offensive_entry_requires_warning(tmp_path):
    p = _entry(tmp_path, category="penetration-testing")
    p.write_text(p.read_text().replace("Authorised use only", "Note"))
    assert any("Authorised use only" in e for e in ve.validate(p))


def test_missing_front_matter_rejected(tmp_path):
    p = tmp_path / "x.md"
    p.write_text(textwrap.dedent("# Title\n"))
    assert ve.validate(p) and "front matter" in ve.validate(p)[0]


def test_published_entries_valid():
    errs = [e for p in ve.tool_entries() for e in ve.validate(p)]
    assert errs == []
