# Lab Validation

How to record evidence that a documented procedure was actually executed, and when that
evidence allows an entry's [verification status](verification-statuses.md) to be raised.

Research tells readers what the documentation says should happen. Lab evidence tells them what
**did** happen, on a stated version and platform. The two must never be confused: a plausible
command is not evidence that it works.

## Lab evidence records

Each test run is recorded as one **lab evidence record**: a Markdown file in
`docs/lab-evidence/`, created from
[`templates/lab-evidence.md`](https://github.com/RiotPhoenix/cybersecurity-knowledge-base/blob/main/templates/lab-evidence.md)
and listed in the [lab evidence index](../lab-evidence/index.md). The tool entry links to its
records from the `### Lab evidence` subsection under *References*.

### Required fields

| Field | Where | Notes |
|---|---|---|
| Record type | `record_type` | Always `lab-evidence`. |
| Tool name | `tool` | Must match the entry's `tool` value. |
| Tool version | `tool_version` | Exact version as reported by the tool (`--version`). |
| Test date | `test_date` | Date the procedure was executed (ISO format, not in the future). |
| Operating system | `operating_system` | Distribution, release, and architecture. |
| Installation method | `installation_method` and section | Package, official binary, container, source build, or development-only install. |
| Environment type | `environment_type` | `lab`, or `production` for authorised production use only. |
| Pass/fail outcome | `outcome` and section | `pass`, `fail`, or `partial`. The *Outcome* section must state it. |
| Tester identity | `tester` | Optional and self-chosen: a public handle or `anonymous`. Never another person's name or e-mail without consent. |
| Sanitisation | `sanitised` | `true` only after private details are removed. |
| Supported entry | `entry` | Path of the tool entry, relative to `docs/`. |
| Environment description | section | General description, using documentation values. |
| Hardware or virtual resources | section | CPU, memory, disk, interfaces. |
| Configuration summary | section | What differs from defaults or from the entry. |
| Test objective | section | What the test is meant to show. |
| Test procedure | section | The steps actually executed. |
| Expected result | section | What the entry or official documentation predicts. |
| Actual observed result | section | What happened, with sanitised output. |
| Deviations | section | Every difference from the documented procedure, or "None". |
| Troubleshooting performed | section | Problems and resolutions, or "None". |
| Known limitations | section | What the test does not prove. |
| Sanitised supporting evidence | section | Excerpts, or where evidence is retained privately. |

### Privacy and sanitisation

Records are published. Before setting `sanitised: true`:

- Replace real addresses with documentation ranges: `192.0.2.0/24`, `198.51.100.0/24`,
  `203.0.113.0/24` (RFC 5737), and `2001:db8::/32` (RFC 3849).
- Replace hostnames and domains with `.example` names.
- Remove usernames, e-mail addresses, MAC addresses, serial numbers, tokens, keys, unseal
  material, and anything from logs that identifies a person or a real network.
- Keep raw evidence privately if you need it. Describe where it is retained, not what it contains.

`scripts/check_lab_evidence.py` rejects records containing private (RFC 1918) or link-local IPv4
addresses, e-mail addresses, MAC addresses outside the documentation range, and private-looking
host names (`.lan`, `.local`, `.home`, `.internal`, `.corp`, and similar).
`scripts/scan_secrets.py` scans for credentials. These checks are a safety net, not a substitute
for reading the record before publishing.

## When a status may be raised

An entry may be marked `lab-tested` only when **all** of the following are true:

1. The documented procedure was actually executed.
2. The environment and the tool version are recorded.
3. The result is recorded, whatever it was.
4. Failures and deviations are disclosed in the record.
5. Evidence is retained appropriately (sanitised excerpts in the record, or private retention
   described in it).
6. The entry reflects the tested procedure: if the test needed changes, the entry is updated
   to match.

`production-validated` additionally requires a record with `environment_type: production`,
describing genuine, authorised production use. Never assign it on the basis of lab tests.

### What a successful test does and does not prove

A record proves that the stated procedure worked once, for the stated version, platform, and
configuration. It does **not** prove that:

- every feature in the entry works;
- other platforms, versions, or installation methods work;
- the deployment is secure, scalable, or suitable for production;
- the procedure still works after later releases.

A successful installation alone does not support a `lab-tested` status for an entry that also
documents configuration, hardening, and usage. Record the scope tested, and keep untested
sections labelled as untested in the entry.

### Failed and partial tests

Failed tests are valuable. Record them with the same care. A `fail` record never supports a status
increase, but it should lead to a correction in the entry or a note in its verification notes. A
`partial` record can support `lab-tested` only for the parts that passed, and the entry must say
which parts remain untested.

## Automated enforcement

`scripts/check_quality.py` requires that an entry with status `lab-tested` or
`production-validated`:

- has a dated `### Lab evidence` subsection under *References*;
- links from it to at least one record in `docs/lab-evidence/`;
- links only to records that pass `check_lab_evidence.py` and whose `entry` field names this entry;
- has at least one linked record with outcome `pass` or `partial`, whose `tool_version` appears in
  the entry's `tested_versions`;
- for `production-validated`, has a supporting record with `environment_type: production`.

`scripts/check_lab_evidence.py` validates the template and every record: required fields and
sections, valid values, a non-future test date, a matching entry, no placeholders, the privacy
rules above, and a link from the index. It runs offline in CI.

Automation checks that evidence is **recorded consistently**. It cannot check that the evidence is
**true**. Reviewers must read the record, compare it with the entry, and question results that seem
too clean. Fabricating a lab record is a serious breach of this project's standards.

## Workflow

1. Copy `templates/lab-evidence.md` to `docs/lab-evidence/<tool-slug>-<YYYY-MM-DD>.md`.
2. Execute the procedure, recording as you go rather than from memory.
3. Fill in every section, sanitise, and set `sanitised: true`.
4. Add the record to the [index](../lab-evidence/index.md).
5. In the entry: add a `### Lab evidence` subsection under *References* that links to the record and
   summarises it with its date; fill in `tested_versions`; update any steps that differed; change the
   status and the *Verification status* and *Tested versions* rows.
6. Add or update the entry's row in the [quality review log](quality-review-log.md).
7. Run the [local checks](../getting-started/local-development.md#validate-before-opening-a-pull-request)
   and open a pull request.
