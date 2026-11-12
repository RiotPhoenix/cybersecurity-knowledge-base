---
tool: Zeek
category: network-security
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://zeek.org/
repository: https://github.com/zeek/zeek
requires_authorisation: true
---

# Zeek

!!! warning "Authorised use only"
    Zeek records detailed metadata about network communications, including DNS queries,
    web requests, and certificate details. Monitor only networks you own or are explicitly
    authorised in writing to monitor, and treat its logs as sensitive personal data.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://zeek.org/> |
| Source repository | <https://github.com/zeek/zeek> |
| Licence | Three-clause BSD licence (`COPYING`); some bundled files carry their own notices |
| Supported operating systems | Linux (official binary packages for Fedora, Debian, Ubuntu, openSUSE, and Raspberry Pi OS), official Docker images; macOS, FreeBSD, and OpenBSD through third-party packages |
| Maintenance status | Active: 9.0.1 (current long-term-support line) and 8.0.11 (previous LTS) released 2026-10-26. Checked 2026-11-12 |
| Category | Network Security |
| Personal suitability | Medium: excellent for learning how networks behave, but needs a traffic copy, disk for logs, and time to learn the log formats |
| Enterprise suitability | High: a standard network-security-monitoring sensor, scalable as a cluster, if you have staff to operate it and a log platform to store its output |
| Tested versions | Not yet tested |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

Zeek (formerly Bro) is an open-source **network security monitoring** (NSM) platform. It
passively observes traffic, reassembles connections, parses dozens of protocols, and writes a
set of structured, correlated logs describing what happened: every connection (`conn.log`),
DNS query and answer (`dns.log`), HTTP request (`http.log`), TLS handshake (`ssl.log`),
certificate (`x509.log`), file transfer (`files.log`), and protocol oddity (`weird.log`). It
also has a domain-specific scripting language for writing custom analysis and detections.

The Zeek project is maintained by an open-source community, with a public release cadence:
a **long-term support (LTS)** release about once a year (versions `x.0.0`), and **feature
releases** about every four months (`x.1`, `x.2`) that are supported only until the next
feature release.

### How Zeek differs from Suricata

| | Zeek | [Suricata](suricata.md) |
|---|---|---|
| Primary output | Transaction logs describing all observed activity | Alerts when traffic matches signatures, plus protocol metadata |
| Detection model | Scripts (behavioural or policy logic you write or install), plus a basic signature framework | Large, community-maintained signature rule sets such as ET Open |
| Typical question answered | "What did this host talk to, and how?" | "Did anything match known-bad patterns?" |
| Inline blocking | No. Zeek is passive | Yes, in IPS mode |

Zeek is **not a drop-in replacement for a signature IDS**. It ships no equivalent of a large
maintained rule set, and its notices are driven by scripts. It is most valuable as the
evidence record that you search during an investigation, and it is commonly deployed
alongside a signature engine on the same traffic copy.

## Features and capabilities

- **Structured logs.** Tab-separated logs by default, with a header describing each field.
  JSON output is available by loading the `policy/tuning/json-logs.zeek` script. Logs share a
  connection identifier (`uid`), so a DNS answer, the connection that followed, and the TLS
  certificate presented can be joined.
- **Protocol analysis.** Analysers for common protocols, independent of port numbers. Zeek
  identifies HTTP on a non-standard port as HTTP.
- **Scripting and packages.** The Zeek language reacts to network events. The `zkg` package
  manager installs community packages. The Spicy toolchain, included in official packages,
  is used to write new protocol parsers.
- **Intelligence framework.** Matches observed indicators (addresses, domains, hashes) against
  lists you supply, and logs hits to `intel.log`.
- **Offline analysis.** `zeek -r capture.pcap` produces the same logs from a capture file,
  which is the safest way to learn.
- **Cluster architecture.** Workers capture and analyse traffic, a manager coordinates, and
  optional proxies and loggers spread load. Workers on Linux can load-balance with AF_PACKET
  fanout.
- **ZeekControl (`zeekctl`).** Manages standalone and cluster deployments: configuration
  checks, deployment, restarts, log rotation and archiving.

Limitations:

- **Visibility depends on placement.** Zeek analyses only the packets delivered to its
  interface. A mirror port, TAP, or equivalent is required to observe other hosts.
- **Encrypted traffic.** Zeek logs TLS metadata (server name, certificate, versions) but not
  encrypted content.
- **Storage and search are your problem.** Zeek writes files. Long-term search requires a log
  platform or disciplined use of command-line tools.
- **Learning curve.** The logs are rich and the scripting language is powerful, but neither is
  self-explanatory.

## System requirements

- **Platform.** Official binary packages are built on the openSUSE Build Service (OBS) for
  Linux distributions. On 2026-11-12 the OBS project offered Fedora 43 and 44, Debian 12 and 13,
  Ubuntu 22.04, 24.04, 26.04, and 26.10, openSUSE Tumbleweed, and Raspberry Pi OS 12 and 13.
  Official Docker images are Debian-based. Homebrew (macOS) and FreeBSD and OpenBSD ports are
  **not maintained by the Zeek project**.
- **Privileges.** Live capture needs raw-socket access. Zeek often runs as root. The official
  security guidance suggests granting only the `CAP_NET_RAW` and `CAP_NET_ADMIN` capabilities
  on Linux instead.
- **Hardware.** No fixed minimum is published. Load scales with traffic volume and the
  scripts loaded. A small lab link is handled by a single standalone process. Busy links need a
  cluster with one worker process per CPU core assigned to capture.
- **Network.** A dedicated capture interface that receives a copy of the traffic, and a
  separate management interface. The Zeek documentation recommends disabling NIC offloading
  features on the capture interface so that Zeek sees packets as they appear on the wire.
- **Disk.** Every connection is logged. Size disk for your retention period and watch growth
  during the first weeks. ZeekControl warns by e-mail when free disk falls below 5% by default.

## Installation

| Method | Use when | Notes |
|---|---|---|
| OBS binary packages (`zeek-9.0`, `zeek-8.0`, `zeek`) | Linux sensors | `zeek-X.0` packages pin an LTS line. `zeek` tracks the latest release. Installs under `/opt/zeek`. |
| Docker images (`zeek/zeek:lts`, `zeek/zeek:latest`, `zeek/zeek:<version>`) | Offline analysis and containerised sensors | Also published to Amazon ECR Public. |
| Homebrew, FreeBSD, OpenBSD ports | Workstations or BSD sensors | Third-party packages. Check the version. |
| Source build | Custom builds or unsupported platforms | See the official *Building from source* guide. |

Choose `zeek-9.0` for the current LTS line. `zeek-8.0` (previous LTS) remains maintained for a
transition period. The Zeek documentation notes that its older `zeek-lts` packages "remain
visible on OBS but are no longer supported".

### Fedora

Prerequisites: an administrator account. The OBS repository file is published for each Fedora
release. Add it, then install the LTS package:

```bash
sudo dnf config-manager addrepo --from-repofile=https://download.opensuse.org/repositories/security:/zeek/Fedora_44/security:zeek.repo
sudo dnf install zeek-9.0
```

`dnf` shows the repository's signing-key fingerprint and asks you to accept it on first use.
The `.repo` file sets `gpgcheck=1`. `sudo` is required to add repositories and install
packages. Zeek is not in Fedora's own repositories.

### Debian and Ubuntu

From the official installation guide, adapted for Debian 13. For Ubuntu, replace `Debian_13`
with `xUbuntu_24.04` (or another listed release):

```bash
echo 'deb https://download.opensuse.org/repositories/security:/zeek/Debian_13/ /' | sudo tee /etc/apt/sources.list.d/security:zeek.list
curl -fsSL https://download.opensuse.org/repositories/security:zeek/Debian_13/Release.key | gpg --dearmor | sudo tee /etc/apt/trusted.gpg.d/security_zeek.gpg > /dev/null
sudo apt update
sudo apt install zeek-9.0
```

The second command downloads the repository's signing key and stores it where `apt` trusts it.
Inspect the key fingerprint (`gpg --show-keys`) if your policy requires it.

### Add Zeek to your path

Packages install into `/opt/zeek`, which is not on the default `PATH`:

```bash
echo 'export PATH=/opt/zeek/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

### Containers

```bash
docker pull zeek/zeek:lts
docker run --rm -v "$PWD":/pcap:Z -w /pcap zeek/zeek:lts zeek -r /pcap/capture.pcap
```

The second command analyses `capture.pcap` from the current directory and writes logs beside
it. It needs no network access or extra privileges, which makes it a safe way to learn. The
`:Z` suffix relabels the directory for SELinux hosts such as Fedora. Live capture from a
container needs host networking and the raw-capture capabilities, which removes most of the
container's network isolation. Persist `/opt/zeek/logs` and `/opt/zeek/spool` and keep
configuration under version control. Pin a version tag and update deliberately. `lts` and
`latest` move.

### macOS and BSD

`brew install zeek`, `sudo pkg install -y zeek` (FreeBSD), or `sudo pkg_add zeek` (OpenBSD)
install third-party packages. These are reasonable for offline analysis on a workstation. Check
that the version is a supported release.

### Verify the installation

```bash
zeek --version
zeek -N Zeek::AF_Packet          # Linux: the AF_PACKET packet source should be listed
zeekctl help | head -n 5
```

Then process a capture file and check that `conn.log` appears in the working directory:

```bash
mkdir -p ~/zeek-test && cd ~/zeek-test
zeek -C -r /path/to/capture.pcap
ls *.log
```

`-C` tells Zeek to ignore invalid checksums, which are common in captures taken on the sending
host because of NIC checksum offloading.

### Updating and removal

- **Patch releases:** `sudo dnf upgrade zeek-9.0` or `sudo apt update && sudo apt upgrade`, then
  `sudo /opt/zeek/bin/zeekctl deploy` to restart with the new version. Release notes (the `NEWS`
  file) list security fixes. 9.0.1 and 8.0.11 fixed several high-severity parser issues.
- **Moving to a new LTS line:** install the new `zeek-X.0` package deliberately. Read the
  deprecations in the release notes: functionality deprecated in one LTS line may be removed in
  the next. Test your `local.zeek` and installed packages with `zeekctl check` before
  `deploy`.
- **Configuration survives upgrades:** `local.zeek` "is not overwritten by Zeek upgrades",
  according to the quickstart. Keep `/opt/zeek/etc` and `/opt/zeek/share/zeek/site` in version
  control anyway.
- **Removal:** `sudo /opt/zeek/bin/zeekctl stop`, then remove the package. Logs in
  `/opt/zeek/logs` remain until deleted deliberately.

## Initial configuration

A standalone sensor on one interface, following the official quickstart.

**Step 1: Choose the capture interface** (here `enp2s0`, connected to a mirror port).
**Step 2: Set it in `/opt/zeek/etc/node.cfg`:**

```ini
[zeek]
type=standalone
host=localhost
interface=enp2s0
```

**Step 3: List local networks in `/opt/zeek/etc/networks.cfg`** (one CIDR per line, with a comment).
   Zeek uses this to decide which side of a connection is local:

```text
192.0.2.0/24        Home lab
198.51.100.0/24     Lab services
```

**Step 4: Review `/opt/zeek/share/zeek/site/local.zeek`.** It loads useful policy scripts by default
   (software detection, known hosts and services, certificate validation, capture-loss
   reporting). To write JSON logs, which many log platforms prefer, add:

```text
@load policy/tuning/json-logs.zeek
```

**Step 5: Set log retention in `/opt/zeek/etc/zeekctl.cfg`.** By default, logs rotate every hour
   (`LogRotationInterval = 3600`) and archived logs **never expire** (`LogExpireInterval = 0`).
   Set an expiry, for example `LogExpireInterval = 30day`. Expiry needs `zeekctl cron` (step 7).
**Step 6: Check and deploy:**

```bash
sudo /opt/zeek/bin/zeekctl check
sudo /opt/zeek/bin/zeekctl deploy
sudo /opt/zeek/bin/zeekctl status
```

**Step 7: Schedule `zeekctl cron`**, which restarts crashed nodes, archives logs, applies expiry, and
   checks disk space. The ZeekControl documentation suggests every five minutes, run as the same
   user that runs Zeek. Add to root's crontab (`sudo crontab -e`):

```text
*/5 * * * * /opt/zeek/bin/zeekctl cron
```

Current logs appear in `/opt/zeek/logs/current/`. Rotated logs are compressed into dated
directories under `/opt/zeek/logs/`.

## Security hardening

From the Zeek *Security considerations* guide, with reasons:

| Measure | Why |
|---|---|
| Place the sensor's management interface in an access-controlled management network, and give the capture interface no IP address. | Zeek parses untrusted packets and often runs with high privileges. It should not be reachable from the networks it monitors. |
| Patch promptly, and stay on a supported LTS or current feature release. | Parser vulnerabilities are fixed in maintenance releases. Feature releases go out of support at the next feature release. |
| Prefer the `CAP_NET_RAW` and `CAP_NET_ADMIN` capabilities to running as root (systemd `AmbientCapabilities=` or a capability-aware ZeekControl extension). | Reduces the impact of a compromise of the Zeek process. |
| Make the log directory and files non-world-readable, and restrict access to named analysts. | The documentation warns that logs contain internal hostnames, URLs, and protocol metadata. |
| Encrypt cluster communication on multi-host clusters. ZeroMQ (the default backend for ZeekControl since 8.1) supports CURVE encryption. | Protects cluster messages from eavesdropping and authenticates nodes. |
| Keep the WebSocket API on its default loopback address (`127.0.0.1:27759`). | The API has no authentication or authorisation and assumes localhost is trusted. |
| Protect the SSH credentials ZeekControl uses on multi-host clusters, and limit that account's rights. | The account has administrative access across the cluster. |
| Set log expiry and monitor disk. | Unbounded retention increases privacy exposure, and a full disk stops logging. |
| Install `zkg` packages only from sources you trust, and review them. | Packages run code inside the sensor. |

## Practical usage examples

Illustrative examples using documentation addresses and placeholder file names. Not executed
for this entry.

### Personal and home-lab use

**Understand DNS and HTTP metadata from a capture.** Record a few minutes of your own lab
traffic with Wireshark or `tcpdump`, then analyse it offline:

```bash
cd ~/zeek-test
zeek -C -r lab-traffic.pcap
zeek-cut ts id.orig_h query qtype_name answers < dns.log | head
zeek-cut ts id.orig_h host uri user_agent < http.log | head
```

`zeek-cut` (included with Zeek) prints the named columns from tab-separated logs. Things to look
for: devices that resolve names you do not recognise, plain-HTTP requests from devices you
assumed used HTTPS, and user agents revealing outdated software.

**Investigate a connection.** Start from `conn.log` to see who talked to whom, for how long, and
how much data moved. Then follow the `uid` into the protocol logs:

```bash
zeek-cut uid id.orig_h id.resp_h id.resp_p proto service duration orig_bytes resp_bytes conn_state < conn.log | sort -k8 -n -r | head
grep '<UID>' *.log
```

The `conn_state` field shows how the connection ended. For example, `S0` means a connection
attempt that received no reply, a common sign of scanning or misconfiguration.

### Enterprise use

**Network security monitoring.** Deploy Zeek clusters at the same choke points as your
signature IDS (egress, data-centre aggregation, zone boundaries), fed by TAPs or packet brokers.
Ship JSON logs to the SIEM or a dedicated log store, keep `conn.log`, `dns.log`, `ssl.log`,
`http.log`, and `files.log` for the retention period your investigations need, and watch
`capture_loss.log` and `stats.log` for sensor health.

**Network incident investigation.** When an endpoint alert arrives, Zeek logs answer the
scoping questions: which external addresses the host contacted before and after the alert, which
domains it resolved, which certificates were presented, which files crossed the wire, and which
other internal hosts contacted the same destinations. Pivot on the destination across all hosts
in `conn.log` to find the scope of an incident.

## Enterprise deployment considerations

- **Authorisation and scope.** Zeek's logs record the communications of employees, customers,
  and third parties. Agree in writing which links are monitored, which logs are kept and for
  how long, who may search them, and how searches are audited. Involve privacy and legal
  stakeholders where required.
- **Cluster design.** A cluster has a manager, optional loggers and proxies, and workers. On
  Linux, workers use `lb_method=af_packet` with `lb_procs=<N>` to spread traffic across
  processes. Pin workers to CPU cores (`pin_cpus`) on busy sensors. Separate loggers reduce load
  on the manager.
- **Cluster backend.** The NEWS file for 9.0 deprecates the Broker backend. ZeroMQ has been
  ZeekControl's default since 8.1, and Broker is likely to be removed in 10.1. New clusters
  should use ZeroMQ, with CURVE encryption across hosts.
- **Capacity and loss monitoring.** Track capture loss and packet drops per worker. Zeek's
  results are incomplete when it drops packets, and gaps are easy to miss.
- **Log pipeline.** Decide the format (JSON simplifies ingestion), the transport to your log
  platform, and the parsing. Size storage for volume per day multiplied by retention. Plan
  index and schema changes when Zeek adds fields in new releases.
- **Change management.** Version `local.zeek`, `node.cfg`, `networks.cfg`, and installed packages.
  Test upgrades in staging, especially when moving between LTS lines.
- **Support.** Zeek is community-supported. Commercial products build on it, but the open-source
  project offers no contractual support.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `zeek: command not found` | `/opt/zeek/bin` is not on `PATH`. Add it, or use full paths. |
| `conn.log` shows only the sensor's own traffic | The interface receives no mirrored traffic. Verify the mirror or TAP with `tcpdump -i <iface>`. |
| Many `bad_TCP_checksum` entries in `weird.log` | Checksum offloading on the capturing host. Use `-C` for captures, and disable offloading (`ethtool -K`) on live capture interfaces. |
| Missing or partial logs for big flows | Offloading features such as GRO or LRO merge packets. Disable them on the capture interface, as the cluster setup guide recommends. |
| `zeekctl deploy` fails | Script or configuration error. Run `zeekctl check` and read the reported file and line. |
| Disk full | `LogExpireInterval = 0` (never expire) or `zeekctl cron` is not scheduled. Set an expiry and add the cron job. |
| High capture loss | Too much traffic for one process. Add workers with AF_PACKET load balancing, reduce loaded scripts, or move to larger hardware. |
| Nodes crash and stay down | `zeekctl cron` not running. It restarts crashed nodes. Check `zeekctl diag` for the crash report. |
| Logs are tab-separated but your platform expects JSON | Load `policy/tuning/json-logs.zeek` in `local.zeek` and redeploy. |

## Alternatives and related tools

- [Suricata](suricata.md): signature-based IDS/IPS with protocol logging. Complements Zeek.
- [Wireshark](wireshark.md): interactive packet analysis when you need payload-level detail.
- [Wazuh](../siem/wazuh.md): endpoint-focused monitoring. Wazuh's ruleset contains Zeek rules
  derived from a third-party project, but no documented integration procedure (see
  verification notes).
- [Security monitoring lab](../../environments/personal/security-monitoring-lab.md): where Zeek
  fits in a home-lab design.

## References

### Official documentation

- [Zeek website](https://zeek.org/)
- [Zeek documentation](https://docs.zeek.org/en/current/)
- [Quick start guide](https://docs.zeek.org/en/current/quickstart.html)
- [Source repository](https://github.com/zeek/zeek)
- [ZeekControl documentation](https://github.com/zeek/zeekctl)
- [Release cadence](https://github.com/zeek/zeek/wiki/Release-Cadence)

### Installation references

- [Installing Zeek](https://docs.zeek.org/en/current/install.html)
- [Zeek packages on the openSUSE Build Service](https://build.opensuse.org/project/show/security:zeek)
- [Official Docker images](https://hub.docker.com/u/zeek)
- [Zeek releases](https://github.com/zeek/zeek/releases)

### Security and deployment references

- [Security considerations](https://docs.zeek.org/en/current/security-considerations.html)
- [Cluster setup](https://docs.zeek.org/en/current/cluster-setup.html)
- [Release notes (NEWS)](https://github.com/zeek/zeek/blob/master/NEWS)
- [Security advisories](https://github.com/zeek/zeek/security/advisories)

### Verification notes

- **Sources checked:** 2026-11-12. Documentation pages were read from the `doc/` directory of the
  `v9.0.1` tag. The separate `zeek-docs` repository is archived, and its `master` branch still
  describes 7.0 as the current LTS.
- **Releases:** 9.0.1 and 8.0.11 published 2026-10-26 (GitHub releases API). Docker Hub's `lts`
  and `latest` tags both pointed at 9.0.1 on 2026-11-12. Under the published release cadence,
  `x.0.0` releases are LTS, which makes 9.0 the current LTS line.
- **Packages:** the OBS project listed `zeek-9.0` 9.0.1, `zeek-8.0` 8.0.11, and `zeek` 9.0.1 for
  Fedora 44 and Debian 13. The Fedora 44 `.repo` file and the Debian 13 and Ubuntu 24.04 signing
  keys were fetched successfully.
- **Contradictions recorded:** the 9.0.1 installation guide still names "8.0.x" and "7.0.x" as the
  current LTS package lines, although OBS publishes `zeek-9.0`. The guide calls `zeek-lts` packages
  unsupported, yet OBS still publishes `zeek-lts` at 9.0.1. This entry follows the release cadence
  and the published packages.
- **Configuration defaults:** `LogRotationInterval = 3600`, `LogExpireInterval = 0`, and
  `MinDiskSpace = 5` were confirmed in ZeekControl's `zeekctl.cfg.in` and `options.py`.
- **Wazuh relationship:** Wazuh 4.14.10's ruleset contains `0635-owlh-zeek_rules.xml`, derived
  from a third-party project. No Wazuh user-manual procedure for Zeek logs was found, so any Zeek
  to Wazuh pipeline is unvalidated.
- **Licence:** the GitHub API reports `NOASSERTION`, because the licence is not auto-detected.
  The `COPYING` file at `v9.0.1` contains the three-clause BSD terms (copyright the Regents of the
  University of California) and notes that some files carry their own notices.
- **Not executed:** Zeek was not installed or run for this entry.
