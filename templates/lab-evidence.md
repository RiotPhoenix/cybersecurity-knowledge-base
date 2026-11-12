---
# Copy to docs/lab-evidence/<tool-slug>-<YYYY-MM-DD>.md, link it from docs/lab-evidence/index.md,
# and link it from the "### Lab evidence" subsection of the tool entry it supports.
# Use documentation addresses (192.0.2.0/24, 198.51.100.0/24, 203.0.113.0/24, 2001:db8::/32)
# and .example names. Never record real hostnames, addresses, usernames, or credentials.
record_type: lab-evidence
tool: Tool Name                      # must match the `tool` value of the entry
tool_version: "1.2.3"                # exact version tested, as reported by the tool
entry: tools/<category>/<tool-slug>.md   # the entry this record supports, relative to docs/
test_date: YYYY-MM-DD                # date the procedure was executed
environment_type: lab                # lab | production (production only with authorised production use)
operating_system: "Fedora 44 (x86_64)"
installation_method: "Distribution package"  # package, official binary, container, source build, ...
outcome: pass                        # pass | fail | partial
tester: "GitHub handle, or anonymous"    # optional identity; no private names or e-mail without consent
sanitised: true                      # set only after removing private and sensitive details
---

# Lab evidence: Tool Name 1.2.3 on Fedora 44

## Environment

Describe the test environment in general terms: physical or virtual, network layout using
documentation addresses, and what else was running. No private infrastructure details.

## Hardware or virtual resources

CPU cores, memory, disk, and network interfaces available to the tool (for example "VM, 2 vCPU,
4 GiB RAM, 40 GB disk, one virtio NIC").

## Installation method

How the tool was installed, with the exact commands or the section of the entry that was
followed.

## Configuration summary

Configuration that differs from the defaults or from the entry, and why.

## Test objective

What the test was meant to show, in one or two sentences. Name the entry sections covered.

## Test procedure

Numbered steps actually executed, with commands. Mark any step that differs from the entry.

## Expected result

What the entry or the official documentation says should happen.

## Actual observed result

What actually happened, including relevant output (sanitised). Record unexpected behaviour.

## Outcome

`pass`, `fail`, or `partial`, with a one-sentence justification. A partial result lists which
parts passed.

## Deviations from the documented procedure

Every difference between what was executed and what the entry documents, or "None".

## Troubleshooting performed

Problems met and how they were resolved, or "None".

## Known limitations

What this test does **not** show (for example: single host only, no load, default rules only,
upgrade path not tested).

## Supporting evidence

Sanitised excerpts of output, logs, or screenshots stored in the repository, or a description of
where evidence is retained privately. Remove hostnames, addresses, usernames, tokens, and keys
first.
