"""MkDocs configuration, navigation coverage, and taxonomy."""
from pathlib import Path

SITE_URL = "https://riotphoenix.github.io/cybersecurity-knowledge-base/"
REPO_URL = "https://github.com/RiotPhoenix/cybersecurity-knowledge-base"
CATEGORIES = [
    "network-security", "vulnerability-management", "penetration-testing",
    "digital-forensics", "osint", "siem", "endpoint-security", "incident-response",
    "threat-intelligence", "cloud-security", "devsecops", "identity-access",
    "password-management", "infrastructure",
]


def nav_pages(nav) -> list[str]:
    out = []
    for item in nav:
        if isinstance(item, str):
            out.append(item)
        elif isinstance(item, dict):
            for v in item.values():
                out += nav_pages(v) if isinstance(v, list) else [v]
    return out


def test_site_and_repo_urls(mkdocs_config):
    assert mkdocs_config["site_url"] == SITE_URL
    assert mkdocs_config["repo_url"] == REPO_URL
    assert mkdocs_config["edit_uri"] == "edit/main/docs/"


def test_strict_and_validation_enabled(mkdocs_config):
    assert mkdocs_config.get("strict") is True
    v = mkdocs_config["validation"]
    assert v["nav"]["omitted_files"] in ("warn", "info") and v["links"]["anchors"] == "warn"


def test_theme_and_search(mkdocs_config):
    theme = mkdocs_config["theme"]
    assert theme["name"] == "mkdocs"
    assert theme["color_mode"] == "dark"
    assert theme["highlightjs"] is False, "CDN-loaded highlight.js must stay disabled"
    assert "search" in mkdocs_config["plugins"]


def test_extra_css_exists(root, mkdocs_config):
    for css in mkdocs_config["extra_css"]:
        assert (root / "docs" / css).is_file(), css


def test_every_page_in_nav_and_every_nav_entry_exists(root, mkdocs_config):
    docs = root / "docs"
    pages = {p.relative_to(docs).as_posix() for p in docs.rglob("*.md")}
    nav = nav_pages(mkdocs_config["nav"])
    assert len(nav) == len(set(nav)), "duplicate nav entries"
    missing_files = [n for n in nav if n not in pages]
    not_in_nav = sorted(pages - set(nav))
    assert not missing_files, f"nav entries without files: {missing_files}"
    assert not not_in_nav, f"pages not reachable from nav: {not_in_nav}"


def test_taxonomy_categories(root):
    tools = root / "docs" / "tools"
    found = sorted(p.name for p in tools.iterdir() if p.is_dir())
    assert found == sorted(CATEGORIES)
    for c in CATEGORIES:
        text = (tools / c / "index.md").read_text()
        for section in ("## Purpose of this category", "## Intended coverage",
                        "## Environment considerations", "## Tool entries"):
            assert section in text, f"{c}: missing {section}"


def test_offensive_categories_have_authorisation_warning(root):
    for c in ("penetration-testing", "osint"):
        assert "Authorised use only" in (root / "docs/tools" / c / "index.md").read_text()


def test_homepage_sections(root):
    text = (root / "docs" / "index.md").read_text()
    for needle in ("## Purpose and audience", "environments/personal/index.md",
                   "environments/enterprise/index.md", "## Tool categories",
                   "## Getting started", "## Contributing", REPO_URL, "Planned"):
        assert needle in text, f"homepage missing {needle!r}"
    for c in CATEGORIES:
        assert f"tools/{c}/index.md" in text
