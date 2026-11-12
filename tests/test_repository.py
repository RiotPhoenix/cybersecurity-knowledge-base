"""Repository structure, governance files, and ignore rules."""
import shutil
import subprocess

import pytest

REQUIRED_FILES = [
    "README.md", "CONTRIBUTING.md", "SECURITY.md", "CHANGELOG.md", "LICENSE",
    "LICENSE-DOCS.md", "mkdocs.yml", "requirements.txt", "requirements-dev.txt",
    ".gitignore", "templates/tool-entry.md", ".github/pull_request_template.md",
    ".github/workflows/docs-check.yml", ".github/workflows/deploy-pages.yml",
    ".github/ISSUE_TEMPLATE/config.yml", "decisions/README.md",
    "docs/index.md", "docs/assets/css/riotphoenix.css", "docs/assets/css/pygments.css",
]


@pytest.mark.parametrize("rel", REQUIRED_FILES)
def test_required_file_exists_and_non_empty(root, rel):
    p = root / rel
    assert p.is_file(), f"missing {rel}"
    assert p.stat().st_size > 0, f"{rel} is empty"


def test_requirements_are_pinned(root):
    for name in ("requirements.txt", "requirements-dev.txt"):
        for line in (root / name).read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-r "):
                continue
            assert "==" in line, f"{name}: '{line}' is not pinned"


def test_adrs_indexed(root):
    index = (root / "decisions" / "README.md").read_text()
    for adr in sorted((root / "decisions").glob("[0-9][0-9][0-9][0-9]-*.md")):
        assert adr.name in index, f"{adr.name} missing from decisions/README.md"


git = shutil.which("git")


@pytest.mark.skipif(git is None, reason="git not available")
@pytest.mark.parametrize("path,ignored", [
    (".venv/bin/python", True),
    ("site/index.html", True),
    ("__pycache__/x.pyc", True),
    ("module.pyc", True),
    (".pytest_cache/v", True),
    (".env", True),
    (".env.local", True),
    (".env.example", False),
    ("docs/index.md", False),
    ("mkdocs.yml", False),
])
def test_gitignore_behaviour(root, path, ignored):
    # --no-index evaluates rules even for tracked paths; only the committed .gitignore
    # is consulted when core.excludesFile and info/exclude are bypassed.
    r = subprocess.run(
        [git, "-c", "core.excludesFile=/dev/null", "check-ignore", "--no-index", "-q", path],
        cwd=root, capture_output=True, text=True)
    if r.returncode not in (0, 1):
        pytest.skip(f"git check-ignore unavailable: {r.stderr.strip()}")
    assert (r.returncode == 0) is ignored, f"{path}: expected ignored={ignored}"
