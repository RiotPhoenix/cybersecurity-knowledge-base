# ADR 0003: Versioning and release strategy

- **Status:** Accepted
- **Date:** 2026-11-11

## Context

Readers and contributors need to know when the knowledge base changes meaningfully, while
individual tool entries carry their own `last_reviewed` dates.

## Decision

The project uses **semantic versioning** adapted for documentation, with Git tags
(`vMAJOR.MINOR.PATCH`) and entries in `CHANGELOG.md`:

| Increment | When |
|---|---|
| **MAJOR** | Breaking structural changes: taxonomy reorganisation, URL scheme changes, template changes that require existing entries to be rewritten. |
| **MINOR** | New tool entries, guides, comparisons, categories, or site features. |
| **PATCH** | Corrections, link fixes, review-date updates, dependency updates, styling fixes. |

- Versions below `1.0.0` indicate that the catalogue is still being populated and structure
  may change.
- `main` is always deployable; the website reflects the latest `main`.
- Individual entries are versioned by their `status` and `last_reviewed` metadata, not by
  the project version.

## Consequences

- Page URLs are treated as a public interface; renaming or moving pages is a breaking change
  unless redirects are provided.
