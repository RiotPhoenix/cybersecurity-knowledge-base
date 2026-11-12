# Verification Statuses

Every tool entry declares exactly one status in its metadata. Statuses describe **evidence**,
not confidence. A status may only be raised when its evidence is recorded in the entry or the
pull request.

| Status | Meaning | Evidence required |
|---|---|---|
| `draft` | Work in progress. May be incomplete. | None — clearly labelled as draft. |
| `research-complete` | All sections written from official sources. | Every factual section cites an official source. |
| `documentation-reviewed` | A second contributor has checked the entry against sources. | Named reviewer and review date. |
| `lab-tested` | Installation, configuration, and examples executed in a lab. | A dated *Lab evidence* subsection recording the operating system, software version, the commands or procedure executed, actual observed results, deviations, and limitations. `tested_versions` filled in. |
| `production-validated` | Deployed and operated in a real authorised production environment. | Description of the environment (without private or sensitive infrastructure details), duration, and date. Never assigned without genuine evidence. |

!!! warning "No unsupported claims"
    Do not mark an entry `lab-tested` or `production-validated` because the instructions
    "should work". Untested installation steps must remain in a `draft` or
    `research-complete` entry and be labelled as untested.

## Statuses and spot checks

Running a few individual commands is useful evidence, but it is not a lab test of the
documented procedure. Record such spot checks in the entry's *Verification notes*, label the
commands in the text, and keep the status at `research-complete` (or `documentation-reviewed`).
Statuses are independent of the [documentation quality gates](quality-framework.md): an entry
must pass the gates whatever its status.

## Review cadence

Entries record a `last_reviewed` date. Entries not reviewed within **12 months** should be
treated as potentially outdated and re-checked against official sources.
`scripts/check_quality.py` warns about such entries.
