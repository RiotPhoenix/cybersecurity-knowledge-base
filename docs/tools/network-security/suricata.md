---
tool: Suricata
category: network-security
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://suricata.io/
repository: https://github.com/OISF/suricata
requires_authorisation: true
---

# Suricata

!!! warning "Authorised use only"
    Suricata inspects network traffic, including other people's communications. Monitor only
    networks you own or are explicitly authorised in writing to monitor. Inline prevention
    (IPS) mode can also block legitimate traffic. Practise in an isolated lab first.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://suricata.io/> |
| Source repository | <https://github.com/OISF/suricata> |
| Licence | GPL-2.0-only |
| Supported operating systems | Linux (OISF Tier 1 and Tier 2 distributions), FreeBSD; Windows and macOS at Tier 2 (see [System requirements](#system-requirements)) |
| Maintenance status | Active: 8.0.8 released 2026-10-29. The 7.0.x branch reached end of life on 2026-07-07. Checked 2026-11-12 |
| Category | Network Security |
| Personal suitability | Medium: valuable for learning detection, but needs a traffic mirror, tuning, and time to triage alerts |
| Enterprise suitability | High: mature, widely deployed NIDS/IPS engine, if you staff sensor engineering and rule management |
| Tested versions | Not yet tested |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

Suricata is an open-source network threat-detection engine developed by the Open Information
Security Foundation (OISF), a non-profit foundation. It reads packets from a network interface
or a capture file, reassembles flows, parses application-layer protocols, and matches the
traffic against **rules** (signatures). It writes alerts and protocol metadata as structured
JSON, known as **EVE** output.

Suricata can run in two fundamentally different modes:

| | Passive IDS (detection) | Inline IPS (prevention) |
|---|---|---|
| Position | Receives a **copy** of traffic (mirror port, TAP, or a capture file) | Sits **in the traffic path** (bridge, NFQUEUE, or similar) |
| Effect on traffic | None. It can only alert | Can drop or reject packets that match `drop` or `reject` rules |
| Failure impact | Missed detections | Lost connectivity, or bypassed protection, depending on the failure mode |
| Typical first deployment | **Yes**. Start here | Only after the rule set is tuned and the failure behaviour is designed and tested |

This guide documents **passive IDS** deployment. Inline IPS is described for awareness in
[Enterprise deployment considerations](#enterprise-deployment-considerations) and is not
recommended as a beginner or home-lab default: a mis-tuned rule or a crashed process can cut
off the network it is meant to protect.

**Suricata compared with Zeek.** Both observe network traffic, but they answer different
questions. Suricata primarily asks "does this traffic match a known-bad pattern?" and produces
alerts, with protocol metadata as a by-product. [Zeek](zeek.md) primarily records "what
happened on the network?" as detailed transaction logs, and detection is something you script
on top. Many monitoring designs run both on the same traffic copy.

## Features and capabilities

- **Signature-based detection.** Rules match packet, stream, and protocol fields. The free
  Emerging Threats Open (ET Open) rule set is the default source used by `suricata-update`.
  Rules can also be written locally.
- **Protocol parsing and logging.** Application-layer parsers for protocols such as HTTP, TLS,
  DNS, SMB, SSH, SMTP, and QUIC produce metadata events even when no rule matches.
- **EVE JSON output.** A single `eve.json` file (enabled by default) carries alerts, flows,
  protocol records, anomalies, file information, and statistics. Each record has an
  `event_type` field, which makes the output straightforward to filter with `jq` or to ingest
  into a SIEM.
- **Capture methods.** On Linux, AF_PACKET is the usual live-capture method (the quickstart
  configures it). Others include AF_XDP, libpcap, DPDK, netmap, and NFQUEUE for inline mode.
  Suricata can also read capture files (`-r file.pcap`) for offline analysis.
- **Packet capture output.** A `pcap-log` output can store packets to disk. It is
  **disabled by default** because it records full payloads and consumes storage quickly.
- **Rule management.** `suricata-update` (bundled with Suricata) downloads rule sets, applies
  local enable/disable/modify filters, writes `/var/lib/suricata/rules/suricata.rules`, and
  tests the result.
- **Live control.** `suricatasc` talks to Suricata's Unix socket (enabled by default through
  `unix-command: enabled: auto`) for commands such as rule reloads and statistics.

Limitations to accept:

- **Visibility is not automatic.** Suricata sees only packets delivered to the interface it
  listens on. Installing it on a host does not make it see the rest of the network (see
  [System requirements](#system-requirements)).
- **Encrypted traffic.** Suricata cannot inspect the content of TLS or other encrypted
  sessions. It can still log and match on handshake metadata such as server names and
  certificate details.
- **Alerts need triage.** Rule sets produce false positives that must be investigated and
  tuned. An untuned sensor quickly becomes noise that nobody reads.
- **Not a SIEM.** Suricata produces events. Storage, search, correlation, and case handling
  require other tools.

## System requirements

- **Operating system.** OISF's support-status page lists Tier 1 platforms (full CI and QA)
  including RHEL-compatible 8 and 9, Ubuntu LTS releases, Debian, and FreeBSD, and Tier 2
  platforms (CI but not full functional QA) including **Fedora (active releases)**, macOS, and
  Windows (MinGW64). x86_64 and 64-bit ARM are Tier 1 architectures. See the verification
  notes: the table on that page also still lists distribution releases that are past their
  end of life.
- **Privileges.** Suricata must **start as root** to open capture interfaces. On Linux it can
  then drop to an unprivileged user. The Fedora and EPEL packages are preconfigured to run as
  the `suricata` user.
- **Hardware.** OISF publishes no fixed minimum. Requirements grow with traffic rate, the
  number of loaded rules, and enabled outputs. Memory use is driven partly by settings such as
  `max-pending-packets`, which is allocated per thread. Measure packet drops (below) rather than
  guessing.
- **Network visibility.** For passive monitoring, the sensor needs a copy of the traffic you
  care about. That usually means a switch **mirror (SPAN) port**, a network **TAP**, or a
  position on a router or hypervisor bridge where the traffic passes. A dedicated capture
  interface without an IP address, plus a separate management interface, is the common design.
- **Disk.** EVE output with protocol logging can grow by gigabytes per day on a busy network.
  Plan rotation and retention before enabling extra event types.
- **Outbound access.** `suricata-update` downloads rule sets over HTTPS. An offline sensor
  needs rules copied in by another route.

## Installation

Use a package that tracks the supported 8.0.x branch. Labelled by platform:

| Platform | Method | Source and notes |
|---|---|---|
| Fedora | Fedora repository package, or OISF COPR `@oisf/suricata-8.0` | Fedora 44 shipped 8.0.8 on 2026-11-12. The COPR is maintained by OISF. |
| RHEL, AlmaLinux, Rocky Linux | EPEL plus OISF COPR | From the official RPM installation page. |
| Ubuntu | OISF PPA `ppa:oisf/suricata-stable` | Maintained by OISF and tracks the latest stable release. |
| Debian | Debian repository | Debian 13 ships 7.0.10 (an upstream end-of-life branch, patched by Debian security updates). `trixie-backports` carried 8.0.8 on 2026-11-12. |
| Windows | Official MSI installer from the download page | Requires Npcap for live capture. Tier 2 support. |
| macOS | Source build | No OISF-maintained package. Tier 2 support. |
| Containers | No official image is listed on the download page | The security guide gives capability requirements for Docker and Podman. Rootless Podman is not supported. |

### Fedora

Prerequisites: an administrator account (`sudo`), and an interface that receives the traffic
to monitor. The Fedora repository package is the simplest route:

```bash
sudo dnf install suricata
```

To follow OISF's own packages instead, enable the COPR repository first (from the official
RPM instructions):

```bash
sudo dnf install dnf-plugins-core
sudo dnf copr enable @oisf/suricata-8.0
sudo dnf install suricata
```

`sudo` is needed because installing packages and enabling repositories changes system
configuration. The packages install configuration under `/etc/suricata`, logs under
`/var/log/suricata`, rules and state under `/var/lib/suricata`, the `suricata` systemd unit,
and command-line options in `/etc/sysconfig/suricata`.

### Debian and Ubuntu

On **Ubuntu**, use the OISF PPA (official instructions):

```bash
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:oisf/suricata-stable
sudo apt-get update
sudo apt-get install suricata jq
```

On **Debian**, `sudo apt-get install suricata` installs the Debian package. On Debian 13 that is
7.0.10. To get the supported 8.0.x branch, install from `trixie-backports` after enabling
backports as described in Debian's own documentation
(`sudo apt-get install -t trixie-backports suricata`). On Debian and Ubuntu, daemon options are
read from `/etc/default/suricata` rather than `/etc/sysconfig/suricata`.

### Windows

Download `Suricata-<VERSION>-1-64bit.msi` from the official download page, and install
[Npcap](https://npcap.com/) for live capture. Windows is a Tier 2 platform and lacks the Linux
privilege-dropping feature. For learning, offline analysis of capture files on Windows is a
reasonable use. For continuous monitoring, prefer a Linux sensor.

### Containers

OISF's security guide says containers need `--cap-add=net_admin --cap-add=net_raw
--cap-add=sys_nice`, and that Suricata **does not work with rootless Podman**, because it must
start with root privileges to access interfaces. It still recommends configuring Suricata
inside the container to drop to a non-root user. No image is listed on the official download
page, so if you use a container, you are responsible for choosing a trustworthy image,
updating it, persisting `/var/log/suricata` and `/var/lib/suricata` in volumes, and mounting
configuration read-only. A sensor container needs host networking (or equivalent) to see a
physical capture interface, which removes much of the network isolation a container would
normally provide.

### Source builds

Source builds (`./configure && make && make install`) require Rust and a set of development
libraries listed in the installation guide. Use them when you need specific compile options
or a platform without packages. Configure with `--prefix=/usr --sysconfdir=/etc
--localstatedir=/var` to match the paths in this guide.

### Verify the installation

```bash
suricata --build-info | head -n 20          # version and compiled-in features
sudo suricata -T -c /etc/suricata/suricata.yaml -v   # test the configuration and rules, then exit
systemctl status suricata
```

`-T` runs Suricata in test mode: it loads the configuration and rules and reports errors without
processing traffic. Once the service is running, the last line of
`/var/log/suricata/suricata.log` should report that all packet-processing threads are
initialised and the engine has started.

### Updating and removal

- **Engine:** update through the package manager (`sudo dnf upgrade suricata` or
  `sudo apt-get update && sudo apt-get upgrade suricata`). Patch releases within a branch are
  described by OISF as safe to install over each other. Before a **major** upgrade, read the
  upgrade guide: major versions change defaults and remove features. Packages do not overwrite
  an existing `classification.config` and `reference.config`, so compare them after upgrades.
- **Branch support:** OISF supports each major branch for about three years. The 7.0.x branch
  reached end of life on 2026-07-07, so plan to run 8.0.x.
- **Rules:** run `sudo suricata-update` regularly (for example, daily from a timer), then
  `sudo systemctl reload suricata` to load them. `suricata-update` tests the rules before
  writing them.
- **Rollback:** keep a copy of `/etc/suricata` and of the last known-good
  `/var/lib/suricata/rules/suricata.rules`. Downgrading packages is distribution-specific. A
  failed engine upgrade on a passive sensor costs visibility, not connectivity.
- **Removal:** `sudo dnf remove suricata` or `sudo apt-get remove suricata`. Logs in
  `/var/log/suricata` and rules in `/var/lib/suricata` may remain. Delete them deliberately,
  because the logs contain sensitive network metadata.

## Initial configuration

The steps below follow the official quickstart and RPM notes. They produce a passive IDS on
one interface.

**Step 1: Identify the capture interface** with `ip addr`. In a mirror-port design this is the NIC
   connected to the mirror port (often with no IP address). The examples use `enp2s0`.
**Step 2: Set `HOME_NET`** in `/etc/suricata/suricata.yaml` to the networks you are protecting. The
   default already covers the RFC 1918 private ranges. Narrow it to your real ranges, because
   many rules depend on the difference between `HOME_NET` and `EXTERNAL_NET`.
**Step 3: Set the AF_PACKET interface.** The shipped configuration names `eth0`. Change it to your
   interface:

```yaml
af-packet:
  - interface: enp2s0
    cluster-id: 99
    cluster-type: cluster_flow
    defrag: yes
    tpacket-v3: yes
```

**Step 4: On Fedora and EL, also update `/etc/sysconfig/suricata`.** The packaged file sets
   `OPTIONS="-i eth0 --user suricata "`, and the systemd unit passes those options to the
   engine. Replace `eth0` with your interface. Keep `--user suricata`.
**Step 5: Download rules.** `sudo suricata-update` fetches ET Open and writes
   `/var/lib/suricata/rules/suricata.rules`, which the default configuration loads.
**Step 6: Test, enable, and start:**

```bash
sudo suricata -T -c /etc/suricata/suricata.yaml -v
sudo systemctl enable --now suricata
sudo tail /var/log/suricata/suricata.log
```

**Step 7: Confirm detection works.** The quickstart uses ET Open rule 2100498, which matches a
   response containing `uid=0(root)`. Requesting the test page from a host whose traffic the
   sensor sees should raise the alert. The request goes to a third-party test site and is
   harmless:

```bash
sudo tail -f /var/log/suricata/fast.log &
curl http://testmynids.org/uid/index.html
```

**Step 8: Read EVE alerts** with `jq`:

```bash
sudo tail -f /var/log/suricata/eve.json | jq 'select(.event_type=="alert")'
```

## Security hardening

Suricata processes untrusted input with elevated privileges. OISF's security guide treats
this combination, and rule-distribution supply chains, as the main risks.

| Measure | Why |
|---|---|
| Run as a non-root user after start-up (`run-as` in `suricata.yaml`, or `--user suricata --group suricata`). Fedora and EPEL packages do this already. | Limits the impact of a parser vulnerability. Only Linux supports dropping privileges. |
| Keep the engine on the supported branch and patch promptly. | Parsers for many protocols are attack surface. 7.0.x no longer receives fixes. |
| Use a dedicated capture interface with no IP address, and manage the sensor over a separate interface. | The sensor cannot be reached through the monitored network, and capture traffic stays separate from management. |
| Restrict access to `/var/log/suricata` to the `suricata` group and named analysts. | EVE logs contain IP addresses, hostnames, URLs, DNS queries, and sometimes credentials sent in clear text. |
| Fetch rules only from sources you trust, review custom rules, and keep `suricata-update`'s test step. | Rules are code that runs against every packet. A malicious or broken rule set can blind or crash the sensor. |
| Add operators to the `suricata` group rather than giving them root. | `suricata-update` and `suricatasc` work without `sudo` for group members. |
| Leave `pcap-log` disabled unless you need packet capture, and then set strict size limits and retention. | Full packet capture stores payloads, multiplying privacy risk and disk use. |
| Keep `security.limit-noproc: true` (default) and consider enabling `security.landlock` after testing. | Prevents Suricata creating processes, and restricts file access on supporting kernels. Landlock is disabled by default. |
| Rotate and expire logs. Packages ship `/etc/logrotate.d/suricata` (daily, five rotations). | Bounds disk use and the window of retained personal data. |
| Prefer passive IDS. Introduce inline IPS only through change control with a designed failure mode. | Inline mode can cause outages and should never be a convenience default. |

## Practical usage examples

Examples use documentation addresses (`192.0.2.0/24`, `198.51.100.0/24`) and placeholder
interface names. They are illustrative and were not executed for this entry.

### Personal and home-lab use

**Monitor a mirrored lab segment.** Configure a managed switch to mirror the lab VLAN's uplink
port to a spare NIC on a mini PC running Suricata. Set `HOME_NET` to the lab subnet, enable the
service, and run `suricata-update` daily. Check packet drops after a busy period:

```bash
sudo tail -n 40 /var/log/suricata/stats.log | grep -E 'capture.kernel_(packets|drops)'
```

A rising `capture.kernel_drops` count means the sensor is missing traffic. Reduce enabled
outputs or rules, or give it more CPU before trusting its results.

**Investigate an alert.** Pull out the alert, then everything Suricata logged about the same flow
using the shared `flow_id`:

```bash
sudo jq -c 'select(.event_type=="alert") | {timestamp, src_ip, dest_ip, flow_id, sig: .alert.signature, sid: .alert.signature_id}' /var/log/suricata/eve.json | tail -n 5
sudo jq -c 'select(.flow_id==<FLOW_ID>)' /var/log/suricata/eve.json
```

Then ask: is the destination expected for this device? What does the rule actually match (read
the rule text in `suricata.rules` by its `sid`)? Is there matching DNS, HTTP, or TLS metadata? An
alert is a lead, not a verdict.

**Tune a noisy rule.** If an alert is confirmed benign, disable the rule for future updates by
adding its signature ID to `/etc/suricata/disable.conf`, then regenerate and reload:

```bash
echo "2100498" | sudo tee -a /etc/suricata/disable.conf
sudo suricata-update
sudo systemctl reload suricata
```

To silence a rule for one host only, use a `suppress` entry in `threshold.config` instead (for
example `suppress gen_id 1, sig_id 2100498, track by_src, ip 192.0.2.10`). The packaged
`suricata.yaml` has the `threshold-file` line **commented out**, so enable it first.

### Enterprise use

**Network intrusion detection at choke points.** Place sensors where traffic converges and is
still unencrypted enough to be useful: internet egress (inside any outbound NAT, so internal
addresses are visible), data-centre aggregation links, and links between security zones. Feed
them from TAPs or packet brokers rather than oversubscribed SPAN ports. Standardise
configuration and rule sets through configuration management, and alert on sensor health
(drops, process restarts, rule-update failures) as well as on detections.

**Security event forwarding.** Ship `eve.json` to a central platform rather than analysing it
on sensors. For example, a [Wazuh](../siem/wazuh.md) agent on the sensor can read the file with
a JSON `localfile` entry, as described in Wazuh's Suricata integration guide. Wazuh's ruleset
includes Suricata rules. Other log shippers can do the same. Decide which event types to ship:
alerts are small, while flow and protocol records are large but valuable for investigations.

## Enterprise deployment considerations

- **Authorisation and scope.** Network monitoring captures employee and third-party
  communications. Define in writing which links are monitored, which event types are retained,
  for how long, and who may search them. Involve legal, privacy, and works-council stakeholders
  where applicable. Document the scope per sensor.
- **Sensor architecture.** Size per link. Use AF_PACKET with multiple worker threads (or
  higher-performance capture methods such as AF_XDP or DPDK) on high-rate links. Follow the
  official high-performance configuration and tuning guidance. Watch kernel and NIC drop
  counters continuously.
- **Rule lifecycle.** Treat rules as managed content: a source list, change approval, local
  overrides in `disable.conf`, `enable.conf`, and `modify.conf`, and staged roll-out. Commercial
  rule subscriptions exist but are outside this entry's scope.
- **Inline IPS.** Inline mode changes stream-inspection behaviour (data is inspected
  immediately, in a sliding window, with a performance cost) and puts the engine in the
  forwarding path. Before using it, decide fail-open versus fail-closed behaviour, test
  hardware or software bypass, start with `alert` rules only, convert to `drop` selectively,
  and get change approval for every blocking rule.
- **Integration.** EVE JSON is consumed by most SIEM and log platforms. Enable `community-id`
  in the EVE configuration (disabled by default) if you want flow identifiers that can be
  correlated with other tools' logs. Confirm that the other tools in your pipeline support it.
- **Retention and access.** Classify EVE data as sensitive. Apply role-based access in the SIEM,
  encrypt it at rest, and set retention to the minimum justified by investigations and policy.
- **Support.** Suricata is community-supported by OISF. Commercial support and appliances come
  from third parties. Decide whether internal expertise is enough.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Service starts but sees no traffic | Wrong interface. Check `af-packet` in `suricata.yaml` **and** `OPTIONS` in `/etc/sysconfig/suricata` (or `/etc/default/suricata`). Confirm with `tcpdump -i <iface> -c 10` that packets arrive. |
| No alerts at all | No rules loaded, or the sensor sees no relevant traffic. Run `sudo suricata-update`, check `suricata.log` for the number of rules loaded, and test with rule 2100498. |
| `suricata -T` reports rule errors | Rules incompatible with the engine version, or a broken local rule. `suricata-update` downloads rules for the detected engine version. Fix or remove local rules. |
| High `capture.kernel_drops` | The sensor is overloaded or the capture configuration is too small. Reduce outputs, enable Hyperscan (`mpm-algo`), add worker threads, or offload to a larger sensor. Also check NIC drops with `ethtool -S`. |
| Many alerts from internal scanners or backups | Expected traffic matching generic rules. Suppress by source address in `threshold.config`, or disable the rule if it is never useful. |
| `suricata-update` permission denied | Not run as root and the user is not in the `suricata` group. Add the user to the group and log in again. |
| Disk filling with `eve.json` | Too many event types or no rotation. Check `/etc/logrotate.d/suricata`, and disable protocol records you do not use. |
| Suricata in a rootless Podman container cannot capture | Not supported by upstream. Use a rootful container with the documented capabilities, or a package installation. |
| Alerts show NAT or proxy addresses only | The sensor is outside the translation point. Move it to a position where original addresses are visible. |

## Alternatives and related tools

- [Zeek](zeek.md): network security monitoring through transaction logs and scripting. Often
  deployed alongside Suricata.
- [Wireshark](wireshark.md): interactive packet analysis for investigating what Suricata
  flagged.
- [Wazuh](../siem/wazuh.md): can collect and alert on Suricata EVE output from a sensor host.
- **Snort**: another long-established signature-based IDS/IPS engine (not yet documented here).
- [Security monitoring lab](../../environments/personal/security-monitoring-lab.md): shows
  where Suricata fits in a home-lab monitoring design.

## References

### Official documentation

- [Suricata website](https://suricata.io/)
- [Suricata user guide](https://docs.suricata.io/en/latest/)
- [Quickstart guide](https://docs.suricata.io/en/latest/quickstart.html)
- [EVE JSON output](https://docs.suricata.io/en/latest/output/eve/eve-json-output.html)
- [IPS concept](https://docs.suricata.io/en/latest/ips/ips-concept.html)
- [Source repository](https://github.com/OISF/suricata)

### Installation references

- [Download page](https://suricata.io/download/)
- [RPM installation (Fedora, EL)](https://docs.suricata.io/en/latest/install/rpm.html)
- [Ubuntu PPA installation](https://docs.suricata.io/en/latest/install/ubuntu.html)
- [Debian installation](https://docs.suricata.io/en/latest/install/debian.html)
- [Upgrading](https://docs.suricata.io/en/latest/upgrade.html)
- [Suricata-Update quick start](https://suricata-update.readthedocs.io/en/latest/quickstart.html)

### Security and deployment references

- [Security considerations](https://docs.suricata.io/en/latest/security.html)
- [Support status (platform tiers)](https://docs.suricata.io/en/latest/support-status.html)
- [End-of-life policy](https://suricata.io/our-story/eol-policy/)
- [Tuning considerations](https://docs.suricata.io/en/latest/performance/tuning-considerations.html)
- [Global thresholds and suppression](https://docs.suricata.io/en/latest/configuration/global-thresholds.html)
- [Wazuh: integrating Suricata](https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html)

### Verification notes

- **Sources checked:** 2026-11-12. The user-guide pages above were read from the documentation
  sources at the `suricata-8.0.8` tag in the official repository.
- **Release and support:** 8.0.8 published 2026-10-29 (GitHub releases API and download page).
  The EOL policy page states 7.0.x reached end of life on 2026-07-07.
- **Packages:** Fedora 44 `suricata` 8.0.8-1.fc44 (`dnf repoquery`). The package's unit file,
  `/etc/sysconfig/suricata`, logrotate file, and default `suricata.yaml` were inspected from the
  downloaded RPM without installing it: `OPTIONS` defaults to `-i eth0 --user suricata`, EVE
  and `fast.log` are enabled, `pcap-log` is disabled, `threshold-file` is commented out, and
  `default-rule-path` is `/var/lib/suricata/rules`. Debian: 7.0.10 in trixie, 8.0.8 in
  trixie-backports (Debian archive query).
- **Contradiction recorded:** the support-status page shipped with 8.0.8 still lists releases
  that are past their end of life (for example RHEL 7, Ubuntu 20.04, Debian 10) as Tier 1. This
  entry does not treat those releases as supported.
- **Conflict recorded:** Wazuh's Suricata integration guide was written for Suricata 6.0.8,
  installs rules by hand, and makes rule files world-writable. This entry follows Suricata's own
  `suricata-update` workflow and uses only the guide's `localfile` step.
- **Not executed:** Suricata was not installed or run for this entry. All commands come from
  the official documentation and package contents, and are illustrative.
- **Unresolved:** no OISF-published container image or macOS package was identified; resource
  sizing is workload-specific and no official minimum exists.
