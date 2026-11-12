# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and releases follow the
[versioning strategy](decisions/0003-versioning.md).

## [Unreleased]

## [0.3.0] - 2026-11-12

### Added

- Five security operations and infrastructure entries, each researched against official sources
  (status `research-complete`, last reviewed 2026-11-12):
    - Network Security: Suricata (passive IDS, with inline IPS described but not recommended as
      a default) and Zeek (network security monitoring).
    - SIEM and Log Management: Wazuh.
    - Penetration Testing: ZAP (Zed Attack Proxy).
    - Password and Secret Management: OpenBao.
- Security monitoring lab: the first reference architecture, covering topology, security zones,
  monitoring interfaces (mirror ports, TAPs), data flows classified as documented, configuration
  required, or conceptual, staged deployment, resource tiers, hardening, backup, maintenance,
  troubleshooting, limitations, and enterprise extensions. The diagram is plain text.
- Lab validation framework: `templates/lab-evidence.md`, contributor guidance on recording and
  sanitising evidence and on when a status may be raised, and a published lab evidence index
  (no records yet).
- `scripts/check_lab_evidence.py`: offline validation of the lab evidence template and records
  (required fields and sections, allowed values, matching entries, privacy rules). Added to CI.
- Command-safety rules `active-web-scan` and `dev-mode-server` in `scripts/check_quality.py`.
- Glossary terms: DAST, IPS, NSM, port mirroring (SPAN), TAP, unsealing.
- Tests for the new entries, the reference architecture, lab evidence records, status
  enforcement, the new safety rules, search and navigation of the new pages, and numbered-list
  rendering. The suite grew from 182 to 321 tests.
- ADR 0005: lab evidence records and status enforcement.

### Changed

- `lab-tested` and `production-validated` now require linked, valid lab evidence records that
  support the entry, on a version listed in `tested_versions`; `production-validated` also needs a
  production record. A dated sentence alone no longer satisfies the check.
- Navigation: Penetration Testing and SIEM and Log Management are now sections listing their
  entries. Added the security monitoring lab, Lab Validation, and Lab Evidence Records pages.
- Homepage, tool catalogue, category pages, and the personal and enterprise tracks link to the new
  entries and the reference architecture.
- Quality framework, verification statuses, contributor guide, local development guide, README,
  CONTRIBUTING, and pull request template updated for the lab evidence checks.
- `scripts/check_external_links.py` now retries with `GET` when a server rejects `HEAD`, so a
  `HEAD`-only 404 is no longer reported as a definite failure.
- KeePassXC: FAQ link corrected to its new location on the official documentation page (the old
  URL returned 404). Redirected Suricata, Flathub, and RFC links updated to their final URLs.
- Maintenance backlog re-checked against current sources and recorded in the quality review log:
    - KeePassXC: default cipher and KDF for new databases identified from the 2.8.0 source code;
      the Wayland Auto-Type conflict between the FAQ and the 2.8.0 release notes persists.
    - Vaultwarden: output location of the built-in backup command identified from the 1.37.5
      source code and added to the entry; rootless Podman behaviour remains undocumented.
    - Greenbone Community Edition: supported-host list, backup procedure, and production
      suitability remain unresolved upstream; new findings added to the verification notes.

### Known limitations

- No entry is lab-tested and no lab evidence records exist yet. All new examples and the reference
  architecture are illustrative and were not executed.
- Technical accuracy (Gate 2) is recorded as *Needs review* for Wazuh and OpenBao (in addition to
  Greenbone Community Edition, KeePassXC, and Vaultwarden). Unresolved items are listed in each
  entry's verification notes.
- All reviews remain author reviews. No entry has had the independent review that
  `documentation-reviewed` requires.

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

[Unreleased]: https://github.com/RiotPhoenix/cybersecurity-knowledge-base/compare/v0.3.0...HEAD
[0.3.0]: https://github.com/RiotPhoenix/cybersecurity-knowledge-base/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/RiotPhoenix/cybersecurity-knowledge-base/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/RiotPhoenix/cybersecurity-knowledge-base/releases/tag/v0.1.0
