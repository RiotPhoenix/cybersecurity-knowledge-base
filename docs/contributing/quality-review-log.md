# Quality Review Log

One row per published tool entry, recording the result of its most recent review against the
[documentation quality gates](quality-framework.md). `scripts/check_quality.py` requires a row
for every non-draft entry. The row's status and review date must match the entry, and no
gate may be recorded as **Fail**.

Results: **Pass**, **Needs review** (usable; specific items unresolved, listed below and in the
entry's verification notes), or **Fail**.

## Current results

| Entry | Status | Gate 1 Structure | Gate 2 Accuracy | Gate 3 Sources | Gate 4 Safety | Reviewed | Notes |
|---|---|---|---|---|---|---|---|
| [Nmap](../tools/network-security/nmap.md) | `research-complete` | Pass | Pass | Pass | Pass | 2026-11-12 | Options checked against `nmap -h` (7.92) and the reference guide; loopback examples spot-checked. |
| [Wireshark](../tools/network-security/wireshark.md) | `research-complete` | Pass | Pass | Pass | Pass | 2026-11-12 | Fields and options checked with `tshark -G fields` / `-h` (4.6.8); loopback example spot-checked. |
| [Greenbone Community Edition](../tools/vulnerability-management/greenbone-community-edition.md) | `research-complete` | Pass | Needs review | Pass | Pass | 2026-11-12 | Container commands reproduced from the official guide, not executed. Re-checked: supported host list still outdated (Fedora 35/36, bookworm as stable) although prerequisites now include Fedora commands; still no documented volume backup procedure; guide still "not intended for production". |
| [Nuclei](../tools/vulnerability-management/nuclei.md) | `research-complete` | Pass | Pass | Pass | Pass | 2026-11-12 | Flags and defaults checked against the official help listing; template paths and release checksums confirmed via the GitHub API. Examples not executed. |
| [KeePassXC](../tools/password-management/keepassxc.md) | `research-complete` | Pass | Needs review | Pass | Pass | 2026-11-12 | Re-checked: default cipher/KDF resolved from 2.8.0 source (KDBX 4, AES-256, Argon2d, 1 s target). GUI timeouts still undocumented. FAQ still conflicts with 2.8.0 release notes on Wayland Auto-Type. CLI options are from the development-branch manual. |
| [Vaultwarden](../tools/password-management/vaultwarden.md) | `research-complete` | Pass | Needs review | Pass | Pass | 2026-11-12 | Compose and backup commands adapted from the README/wiki, not executed. Defaults come from `.env.template`, which the project says is not a guarantee. Re-checked: `/vaultwarden backup` output location resolved from 1.37.5 source. Rootless Podman behaviour still undocumented upstream. |
| [Suricata](../tools/network-security/suricata.md) | `research-complete` | Pass | Pass | Pass | Pass | 2026-11-12 | Commands from the 8.0.8 user-guide sources; Fedora 44 package contents (unit, sysconfig, default YAML) inspected from the RPM. Support-status table lists end-of-life distributions (recorded). Not executed. |
| [Zeek](../tools/network-security/zeek.md) | `research-complete` | Pass | Pass | Pass | Pass | 2026-11-12 | Docs read from the `v9.0.1` tag; OBS packages, repo file, and signing keys checked; ZeekControl defaults from source. Install guide's LTS package list is stale (recorded). Not executed. |
| [Wazuh](../tools/siem/wazuh.md) | `research-complete` | Pass | Needs review | Pass | Pass | 2026-11-12 | 4.14 docs and `v4.14.10` sources checked (ports, enrolment defaults, Docker Compose). Edited Docker port mappings are an unexecuted adaptation. Fedora agent support not stated upstream. |
| [ZAP](../tools/penetration-testing/zap.md) | `research-complete` | Pass | Pass | Pass | Pass | 2026-11-12 | Install channels, scan scripts, modes, and Automation Framework keys checked against the website and its Markdown sources. Java versions on Fedora/Debian not tested. Active-scan examples carry justified exceptions and target an internal-only lab network. |
| [OpenBao](../tools/password-management/openbao.md) | `research-complete` | Pass | Needs review | Pass | Pass | 2026-11-12 | Docs and code read at `v2.7.2`; Fedora 2.6.5 package inspected. Fedora's default `file` storage is removed in 2.7 (documented in the entry). PebbleDB backup method is not documented upstream. Configuration assembled from documentation, not executed. |

## Review method

Each review for the results above covered:

- **Gate 1:** `validate_entries.py`, `check_quality.py`, `check_links.py`, a strict MkDocs
  build, and inspection of the generated HTML and search index.
- **Gate 2:** each installation method, package name, path, flag, and security-relevant
  default compared with the official documentation listed in the entry. Where available,
  commands and options were also checked locally: `--help` output, `tshark -G fields`, and
  `dnf` and packages.debian.org package queries.
- **Gate 3:** each significant claim traced to a cited official source. Unverifiable claims
  were removed or listed as unresolved in the entry's verification notes.
- **Gate 4:** the editorial checklist in the [quality framework](quality-framework.md),
  covering privileges, network exposure, credential handling, backup and recovery, and the
  honesty of suitability ratings.

Since the lab validation framework was introduced, Gate 3 also covers lab evidence records:
an entry claiming `lab-tested` or `production-validated` must link to valid records (see
[lab validation](lab-validation.md)). No entry currently makes that claim.

These reviews were performed by the entries' author. An independent second review, which
the `documentation-reviewed` status requires, has not yet taken place.

## Maintenance backlog review (2026-11-12)

Items carried forward from the previous release were re-checked against current official sources.
Nothing was resolved by assumption.

| Entry | Item | Outcome |
|---|---|---|
| Greenbone Community Edition | Supported deployment hosts | **Unresolved.** The preamble still lists Fedora 35 and 36 and calls bookworm "Debian stable". The rewritten prerequisites page (2026-07-14) adds Fedora/CentOS commands and mentions Podman. The conflict is recorded in the entry. |
| Greenbone Community Edition | Backup and recovery | **Unresolved.** No backup or restore procedure exists for container volumes in any of the 83 documentation pages. Only the Kali pages warn to back up PostgreSQL before upgrades. |
| Greenbone Community Edition | Production suitability | **Unchanged.** The container guide still says it "is not intended for production setups". |
| KeePassXC | Wayland Auto-Type | **Conflict persists.** The FAQ says X11 only. The 2.8.0 release notes add Wayland Auto-Type through XDG Desktop Portals. Both are cited in the entry. |
| KeePassXC | Cryptographic defaults | **Resolved from source code** (2.8.0): KDBX 4, AES-256, Argon2d, 1000 ms target decryption time. The user documentation still does not state them. |
| Vaultwarden | Rootless Podman | **Unresolved.** The wiki's Podman page covers rootful Quadlet units and an older `podman run` example, not the non-root `user:` setting under rootless Podman. Needs a lab test. |
| Vaultwarden | Backup command output location | **Resolved from source code** (1.37.5): `db_<UTC timestamp>.sqlite3` in the database directory, SQLite only. The entry now states it. |
| Vaultwarden | Container deployment guidance | **No change needed.** The entry's loopback-only port binding is stricter than the wiki's examples, which publish on all interfaces. |

## External link check (2026-11-12)

`scripts/check_external_links.py` was run once over all eleven tool entries and the security
monitoring lab page: 199 unique URLs (counted per file).

| Result | Count | Details |
|---|---|---|
| OK | 193 | |
| Redirected | 3 | Suricata end-of-life policy, Flathub ZAP page, RFC 5737. All redirected within the same official site and were updated to the final URL. |
| Definite failure (404) | 2 | **KeePassXC FAQ** (`keepassxc.org/faq/`): also 404 when re-checked manually with GET. The FAQ now lives on the official documentation page, and the link was corrected to `keepassxc.org/docs/#faq`. **openSUSE Build Service project page for Zeek**: a checker false positive. The server answers `HEAD` with 404 but serves the page on `GET` (HTTP 200 when re-checked manually). The checker now retries with `GET` before reporting a failure. |
| Unverified | 1 | `https://127.0.0.1` in the Greenbone entry: the local web interface address in an example, not a cited source. Expected. |
| Timeouts or rate limiting | 0 | |

A working URL proves only that the page answers. Cited content was read during research, not
re-read by this check.
