"""GitHub Actions workflow syntax and security properties."""
import re

import pytest
import yaml

WORKFLOWS = ("docs-check.yml", "deploy-pages.yml")
SHA_PIN = re.compile(r"^[\w.-]+/[\w.-]+(/[\w./-]+)?@[0-9a-f]{40}$")


def load(root, name):
    data = yaml.safe_load((root / ".github/workflows" / name).read_text())
    # PyYAML (YAML 1.1) parses the bare key `on` as boolean True.
    if True in data:
        data["on"] = data.pop(True)
    return data


def steps(wf):
    for job in wf["jobs"].values():
        yield from job.get("steps", [])


@pytest.mark.parametrize("name", WORKFLOWS)
def test_workflow_parses(root, name):
    wf = load(root, name)
    assert wf["name"] and wf["on"] and wf["jobs"]


@pytest.mark.parametrize("name", WORKFLOWS)
def test_actions_pinned_to_sha_and_official(root, name):
    for s in steps(load(root, name)):
        if "uses" in s:
            assert SHA_PIN.match(s["uses"]), f"{s['uses']} not pinned to a full commit SHA"
            assert s["uses"].startswith("actions/"), f"unexpected third-party action {s['uses']}"


@pytest.mark.parametrize("name", WORKFLOWS)
def test_checkout_does_not_persist_credentials(root, name):
    for s in steps(load(root, name)):
        if s.get("uses", "").startswith("actions/checkout@"):
            assert s.get("with", {}).get("persist-credentials") is False


def test_docs_check_is_read_only(root):
    wf = load(root, "docs-check.yml")
    assert wf["permissions"] == {"contents": "read"}
    assert "pull_request" in wf["on"] and "pull_request_target" not in wf["on"]
    runs = " ".join(s.get("run", "") for s in steps(wf))
    for cmd in ("mkdocs build --strict", "check_links.py", "pytest", "scan_secrets.py",
                "validate_entries.py", "check_quality.py", "pip check"):
        assert cmd in runs, f"docs-check does not run {cmd}"


def test_deploy_pages_security(root):
    wf = load(root, "deploy-pages.yml")
    assert set(wf["on"]) <= {"push", "workflow_dispatch"}, "deploy must not run on PRs"
    assert wf["on"]["push"]["branches"] == ["main"]
    assert wf["permissions"] == {}
    assert wf["concurrency"]["group"] == "pages"
    assert wf["concurrency"]["cancel-in-progress"] is False
    build, deploy = wf["jobs"]["build"], wf["jobs"]["deploy"]
    assert build["permissions"] == {"contents": "read"}
    assert "refs/heads/main" in build["if"]
    assert deploy["permissions"] == {"pages": "write", "id-token": "write"}
    assert deploy["environment"]["name"] == "github-pages"
    assert deploy["needs"] == "build"
    uses = [s.get("uses", "") for s in steps(wf)]
    for action in ("configure-pages", "upload-pages-artifact", "deploy-pages"):
        assert any(f"actions/{action}@" in u for u in uses)
    upload = next(s for s in steps(wf) if "upload-pages-artifact" in s.get("uses", ""))
    assert upload["with"]["path"] == "site"


@pytest.mark.parametrize("name", WORKFLOWS)
def test_no_inline_secrets(root, name):
    text = (root / ".github/workflows" / name).read_text()
    assert not re.search(r"\$\{\{\s*secrets\.", text), "workflows should not need repository secrets"
