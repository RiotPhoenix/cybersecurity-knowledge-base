# ADR 0005: Lab evidence records and status enforcement

- **Status:** Accepted
- **Date:** 2026-11-12

## Context

ADR 0004 introduced documentation quality gates, and the verification-status model required a
dated *Lab evidence* subsection before an entry could be marked `lab-tested`. A dated sentence is
easy to write and hard to review: it does not say which version was tested, what was executed,
what was observed, or what failed. As entries begin to describe services (network sensors, SIEM
platforms, secrets managers) whose behaviour depends heavily on environment and configuration,
the gap between "documented" and "tested" matters more, and readers need a consistent record of
real executions.

## Decision

- Each test run is recorded as a **lab evidence record**: a Markdown file in `docs/lab-evidence/`,
  created from `templates/lab-evidence.md` and listed in the published lab evidence index.
- A record has required front matter (tool, exact version, entry, test date, environment type,
  operating system, installation method, outcome, optional tester identity, and a sanitisation
  confirmation) and required sections (environment, resources, installation, configuration,
  objective, procedure, expected and observed results, outcome, deviations, troubleshooting,
  limitations, and supporting evidence).
- `scripts/check_lab_evidence.py` validates the template and every record offline: required
  fields and sections, allowed values, a non-future test date, a matching entry, no template
  placeholders, a link from the index, and privacy rules that reject private IPv4 addresses,
  e-mail addresses, MAC addresses outside the documentation range, and private-looking host
  names. It runs in CI.
- `scripts/check_quality.py` requires entries at `lab-tested` or `production-validated` to link to
  at least one valid record for that entry, with outcome `pass` or `partial`, on a version listed
  in `tested_versions`. `production-validated` additionally requires a record with
  `environment_type: production`.
- Two command-safety rules are added under the ADR 0004 mechanism: `active-web-scan` (active DAST
  scans) and `dev-mode-server` (secrets servers in development mode). Legitimate examples must
  carry a justified `quality-allow` exception.

## Consequences

- Raising a status takes more effort, but the evidence is reviewable, comparable across entries,
  and honest about failures and limitations. Failed tests are recorded rather than discarded.
- The previous minimal form of evidence (a dated line) no longer satisfies the checks. No published
  entry was `lab-tested`, so no entry needed rewriting, and this is not a breaking change under
  ADR 0003.
- Privacy rules are pattern-based and can produce false positives (for example, an address in a
  quoted vendor example). Records should be rewritten with documentation values rather than the
  rules being relaxed.
- Automation confirms that evidence is recorded consistently, not that it is true. Reviewers must
  still read records critically, and fabricated records remain a policy violation that tooling
  cannot detect.
