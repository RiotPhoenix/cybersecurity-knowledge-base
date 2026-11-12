---
tool: OpenBao
category: password-management
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://openbao.org/
repository: https://github.com/openbao/openbao
requires_authorisation: false
---

# OpenBao

!!! danger "Development mode is never a deployment"
    `bao server -dev` starts an unsealed, in-memory server without TLS that **loses all data on
    restart** and logs a root token. The OpenBao documentation says: "Never, ever, ever run a
    'dev' mode server in production." Use it only for short, local experiments with throw-away
    data. Everything below except the clearly labelled learning example describes a real
    (non-dev) deployment.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://openbao.org/> |
| Source repository | <https://github.com/openbao/openbao> |
| Licence | MPL-2.0 |
| Supported operating systems | Linux (official `.deb`, `.rpm`, and archive packages; Fedora and EPEL packages), macOS, Windows, FreeBSD, NetBSD, OpenBSD; official container images; Kubernetes via Helm |
| Maintenance status | Active: 2.7.2 released 2026-10-26 (2.6.5 on the same day). Only the latest release is supported. Checked 2026-11-12 |
| Category | Password and Secret Management |
| Personal suitability | Medium: excellent for learning secrets management, but a real deployment needs TLS, unseal-key custody, backups, and care |
| Enterprise suitability | High: a community-governed secrets manager suited to centralised secrets and credential lifecycle management, if operated with mature processes |
| Tested versions | Not yet tested |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

OpenBao is an "identity-based secrets and encryption management system". It stores secrets
(API keys, passwords, certificates, encryption keys), issues short-lived credentials on demand,
and performs encryption as a service, with every access gated by authentication, path-based
policies, and an audit trail. Its website describes it as a "community-driven secrets manager and
fork of Vault managed by the Linux Foundation's OpenSSF". Its command-line tool is `bao`.

Core workflow, from the documentation:

1. **Authenticate**: a client (person, machine, or application) logs in with an auth method
   such as userpass, AppRole, OIDC, LDAP, Kubernetes, or TLS certificates.
2. **Validate**: OpenBao checks the identity against the configured source and issues a
   **token** associated with **policies**.
3. **Authorise**: policies define which paths and operations the token may use.
4. **Access**: the client reads secrets, requests credentials, or calls encryption endpoints.

OpenBao is for **machine and application secrets** and operator access. It is not a
replacement for a personal password manager such as [KeePassXC](keepassxc.md) or
[Vaultwarden](vaultwarden.md), which are designed around people storing their own passwords.

## Features and capabilities

- **Secrets engines:** key/value (KV version 2 keeps versions), databases (dynamic and rotated
  credentials), PKI (certificate issuance), Transit (encryption as a service), SSH, and others.
- **Authentication methods:** tokens, userpass, AppRole, JWT/OIDC, LDAP, Kubernetes, TLS
  certificates, and more.
- **Policies** written in HCL, granting capabilities (`read`, `create`, `update`, `delete`,
  `list`, and so on) on paths. Access is denied unless a policy grants it.
- **Leases and revocation.** Dynamic secrets have a time-to-live and can be revoked individually
  or by prefix.
- **Audit devices** that log every request and response (with secrets HMAC-hashed) to a file,
  syslog, a socket, or an HTTP endpoint. In 2.7, audit devices are **declared in the server configuration**:
  creating them through the API is disabled by default (`unsafe_allow_api_audit_creation =
  false`).
- **Seal and unseal.** Data is encrypted at rest. On start-up the server is sealed until enough
  **unseal key shares** (Shamir's Secret Sharing, five shares and a threshold of three by default)
  are supplied, or an **auto-unseal** seal (cloud KMS, PKCS#11 HSM, Transit, or a static key) does
  it automatically.
- **Storage backends** in 2.7: **Integrated Storage (Raft)**, **PostgreSQL**, **PebbleDB** (single
  server, no HA), and in-memory. The `file` backend was **removed in 2.7.0**.
- **High availability** with Raft (multiple OpenBao nodes) or PostgreSQL (`ha_enabled`).
- **Web UI** (`ui = true`), HTTP API, CLI, and OpenBao Agent and Proxy for applications.

Operational limitations:

- **Unseal key custody is your problem.** If you lose enough unseal key shares (or the auto-unseal
  key), the data cannot be decrypted. There is no vendor recovery.
- **It becomes critical infrastructure.** Applications that fetch secrets at start-up fail when
  OpenBao is sealed or down. Plan for availability before depending on it.
- **Support model.** Community-maintained releases, roughly monthly. The support policy says the
  latest release does not reach end of life, but users on older releases will be asked to test
  the latest release, so plan to keep up.
- **Not compatible with every Vault Enterprise feature.** OpenBao is a fork of the open-source
  codebase. Check feature parity for anything you rely on before migrating.

## System requirements

- **Platforms:** release archives for Linux, macOS, Windows, FreeBSD, NetBSD, and OpenBSD on
  several architectures; `.deb`, `.rpm`, and Arch packages; container images based on Alpine
  (`ghcr.io/openbao/openbao`, also on Quay and Docker Hub) and on Red Hat UBI (`openbao-ubi`).
- **Resources:** no official minimum is published. A single-node home-lab server is light. Size
  production clusters from load testing.
- **Privileges:** installation needs administrator rights. The Fedora package runs the server as
  the unprivileged `openbao` user under a hardened systemd unit.
- **Swap:** the documentation recommends disabling swap for the OpenBao process, or encrypting
  swap, because secrets in memory could otherwise be paged to disk. The packaged systemd unit
  sets `MemorySwapMax=0`.
- **Network:** clients reach the API on 8200/TCP by default. Cluster members also use a cluster
  port (8201/TCP in the documentation's examples). TLS certificates for the API listener.

## Installation

| Method | Use when | Notes |
|---|---|---|
| Fedora repository / EPEL (`dnf install openbao`) | Fedora or RHEL-compatible hosts | Fedora 44 shipped **2.6.5** on 2026-11-12, behind the latest 2.7.2. See the storage warning below. |
| Official `.deb` / `.rpm` from the release page | Debian, Ubuntu, other Linux | Signed with GPG and Sigstore. Includes a systemd unit and default configuration. |
| Release archive (`.tar.gz`, or `.zip` on Windows) | Any platform | A single `bao` binary. |
| Homebrew (`brew install openbao`), FreeBSD (`pkg install openbao`) | macOS, FreeBSD | Listed in the official installation page. |
| Container images | Containers and Kubernetes | `ghcr.io/openbao/openbao`; Helm chart for Kubernetes. |
| Source build (`make dev`) | Development only | The documentation says these instructions are for a **development** build. |

### Fedora

```bash
sudo dnf install openbao
```

The package installs `/usr/bin/bao`, the `openbao.service` unit (running as user `openbao`, with
`ProtectSystem=full`, `PrivateTmp`, `NoNewPrivileges`, and `MemorySwapMax=0`), configuration in
`/etc/openbao.d/openbao.hcl`, and data under `/var/lib/openbao`.

!!! warning "Fedora's packaged configuration uses the removed `file` backend"
    The Fedora 2.6.5 package's default `openbao.hcl` uses `storage "file"`, listens on
    `127.0.0.1:8200` with `tls_disable = 1`, and enables the UI. The `file` backend is deprecated
    in 2.6 and **removed in 2.7.0**, and upstream's 2.7 packages default to `pebbledb` instead.
    Do not build a new deployment on `file`: replace the storage stanza before initialising (see
    [Initial configuration](#initial-configuration)). If you already have data in `file`
    storage, migrate it with `bao operator migrate` (which still reads `file` until 2.8.0)
    **before** upgrading to 2.7.

### Debian and Ubuntu (official package)

Download the package, its checksum file, and signature from the GitHub release page, verify, and
install. The release publishes `checksums.txt`, a GPG signature (`checksums.txt.gpgsig`), the
signing key (`openbao-gpg-pub-20240618.asc`), and Sigstore bundles:

```bash
VERSION=2.7.2
BASE=https://github.com/openbao/openbao/releases/download/v${VERSION}
curl -fsSLO "${BASE}/openbao_${VERSION}_linux_amd64.deb"
curl -fsSLO "${BASE}/checksums.txt"
curl -fsSLO "${BASE}/checksums.txt.gpgsig"
curl -fsSLO "${BASE}/openbao-gpg-pub-20240618.asc"
gpg --import openbao-gpg-pub-20240618.asc
gpg --verify checksums.txt.gpgsig checksums.txt
sha256sum --check --ignore-missing checksums.txt
sudo apt install ./openbao_${VERSION}_linux_amd64.deb
```

Compare the imported key's fingerprint with one published through an independent channel (for
example the project website or announcements) before trusting the signature.

### Windows and macOS

Download `openbao_<VERSION>_windows_amd64.zip` (or `darwin_*.tar.gz`), verify it against
`checksums.txt`, and place `bao.exe` (or `bao`) on your `PATH`. On macOS, `brew install openbao`
is listed in the official installation page. Windows and macOS are reasonable for the CLI and for
learning. For servers, prefer Linux with systemd.

### Containers

```bash
docker pull ghcr.io/openbao/openbao:2.7.2
```

For a non-dev container deployment you must provide: a configuration file (mounted read-only),
a **persistent volume** for the storage path, TLS certificate and key files (read-only, from a
secret store), the API port published on a specific interface only, and a plan for unsealing after
every restart. You are responsible for updating the image. On Kubernetes, use the official Helm
chart documented under *Platform*.

### Learning only: development server

<!-- quality-allow: dev-mode-server -- learning-only example on loopback with throw-away data; never for real secrets -->
```bash
bao server -dev
```

This listens on `127.0.0.1:8200` without TLS, is already unsealed, keeps everything in memory, and
prints a root token. Stop it with Ctrl+C when you finish. Never store real secrets in it, and
never expose it beyond loopback.

### Verify the installation

```bash
bao version
systemctl status openbao        # after configuring and starting the service
bao status                      # with BAO_ADDR set (see below)
```

`bao status` reports `Initialized`, `Sealed`, the storage type, and HA mode. Before initialisation
it shows `Initialized false`.

### Updating and removal

- **Read the changelog before every update.** OpenBao releases include security fixes (2.7.2 fixed
  several advisories) and removals (the `file` backend in 2.7.0).
- **Back up first** (Raft snapshot, PostgreSQL backup, or a copy of the PebbleDB directory taken
  while the service is stopped), and confirm you hold enough unseal keys.
- **Single node:** update the package or image and restart. The server comes back **sealed** unless
  you use auto-unseal, so unseal it again.
- **HA clusters:** follow the HA upgrade guide: upgrade and unseal each standby node in turn,
  confirming with `bao status` that it reports the new version and `standby` mode, then let an
  upgraded standby take over from the active node. Check `bao operator raft list-peers` on Raft
  clusters.
- **Rollback:** restore from the pre-upgrade backup with the previous version. Do not assume a
  newer storage format can be read by an older version.
- **Removal:** stop the service and remove the package. Data in `/var/lib/openbao` and any audit
  logs remain. Destroy them deliberately, together with unseal keys, once they are no longer needed.

## Initial configuration

A single-node server with Raft storage, TLS, and a file audit device. `bao.lab.example` and
`192.0.2.30` are placeholders. Replace the Fedora package's default `/etc/openbao.d/openbao.hcl`:

```hcl
ui           = true
api_addr     = "https://bao.lab.example:8200"
cluster_addr = "https://bao.lab.example:8201"

storage "raft" {
  path    = "/var/lib/openbao/data"
  node_id = "bao-1"
}

listener "tcp" {
  address       = "192.0.2.30:8200"
  tls_cert_file = "/etc/openbao.d/tls/tls.crt"
  tls_key_file  = "/etc/openbao.d/tls/tls.key"
}

audit "file" "to-file" {
  description = "Audit log on local disk"
  options {
    file_path = "/var/log/openbao/audit.log"
  }
}
```

Why Raft here: it is production-ready, needs no extra software, supports snapshots for backup,
and lets you add nodes later. The OpenBao documentation notes that it recommends **PostgreSQL** to
operators new to OpenBao as "an easier storage backend to safely operate than Raft". Choose
PostgreSQL if you already run it well.

**Step 1: Prepare directories and certificates.** Issue a certificate for `bao.lab.example` from your
   lab CA, place it with its key in `/etc/openbao.d/tls/` (key readable only by `openbao`), and
   create the audit log directory:

```bash
sudo install -d -o openbao -g openbao -m 0750 /var/lib/openbao/data /var/log/openbao
sudo chown root:openbao /etc/openbao.d/tls/tls.key
sudo chmod 0640 /etc/openbao.d/tls/tls.key
sudo systemctl enable --now openbao
```

**Step 2: Point the CLI at the server and trust the CA:**

```bash
export BAO_ADDR="https://bao.lab.example:8200"
export BAO_CACERT="$HOME/lab-ca.pem"
bao status
```

**Step 3: Initialise** (once per cluster). By default this creates five unseal key shares with a
   threshold of three, and an initial root token. Consider `-pgp-keys` so each share is encrypted
   to the person who will hold it:

```bash
bao operator init
```

   Record each unseal key share and the root token **offline** and **separately** (for example in
   different password managers or sealed envelopes held by different people). Never store them
   in a repository, a ticket, chat, or the same machine as the server. This output is the most
   sensitive material OpenBao ever produces.

**Step 4: Unseal** by entering three different shares (each `bao operator unseal` prompts for one):

```bash
bao operator unseal
bao operator unseal
bao operator unseal
```

**Step 5: Log in with the root token** (`bao login`, which prompts), create an administrator policy and
   a non-root way to authenticate (for example userpass for yourself, AppRole for machines), test
   it, then **revoke the root token** with `bao token revoke -self`. Generate a new root token
   with `bao operator generate-root` and the unseal-key holders only when genuinely needed.
**Step 6: Confirm auditing works:** after any request, `/var/log/openbao/audit.log` should contain a
   JSON entry. If every audit device fails, OpenBao refuses requests, which is why the audit log
   directory needs monitoring for space.

## Security hardening

| Measure | Why |
|---|---|
| Never use `-dev` beyond local experiments. | Dev mode is unsealed, in-memory, without TLS, and authenticated with a root token. |
| Enable TLS on every listener that is not strictly loopback-only (the packaged `tls_disable = 1` is acceptable only on `127.0.0.1`), and keep `tls_min_version` at TLS 1.2 or higher (default `tls12`). | Tokens and secrets travel in API requests. |
| Separate unseal key shares among several trusted people or locations, or use auto-unseal with an HSM or KMS whose access is itself tightly controlled. | No single person or stolen backup should be able to unseal. |
| Revoke the initial root token after setup, and use `generate-root` only for emergencies. | Root tokens bypass all policies. |
| Write least-privilege policies per application and per team, with short token TTLs. | Limits the damage of a leaked token. |
| Declare audit devices in the configuration, ship audit logs to a separate system, and keep `unsafe_allow_api_audit_creation` disabled except temporarily. | Preserves an independent record of who accessed which secret. |
| Disable swap for the process (`MemorySwapMax=0` in the packaged unit) or encrypt swap. | Prevents secrets being written to disk in memory pages. |
| Run on a dedicated host or VM, restrict SSH, and expose 8200 only to the clients that need it. | The server holds every secret. Its host is the highest-value target in the lab. |
| Protect backups and snapshots like the server itself, and test restores. | Snapshots contain the encrypted data. With the unseal keys they reveal everything. |
| Follow releases and security advisories, and upgrade promptly. | Only the latest release is supported. |

## Practical usage examples

Illustrative examples against the server configured above. Values are placeholders. Not executed
for this entry.

### Personal and home-lab use

**Manage secrets for self-hosted services.** Store the database password for a lab application in
KV version 2, reading the value from standard input so it never appears in shell history or the
process list:

```bash
bao secrets enable -path=secret kv-v2
read -rsp 'Database password: ' DBPW; echo
printf '%s' "$DBPW" | bao kv put -mount=secret homelab/grafana db_password=-; unset DBPW
bao kv get -mount=secret homelab/grafana
bao kv metadata get -mount=secret homelab/grafana     # versions kept by KV v2
```

**Learn policy-based access control.** Give one service read-only access to only its own secret,
and let it authenticate with AppRole:

```bash
cat > grafana-read.hcl << 'EOF'
path "secret/data/homelab/grafana" {
  capabilities = ["read"]
}
EOF
bao policy write grafana-read grafana-read.hcl
bao auth enable approle
bao write auth/approle/role/grafana token_policies=grafana-read token_ttl=1h token_max_ttl=4h
bao read auth/approle/role/grafana/role-id
bao write -f auth/approle/role/grafana/secret-id
```

Deliver the role ID and secret ID to the service through different channels. Then test that a
token issued to the role can read `homelab/grafana` but receives "permission denied" for any other
path. Read the audit log to see both requests.

### Enterprise use

**Centralised secrets management.** Replace secrets scattered across configuration files, CI
variables, and wikis with paths in OpenBao, organised by team and environment. Applications
authenticate with platform identities (Kubernetes service accounts, cloud identities, or TLS
certificates) instead of shared static secrets. Policies are code-reviewed and deployed from a
repository. Audit logs flow to the SIEM.

**Credential lifecycle management.** Use the database secrets engine to issue short-lived database
credentials per application instance, or to rotate static database account passwords on a
schedule. Use the PKI engine for short-lived internal TLS certificates. Revoke leases by prefix
during an incident (for example, every credential issued to a compromised application). Measure
progress by the number of long-lived static secrets that remain.

## Enterprise deployment considerations

- **High availability.** Run a Raft cluster of three or five nodes across failure domains, or
  OpenBao nodes in front of a highly available PostgreSQL cluster. Use a load balancer that
  respects the active and standby roles, and set `api_addr` and `cluster_addr` per node.
- **Unseal strategy.** Auto-unseal through an HSM (PKCS#11) or a cloud KMS removes manual unsealing
  after restarts but moves trust to that key service. With auto-unseal, initialisation produces
  **recovery keys** rather than unseal keys. Document custody of either.
- **Backup and recovery.** Schedule Raft snapshots (`bao operator raft snapshot save`) or PostgreSQL
  backups, encrypt and store them off-cluster, and rehearse restoring to an isolated environment,
  including unsealing with the real key holders.
- **Break-glass procedures.** Define how a root token is generated in an emergency, who must be
  present, and how its use is reviewed.
- **Governance.** Manage policies, auth methods, and secrets-engine configuration as code with
  review. Name an owner for every secrets path. Review policies regularly for over-broad grants.
- **Migration from Vault.** OpenBao is a fork. Plan migrations with care, check feature parity and
  storage compatibility for your Vault version, and test on a copy.
- **Support.** A community project under the Linux Foundation's OpenSSF, with roughly monthly
  releases and no contractual support from the project. Decide whether internal expertise or a third-party support
  arrangement is required.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `bao status` shows `Sealed true` after a restart | Expected without auto-unseal. Unseal with the threshold number of shares. |
| Server fails to start after upgrading to 2.7 | The configuration still uses `storage "file"`, which 2.7.0 removed. Restore the previous version, migrate with `bao operator migrate` to Raft (or PebbleDB), then upgrade. |
| CLI error `x509: certificate signed by unknown authority` | The client does not trust the server's CA. Set `BAO_CACERT` to the CA file. Do not disable verification. |
| CLI connects to `127.0.0.1:8200` instead of your server | `BAO_ADDR` is not set in the current shell. Export it. |
| `bao audit enable` returns an error | API-created audit devices are disabled by default in 2.7. Declare the device in the `audit` stanza of the configuration and reload (SIGHUP) or restart. |
| All requests fail after the audit disk filled | OpenBao blocks requests when it cannot write to any audit device. Free space, rotate audit logs, and monitor the disk. |
| "permission denied" for a request that should work | The token's policies do not cover the path. KV v2 data lives under `<mount>/data/<path>`, so policies must use that form. Check with `bao token capabilities <path>`. |
| Raft node cannot join | `cluster_addr` not reachable, TLS mismatch, or wrong `node_id`. Check connectivity on the cluster port and the server logs. |
| Lost unseal keys | Without the threshold number of shares (or the auto-unseal key), data cannot be recovered. Restore from a backup only helps if you still hold the keys for it. |

## Alternatives and related tools

- **HashiCorp Vault**: the project OpenBao was forked from, with commercial editions. Check its
  current licence terms against your intended use.
- **Infisical** and cloud-provider secret managers (AWS Secrets Manager, Azure Key Vault, Google
  Secret Manager): managed or alternative options (not yet documented here).
- [KeePassXC](keepassxc.md) and [Vaultwarden](vaultwarden.md): password managers for people rather
  than machines.
- [Security monitoring lab](../../environments/personal/security-monitoring-lab.md): uses OpenBao
  for lab service credentials.

## References

### Official documentation

- [OpenBao website](https://openbao.org/)
- [OpenBao documentation](https://openbao.org/docs/)
- [What is OpenBao?](https://openbao.org/docs/what-is-openbao/)
- [Seal and unseal concepts](https://openbao.org/docs/concepts/seal/)
- [Policies](https://openbao.org/docs/concepts/policies/)
- [Source repository](https://github.com/openbao/openbao)

### Installation references

- [Installing OpenBao](https://openbao.org/docs/install/)
- [Downloads](https://openbao.org/downloads/)
- [Releases](https://github.com/openbao/openbao/releases)
- [Changelog](https://github.com/openbao/openbao/blob/main/CHANGELOG.md)
- [Container images (GHCR)](https://github.com/openbao/openbao/pkgs/container/openbao)

### Security and deployment references

- ["Dev" server mode](https://openbao.org/docs/concepts/dev-server/)
- [Storage backends](https://openbao.org/docs/configuration/storage/)
- [Integrated Storage (Raft) backend](https://openbao.org/docs/configuration/storage/raft/)
- [TCP listener and TLS](https://openbao.org/docs/configuration/listener/tcp/)
- [Declarative audit devices](https://openbao.org/docs/configuration/audit/)
- [`operator migrate`](https://openbao.org/docs/commands/operator/migrate/)
- [Support and release end-of-life policy](https://openbao.org/community/policies/support/)
- [Upgrading HA clusters](https://openbao.org/docs/guides/upgrade/ha/)
- [Blocked audit devices](https://openbao.org/docs/audit/#blocked-audit-devices)

### Verification notes

- **Sources checked:** 2026-11-12. Documentation was read from the `website/content` sources at the
  `v2.7.2` tag of the official repository.
- **Releases:** 2.7.2 and 2.6.5 published 2026-10-26 (GitHub releases API). The 2.7.2 release assets
  include `.deb`, `.rpm`, archives, `checksums.txt` with GPG and Sigstore signatures, and the GPG
  public key file.
- **Storage:** `internal/command/commands.go` at `v2.7.2` registers only `inmem`, `inmem_ha`, `raft`,
  `postgresql`, and `pebbledb`. The changelog records the removal of the `file` backend in 2.7.0, the
  switch of packaged default configuration to `pebbledb` in 2.7.1, and that `file` remains readable
  by `bao operator migrate` until 2.8.0.
- **Fedora package:** `openbao` 2.6.5-1.fc44 (`dnf repoquery`). Its unit file and default
  `openbao.hcl` were inspected from the downloaded RPM without installing it.
- **Contradiction recorded:** the installation page says release binaries are packaged "as a zip
  file", but the 2.7.2 release ships `.tar.gz` archives for Linux and macOS (zip only for Windows).
- **Defaults confirmed in the documentation:** `operator init` key shares 5 and threshold 3; TCP
  listener `tls_min_version` `tls12`; `unsafe_allow_api_audit_creation` `false`.
- **Not executed:** OpenBao was not installed or run for this entry. The configuration and commands
  are assembled from the documentation.
- **Unresolved:** a documented backup procedure for PebbleDB storage (this entry suggests a copy
  taken while stopped, which is not an official procedure); official sizing guidance.
