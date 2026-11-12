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

Both tools observe or probe networks and require authorisation. Not yet documented:
firewalls, NIDS, VPN, DNS filtering, and flow monitoring.
