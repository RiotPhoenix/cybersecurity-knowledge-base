# Password and Secret Management

Tools that generate, store, share, and rotate passwords, keys, and machine secrets.

## Purpose of this category

This category groups tools by the security problem they address, so readers can find
options for a given need and compare them consistently. Each tool entry follows the
[tool entry template](../../contributing/tool-template.md) and carries an explicit
[verification status](../../contributing/verification-statuses.md).

## Intended coverage

- Personal and team password managers
- Machine secrets vaults
- Key management and hardware tokens
- Secret rotation
- Secret-sprawl detection

## Environment considerations

| Environment | Typical focus |
|---|---|
| [Personal / home lab](../../environments/personal/index.md) | Choosing and configuring a password manager and backing up recovery material. |
| [Enterprise](../../environments/enterprise/index.md) | Centralised vaulting, access policies, rotation automation, auditability, and break-glass procedures. |

## Tool entries

Each entry records its [verification status](../../contributing/verification-statuses.md)
and a [quality review](../../contributing/quality-review-log.md) against the
[documentation quality gates](../../contributing/quality-framework.md). *Research complete* means checked against official sources, not lab-tested.

| Tool | What it is for | Personal | Enterprise | Status |
|---|---|---|---|---|
| [KeePassXC](keepassxc.md) | Offline, file-based encrypted password database | High | Low to Medium (no central administration) | Research complete |
| [Vaultwarden](vaultwarden.md) | Unofficial, self-hosted Bitwarden-compatible server | Medium to High | Low to Medium (community-supported) | Research complete |

Choose KeePassXC if you want no server to run; choose a server such as Vaultwarden if you
need multi-device sync and sharing and can operate HTTPS, backups, and updates reliably.
Not yet documented: machine-secrets vaults, key management, and secret-sprawl detection.
