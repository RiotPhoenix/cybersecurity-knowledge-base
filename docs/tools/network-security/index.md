# Network Security

Tools that observe, filter, and protect network traffic and network-connected services.

## Purpose of this category

This category groups tools by the security problem they address, so readers can find
options for a given need and compare them consistently. Each tool entry follows the
[tool entry template](../../contributing/tool-template.md) and carries an explicit
[verification status](../../contributing/verification-statuses.md).

## Intended coverage

- Packet capture and protocol analysis
- Network scanning and service discovery (defensive inventory)
- Firewalls and packet filtering
- Network intrusion detection and prevention (NIDS/NIPS)
- VPNs and encrypted tunnelling
- DNS security and filtering
- Network flow monitoring

## Environment considerations

| Environment | Typical focus |
|---|---|
| [Personal / home lab](../../environments/personal/index.md) | Securing a home router, segmenting IoT devices, and understanding what is on your own network. |
| [Enterprise](../../environments/enterprise/index.md) | Perimeter and internal segmentation, east–west traffic visibility, NIDS deployment at scale, and change-controlled firewall policy. |

## Tool entries

Each entry records its [verification status](../../contributing/verification-statuses.md)
and a [quality review](../../contributing/quality-review-log.md) against the
[documentation quality gates](../../contributing/quality-framework.md). *Research complete* means checked against official sources, not lab-tested.

| Tool | What it is for | Personal | Enterprise | Status |
|---|---|---|---|---|
| [Nmap](nmap.md) | Host discovery, port and service scanning, segmentation validation | High | High (with scope control) | Research complete |
| [Wireshark](wireshark.md) | Packet capture and protocol analysis for troubleshooting and investigation | High | High (as an analyst tool) | Research complete |
| [Suricata](suricata.md) | Signature-based network intrusion detection (passive IDS), with optional inline prevention | Medium | High (with sensor and rule management) | Research complete |
| [Zeek](zeek.md) | Network security monitoring: structured logs of connections, DNS, HTTP, TLS, and files | Medium | High (with a log platform) | Research complete |

All four tools observe or probe networks and require authorisation. Suricata and Zeek are
complementary rather than interchangeable: Suricata alerts on known-bad patterns, while Zeek
records what happened. Both need a copy of the traffic (a mirror port or TAP) to see more than
their own host. See the [security monitoring lab](../../environments/personal/security-monitoring-lab.md)
for how they fit together. Not yet documented: firewalls, VPN, DNS filtering, and flow monitoring.
