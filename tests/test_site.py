"""Build the site and inspect the generated output."""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_URL = "https://github.com/RiotPhoenix/cybersecurity-knowledge-base"


@pytest.fixture(scope="module")
def site(root, tmp_path_factory) -> Path:
    out = tmp_path_factory.mktemp("site")
    r = subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "-q",
                        "--site-dir", str(out)], cwd=root, capture_output=True, text=True)
    assert r.returncode == 0, f"strict build failed:\n{r.stdout}\n{r.stderr}"
    return out


def test_core_pages_generated(site):
    for p in ("index.html", "404.html", "sitemap.xml", "search/search_index.json",
              "tools/index.html", "tools/siem/index.html",
              "environments/enterprise/index.html", "contributing/tool-template/index.html"):
        assert (site / p).is_file(), p


def test_search_index_populated(site):
    import json
    docs = json.loads((site / "search/search_index.json").read_text())["docs"]
    assert any("Network Security" in d["title"] for d in docs)


PUBLISHED_ENTRIES = {
    "tools/network-security/nmap/": "Nmap",
    "tools/network-security/wireshark/": "Wireshark",
    "tools/vulnerability-management/greenbone-community-edition/": "Greenbone Community Edition",
    "tools/vulnerability-management/nuclei/": "Nuclei",
    "tools/password-management/keepassxc/": "KeePassXC",
    "tools/password-management/vaultwarden/": "Vaultwarden",
}


def test_published_entries_built_and_searchable(site):
    import json
    docs = json.loads((site / "search/search_index.json").read_text())["docs"]
    pages = {d["location"]: d["title"] for d in docs if "#" not in d["location"]}
    for loc, title in PUBLISHED_ENTRIES.items():
        assert (site / loc / "index.html").is_file(), loc
        assert pages.get(loc) == title, f"{loc} missing from search index"
        sections = [d for d in docs if d["location"].startswith(loc + "#")]
        assert any(d["title"] == "Installation" for d in sections), f"{loc}: sections not indexed"


def test_published_entries_in_navigation(site):
    html = (site / "index.html").read_text()
    for loc in PUBLISHED_ENTRIES:
        assert f'href="{loc}"' in html, f"{loc} not in site navigation"


def test_entries_render_admonitions_and_code(site):
    html = (site / "tools/network-security/nmap/index.html").read_text()
    assert 'class="admonition warning"' in html
    assert 'class="highlight"' in html


def test_no_unrendered_code_fences(site):
    """A fence the Markdown parser missed renders as inline code starting with its language."""
    import re as _re
    bad = _re.compile(r"<code>(bash|sh|yaml|text|powershell|markdown|console|json|ini)\n")
    for html in site.rglob("*.html"):
        assert not bad.search(html.read_text()), f"{html.relative_to(site)}: unrendered code fence"


def test_sitemap_uses_site_url(site):
    xml = (site / "sitemap.xml").read_text()
    assert "https://riotphoenix.github.io/cybersecurity-knowledge-base/" in xml
    assert "localhost" not in xml and "127.0.0.1" not in xml


def test_repo_link_present(site):
    assert REPO_URL in (site / "index.html").read_text()


def test_no_external_assets_loaded(site):
    """Scripts and stylesheets must be served locally (no CDN, no analytics)."""
    for html in site.rglob("*.html"):
        text = html.read_text()
        for tag in re.findall(r"<(?:script|link)\b[^>]*>", text):
            if "rel=\"canonical\"" in tag:
                continue
            src = re.search(r"(?:src|href)=\"([^\"]+)\"", tag)
            if src and re.match(r"^(https?:)?//", src.group(1)):
                if tag.startswith("<link") and "stylesheet" not in tag and "<script" not in tag:
                    continue
                pytest.fail(f"{html.relative_to(site)} loads external asset {src.group(1)}")


def test_custom_css_referenced(site):
    text = (site / "index.html").read_text()
    assert "assets/css/riotphoenix.css" in text and "assets/css/pygments.css" in text


def test_local_asset_references_resolve(site):
    for html in site.rglob("*.html"):
        text = html.read_text()
        for ref in re.findall(r"(?:src|href)=\"([^\"#?]+\.(?:css|js|png|ico|svg|woff2?))\"", text):
            if re.match(r"^(https?:)?//", ref):
                continue
            base = "/cybersecurity-knowledge-base/"
            if ref.startswith(base):          # 404.html uses root-absolute URLs by design
                target = site / ref[len(base):]
            else:
                target = (html.parent / ref).resolve()
            assert target.is_file(), f"{html.relative_to(site)} -> missing asset {ref}"
