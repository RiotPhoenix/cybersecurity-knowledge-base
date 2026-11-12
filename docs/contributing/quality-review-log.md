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
| [Greenbone Community Edition](../tools/vulnerability-management/greenbone-community-edition.md) | `research-complete` | Pass | Needs review | Pass | Pass | 2026-11-12 | Container commands reproduced from the official guide, not executed. Supported host list is out of date for Fedora. No documented volume backup procedure. |
| [Nuclei](../tools/vulnerability-management/nuclei.md) | `research-complete` | Pass | Pass | Pass | Pass | 2026-11-12 | Flags and defaults checked against the official help listing; template paths and release checksums confirmed via the GitHub API. Examples not executed. |
| [KeePassXC](../tools/password-management/keepassxc.md) | `research-complete` | Pass | Needs review | Pass | Pass | 2026-11-12 | Default cipher/KDF and GUI timeouts not documented upstream. FAQ and 2.8.0 docs conflict on Wayland Auto-Type. CLI options are from the development-branch manual. |
| [Vaultwarden](../tools/password-management/vaultwarden.md) | `research-complete` | Pass | Needs review | Pass | Pass | 2026-11-12 | Compose and backup commands adapted from the README/wiki, not executed. Defaults come from `.env.template`, which the project says is not a guarantee. Rootless Podman behaviour unresolved. |

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

These reviews were performed by the entries' author. An independent second review, which
the `documentation-reviewed` status requires, has not yet taken place.
