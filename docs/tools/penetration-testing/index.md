# Penetration Testing

Tools used by authorised testers to emulate attacker techniques and validate security controls.

!!! warning "Authorised use only"
    Tools in this category can cause harm or break the law when used without permission.
    Use them only against systems you own or have **explicit written authorisation** to test,
    and practise in an isolated lab. Every entry in this category must document its
    authorisation boundaries and use safe laboratory examples only.

## Purpose of this category

This category groups tools by the security problem they address, so readers can find
options for a given need and compare them consistently. Each tool entry follows the
[tool entry template](../../contributing/tool-template.md) and carries an explicit
[verification status](../../contributing/verification-statuses.md).

## Intended coverage

- Reconnaissance and enumeration
- Exploitation frameworks
- Web application testing proxies
- Credential and authentication testing
- Wireless security assessment
- Post-exploitation and reporting
- Purpose-built testing distributions and lab targets

## Environment considerations

| Environment | Typical focus |
|---|---|
| [Personal / home lab](../../environments/personal/index.md) | Learning offensive techniques against intentionally vulnerable lab targets you own. |
| [Enterprise](../../environments/enterprise/index.md) | Scoped, contracted engagements with rules of engagement, evidence handling, and coordination with defenders. |

## Tool entries

Each entry records its [verification status](../../contributing/verification-statuses.md)
and a [quality review](../../contributing/quality-review-log.md) against the
[documentation quality gates](../../contributing/quality-framework.md). *Research complete* means checked against official sources, not lab-tested.

| Tool | What it is for | Personal | Enterprise | Status |
|---|---|---|---|---|
| [ZAP](zap.md) | Intercepting proxy and web application scanner (passive analysis and active testing) | High (against lab applications) | Medium to High (with scope and triage processes) | Research complete |

Passive analysis and active scanning are different activities: active scans send attacks and
always need written authorisation. Not yet documented: exploitation frameworks, credential testing,
wireless assessment, and testing distributions.
