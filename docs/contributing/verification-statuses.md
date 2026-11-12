# Verification Statuses

Every tool entry declares exactly one status in its metadata. Statuses describe **evidence**,
not confidence. A status may only be raised when its evidence is recorded in the entry or the
pull request.

| Status | Meaning | Evidence required |
|---|---|---|
| `draft` | Work in progress. May be incomplete. | None — clearly labelled as draft. |
| `research-complete` | All sections written from official sources. | Every factual section cites an official source. |
| `documentation-reviewed` | A second contributor has checked the entry against sources. | Named reviewer and review date. |
| `lab-tested` | Installation, configuration, and examples executed in a lab. | Exact tested versions, OS/platform, and date; deviations noted. |
| `production-validated` | Deployed and operated in a real production environment. | Description of the environment (without private details), duration, and date. |

!!! warning "No unsupported claims"
    Do not mark an entry `lab-tested` or `production-validated` because the instructions
    "should work". Untested installation steps must remain in a `draft` or
    `research-complete` entry and be labelled as untested.

## Review cadence

Entries record a `last_reviewed` date. Entries not reviewed within **12 months** should be
treated as potentially outdated and re-checked against official sources.
