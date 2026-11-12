# Cybersecurity Knowledge Base

[![Documentation checks](https://github.com/RiotPhoenix/cybersecurity-knowledge-base/actions/workflows/docs-check.yml/badge.svg)](https://github.com/RiotPhoenix/cybersecurity-knowledge-base/actions/workflows/docs-check.yml)
[![Deploy documentation](https://github.com/RiotPhoenix/cybersecurity-knowledge-base/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/RiotPhoenix/cybersecurity-knowledge-base/actions/workflows/deploy-pages.yml)

A structured, verification-focused reference for cybersecurity tools across personal,
home-lab, professional, and enterprise environments.

**Website:** <https://riotphoenix.github.io/cybersecurity-knowledge-base/>

> **Status: v0.2.0.** Six tool entries are published (Nmap, Wireshark, Greenbone Community
> Edition, Nuclei, KeePassXC, and Vaultwarden), each checked against official sources and the
> documentation quality gates. None is yet marked lab-tested. Other categories are still being
> populated.

## What each tool entry covers

Overview and capabilities · official website, source, and licence · supported platforms and
maintenance status · personal and enterprise suitability · installation and initial
configuration · security hardening · practical usage · enterprise deployment ·
troubleshooting · alternatives · references · tested versions, verification status, and
last-reviewed date.

## Categories

Network Security · Vulnerability Management · Penetration Testing · Digital Forensics ·
OSINT · SIEM and Log Management · Endpoint Security · Incident Response · Threat
Intelligence · Cloud Security · DevSecOps · Identity and Access Management · Password and
Secret Management · Infrastructure and Home Labs

## Quick start (Fedora)

```bash
git clone https://github.com/RiotPhoenix/cybersecurity-knowledge-base.git
cd cybersecurity-knowledge-base
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m mkdocs serve      # http://127.0.0.1:8000/cybersecurity-knowledge-base/
```

Full instructions: [Local Development](docs/getting-started/local-development.md).

## Validation

```bash
python -m mkdocs build --strict
python scripts/check_links.py
python scripts/scan_secrets.py
python scripts/validate_entries.py
python scripts/check_quality.py
python scripts/check_lab_evidence.py
python -m pytest
```

## Repository layout

| Path | Purpose |
|---|---|
| `docs/` | Website content (Markdown) and stylesheets |
| `templates/` | Tool entry and lab evidence templates |
| `scripts/` | Validation scripts (links, secrets, entry structure, documentation quality, lab evidence) |
| `tests/` | Automated tests (`pytest`) |
| `decisions/` | Architecture decision records |
| `.github/` | CI/CD workflows, issue and pull request templates |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) and the
[authoring standards](docs/contributing/authoring-standards.md). Report security issues as
described in [SECURITY.md](SECURITY.md).

## Licence

- Documentation (`docs/`, `templates/`): [CC BY 4.0](LICENSE-DOCS.md)
- Code (scripts, tests, workflows, configuration, styles): [MIT](LICENSE)

See [ADR 0002](decisions/0002-licensing.md) for the rationale.

## Disclaimer

This knowledge base is provided for educational and defensive purposes. Use offensive
security tools only on systems you own or are explicitly authorised to test. Always confirm
guidance against official vendor documentation.
