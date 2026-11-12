# Cybersecurity Knowledge Base

A structured, verification-focused reference for cybersecurity tools — what they do, where
they fit, how to install and harden them, and how they compare — across **personal,
home-lab, professional, and enterprise** environments.

!!! info "Project status"
    The first six tool entries are published, in network security, vulnerability management,
    and password management. Each was checked against official sources and the
    [documentation quality gates](contributing/quality-framework.md), and none is yet
    lab-tested. Sections marked *Planned* describe intended coverage, not finished content.
    Every entry carries an explicit [verification status](contributing/verification-statuses.md)
    and last-reviewed date.

## Purpose and audience

Security tooling documentation is scattered across vendor sites, wikis, and outdated blog
posts. This knowledge base aims to give each tool a consistent, sourced entry so readers can
evaluate and deploy it with confidence. It is written for:

- **Students and self-learners** building skills in a home lab.
- **Practitioners** — analysts, engineers, administrators, and testers — looking for a
  dependable reference.
- **Teams and decision-makers** comparing options for enterprise deployment.

## Choose your track

| Track | For | Start here |
|---|---|---|
| **Personal and home lab** | Individuals securing their own devices and building isolated learning labs. | [Personal track](environments/personal/index.md) |
| **Enterprise** | Organisations deploying tools at scale with governance, change control, and audit requirements. | [Enterprise track](environments/enterprise/index.md) |

## Documented tools

| Tool | Category | Use it to… | Status |
|---|---|---|---|
| [Nmap](tools/network-security/nmap.md) | Network Security | Discover hosts and services, and validate segmentation, on networks you are authorised to scan | Research complete |
| [Wireshark](tools/network-security/wireshark.md) | Network Security | Capture and analyse packets for troubleshooting and investigation | Research complete |
| [Greenbone Community Edition](tools/vulnerability-management/greenbone-community-edition.md) | Vulnerability Management | Run scheduled network vulnerability assessments | Research complete |
| [Nuclei](tools/vulnerability-management/nuclei.md) | Vulnerability Management | Run targeted, template-based vulnerability checks | Research complete |
| [KeePassXC](tools/password-management/keepassxc.md) | Password and Secret Management | Keep passwords in an offline encrypted database | Research complete |
| [Vaultwarden](tools/password-management/vaultwarden.md) | Password and Secret Management | Self-host a Bitwarden-compatible password server (unofficial) | Research complete |

## Tool categories

| Category | Scope | Status |
|---|---|---|
| [Network Security](tools/network-security/index.md) | Traffic analysis, firewalls, NIDS, VPN, DNS security | 2 entries |
| [Vulnerability Management](tools/vulnerability-management/index.md) | Scanning, prioritisation, remediation tracking | 2 entries |
| [Penetration Testing](tools/penetration-testing/index.md) | Authorised offensive testing and control validation | Planned |
| [Digital Forensics](tools/digital-forensics/index.md) | Evidence acquisition, preservation, analysis | Planned |
| [OSINT](tools/osint/index.md) | Public-source research and exposure assessment | Planned |
| [SIEM and Log Management](tools/siem/index.md) | Collection, search, correlation, detection | Planned |
| [Endpoint Security](tools/endpoint-security/index.md) | EDR, host hardening, integrity monitoring | Planned |
| [Incident Response](tools/incident-response/index.md) | Triage, containment, case management | Planned |
| [Threat Intelligence](tools/threat-intelligence/index.md) | Collection, enrichment, sharing | Planned |
| [Cloud Security](tools/cloud-security/index.md) | Posture, IaC, cloud identity, containers | Planned |
| [DevSecOps](tools/devsecops/index.md) | Pipeline security, SAST, supply chain | Planned |
| [Identity and Access Management](tools/identity-access/index.md) | SSO, MFA, directories, privileged access | Planned |
| [Password and Secret Management](tools/password-management/index.md) | Password managers, vaults, key management | 2 entries |
| [Infrastructure and Home Labs](tools/infrastructure/index.md) | Virtualisation, segmentation, lab design | Planned |

## Getting started

- New here? Read [how this knowledge base works](getting-started/index.md).
- Want to build the site locally? Follow the [local development guide](getting-started/local-development.md).
- Browse the [glossary](glossary/index.md) for common terms.

## What is available now

| Section | Status |
|---|---|
| Category taxonomy and introductions | Available |
| Tool entry template, editorial standards, and quality framework | Available |
| Environment tracks, with links to documented tools | Available |
| Glossary (core terms) | Available |
| Tool entries | 6 published; more planned |
| Guides, comparisons, framework mappings | Planned |

## Contributing

Contributions are welcome — new tool entries, corrections, and verification evidence.
Start with the [contributing overview](contributing/index.md) and the
[authoring standards](contributing/authoring-standards.md).

Source repository:
[github.com/RiotPhoenix/cybersecurity-knowledge-base](https://github.com/RiotPhoenix/cybersecurity-knowledge-base)
