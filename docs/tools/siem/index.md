# SIEM and Log Management

Platforms that collect, normalise, store, search, and correlate security-relevant logs and events.

## Purpose of this category

This category groups tools by the security problem they address, so readers can find
options for a given need and compare them consistently. Each tool entry follows the
[tool entry template](../../contributing/tool-template.md) and carries an explicit
[verification status](../../contributing/verification-statuses.md).

## Intended coverage

- Log collection agents and forwarders
- Parsing and normalisation
- Search, dashboards, and alerting
- Detection rules and correlation
- Retention and storage tiering
- Home-lab log pipelines

## Environment considerations

| Environment | Typical focus |
|---|---|
| [Personal / home lab](../../environments/personal/index.md) | Centralising logs from a home lab to learn detection engineering. |
| [Enterprise](../../environments/enterprise/index.md) | Ingestion scale and cost, retention requirements, detection content lifecycle, SOC workflows, and high availability. |

## Tool entries

Each entry records its [verification status](../../contributing/verification-statuses.md)
and a [quality review](../../contributing/quality-review-log.md) against the
[documentation quality gates](../../contributing/quality-framework.md). *Research complete* means checked against official sources, not lab-tested.

| Tool | What it is for | Personal | Enterprise | Status |
|---|---|---|---|---|
| [Wazuh](wazuh.md) | Endpoint monitoring, log collection, file integrity monitoring, vulnerability detection, and central alerting | Medium (needs 4 vCPU and 8 GiB for the central stack) | Medium to High | Research complete |

Wazuh agents monitor **endpoints**. For network traffic visibility, pair it with a network sensor
such as [Suricata](../network-security/suricata.md), whose alerts a Wazuh agent can collect. Not yet
documented: dedicated log platforms and forwarders.
