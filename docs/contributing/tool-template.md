# Tool Entry Template

Every tool entry starts from
[`templates/tool-entry.md`](https://github.com/RiotPhoenix/cybersecurity-knowledge-base/blob/main/templates/tool-entry.md).
Its structure is enforced automatically by `scripts/validate_entries.py` in continuous
integration.

## Metadata (front matter)

| Key | Required | Description |
|---|---|---|
| `tool` | Yes | Tool name as published by its maintainers. |
| `category` | Yes | Category directory name; must match the entry's location. |
| `status` | Yes | One of the [verification statuses](verification-statuses.md). |
| `last_reviewed` | Yes | ISO date (`YYYY-MM-DD`) the entry was last checked against official sources. |
| `tested_versions` | Yes | List of exact versions and platforms tested. Must be non-empty for `lab-tested` and above, and empty below that. |
| `website` | Yes | Official website (`https://` URL). Must also appear in *At a glance* and *References*. |
| `repository` | Yes | Canonical source repository (`https://` URL), or `Proprietary`. |
| `requires_authorisation` | Yes | `true` for tools that scan, intercept, or attack systems. Requires the *Authorised use only* warning and an authorisation and scope discussion. |

## "At a glance" table

- Official website · Source repository · Licence
- Supported operating systems · Maintenance status · Category
- Personal suitability · Enterprise suitability
- Tested versions · Verification status · Last reviewed

## Sections (in order)

| # | Section | Contents |
|---|---|---|
| 1 | Overview | What the tool is, the problem it solves, who maintains it. |
| 2 | Features and capabilities | Capabilities and explicit limitations. |
| 3 | System requirements | Hardware, software, network, and privilege requirements. |
| 4 | Installation | Official installation methods by operating system, prerequisites, and privileges. Required subsections: verifying the installation, and updating (with removal or rollback). |
| 5 | Initial configuration | Minimum configuration to a working, safe state. |
| 6 | Security hardening | Recommended secure settings, with reasons. |
| 7 | Practical usage examples | Common tasks; lab targets and reserved addresses only. Required subsections: personal/home-lab use and enterprise use. |
| 8 | Enterprise deployment considerations | Architecture, scaling, HA, integration, governance. |
| 9 | Troubleshooting | Common problems, maintenance and upgrade notes. |
| 10 | Alternatives and related tools | Comparable tools with links. |
| 11 | References | Required subsections: *Official documentation*, *Installation references*, *Security and deployment references*, and *Verification notes* (dated). `lab-tested` and above also need *Lab evidence*. |

Entries in the [Penetration Testing](../tools/penetration-testing/index.md) and
[OSINT](../tools/osint/index.md) categories, and any entry with
`requires_authorisation: true`, must also include the **Authorised use only** warning.

The *At a glance* table plus the eleven sections give the 22 required elements of every
entry. Further content requirements are set by the
[documentation quality framework](quality-framework.md).

## Validate an entry

```bash
python scripts/validate_entries.py docs/tools/<category>/<tool-slug>.md
python scripts/check_quality.py docs/tools/<category>/<tool-slug>.md
```
