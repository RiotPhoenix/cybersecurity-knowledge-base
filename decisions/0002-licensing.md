# ADR 0002: Dual licensing — MIT for code, CC BY 4.0 for documentation

- **Status:** Accepted
- **Date:** 2026-11-11

## Context

The repository contains two kinds of material: prose documentation, and code (validation
scripts, tests, workflows, configuration, and stylesheets). Software licences are a poor fit
for prose, and content licences are a poor fit for code.

## Decision

- **Documentation** (`docs/`, `templates/`) is licensed under **CC BY 4.0**, permitting reuse
  and adaptation with attribution.
- **Code** is licensed under the **MIT licence**.
- Third-party trademarks, logos, screenshots, and documentation are not covered and are not
  redistributed without permission; entries link to official sources instead.

## Consequences

- Readers can reuse documentation in training materials or internal wikis with attribution.
- Contributors agree to these licences when contributing (stated in `CONTRIBUTING.md`).
- Any future inclusion of third-party material must carry its own licence notice.
