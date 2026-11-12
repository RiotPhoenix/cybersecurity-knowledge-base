# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases follow the
[versioning strategy](decisions/0003-versioning.md).

## [Unreleased]

## [0.2.0] - 2026-11-12

### Added

- First six tool entries, each researched against official sources (status
  `research-complete`, last reviewed 2026-11-12):
    - Network Security: Nmap, Wireshark.
    - Vulnerability Management: Greenbone Community Edition, Nuclei.
    - Password and Secret Management: KeePassXC, Vaultwarden.
- Documentation quality framework with four gates (structure, technical accuracy, sources and
  evidence, operational safety and usability), an editorial review checklist, and a quality
  review log recording per-gate results for every published entry.
- `scripts/check_quality.py`: offline checks for placeholder text, code-fence formatting,
  metadata consistency, required subsections, minimum section depth, source citations,
  status-versus-testing consistency, risky command patterns (with justified exceptions),
  navigation and category links, and review records. Added to CI.
- `scripts/check_external_links.py`: optional, manual check of cited external URLs (not part
  of routine builds or CI).
- Regression tests for the quality checks, and site tests for published entries (build, search
  index, navigation, rendering of admonitions and code blocks, unrendered code fences).
- ADR 0004: documentation quality gates.

### Changed

- Tool entry template: new required metadata (`website`, `repository`,
  `requires_authorisation`) and required subsections for installation verification, updating,
  personal and enterprise use cases, and structured references with dated verification notes.
  `validate_entries.py` enforces the new metadata.
- Verification-status guidance now specifies lab evidence fields and how to record spot checks.
- Navigation: Network Security, Vulnerability Management, and Password and Secret Management
  are now sections listing their entries. Added Quality Framework and Quality Review Log pages
  under Contributing.
- Homepage, tool catalogue, category pages, and the personal and enterprise environment tracks
  now link to the documented tools. The tracks gained tool-selection, resource, maintenance,
  and governance guidance.
- Contributor guide, local development guide, README, and pull request template updated for the
  new checks.

### Known limitations

- No entry is lab-tested. Wireshark and Nmap commands were spot-checked on loopback (Fedora 44);
  all other examples are illustrative.
- Technical accuracy (Gate 2) is recorded as *Needs review* for Greenbone Community Edition,
  KeePassXC, and Vaultwarden. Unresolved items are listed in each entry's verification notes.
- All reviews so far are author reviews. No entry has yet had the independent review that
  `documentation-reviewed` requires.

## [0.1.0] - 2026-11-11

### Added

- MkDocs site using the standard theme with a dark-first RiotPhoenix stylesheet and local
  (CDN-free) syntax highlighting.
- Homepage, getting-started, local development, and GitHub Pages deployment guides.
- Fourteen-category tool taxonomy with an introductory page per category.
- Personal/home-lab and enterprise environment tracks.
- Tool entry template, authoring standards, and verification status definitions.
- Placeholder sections for guides, comparisons, and frameworks; core glossary.
- Validation scripts for links, secrets, and tool-entry structure; `pytest` suite.
- GitHub Actions workflows for documentation checks and GitHub Pages deployment.
- Issue templates, pull request template, governance documents, and ADRs.
- MIT licence for code and CC BY 4.0 for documentation.

[Unreleased]: https://github.com/RiotPhoenix/cybersecurity-knowledge-base/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/RiotPhoenix/cybersecurity-knowledge-base/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/RiotPhoenix/cybersecurity-knowledge-base/releases/tag/v0.1.0
