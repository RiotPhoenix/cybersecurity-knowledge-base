---
tool: Vaultwarden
category: password-management
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://github.com/dani-garcia/vaultwarden
repository: https://github.com/dani-garcia/vaultwarden
requires_authorisation: false
---

# Vaultwarden

!!! info "Unofficial, community-maintained software"
    Vaultwarden is an **unofficial** server compatible with the Bitwarden client API. The
    project states that it "is not associated with Bitwarden or Bitwarden, Inc." It is not
    the official Bitwarden server, and Bitwarden does not support or certify it. Report
    problems to the Vaultwarden project, **not** to Bitwarden's support channels.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://github.com/dani-garcia/vaultwarden> (the project's home is its GitHub repository and wiki) |
| Source repository | <https://github.com/dani-garcia/vaultwarden> |
| Licence | AGPL-3.0 |
| Supported operating systems | Linux container images (official); native builds from source; third-party packages for several distributions |
| Maintenance status | Active: 1.37.5 released 2026-11-01, including security fixes. Checked 2026-11-12 |
| Category | Password and Secret Management |
| Personal suitability | Medium to High: lightweight and capable for households, if you can run a server, HTTPS, backups, and updates reliably |
| Enterprise suitability | Low to Medium: technically capable, but community-supported with no vendor contract, SLA, or certification; evaluate governance and recovery risks carefully |
| Tested versions | Not tested |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

Vaultwarden is a self-hosted password-manager server written in Rust. It implements a
"nearly complete" version of the Bitwarden client API, so the official Bitwarden apps,
browser extensions, and CLI can connect to it, and it serves a web vault. It was previously
called `bitwarden_rs`. It is designed to be much lighter than the official Bitwarden
self-hosted server, typically running as a single container with an SQLite database.

The project README notes that one active maintainer is employed by Bitwarden and contributes
in a personal capacity, independent of Bitwarden. That does not make Vaultwarden a Bitwarden
product.

**Vaultwarden vs the official Bitwarden server:**

| | Vaultwarden | Official Bitwarden self-hosted server |
|---|---|---|
| Maintainer | Community (Vaultwarden project) | Bitwarden, Inc. |
| Support | Community channels (GitHub, Matrix, Discourse) | Vendor support with commercial plans |
| Footprint | Single lightweight container | Multiple services, larger footprint |
| Client compatibility | Uses Bitwarden clients; client updates can occasionally require server updates | Developed alongside the clients |

## Features and capabilities

From the project README: personal vaults, Send, attachments, website icons, personal API key,
organisations (collections, member roles, groups, event logs, admin password reset, directory
connector, policies), two-factor authentication (authenticator apps, e-mail, FIDO2 WebAuthn,
YubiKey, Duo), emergency access, and an admin page. SSO via OpenID Connect is available
(`SSO_ENABLED`).

- **Databases:** SQLite (default; "the most widely used/tested, and recommended for most
  users"), MySQL/MariaDB, and PostgreSQL. Migrating from SQLite to another backend is
  described as "unsupported and has not been robustly tested".
- **Built-in protections:** login and admin rate limiting (defaults: one login per 60 seconds
  on average with bursts of 10; admin one per 300 seconds with bursts of 3), and WebSocket
  notifications on the main port.

Limitations:

- **Unofficial:** compatibility depends on the project keeping pace with Bitwarden client
  changes. For example, the 1.37.4 release notes say older Bitwarden CLI versions can no longer
  receive Sends.
- **Small maintainer team, community support only.**
- **Operator responsibility:** HTTPS, backups, updates, monitoring, and incident response are
  yours. A neglected self-hosted vault is a high-value, internet-exposed target.

## System requirements

- **Runtime:** a container engine (Docker or Podman) on Linux is the documented route. For
  non-container installs, the wiki suggests extracting the binary from the official images,
  building from source, or using a third-party package.
- **Resources:** light. A small VM or single-board computer is typical for a household.
  No official minimum is stated.
- **Network:** a DNS name and **HTTPS**. The web vault "requires the use of HTTPS and a secure
  context for the Web Crypto API". The project recommends a reverse proxy for TLS rather
  than Vaultwarden's built-in TLS. E-mail (SMTP) is needed for invitations, verification,
  and many notifications.
- **Privileges:** administrator access to install the container engine and reverse proxy.
  Vaultwarden itself can run as a non-root user (see [Security hardening](#security-hardening)).

## Installation

The official images are `vaultwarden/server` (Docker Hub), `ghcr.io/dani-garcia/vaultwarden`,
and `quay.io/vaultwarden/server`. Tags: `latest` (latest release, which the project says is
"recommended for most users"), specific versions such as `1.37.5`, `-alpine` variants, and
`testing`. `testing` tracks unreleased commits and is not for production.

### Distribution packages

The Fedora 44 repositories included a `vaultwarden` package. On 2026-11-12 it was **version
1.37.1**, which predates the security fixes published in 1.37.4 and 1.37.5. The Vaultwarden
wiki lists distribution packages as third-party: "As these packages are not maintained or
controlled by vaultwarden, they can lag behind official releases". Debian stable has no
package. Prefer the official container images unless your distribution package is current.

### Container installation (Docker Compose)

Prerequisites: Docker Engine with the Compose plugin (or Podman with a Compose
implementation), installed following your platform's official instructions; a DNS name such
as `vault.example.com` pointing at the host; and a reverse proxy for HTTPS (example below).

**Step 1: create a directory** for the deployment and its persistent data:

```bash
sudo mkdir -p /srv/vaultwarden/vw-data
cd /srv/vaultwarden
```

`sudo` is needed because `/srv` is owned by root. All vault data lives in `vw-data/`, which is
mounted at `/data` in the container. Back it up (see below).

**Step 2: create `compose.yaml`.** This is based on the project README's example. It publishes
the container **only on the loopback interface**, so it is reachable solely through the reverse
proxy on the same host:

```yaml
services:
  vaultwarden:
    image: vaultwarden/server:latest    # or pin a version, e.g. vaultwarden/server:<VERSION>
    container_name: vaultwarden
    restart: unless-stopped
    environment:
      DOMAIN: "https://vault.example.com"
      SIGNUPS_ALLOWED: "true"           # temporary: set to "false" after creating accounts
      SHOW_PASSWORD_HINT: "false"
    volumes:
      - ./vw-data/:/data/
    ports:
      - 127.0.0.1:8000:80
```

**Step 3: start it:**

```bash
sudo docker compose up -d
sudo docker compose logs -f vaultwarden    # Ctrl+C to stop following
```

### HTTPS with a reverse proxy

The wiki's [proxy examples](https://github.com/dani-garcia/vaultwarden/wiki/Proxy-examples)
cover Caddy, nginx, Apache, Traefik, HAProxy, and others. A minimal Caddy configuration,
following the wiki's example, is shown below. Caddy obtains and renews certificates
automatically when the name is publicly resolvable; see Caddy's
[automatic HTTPS](https://caddyserver.com/docs/automatic-https) documentation.

```text
vault.example.com {
    reverse_proxy 127.0.0.1:8000 {
        header_up X-Real-IP {remote_host}
    }
}
```

Vaultwarden reads the client address from the `X-Real-IP` header by default (`IP_HEADER`). That
matters for rate limiting and Fail2Ban. Any proxy you use must also pass WebSocket `Upgrade`
and `Connection` headers for live sync notifications.

### Verify the installation

```bash
sudo docker compose ps                      # vaultwarden should be "running" / "healthy"
curl -fsS -o /dev/null -w '%{http_code}\n' https://vault.example.com/   # expect 200
```

Then open `https://vault.example.com` in a browser, create your account, and log in with a
Bitwarden client by setting its server URL to your domain (self-hosted option).

### Updating and removal

Read the [release notes](https://github.com/dani-garcia/vaultwarden/releases) first, because
they flag security fixes and compatibility changes. **Back up before every update**, then:

```bash
cd /srv/vaultwarden
sudo docker compose pull
sudo docker compose up -d
```

To roll back, restore the backup taken before the update and pin the previous version tag in
`compose.yaml`. Database migrations may not be reversible, which is why the backup comes first.
The wiki warns that cleanup commands such as `docker system prune -f` can remove unrelated
containers.

**Removal:** `sudo docker compose down` stops the service. The data in `vw-data/` stays until you
delete it. Delete it only after confirming users have exported or migrated their vaults.

## Initial configuration

1. **Create the accounts you need** while `SIGNUPS_ALLOWED` is `"true"`, ideally before the
   service is reachable from the internet. If the host must be publicly reachable earlier (for
   example so the reverse proxy can obtain a certificate), create the accounts immediately after
   the first start and close registration straight away, so the window for strangers to
   register is as short as possible.
2. **Close registration.** Set `SIGNUPS_ALLOWED: "false"` and recreate the container
   (`sudo docker compose up -d`). By default, "anyone who can access your instance can register".
   Organisation owners can still invite users while signups are off. Set
   `INVITATIONS_ALLOWED: "false"` to prevent that too. Alternatively, use
   `SIGNUPS_DOMAINS_WHITELIST` to allow only specific e-mail domains (it overrides
   `SIGNUPS_ALLOWED`).
3. **Configure SMTP** (`SMTP_HOST`, `SMTP_FROM`, `SMTP_PORT`, `SMTP_SECURITY`, `SMTP_USERNAME`,
   `SMTP_PASSWORD`) so invitations, e-mail verification, and new-device notices work. Supply the
   SMTP password through a file (`SMTP_PASSWORD_FILE`) or a protected environment file, not in a
   world-readable compose file.
4. **Leave the admin page disabled unless you need it.** It is disabled when `ADMIN_TOKEN` is not
   set. If you enable it, use an Argon2 PHC hash generated with the built-in command (the wiki
   documents `docker run --rm -it vaultwarden/server /vaultwarden hash`), not a plain-text token,
   and follow the wiki's rules on escaping `$` characters in Compose files. Settings saved from
   the admin page go into `config.json`, which overrides environment variables.
5. **Require two-step login** for every user (authenticator app or FIDO2 key) through user
   guidance or organisation policies.

## Security hardening

From the project's [Hardening Guide](https://github.com/dani-garcia/vaultwarden/wiki/Hardening-Guide)
and configuration template, with reasons:

| Measure | Why |
|---|---|
| Keep up with releases; subscribe to repository releases or security advisories. | 1.37.4 and 1.37.5 fixed advisories (organisation member revocation, emergency access, website icons). |
| Terminate HTTPS at a reverse proxy; do not expose port 80 of the container directly. | Protects credentials and session tokens in transit, and the web vault requires a secure context. |
| Disable open registration (`SIGNUPS_ALLOWED=false`), and invitations if not needed. | Prevents strangers creating accounts on an internet-facing server. |
| Keep password hints off (`SHOW_PASSWORD_HINT=false`; consider `PASSWORD_HINTS_ALLOWED=false`). | The template warns that showing hints without SMTP gives "unauthenticated access to potentially sensitive data". |
| Leave the admin page disabled, or protect it with a hashed token. Never set `DISABLE_ADMIN_TOKEN` unless another authentication layer protects `/admin`. | The admin page controls all users and settings. |
| Run the container as a non-root user (`user: "1000:1000"` in Compose, or `docker run -u 1000:1000`) with `vw-data/` owned by that user. | The default image runs as root. The Hardening Guide recommends a non-root user. |
| Mount only the data directory, with certificate files read-only if used. | Limits what a compromised process can change. |
| Enable file logging (`LOG_FILE`) and Fail2Ban for failed logins and admin attempts. | Adds IP banning on top of the built-in rate limits. With Docker, Fail2Ban must act on the forwarding chain, as the wiki explains. |
| Redact the `access_token` query parameter in reverse-proxy logs. | The Hardening Guide notes that notification requests put the token in the URL. |
| Consider `DISABLE_ICON_DOWNLOAD=true` or a different `ICON_SERVICE`. | By default the server fetches website icons itself (`ICON_SERVICE=internal`), making outbound requests to sites stored in vaults. A 1.37.5 advisory concerned this feature. |
| Protect backups as carefully as the server. | Vault items are encrypted by the clients, but the database also holds account metadata, and attachments and configuration are sensitive. |

## Practical usage examples

Illustrative examples, not executed for this entry. `vault.example.com` and paths are
placeholders.

### Personal and home-lab use

**Self-host a household vault.** Run the Compose deployment above on a home server, create
accounts for each household member, then close registration. Create an organisation with a
"Household" collection for shared credentials such as the broadband account or streaming
services. Each person keeps a personal vault for everything else.

**Keep it off the internet.** For many households, the simplest hardening is not to expose the
server publicly at all. Reach it over a home VPN when away. The service still needs a trusted
HTTPS certificate for the clients and web vault to work properly.

**Back up the vault.** The wiki lists `db.sqlite3` and `attachments/` as required, `config.json`
and `rsa_key*` as recommended, and `sends/` and `icon_cache/` as optional. A consistent SQLite
copy (requires the `sqlite3` tool on the host, because the image does not include it), followed
by an encrypted archive:

```bash
cd /srv/vaultwarden
sudo mkdir -p /srv/backups/vaultwarden
sudo sqlite3 vw-data/db.sqlite3 ".backup '/srv/backups/vaultwarden/db-$(date '+%Y%m%d-%H%M').sqlite3'"
sudo tar -C /srv/vaultwarden -czf /srv/backups/vaultwarden/files-$(date +%F).tar.gz \
  vw-data/attachments vw-data/config.json vw-data/rsa_key*
gpg --symmetric --cipher-algo AES256 /srv/backups/vaultwarden/files-$(date +%F).tar.gz   # prompts for a passphrase
```

Adjust the file list to what exists in your data directory: `config.json` exists only if the
admin page has saved settings. The wiki also documents `/vaultwarden backup` inside the
container (since 1.32.1) and advises against relying on filesystem or VM snapshots. Copy
encrypted backups off the host, and **test a restore**. The wiki's restore procedure is: stop
Vaultwarden, replace the files in the data directory, and delete any existing
`db.sqlite3-wal` file when restoring from a `.backup` copy.

### Enterprise use

**Evaluate self-hosted password infrastructure.** Run Vaultwarden in a test environment and
assess it against your requirements before any production decision:

- **Support:** who fixes a critical bug at 02:00? There is no vendor, so the answer is your
  own team plus the community.
- **Governance:** do organisation policies, event logs, and SSO (OIDC) meet your audit and
  access-control requirements? Test them.
- **Recovery:** practise full restores, loss of the host, and recovery of user access, including
  the effect of users forgetting master passwords. The server cannot decrypt vaults.
- **Operations:** patch cadence, monitoring, high availability (external MySQL or PostgreSQL),
  and incident response for an internet-facing credential store.
- **Client compatibility:** confirm that the Bitwarden client versions your users run work with
  your Vaultwarden version, and plan how you will handle client auto-updates.

Record the outcome. Many organisations conclude that a vendor-supported product, such as
Bitwarden's own offering, is more appropriate for production.

## Enterprise deployment considerations

- **Unofficial status.** There is no contract, SLA, security certification, or vendor
  escalation. Bitwarden support will not help with a Vaultwarden server. Risk acceptance
  should be explicit and owned.
- **Identity integration.** SSO via OpenID Connect (`SSO_ENABLED`) and the Bitwarden Directory
  Connector are listed as supported. Validate them against your identity provider and offboarding
  process before relying on them.
- **High availability and scale.** SQLite suits a single instance. HA designs need an external
  MySQL/MariaDB or PostgreSQL database and shared attachment storage. These are less widely
  used than SQLite, according to the project.
- **Data protection.** Clients encrypt vault data, but you are responsible for server
  hardening, backups (encrypted, off-site, tested), log retention, and the confidentiality of
  account metadata.
- **Change management.** Pin image versions, test updates in staging (including current client
  versions), and keep rollback backups. Watch security advisories and patch quickly.
- **External services.** Mobile push notifications (`PUSH_ENABLED`) require an installation ID and
  key from Bitwarden's hosting service, which creates a dependency on a Bitwarden-operated service.
  Icon fetching makes outbound requests. Review both against your data-flow policies.
- **Exit plan.** Users can export their vaults with Bitwarden clients. Document how you would
  migrate to another product.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Web vault loads but login/registration fails with crypto errors | Not served over HTTPS (no secure context). Put it behind an HTTPS reverse proxy and set `DOMAIN` to the `https://` URL. |
| Links in e-mails or attachments point to the wrong address | `DOMAIN` is missing or wrong. Set it to the exact external URL. |
| New users cannot register | `SIGNUPS_ALLOWED` is `false` (intended). Invite them from an organisation (requires SMTP for e-mailed invitations), or temporarily allow signups. |
| Changes to environment variables have no effect | `config.json` (written by the admin page) overrides environment variables, or the container was not recreated. Edit or remove the setting in the admin page, then run `docker compose up -d`. |
| Rate limiting or Fail2Ban bans the proxy's address | The proxy does not send `X-Real-IP` (or the header named in `IP_HEADER`). Configure the header in the proxy. |
| Clients do not update live | WebSocket headers not passed by the proxy. Add `Upgrade`/`Connection` handling as in the proxy examples. (Port 3012 is no longer used; WebSockets run on the main port since 1.29.0.) |
| Admin page warns about a plain-text token | Replace `ADMIN_TOKEN` with an Argon2 PHC hash from `/vaultwarden hash`. |
| A Bitwarden client stopped working after it updated | A client-server compatibility change. Check the Vaultwarden release notes and update the server. |
| Container cannot write data after switching to a non-root user | `vw-data/` is still owned by root. Change ownership to the configured UID:GID. |

## Alternatives and related tools

- **Bitwarden** (official cloud service or official self-hosted server): vendor-supported and
  commercially licensed for business use.
- [KeePassXC](keepassxc.md): offline, file-based password manager with no server to run.
- **Passbolt** and other self-hosted team password managers, with different trust and
  client models.
- Secrets vaults (for example HashiCorp Vault or OpenBao) for machine and application secrets,
  rather than human passwords.

## References

### Official documentation

- [Vaultwarden repository and README](https://github.com/dani-garcia/vaultwarden)
- [Vaultwarden wiki](https://github.com/dani-garcia/vaultwarden/wiki)
- [Configuration overview](https://github.com/dani-garcia/vaultwarden/wiki/Configuration-overview)
  and the [configuration template (.env.template)](https://github.com/dani-garcia/vaultwarden/blob/main/.env.template)
- [Which container image to use](https://github.com/dani-garcia/vaultwarden/wiki/Which-container-image-to-use)

### Installation references

- [Using Docker Compose](https://github.com/dani-garcia/vaultwarden/wiki/Using-Docker-Compose)
- [Enabling HTTPS](https://github.com/dani-garcia/vaultwarden/wiki/Enabling-HTTPS) and
  [proxy examples](https://github.com/dani-garcia/vaultwarden/wiki/Proxy-examples)
- [Updating the image](https://github.com/dani-garcia/vaultwarden/wiki/Updating-the-vaultwarden-image)
- [Third-party packages](https://github.com/dani-garcia/vaultwarden/wiki/Third-party-packages)
- [Releases](https://github.com/dani-garcia/vaultwarden/releases)

### Security and deployment references

- [Hardening Guide](https://github.com/dani-garcia/vaultwarden/wiki/Hardening-Guide)
- [Enabling the admin page](https://github.com/dani-garcia/vaultwarden/wiki/Enabling-admin-page)
- [Disabling registration](https://github.com/dani-garcia/vaultwarden/wiki/Disable-registration-of-new-users)
- [Backing up your vault](https://github.com/dani-garcia/vaultwarden/wiki/Backing-up-your-vault)
- [Fail2Ban setup](https://github.com/dani-garcia/vaultwarden/wiki/Fail2Ban-Setup)
- [SMTP configuration](https://github.com/dani-garcia/vaultwarden/wiki/SMTP-Configuration)
- [Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https)

### Verification notes

- **Sources checked:** 2026-11-12, against the pages listed above. Default values come from
  `.env.template` on the `main` branch, which the wiki describes as documentation, "not a
  guarantee" (the source of truth is the code).
- **Release:** 1.37.5, published 2026-11-01 (GitHub releases API).
- **Distribution packages:** the Fedora 44 `vaultwarden` package was 1.37.1 (`dnf`). Debian
  stable had none (packages.debian.org).
- **Conflict noted:** the wiki's 2021 *Password hint display* page implies hints are shown when
  SMTP is not configured, while the current template documents `SHOW_PASSWORD_HINT` defaulting to
  `false`. This entry sets it explicitly to `false` either way.
- **Not executed:** Vaultwarden was not deployed for this entry. The Compose file and backup
  commands are adapted from the README and wiki and are illustrative.
- **Unresolved:** behaviour of the non-root configuration on rootless Podman; the output location
  of the built-in `/vaultwarden backup` command.
