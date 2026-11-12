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
| `tested_versions` | Yes | List of exact versions and platforms tested; required to be non-empty for `lab-tested` and above. |

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
| 4 | Installation | Official installation methods; untested steps labelled. |
| 5 | Initial configuration | Minimum configuration to a working, safe state. |
| 6 | Security hardening | Recommended secure settings, with reasons. |
| 7 | Practical usage examples | Common tasks; lab targets and reserved addresses only. |
| 8 | Enterprise deployment considerations | Architecture, scaling, HA, integration, governance. |
| 9 | Troubleshooting | Common problems, maintenance and upgrade notes. |
| 10 | Alternatives and related tools | Comparable tools with links. |
| 11 | References | Official documentation, release notes, other authoritative sources. |

Entries in the [Penetration Testing](../tools/penetration-testing/index.md) and
[OSINT](../tools/osint/index.md) categories must also include the **Authorised use only**
warning.

## Validate an entry

```bash
python scripts/validate_entries.py docs/tools/<category>/<tool-slug>.md
```
