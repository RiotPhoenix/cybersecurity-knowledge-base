# Documentation Quality Framework

Every tool entry must pass four quality gates before it is published as anything other than
a `draft`. The gates apply to new entries and to every re-review of an existing entry.

Automated checks catch structural and obviously unsafe problems quickly. They **cannot**
establish that technical content is correct: a command that looks plausible is not evidence
that it works. Gate 2 and parts of Gates 3 and 4 therefore always need a human reviewer
working from official sources, and the result is recorded in the
[quality review log](quality-review-log.md).

## The four gates

| Gate | Question it answers | Automated | Editorial (human) |
|---|---|---|---|
| **1. Structural quality** | Is the entry complete, well-formed, and discoverable? | Mostly | Rendering and readability |
| **2. Technical accuracy** | Are the commands, packages, paths, flags, and defaults correct for the versions described? | No | Entirely |
| **3. Source and evidence quality** | Can every significant claim be traced to an authoritative source, and is tested content distinguished from documented content? | Partly | Claim-by-claim tracing |
| **4. Operational safety and usability** | Does the entry lead readers to a safe deployment, and can the intended reader follow it? | Partly | Judgement of risk and clarity |

### Gate 1: Structural quality

The entry must have:

- Front matter with every required key (`tool`, `category`, `status`, `last_reviewed`,
  `tested_versions`, `website`, `repository`, `requires_authorisation`), a valid category and
  status, and a review date that is a real date and not in the future.
- All template sections in order, every *At a glance* row, and the required subsections:
  installation verification, update procedure, personal and enterprise use cases, and the
  four reference subsections.
- No leftover template or placeholder text (`YYYY-MM-DD`, `TODO`, `TBD`, …).
- *At a glance* rows that agree with the front matter (verification status, review date,
  website, repository).
- A language on every fenced code block, fences starting at column 0 (fences indented inside
  lists or admonitions do not render), and no unclosed code blocks.
- Working internal links and anchors, an entry in the `mkdocs.yml` navigation, a link from
  its category index, and inclusion in the site search index.

**Enforced by:** `scripts/validate_entries.py`, `scripts/check_quality.py`,
`scripts/check_links.py`, `mkdocs build --strict`, and the `pytest` suite.

Editorial check: read the rendered page. Do tables, admonitions, and code blocks display
correctly, and does the page read in a sensible order?

### Gate 2: Technical accuracy

The reviewer confirms against current official documentation that:

- Installation commands correspond to methods the maintainers or the named distribution
  actually support, and that package names are correct for each labelled platform.
- Configuration paths, service names, environment variables, and command flags exist and do
  what the entry says.
- Security-relevant defaults (listen addresses, default accounts, registration settings,
  update behaviour) are described correctly.
- Version-sensitive instructions are identified as such, unsupported platforms are not
  presented as supported, and deprecated methods are not presented as current.
- Commands are not combined across distributions without explanation.

Useful techniques: check each flag against the tool's own `--help` output or manual page;
query package repositories (`dnf repoquery`, `packages.debian.org`); compare defaults with the
project's configuration template or source.

**Enforced by:** the reviewer, recorded in the [review log](quality-review-log.md). Nothing in
this gate is automated.

### Gate 3: Source and evidence quality

- The References section has the subsections **Official documentation**, **Installation
  references**, **Security and deployment references**, and **Verification notes**.
- The official website and source repository from the front matter are cited.
- At least five distinct HTTPS sources are cited, and no plain-HTTP references.
- *Verification notes* record the date sources were checked, what was verified, what (if
  anything) was executed, and unresolved questions.
- Testing claims match the status: `tested_versions` stays empty below `lab-tested`, and
  first-person claims such as "we tested" may appear only in the verification notes.
  `lab-tested` and above require a dated **Lab evidence** subsection.
- Significant technical claims are traceable to a cited source. Claims that cannot be verified
  are removed, qualified, or listed as unresolved. Citations and URLs are never invented.

**Enforced by:** `scripts/check_quality.py` (structure of the evidence) and the reviewer
(whether each claim is actually supported).

### Gate 4: Operational safety and usability

- Tools that scan, intercept, or attack systems set `requires_authorisation: true`. They must
  then carry the **Authorised use only** warning and discuss authorisation and scope in
  *Enterprise deployment considerations*.
- *Installation*, *Security hardening*, *Enterprise deployment considerations*, and
  *Troubleshooting* meet minimum-depth thresholds, so they cannot be left as one-liners.
- Code blocks are scanned for risky patterns (table below). A flagged block is rejected unless
  it carries a justification.
- The reviewer checks privileges, network exposure, credential handling, defaults, backup and
  recovery, enterprise risks, troubleshooting completeness, and whether personal and enterprise
  suitability ratings are honest.

**Enforced by:** `scripts/check_quality.py` and the reviewer.

## Automated command-safety rules

`scripts/check_quality.py` checks fenced code blocks (not prose) for:

| Rule ID | Flags | Example of what is flagged |
|---|---|---|
| `pipe-to-shell` | Downloaded scripts piped into a shell | `curl` or `wget` output piped to `sh`/`bash`; `iwr` piped to `iex` |
| `tls-verification-disabled` | Certificate verification turned off | `curl -k`, `--no-check-certificate`, `verify=False` |
| `security-control-disabled` | Firewall, SELinux, or malware protection disabled | `setenforce 0`, `systemctl disable firewalld`, `ufw disable` |
| `world-writable` | World-writable permissions | `chmod 777` |
| `hardcoded-credential` | Literal secrets in commands or configuration | `--password=…` with a real-looking value, `admin:admin` |
| `exposed-interface` | Services published on all interfaces, or admin protection disabled | `-p 8080:80`, `--listen=0.0.0.0`, `DISABLE_ADMIN_TOKEN=true` |
| `intrusive-scan` | Intrusive scanner options | `nmap -T5`, `--script exploit`, Nuclei `-itags dos`, `-dast` |
| `privileged-gui` | Packet-analysis GUI run as root | `sudo wireshark` |

Placeholders such as `<PASSWORD>`, `$VARIABLE`, and `${VARIABLE}` are not treated as
credentials. Publish container ports on `127.0.0.1` unless wider exposure is the point of the
example.

**Justified exceptions.** If an entry must show a flagged command (for example, to explain why
it is dangerous), put a justification on the line directly before the code fence:

```markdown
<!-- quality-allow: tls-verification-disabled -- shows the insecure form being replaced below -->
```

The justification must name known rule IDs and give a reason of at least ten characters.
Reviewers should question every exception.

## Running the checks

```bash
python scripts/validate_entries.py            # template structure (Gate 1)
python scripts/check_quality.py               # Gates 1, 3, 4 automation and review records
python scripts/check_links.py                 # internal links outside MkDocs
python -m mkdocs build --strict               # rendering, navigation, links, anchors
python -m pytest -ra                          # regression tests, site build, search index
```

All of these run offline and deterministically. `check_quality.py` also prints a **warning**
(not an error) when an entry's `last_reviewed` date is more than 12 months old.

### Optional external link check

```bash
python scripts/check_external_links.py [docs/tools/<category>/<tool>.md ...]
```

This contacts every cited website, so it is **not** part of routine local builds or CI. Run it
during a review. Its limitations:

- A working URL proves only that the page answers, not that it still says what the entry
  claims. Reviewers must still re-read the source.
- Some sites block automated clients or rate-limit them (HTTP 403/429), and some need
  JavaScript. These are reported as *unverified*, not broken.
- Results vary with network conditions, so a single failure should be re-checked by hand.

## Editorial review checklist

For each entry, read the rendered page as someone who did not write it:

1. Does the introduction explain what the tool actually does?
2. Are its limitations clear?
3. Are installation instructions understandable without guessing missing steps?
4. Are prerequisites stated?
5. Are commands accurate and appropriately scoped (Gate 2)?
6. Are required privileges explained?
7. Are security implications documented?
8. Are personal and enterprise use cases meaningful?
9. Are troubleshooting steps useful?
10. Are official sources traceable (Gate 3)?
11. Are unsupported claims avoided?
12. Is the verification status accurate?

Correct deficiencies before recording the review. Record one result per gate in the
[quality review log](quality-review-log.md):

| Result | Meaning |
|---|---|
| **Pass** | The gate's criteria are met, with evidence noted. |
| **Needs review** | Usable, but specific items are unresolved and listed in the entry's verification notes; re-review is due. |
| **Fail** | Criteria not met. A failed entry must be corrected or returned to `draft`; `check_quality.py` rejects a non-draft entry with a recorded Fail. |

Numerical quality scores are not used: without a defined assessment method they would imply
false precision.

## Relationship to verification statuses

The gates and [verification statuses](verification-statuses.md) measure different things. The
gates measure whether the *documentation* is complete, sourced, and safe. The status measures
how much *evidence of execution* exists. An entry at `research-complete` can pass all four gates
without any hands-on testing; it must simply not claim testing it has not had.
