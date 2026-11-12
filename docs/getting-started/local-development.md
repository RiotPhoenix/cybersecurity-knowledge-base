# Local Development

These steps build and preview the site on Fedora Linux. They work on any Linux, macOS, or
WSL system with Python 3.10+ and Git.

## Prerequisites (Fedora)

```bash
sudo dnf install -y git python3
```

The project pins its Python dependencies in `requirements.txt` (site build) and
`requirements-dev.txt` (tests). All packages are installed into a project-local virtual
environment — never into system Python and never with `sudo pip`.

## Set up

```bash
git clone https://github.com/RiotPhoenix/cybersecurity-knowledge-base.git
cd cybersecurity-knowledge-base
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-dev.txt
python -m pip check
```

## Preview

```bash
python -m mkdocs serve
```

Open <http://127.0.0.1:8000/cybersecurity-knowledge-base/>. Pages reload as you edit files
in `docs/`.

## Validate before opening a pull request

Run the same checks as continuous integration:

```bash
python -m mkdocs build --strict
python scripts/check_links.py
python scripts/validate_entries.py
python scripts/check_quality.py
python scripts/scan_secrets.py
python -m pytest
```

| Check | What it verifies |
|---|---|
| `mkdocs build --strict` | Site builds; every page is in the navigation; no broken internal links or anchors. |
| `scripts/check_links.py` | Relative links in repository Markdown outside `docs/` (README, guides, templates). |
| `scripts/validate_entries.py` | Tool entries follow the template: metadata, sections, and *At a glance* rows. |
| `scripts/check_quality.py` | Automated parts of the [documentation quality gates](../contributing/quality-framework.md), such as sources, required subsections, risky commands, and review records. |
| `scripts/scan_secrets.py` | No credentials, private keys, or token-like strings in tracked files. |
| `pytest` | Required files, configuration, template completeness, tool-entry metadata, quality-check regression tests, search index, workflow syntax, palette contrast. |

All of these run offline. The optional `scripts/check_external_links.py` contacts external
websites and is run manually during reviews; see the
[quality framework](../contributing/quality-framework.md#optional-external-link-check).

## Updating dependencies

Dependencies are fully pinned for reproducible builds. To update:

1. Create a fresh environment: `python3 -m venv /tmp/ckb-venv && source /tmp/ckb-venv/bin/activate`.
2. Install the direct dependencies unpinned: `pip install mkdocs Markdown Pygments PyYAML pytest`.
3. Review release notes for any major-version changes.
4. Record the new versions from `pip freeze` in `requirements.txt` (runtime) and
   `requirements-dev.txt` (test-only packages).
5. Run the full validation suite and inspect the rendered site.
6. Note the update in `CHANGELOG.md`.

## Regenerating syntax-highlighting styles

Code highlighting uses Pygments with a local stylesheet (no external CDN). To regenerate it:

```bash
pygmentize -S github-dark -f html -a .highlight > docs/assets/css/pygments.css
```
