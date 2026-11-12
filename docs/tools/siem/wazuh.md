---
tool: Wazuh
category: siem
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://wazuh.com/
repository: https://github.com/wazuh/wazuh
requires_authorisation: false
---

# Wazuh

!!! info "Endpoint monitoring collects personal data"
    Wazuh agents read logs, file changes, and software inventories on the machines they run on.
    Deploy agents only on systems you administer, and in organisations, only under a monitoring
    policy that users have been told about.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://wazuh.com/> |
| Source repository | <https://github.com/wazuh/wazuh> (server and agent; the indexer, dashboard, and Docker files are in other repositories under the [wazuh organisation](https://github.com/wazuh)) |
| Licence | GPL-2.0 (server and agent, with an OpenSSL linking exception) and Apache-2.0 (other components), as stated in the documentation |
| Supported operating systems | Central components: 64-bit Linux (Amazon Linux, CentOS Stream 10, RHEL 7 to 10, Ubuntu 16.04 to 24.04 recommended), or Docker. Agents: Linux, Windows, macOS, Solaris, AIX, HP-UX |
| Maintenance status | Active: 4.14.10 released 2026-11-09. 5.0.0 is at release-candidate stage (rc2, 2026-10-30). Checked 2026-11-12 |
| Category | SIEM and Log Management |
| Personal suitability | Medium: capable and free, but the central stack needs about 4 vCPU and 8 GiB RAM, plus regular maintenance |
| Enterprise suitability | Medium to High: scalable and widely used, with commercial support available from the vendor; plan for indexer operations and a version-locked upgrade process |
| Tested versions | Not yet tested |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

Wazuh is an open-source security platform, developed by Wazuh Inc., that combines endpoint
monitoring with log collection, detection rules, and alerting. Its documentation describes it
as providing "unified XDR and SIEM protection for endpoints and cloud workloads". It grew out
of the OSSEC host intrusion detection project.

Wazuh has four components:

| Component | Role | Default port |
|---|---|---|
| **Agent** | Runs on each monitored endpoint. Collects logs, file-integrity events, inventory, and configuration-assessment results. | Connects out to the server on 1514/TCP; enrols on 1515/TCP |
| **Server** (manager) | Decodes events, applies rules, raises alerts, manages agents. Uses Filebeat to send data to the indexer. | API on 55000/TCP |
| **Indexer** | Stores and searches alerts and events. A search engine based on OpenSearch. | 9200/TCP (REST API); 9300 to 9400/TCP (cluster) |
| **Dashboard** | Web interface for searching, visualising, and managing. | 443/TCP |

**Endpoint monitoring is not network monitoring.** Wazuh agents see what happens *on the host*:
log entries, processes, files, packages, and configuration. They do not observe traffic between
other devices. For network visibility, pair Wazuh with a network sensor such as
[Suricata](../network-security/suricata.md) or [Zeek](../network-security/zeek.md), whose output
an agent can collect.

**What Wazuh is not.** Wazuh covers many SIEM and XDR use cases, but it does not automatically
replace every capability of a commercial SIEM, EDR, or XDR product. For example, compare
large-scale data ingestion and retention economics, behavioural endpoint protection and
remediation, managed threat-hunting services, and vendor-maintained content for your log
sources against your requirements before treating it as a replacement.

## Features and capabilities

- **Log data collection** from files, the Windows event channel, journald, syslog, and command
  output. JSON log files (such as Suricata's EVE output) can be read with the `json` log format.
- **File integrity monitoring (FIM).** The `syscheck` module records hashes and attributes of
  monitored files, on a schedule or in real time (`realtime="yes"`, Linux and Windows only), and
  alerts on changes. Since 4.13.0, Windows FIM no longer supports network paths or mapped drives.
- **Detection rules and decoders.** A large ruleset of XML decoders and rules ships with the
  server, and you can add local rules. Rules assign levels (0 to 15) that drive alerting.
- **Vulnerability detection.** Enabled by default on the manager. It uses the agents' software
  inventory (Syscollector) and a vulnerability feed downloaded from Wazuh's CTI service
  (`cti.wazuh.com`), updated hourly by default.
- **Security configuration assessment (SCA).** Checks endpoints against policy files based on
  hardening benchmarks.
- **Active response.** Can run scripts on agents when rules fire, for example to block an
  address. Use with caution: automated responses can disrupt legitimate users.
- **Agentless and syslog collection** for network devices, and integrations for cloud services.
- **Clustering** of the server and the indexer for scale and high availability.

Limitations:

- **Resource-hungry central stack.** The indexer is the heaviest part (see below).
- **Strict version coupling.** All central components must run the same version, including
  the patch level, and the manager must be the same version as, or newer than, the agents.
- **Tuning required.** Default rules generate many low-level alerts. Useful alerting needs
  tuning to your environment.
- **Operational dependency on Wazuh-hosted services** for the vulnerability feed, unless you
  follow the offline update procedures.

## System requirements

From the quickstart (all central components on one host, about 90 days of indexed alerts):

| Agents | CPU | RAM | Storage (90 days) |
|---|---|---|---|
| 1 to 25 | 4 vCPU | 8 GiB | 50 GB |
| 26 to 50 | 8 vCPU | 8 GiB | 100 GB |
| 51 to 100 | 8 vCPU | 8 GiB | 200 GB |

- **Central components:** 64-bit x86_64 or AArch64 Linux. The documentation recommends Amazon
  Linux 2 and 2023, CentOS Stream 10, RHEL 7 to 10, and Ubuntu 16.04 to 24.04. **Fedora and
  Debian are not in that list.** Install the central stack on a recommended distribution, or use
  Docker, rather than on a Fedora workstation.
- **Docker single-node stack:** at least 4 CPU cores, 8 GB RAM, and 50 GB disk on the Docker host,
  plus the kernel setting `vm.max_map_count=262144` for the indexer.
- **Agents:** lightweight, about 35 MB of RAM on average according to the documentation. Root or
  Administrator rights to install.
- **Network:** agents must reach the server on 1514/TCP and 1515/TCP (enrolment). Analysts need
  the dashboard on 443/TCP. The server needs outbound HTTPS to `cti.wazuh.com` for vulnerability
  data.

## Installation

| Method | Use when | Notes |
|---|---|---|
| Installation assistant (`wazuh-install.sh -a`) | All-in-one lab or small deployment | Fastest. Generates certificates and random passwords. |
| Step-by-step package installation | Distributed or customised deployments | Install the indexer, then the server, then the dashboard. |
| Docker (`wazuh-docker`, single-node or multi-node) | Container hosts | Official Compose files. **Ships with documented default passwords** that you must change. |
| Agent packages (APT, DNF/Yum, ZYpp, MSI, PKG) | Every monitored endpoint | Configured with deployment variables. |
| Virtual machine image, Kubernetes, Ansible, Puppet | Evaluation or automation | Listed as installation alternatives (not covered here). |

### Central components with the installation assistant

On a fresh Ubuntu 24.04 or RHEL-compatible host (not Fedora) with at least 4 vCPU and 8 GiB RAM.
The official quickstart downloads and runs the script in one line. The steps are separated
here so you can read the script before running it as root:

```bash
curl -fsSO https://packages.wazuh.com/4.14/wazuh-install.sh
less wazuh-install.sh
sudo bash ./wazuh-install.sh -a
```

`-a` installs the indexer, server, and dashboard on the same host. Root is required because the
script adds package repositories, installs services, and generates certificates. At the end it
prints the dashboard URL and the `admin` password. All generated passwords are saved in
`wazuh-passwords.txt` inside `wazuh-install-files.tar`, in the directory where you ran the
script. That archive also contains the certificates. Move it to protected offline storage
(for example, your password manager or an encrypted volume), then delete the copy on the server.

The dashboard uses a self-signed certificate, so browsers show a warning on first access. For
anything beyond a short-lived lab, replace it with a certificate from a trusted internal CA.

After installation, the official documentation recommends **disabling the Wazuh package
repository** to prevent an unplanned upgrade breaking version alignment:

```bash
sudo sed -i "s/^enabled=1/enabled=0/" /etc/yum.repos.d/wazuh.repo        # RHEL-compatible
sudo sed -i "s/^deb /#deb /" /etc/apt/sources.list.d/wazuh.list && sudo apt update   # Ubuntu
```

### Docker single-node stack

From the official Docker deployment guide. Prerequisites: Docker Engine with the Compose plugin,
Git, and the kernel setting below on the Docker host:

```bash
echo "vm.max_map_count=262144" | sudo tee /etc/sysctl.d/99-wazuh-max-map-count.conf
sudo sysctl --system
git clone https://github.com/wazuh/wazuh-docker.git -b v4.14.10
cd wazuh-docker/single-node
docker compose -f generate-indexer-certs.yml run --rm generator
```

Before starting the stack, review `docker-compose.yml`. The shipped file:

- publishes **every** port on all host interfaces, including the indexer API (9200) and the
  server API (55000), which do not need to be reachable from other hosts in a single-node lab;
- sets the indexer, dashboard, and API credentials to **default values that are published in
  the repository and documentation**.

Bind administrative ports to loopback, publish agent ports only on the lab interface (here the
documentation address `192.0.2.20`), and follow the official procedure *Changing the default
password of Wazuh users* for Docker **before** the dashboard is reachable from any network:

```yaml
# Edited port mappings in docker-compose.yml (excerpt)
  wazuh.manager:
    ports:
      - "192.0.2.20:1514:1514"
      - "192.0.2.20:1515:1515"
      - "127.0.0.1:55000:55000"
  wazuh.indexer:
    ports:
      - "127.0.0.1:9200:9200"
  wazuh.dashboard:
    ports:
      - "192.0.2.20:443:5601"
```

Then start the stack with `docker compose up -d`. Persistent data lives in the named volumes
defined in the Compose file. Back them up (see [Security hardening](#security-hardening)). Docker
does not reload configuration dynamically, so restart the stack after configuration changes.

### Agents on Linux (including Fedora)

Add the Wazuh repository (RPM-based example from the official agent guide, for RHEL 9 and later
syntax):

```bash
sudo rpm --import https://packages.wazuh.com/key/GPG-KEY-WAZUH
sudo tee /etc/yum.repos.d/wazuh.repo > /dev/null << 'EOF'
[wazuh]
gpgcheck=1
gpgkey=https://packages.wazuh.com/key/GPG-KEY-WAZUH
enabled=1
name=EL-$releasever - Wazuh
baseurl=https://packages.wazuh.com/4.x/yum/
priority=1
EOF
```

Install the agent, pointing it at your manager (the documentation address `192.0.2.20` and the
name `lab-ws01` are placeholders). The packages are generic RPM and DEB builds. Fedora is not
named individually in the agent documentation reviewed:

```bash
sudo WAZUH_MANAGER="192.0.2.20" WAZUH_AGENT_NAME="lab-ws01" dnf install wazuh-agent
```

On Debian and Ubuntu, import the key into `/usr/share/keyrings/wazuh.gpg`, add
`deb [signed-by=/usr/share/keyrings/wazuh.gpg] https://packages.wazuh.com/4.x/apt/ stable main`
to `/etc/apt/sources.list.d/wazuh.list`, and run the same command with `apt-get install`.
Windows and macOS agents are installed from MSI and PKG packages with equivalent deployment
variables. See the official agent installation pages.

If the manager requires an enrolment password (recommended, see below), write it to the agent's
`authd.pass` file before starting the service, rather than putting it on the command line where
it is saved in shell history:

```bash
read -rsp 'Enrolment password: ' WPW; echo
printf '%s\n' "$WPW" | sudo tee /var/ossec/etc/authd.pass > /dev/null; unset WPW
sudo chmod 640 /var/ossec/etc/authd.pass
sudo chown root:wazuh /var/ossec/etc/authd.pass
sudo systemctl daemon-reload
sudo systemctl enable --now wazuh-agent
```

Agents should not be newer than the manager. The documentation recommends disabling the
repository on agents too (`sudo sed -i "s/^enabled=1/enabled=0/" /etc/yum.repos.d/wazuh.repo`).

### Verify the installation

- **Central stack:** `sudo systemctl status wazuh-indexer wazuh-manager wazuh-dashboard`, or
  `docker compose ps` for Docker. All should be running. Open `https://<DASHBOARD_ADDRESS>` and
  log in.
- **Agent:** `sudo systemctl status wazuh-agent`, then check the agent log for a successful
  connection: `sudo grep -iE 'connected|enroll' /var/ossec/logs/ossec.log | tail`.
- **On the manager:** `sudo /var/ossec/bin/agent_control -l` lists agents and their status. The
  agent should also appear as *active* in the dashboard.

### Updating and removal

- **Order matters.** Upgrade the central components first, keeping them at identical versions,
  then upgrade agents. The upgrade guide states that all central components must match exactly
  and that the manager must be the same version as, or newer than, the agents. Note also that
  Wazuh indexer 4.14.10 is "specifically compatible with Filebeat-OSS 7.10.2".
- **Procedure:** follow the version-specific upgrade guide. Re-enable the repository only for the
  upgrade, then disable it again. Back up configuration (and take indexer snapshots) first.
  Agents can be upgraded remotely from the manager or the API.
- **Major versions:** 5.0.0 is in release-candidate testing. Do not deploy release candidates in
  production, and expect a dedicated migration guide for the major version.
- **Removal:** the installation assistant uninstalls the central components with `-u`
  (`sudo bash ./wazuh-install.sh -u`). Agents are removed with the package manager. Remove the
  agent from the manager as well, so stale agents do not clutter inventories.

## Initial configuration

**Step 1: Protect the generated credentials.** Store the passwords from the installation archive (or
   your new Docker passwords) in a password manager, and change the `admin` password with the
   Wazuh passwords tool if it was ever shown on screen in a shared session.
**Step 2: Require an enrolment password.** By default, any agent that can reach port 1515 can enrol.
   Enable password authentication on the manager in `/var/ossec/etc/ossec.conf`:

```xml
<auth>
  <use_password>yes</use_password>
</auth>
```

   Then create `/var/ossec/etc/authd.pass` on the manager (mode 640, owner `root:wazuh`), and
   restart with `sudo systemctl restart wazuh-manager`. Without a password file, the manager
   generates a random password at each restart and logs it in `ossec.log`.
**Step 3: Enrol a first agent** as described above, and confirm it is active.
**Step 4: Choose what to monitor.** Review the agent's `/var/ossec/etc/ossec.conf`: log sources
   (`<localfile>`), FIM directories (`<syscheck>`), and SCA. Prefer central configuration through
   agent groups (`/var/ossec/etc/shared/<group>/agent.conf` on the manager) once you have more
   than a few agents.
**Step 5: Set alert retention** in the indexer to match your storage. The sizing table assumes 90 days.

## Security hardening

| Measure | Why |
|---|---|
| Change every default credential before exposure (Docker), and protect the installation archive's password file (assistant). | The Docker defaults are public. The archive contains every component's credentials and certificates. |
| Expose only what is needed: agents need 1514 and 1515, analysts need 443. Keep 9200 and 55000 on loopback or a management network, and firewall the rest. | The indexer and server APIs are powerful administrative interfaces. |
| Require enrolment passwords, and consider manager identity verification (agents verify the manager's certificate against a CA) and agent certificate verification. | Stops rogue agents from enrolling, and stops agents enrolling with an impostor manager. |
| Replace self-signed dashboard and component certificates with certificates from an internal CA, and track their expiry. | Users learn to ignore certificate warnings, which defeats TLS. |
| Disable the package repositories between planned upgrades (official recommendation). | An accidental partial upgrade breaks the strict version alignment. |
| Use role-based access in the dashboard, and give analysts named accounts instead of sharing `admin`. | Accountability and least privilege for a system that holds sensitive endpoint data. |
| Restrict and review active-response rules. | Automatic blocking or process killing on false positives can cause outages. |
| Back up configuration (`/var/ossec/etc`, custom rules and decoders, `client.keys`), certificates, and indexer data (snapshots), and test restores. | The backup guide documents these files. Losing `client.keys` means re-enrolling every agent. |
| Keep the central stack on a dedicated, patched host or VM. | The indexer and manager are high-value targets: they hold data from every endpoint. |

## Practical usage examples

Illustrative examples. Addresses are documentation addresses and paths are placeholders. Not
executed for this entry.

### Personal and home-lab use

**Monitor a Linux workstation or lab server.** Install the agent on the machine, enrol it, and
watch for authentication failures, `sudo` use, package changes, and SCA results. In the dashboard,
filter alerts by the agent name. On a home lab, most value comes from noticing changes you did not
make.

**File integrity monitoring of configuration directories.** Add real-time monitoring of a
directory that should rarely change, in the agent's `ossec.conf` (the directory must exist before
the agent restarts):

```xml
<syscheck>
  <directories realtime="yes" check_all="yes">/etc/ssh</directories>
  <directories realtime="yes" check_all="yes">/srv/homelab/config</directories>
</syscheck>
```

Restart with `sudo systemctl restart wazuh-agent`, change a test file in the directory, and confirm
that a FIM alert appears. Avoid real-time monitoring of busy directories such as log or cache
folders: they create noise and load.

**Collect Suricata alerts from a sensor.** On a Suricata sensor with a Wazuh agent, add the EVE log
as a JSON source (from Wazuh's Suricata integration guide). Wazuh's ruleset includes Suricata
rules:

```xml
<localfile>
  <log_format>json</log_format>
  <location>/var/log/suricata/eve.json</location>
</localfile>
```

Large EVE files with flow and protocol records can overload a small Wazuh server. Consider
configuring a separate EVE output for alerts only, and pointing the agent at that file instead.

### Enterprise use

**Endpoint security monitoring.** Deploy agents to servers and workstations by group (for example
by operating system and role), push centrally managed configuration through group `agent.conf`
files, and use SCA policies aligned with your hardening baseline. Track agent coverage: an
unenrolled or disconnected agent is a blind spot.

**Centralised security event analysis.** Forward network security events from sensors, firewall
syslog, and cloud audit logs into the same platform. Write local rules for your environment
(for example, logins to privileged accounts outside change windows), tune noisy default rules,
and integrate alerting with ticketing or on-call tools. Validate every new log source: confirm
that decoders parse it and that the expected rules fire on test events.

## Enterprise deployment considerations

- **Architecture.** Beyond about 100 agents, the quickstart recommends a distributed deployment:
  a multi-node indexer cluster and a server cluster (one master and workers) behind a load
  balancer for agent connections.
- **Version governance.** The exact-version requirement for central components means upgrades
  must be planned, staged, and done together. Agent upgrades must follow, never lead.
- **Data volume and retention.** Indexer storage drives cost. Decide what to index, how long to
  keep it hot, and whether to archive. Test the restore of indexer snapshots.
- **Identity and access.** Integrate dashboard authentication with your identity provider where
  supported, use role-based access, and log administrative actions.
- **Certificates and secrets.** Run component and agent certificates from an internal CA with a
  renewal process. Store enrolment passwords and API credentials in a secrets manager such as
  [OpenBao](../password-management/openbao.md).
- **Privacy and policy.** Endpoint logs reveal user activity. Document what is collected, why, how
  long it is kept, and who can search it.
- **Support model.** The software is open source. Wazuh Inc. sells support and a hosted cloud
  service. Decide whether community support is acceptable for production.
- **Coverage gaps.** Map Wazuh's detections against your threat model. Decide where you still need
  EDR (behavioural blocking and response), network detection, or vendor content.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Agent stays *never connected* or *disconnected* | Agent cannot reach 1514/TCP or 1515/TCP on the manager, or `WAZUH_MANAGER` points to the wrong address. Test with `nc -zv <manager> 1514`, check firewalls, and read `/var/ossec/logs/ossec.log` on the agent. |
| Enrolment rejected | Password authentication enabled but the agent has no or a wrong `authd.pass`. Compare with the manager's file and check its permissions (640, `root:wazuh`). |
| Indexer container exits or fails to start in Docker | `vm.max_map_count` below 262144 on the Docker host. Set it persistently and restart. |
| Dashboard reports "Wazuh dashboard server is not ready yet" | The indexer takes about a minute to start. If it persists, check indexer logs and resources. |
| Components fail after an upgrade | Version mismatch between central components, or a Filebeat version mismatch. Align every component to the same version. |
| No vulnerability results | Syscollector not reporting inventory, or the manager cannot reach `cti.wazuh.com`. Check outbound HTTPS and the manager logs. |
| FIM changes not detected in real time | Directory missing when the agent started, or real-time not supported on the platform. Create the directory and restart, or rely on scheduled scans. |
| Alert volume overwhelming | Default rules untuned. Raise alert thresholds for noisy rule groups and add local rules with lower levels for known-benign events. |
| Server or indexer is slow | Undersized host for the agent count or ingest rate. Compare with the sizing table and move to a distributed deployment. |

## Alternatives and related tools

- [Suricata](../network-security/suricata.md) and [Zeek](../network-security/zeek.md): network
  sensors whose output Wazuh can collect. They cover the network view that agents do not.
- [Greenbone Community Edition](../vulnerability-management/greenbone-community-edition.md):
  network-based vulnerability scanning, which complements Wazuh's inventory-based detection.
- **Elastic Stack**, **Graylog**, and **OpenSearch**: log platforms (not yet documented here).
  Wazuh's indexer is based on OpenSearch.
- **OSSEC**: the host intrusion detection project Wazuh descends from.

## References

### Official documentation

- [Wazuh website](https://wazuh.com/)
- [Wazuh documentation](https://documentation.wazuh.com/current/index.html)
- [Architecture and required ports](https://documentation.wazuh.com/current/getting-started/architecture.html)
- [File integrity monitoring: basic settings](https://documentation.wazuh.com/current/user-manual/capabilities/file-integrity/basic-settings.html)
- [Vulnerability detection configuration](https://documentation.wazuh.com/current/user-manual/capabilities/vulnerability-detection/configuring-scans.html)
- [Source repository](https://github.com/wazuh/wazuh)

### Installation references

- [Quickstart](https://documentation.wazuh.com/current/quickstart.html)
- [Installation guide](https://documentation.wazuh.com/current/installation-guide/index.html)
- [Deploying agents on Linux](https://documentation.wazuh.com/current/installation-guide/wazuh-agent/wazuh-agent-package-linux.html)
- [Docker deployment](https://documentation.wazuh.com/current/deployment-options/docker/wazuh-container.html)
- [Upgrade guide](https://documentation.wazuh.com/current/upgrade-guide/index.html)
- [Wazuh releases](https://github.com/wazuh/wazuh/releases)

### Security and deployment references

- [Agent enrolment](https://documentation.wazuh.com/current/user-manual/agent/agent-enrollment/index.html)
- [Enrolment with password authentication](https://documentation.wazuh.com/current/user-manual/agent/agent-enrollment/security-options/using-password-authentication.html)
- [Manager identity verification](https://documentation.wazuh.com/current/user-manual/agent/agent-enrollment/security-options/manager-identity-verification.html)
- [Password management](https://documentation.wazuh.com/current/user-manual/user-administration/password-management.html)
- [Creating a backup](https://documentation.wazuh.com/current/migration-guide/creating/index.html)
- [Suricata integration (proof of concept)](https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html)
- [wazuh-docker repository](https://github.com/wazuh/wazuh-docker)

### Verification notes

- **Sources checked:** 2026-11-12, against the `current` documentation (4.14 series) and the
  pages listed above.
- **Releases:** 4.14.10 published 2026-11-09. 4.14.11-rc1 and 5.0.0-rc2 were pre-releases on
  2026-11-12 (GitHub releases API).
- **Docker defaults:** the `single-node/docker-compose.yml` at tag `v4.14.10` publishes ports 1514,
  1515, 514/udp, 55000, 9200, and 443 without a host address, and sets credentials to values that
  appear in the file and in the documentation. This entry recommends loopback binding and changing
  the credentials. The edited port mappings are an adaptation and were not run.
- **Supported platforms:** the quickstart's recommended list for central components excludes
  Fedora and Debian. Agent packages are generic. No statement specifically covering Fedora agents
  was found.
- **Licence:** the documentation states GPLv2 and Apache-2.0 for the components. The server
  repository's `LICENSE` file is GPLv2 with an OpenSSL linking exception. The GitHub API reports
  `NOASSERTION`.
- **Integrations:** Suricata EVE collection is documented in the proof-of-concept guide (written
  for Suricata 6.0.8). The 4.14.10 ruleset contains `0475-suricata_rules.xml`. A Zeek ruleset file
  derived from a third-party project exists, but no Zeek procedure is documented.
- **Enrolment defaults:** the `etc/ossec.conf` template at `v4.14.10` sets
  `<use_password>no</use_password>` and `<ssl_verify_host>no</ssl_verify_host>` in the `<auth>`
  section, which is why this entry recommends enabling password authentication.
- **Not executed:** Wazuh was not installed or run for this entry.
- **Unresolved:** whether Fedora is a supported agent platform; behaviour of the edited Docker port
  mappings with the dashboard and agents (not run).
