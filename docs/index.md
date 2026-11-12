# Cybersecurity Knowledge Base

A structured, verification-focused reference for cybersecurity tools — what they do, where
they fit, how to install and harden them, and how they compare — across **personal,
home-lab, professional, and enterprise** environments.

!!! info "Project status"
    Eleven tool entries are published, across network security, vulnerability management,
    SIEM, penetration testing, and password and secret management, together with a
    [home-lab security monitoring architecture](environments/personal/security-monitoring-lab.md).
    Each entry was checked against official sources and the
    [documentation quality gates](contributing/quality-framework.md). None is yet lab-tested:
    the [lab validation framework](contributing/lab-validation.md) defines the evidence needed. Sections marked *Planned* describe intended coverage, not finished content.
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
| [Suricata](tools/network-security/suricata.md) | Network Security | Detect known threats in mirrored network traffic (passive IDS) | Research complete |
| [Zeek](tools/network-security/zeek.md) | Network Security | Record connection, DNS, HTTP, and TLS activity for investigation | Research complete |
| [Wazuh](tools/siem/wazuh.md) | SIEM and Log Management | Monitor endpoints and centralise security alerts | Research complete |
| [ZAP](tools/penetration-testing/zap.md) | Penetration Testing | Test web applications you are authorised to assess | Research complete |
| [OpenBao](tools/password-management/openbao.md) | Password and Secret Management | Store and control access to machine and application secrets | Research complete |

## Reference architecture

The [security monitoring lab](environments/personal/security-monitoring-lab.md) shows how
Suricata, Zeek, Wazuh, Nmap, Greenbone, and OpenBao can be combined in a segmented home lab, with
staged hardware tiers, data flows, and a clear split between documented integrations and
conceptual ones.

## Tool categories

| Category | Scope | Status |
|---|---|---|
| [Network Security](tools/network-security/index.md) | Traffic analysis, firewalls, NIDS, VPN, DNS security | 4 entries |
| [Vulnerability Management](tools/vulnerability-management/index.md) | Scanning, prioritisation, remediation tracking | 2 entries |
| [Penetration Testing](tools/penetration-testing/index.md) | Authorised offensive testing and control validation | 1 entry |
| [Digital Forensics](tools/digital-forensics/index.md) | Evidence acquisition, preservation, analysis | Planned |
| [OSINT](tools/osint/index.md) | Public-source research and exposure assessment | Planned |
| [SIEM and Log Management](tools/siem/index.md) | Collection, search, correlation, detection | 1 entry |
| [Endpoint Security](tools/endpoint-security/index.md) | EDR, host hardening, integrity monitoring | Planned |
| [Incident Response](tools/incident-response/index.md) | Triage, containment, case management | Planned |
| [Threat Intelligence](tools/threat-intelligence/index.md) | Collection, enrichment, sharing | Planned |
| [Cloud Security](tools/cloud-security/index.md) | Posture, IaC, cloud identity, containers | Planned |
| [DevSecOps](tools/devsecops/index.md) | Pipeline security, SAST, supply chain | Planned |
| [Identity and Access Management](tools/identity-access/index.md) | SSO, MFA, directories, privileged access | Planned |
| [Password and Secret Management](tools/password-management/index.md) | Password managers, vaults, key management | 3 entries |
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
| Environment tracks, with links to documented tools and the reference architecture | Available |
| Glossary (core terms) | Available |
| Tool entries | 11 published; more planned |
| Reference architectures | 1 (home-lab security monitoring) |
| Lab validation framework and evidence template | Available (no lab records yet) |
| Guides, comparisons, framework mappings | Planned |

## Contributing

Contributions are welcome — new tool entries, corrections, and verification evidence.
Start with the [contributing overview](contributing/index.md) and the
[authoring standards](contributing/authoring-standards.md).

Source repository:
[github.com/RiotPhoenix/cybersecurity-knowledge-base](https://github.com/RiotPhoenix/cybersecurity-knowledge-base)
