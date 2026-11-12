# Enterprise

Guidance for organisations evaluating and deploying security tooling at scale.

!!! warning "Installable is not the same as enterprise-ready"
    Many open-source tools can be installed in minutes. That does not make them suitable for
    production. Suitability depends on support, governance, auditability, recovery, and who
    will operate the tool for years. Each entry rates enterprise suitability separately for
    this reason.

## Evaluation considerations

| Area | Questions to ask |
|---|---|
| Fit | Which risks does the tool address, and what does it overlap with? |
| Scale | How does it behave at your asset, user, or data volume? |
| Integration | Does it integrate with identity, SIEM, ticketing, and asset inventory? |
| Operations | Who runs it? What are the upgrade, backup, and high-availability requirements? |
| Governance | Does it support role-based access, audit logging, and data-retention requirements? |
| Supportability | What is the maintenance status, release cadence, and support model? |
| Licensing | Do licence terms permit your intended commercial use? |

## Operating principles

- **Operational ownership.** Name an owner for every tool, responsible for updates, data feeds,
  user access, backups, and retirement. Unowned security tools decay into risks.
- **Access control.** Restrict who can run scanners, capture traffic, or administer credential
  stores. Prefer named accounts integrated with your identity provider over shared logins.
- **Change management.** Treat active scans and configuration changes as changes, with
  approved scope, time windows, and rollback. Register recurring scans as standard changes.
- **Logging and auditability.** Know what each tool records about its own use (often very
  little) and fill gaps with platform logging or controlled data stores.
- **Support and maintenance.** Community projects have no contractual support. Decide whether
  internal expertise is enough or whether a commercially supported edition is required.
- **Data protection.** Packet captures, scan results, and vault backups are sensitive. Define
  classification, encryption, retention, and legal-hold handling before collecting them.
- **Deployment scale and integration.** Check how results reach ticketing, CMDB, and SIEM, and
  whether the tool's architecture fits multiple sites or segments.
- **Security governance.** Authorise active tools in writing (scope, rules of engagement,
  contacts). Review template and plugin sources, and verify downloads.

## Documented tools: enterprise view

| Tool | Enterprise fit | Key limitation to accept or mitigate |
|---|---|---|
| [Nmap](../../tools/network-security/nmap.md) | Authorised discovery, exposure checks, segmentation validation | Needs scope control and coordination with network and security operations. Redistribution in products requires an OEM licence. |
| [Wireshark](../../tools/network-security/wireshark.md) | Analyst workstation tool for troubleshooting and incident response | Not a monitoring platform. Captures are sensitive personal and business data. Capture rights must be restricted. |
| [Greenbone Community Edition](../../tools/vulnerability-management/greenbone-community-edition.md) | Evaluation and smaller assessment programmes | No vendor support. The container setup is documented as not for production. The community feed omits enterprise-product checks. |
| [Nuclei](../../tools/vulnerability-management/nuclei.md) | Targeted, repeatable checks within a governed programme | Template trust and review. Default use of public out-of-band servers. Fast-changing flags. |
| [KeePassXC](../../tools/password-management/keepassxc.md) | Individual administrators and small teams | No central administration, audit trail, or per-user revocation. |
| [Vaultwarden](../../tools/password-management/vaultwarden.md) | Evaluation of self-hosted password infrastructure | Unofficial and community-supported. You carry all operational, recovery, and compatibility risk. |

## Planned coverage

!!! note "Planned"
    - Deployment architecture patterns per category.
    - Integration guides (identity, logging, ticketing).
    - Change-management and rollout checklists.
    - Mappings to recognised control frameworks.
