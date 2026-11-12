---
# Copy to docs/tools/<category>/<tool-slug>.md and add it to the nav in mkdocs.yml.
tool: Tool Name
category: network-security          # one of the category directory names under docs/tools/
status: draft                       # draft | research-complete | documentation-reviewed | lab-tested | production-validated
last_reviewed: YYYY-MM-DD
tested_versions: []                 # e.g. ["1.2.3 on Fedora 44"]; empty until lab-tested
website: https://example.com        # official website (https)
repository: https://example.com/source   # canonical source repository (https) or "Proprietary"
requires_authorisation: false       # true for scanners, interception and offensive tools
---

# Tool Name

<!-- Tools that scan, intercept or attack systems: keep this admonition. Otherwise delete it. -->
!!! warning "Authorised use only"
    Use this tool only against systems you own or have explicit written authorisation to test.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://example.com> |
| Source repository | <https://example.com/source> or "Proprietary" |
| Licence | SPDX identifier or licence name |
| Supported operating systems | Linux, Windows, macOS, … |
| Maintenance status | Active / Maintenance only / Unmaintained — checked YYYY-MM-DD |
| Category | Category name |
| Personal suitability | High / Medium / Low — one-line reason |
| Enterprise suitability | High / Medium / Low — one-line reason |
| Tested versions | Exact versions and platforms, or "Not yet tested" |
| Verification status | Draft |
| Last reviewed | YYYY-MM-DD |

## Overview

What the tool is, the problem it solves, and who maintains it.

## Features and capabilities

Key capabilities, and explicit limitations.

## System requirements

Hardware, software, network, and privilege requirements, from official documentation.

## Installation

Official installation method(s), labelled by operating system. State prerequisites and why
elevated privileges are needed. Label untested steps as untested.

### Verify the installation

How to confirm the installation worked, and what output to expect.

### Updating and removal

How to update the software, and removal or rollback considerations.

## Initial configuration

Minimum configuration to reach a working, safe state.

## Security hardening

Recommended secure settings, with the reason for each.

## Practical usage examples

Common tasks with commands and expected results. Lab targets and reserved addresses only.

### Personal and home-lab use

Realistic personal use cases.

### Enterprise use

Realistic enterprise use cases.

## Enterprise deployment considerations

Architecture, scaling, high availability, integration, access control, and governance.

## Troubleshooting

Common problems, causes, and fixes. Maintenance and upgrade notes.

## Alternatives and related tools

Comparable tools, with links to their entries where available.

## References

### Official documentation

- Official website and documentation links.

### Installation references

- Official installation and download pages.

### Security and deployment references

- Security advisories, hardening and deployment guidance.

### Verification notes

- Date the sources above were checked (YYYY-MM-DD), what was verified, what was executed
  (if anything), and unresolved questions.
