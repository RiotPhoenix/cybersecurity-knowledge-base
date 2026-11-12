# ADR 0004: Documentation quality gates for tool entries

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

The first tool entries showed that template structure alone does not ensure quality. An entry
can have every section and still contain unsupported commands, unsafe defaults, missing
sources, or testing claims without evidence. The catalogue is intended to grow to hundreds of
entries, so quality expectations must be explicit, repeatable, and partly automated, without
pretending that automation can judge technical correctness.

## Decision

- Every non-draft tool entry must pass four quality gates: **structural quality**, **technical
  accuracy**, **source and evidence quality**, and **operational safety and usability**. They
  are defined in `docs/contributing/quality-framework.md`.
- The tool entry template gains three required metadata keys (`website`, `repository`,
  `requires_authorisation`) and required subsections: installation verification, updating,
  personal and enterprise use cases, and four reference subsections including dated
  *Verification notes*.
- `scripts/check_quality.py` automates what can be checked offline and deterministically:
  placeholders, code-fence formatting, metadata consistency, required subsections, minimum
  section depth, source citations, consistency between status and testing claims, risky command
  patterns, navigation and category links, and the presence of a review record. It is required
  in CI.
- Risky command patterns can be accepted only with an inline, justified `quality-allow`
  comment, so exceptions stay visible to reviewers.
- Human review results are recorded per gate (Pass / Needs review / Fail) in
  `docs/contributing/quality-review-log.md`. Numerical scores are not used.
- External link checking (`scripts/check_external_links.py`) is optional and manual. Routine
  builds must not depend on third-party websites.
- The verification-status model is unchanged. The gates measure documentation quality;
  statuses measure execution evidence.

## Consequences

- Entries are longer and slower to write, but readers can rely on a consistent minimum standard
  and can see what was and was not verified.
- The template change is not a breaking change under ADR 0003, because no entries existed that
  needed rewriting.
- Pattern-based safety checks will produce occasional false positives. They are handled with
  justified exceptions, or by refining a rule, rather than by weakening the gate.
- Gate 2 always needs a reviewer. Automation reports structure, not truth.
