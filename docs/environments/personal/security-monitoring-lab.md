# Security Monitoring Lab: Reference Architecture

A resource-conscious design for a home lab that combines network monitoring, endpoint
monitoring, vulnerability assessment, and secrets storage. It shows how the documented tools fit
together, which connections between them are **documented integrations**, and which are only
**conceptual** and need your own validation.

!!! warning "Design guidance, not a tested deployment"
    This architecture is assembled from each tool's official documentation. It has **not** been
    built and tested as a whole. Resource figures are either quoted from official documentation
    or labelled as assumptions. Validate each stage in your own lab, and record what you test
    with the [lab evidence template](../../contributing/lab-validation.md).

## 1. Purpose

- Learn how network and endpoint security monitoring work, using real tools on a network you
  own.
- Build a lab where you can generate known activity (scans, test alerts, file changes) and see
  how each tool records it.
- Practise the operational side: segmentation, credential handling, updates, backups, and
  troubleshooting.

It is **not** a production security operations platform for a household or business.

## 2. Intended audience

Learners, home-lab builders, and IT staff preparing for professional work, who are comfortable
with Linux administration, virtual machines or containers, and basic networking (VLANs, subnets,
routing). Enterprise readers can use it as a small-scale model. Section 16 lists what changes at
enterprise scale.

## 3. Hardware assumptions

These are **assumptions** for planning, not official requirements:

| Item | Assumption | Why |
|---|---|---|
| Router/firewall | A device that supports VLANs and firewall rules between them (a router appliance, or a small PC running a firewall distribution) | Segmentation is the foundation of the design. |
| Managed switch | Supports VLANs and **port mirroring** (SPAN) | Gives the sensor a copy of lab traffic. |
| Sensor host | Mini PC with at least 4 CPU cores, 8 to 16 GB RAM, an SSD, and **two network interfaces** (one for capture, one for management) | Suricata and Zeek publish no fixed minimum. This is a modest starting point for a low-traffic lab link. |
| Monitoring server | A second machine or VM host with at least 4 vCPU, 8 GiB RAM, and 50 GB of storage for Wazuh | Wazuh's quickstart lists 4 vCPU, 8 GiB RAM, and 50 GB for 1 to 25 agents with 90 days of alerts. |
| Lab hosts | VMs on a hypervisor, or spare machines | Targets to monitor and scan. |
| Admin workstation | Your normal laptop or desktop | Runs Nmap, ZAP, browsers, and the OpenBao CLI. |

A single mini PC **cannot realistically run the complete stack at once**. Wazuh alone is sized at
8 GiB RAM, and Greenbone recommends 8 GB. Running both, plus Suricata and Zeek, plus lab VMs, on
one 16 GB machine leaves no headroom. The design is therefore staged (section 9).

## 4. Network topology

All addresses below are from the documentation ranges reserved by RFC 5737, and all names use the
reserved `.example` domain. Replace them with your own plan, and do not publish your real one.

```text
                              Internet
                                  |
                       +----------+-----------+
                       |   Router / firewall  |   inter-VLAN rules, default deny
                       +--+-------+--------+--+
                          |       |        |
            VLAN 10 Mgmt  |       |        |  VLAN 30 Home (not monitored)
          192.0.2.0/24    |       |        |  family devices, out of scope
                          |       |        |
                 +--------+-------+--------+---------------------+
                 |              Managed switch                   |
                 |  port 8 = mirror of the VLAN 20 uplink        |
                 +--+-----------+---------------+--------+-------+
                    |           |               |        |
                    |           |               |        +-- mirror (port 8)
                    |           |               |               |
          +---------+---+ +-----+--------+  +---+----------+ +--+-------------------+
          | Admin       | | Monitoring   |  | Lab hosts    | | Sensor (mini PC)     |
          | workstation | | server       |  | VLAN 20 Lab  | |  nic1: capture, no IP|
          | Nmap, ZAP,  | | Wazuh stack  |  | 198.51.100.  | |  nic2: mgmt, VLAN 10 |
          | bao CLI     | | OpenBao      |  |   0/24       | |  Suricata + Zeek     |
          | (VLAN 10)   | | Greenbone VM |  | Wazuh agents | |  Wazuh agent         |
          +-------------+ | (VLAN 10)    |  | Juice Shop   | +----------------------+
                          +--------------+  | (isolated)   |
                                            +--------------+

  Flows:  agents --1514/1515 TCP--> Wazuh server      analysts --443--> Wazuh dashboard
          Greenbone, Nmap --scans--> VLAN 20 only     services --8200 TLS--> OpenBao
          sensor nic1 <-- copy of VLAN 20 uplink traffic (receive only)
```

The diagram is plain text so that it renders without external services and can be edited in any
text editor.

## 5. Security zones

| Zone | Contents | Allowed to reach | Reachable from |
|---|---|---|---|
| **Management (VLAN 10, `192.0.2.0/24`)** | Admin workstation, monitoring server, OpenBao, Greenbone, sensor management interface | Lab (for scanning and agent management), internet (updates, feeds) | Nowhere outside the zone, except agent ports 1514/1515 from the lab zone |
| **Lab (VLAN 20, `198.51.100.0/24`)** | Lab servers, deliberately vulnerable applications, Wazuh agents | Wazuh server on 1514/1515 only. Internet only when needed for updates, then closed again | Management zone |
| **Capture** | Sensor capture interface (no IP address) | Nothing. Receives mirrored packets only | Nothing |
| **Home (VLAN 30)** | Household devices | Internet | Nothing in the lab |

Rules of thumb:

- **Default deny between VLANs** on the router, then open only the flows listed in section 7.
- **Deliberately vulnerable applications** (for example OWASP Juice Shop for ZAP practice) run
  bound to loopback, or on an isolated network segment with no internet access.
- **Household devices are out of scope.** Monitoring other people's devices and traffic without
  their agreement raises privacy and, in some jurisdictions, legal issues. Keep the mirror on the
  lab VLAN.

## 6. Monitoring interfaces

Passive network monitoring **only sees traffic that is delivered to the sensor's capture
interface**. Installing Suricata or Zeek on a machine gives you visibility of that machine's own
traffic, not of the network. Options for getting a copy of lab traffic:

| Method | How it works | Trade-offs |
|---|---|---|
| **Switch port mirroring (SPAN)** | The switch copies traffic from chosen ports or VLANs to the mirror port. | Cheap and common on managed switches. A mirror port can drop packets when the mirrored traffic exceeds its capacity, and some switches mirror only one direction or only some VLANs. Check your switch's documentation. |
| **Network TAP** | A passive or active device inserted in a link copies both directions to monitoring ports. | Reliable full-duplex copy, no switch configuration. Costs money and needs a link to insert into. |
| **Monitor on the router or hypervisor** | Run the sensor where traffic already passes (a router host or a virtual bridge that supports mirroring). | No extra hardware. Adds load and attack surface to a critical device. Feasibility depends on the platform. |
| **Offline captures** | Record traffic with Wireshark or `tcpdump` and analyse it with `zeek -r` and `suricata -r`. | No visibility infrastructure needed and ideal for learning. Not continuous monitoring. |

Mirror the **uplink of the lab VLAN** (traffic between lab hosts and the rest of the network)
first. East-west traffic between lab hosts on the same switch is only visible if those ports are
mirrored too. The capture NIC gets no IP address, so the sensor cannot be reached through the
monitored network. Zeek's documentation recommends disabling NIC offloading on capture interfaces.

## 7. Data flows

Each flow is classified:

- **Documented**: described in the official documentation of the tools involved.
- **Configuration required**: a supported feature, but you must configure and validate it.
- **Conceptual**: a sensible workflow, but no documented integration was found. Data does not
  move between the tools unless you build and validate the connection yourself.

| # | From | To | What | Status |
|---|---|---|---|---|
| 1 | Switch mirror port | Sensor capture NIC | Copy of lab traffic | Configuration required (switch documentation) |
| 2 | Suricata | Local disk (`/var/log/suricata/eve.json`) | Alerts and protocol events | Documented (Suricata) |
| 3 | Zeek | Local disk (`/opt/zeek/logs`) | Connection and protocol logs | Documented (Zeek) |
| 4 | Wazuh agent on the sensor | Wazuh server | Suricata EVE events via a JSON `localfile` entry | **Documented** (Wazuh's Suricata integration guide) |
| 5 | Wazuh agent on the sensor | Wazuh server | Zeek logs | **Conceptual**. A Zeek ruleset file exists in Wazuh's ruleset, but no procedure is documented. Validate decoders and rules yourself |
| 6 | Wazuh agents on lab hosts | Wazuh server (1514/1515 TCP) | Host logs, FIM, inventory, SCA | Documented (Wazuh) |
| 7 | Analyst browser | Wazuh dashboard (443) | Search and alert review | Documented (Wazuh) |
| 8 | Nmap (admin workstation) | Lab hosts | Discovery and port scans | Documented (Nmap). Results stay in files. **No integration** with Wazuh or Greenbone is assumed |
| 9 | Greenbone | Lab hosts | Scheduled vulnerability scans, reports in its web interface | Documented (Greenbone). **No integration** with Wazuh is assumed |
| 10 | Admin, services | OpenBao (8200, TLS) | Storing and reading lab credentials | Documented (OpenBao). The other tools have **no native OpenBao integration** assumed here: credentials are fetched with the `bao` CLI or API by you or your scripts |
| 11 | OpenBao | Wazuh agent on the OpenBao host | OpenBao audit log as JSON | **Conceptual**. Wazuh can read JSON files generically, but no OpenBao rules or procedure were verified |
| 12 | Suricata and Wazuh (sensor and monitoring server) | Internet | Rule and vulnerability-feed updates | Documented (each tool). Allow outbound HTTPS from the management zone only |

Scanning traffic (flows 8 and 9) crosses the mirrored uplink, so Suricata and Zeek will record and
may alert on your own scans. That is useful practice: confirm you can recognise your scanner in the
logs.

## 8. Tool responsibilities

| Tool | Responsibility in this lab | Runs on |
|---|---|---|
| [Suricata](../../tools/network-security/suricata.md) | Passive signature-based detection on the mirrored lab traffic. **Not** inline: it cannot block anything | Sensor |
| [Zeek](../../tools/network-security/zeek.md) | Records connections, DNS, HTTP, TLS, and files on the same traffic copy, as the evidence base for investigations | Sensor |
| [Wazuh](../../tools/siem/wazuh.md) | Endpoint monitoring through agents, central alerting, and collection of Suricata alerts | Monitoring server (central), agents on lab hosts and the sensor |
| [Nmap](../../tools/network-security/nmap.md) | Asset discovery and checking that segmentation rules hold (for example, that the lab cannot reach the management zone except where allowed) | Admin workstation |
| [Greenbone Community Edition](../../tools/vulnerability-management/greenbone-community-edition.md) | Scheduled authenticated and unauthenticated vulnerability scans of lab hosts | Dedicated VM in the management zone |
| [OpenBao](../../tools/password-management/openbao.md) | Secure storage of lab credentials: Greenbone scan credentials, the Wazuh enrolment password, and service passwords | Monitoring server or its own small VM |
| [ZAP](../../tools/penetration-testing/zap.md) (optional) | Web application testing against deliberately vulnerable lab applications | Admin workstation |
| [Wireshark](../../tools/network-security/wireshark.md) (optional) | Packet-level analysis of captures and alerts | Admin workstation |

"Centralised logs" in this lab means the Wazuh indexer for alerts and endpoint events, plus local
Zeek and Suricata logs on the sensor for detailed investigation. Shipping full Zeek and Suricata
protocol logs into Wazuh is possible only as far as flows 4 and 5 allow, and it costs storage.

## 9. Deployment sequence

Build in stages, and validate each stage before starting the next. Record what you test.

### Stage 0: segmentation (prerequisite)

1. Create the management, lab, and home VLANs and default-deny rules between them.
2. From the admin workstation, use Nmap to confirm that a lab host cannot reach the management
   zone, and that the home VLAN cannot reach the lab.

### Stage 1: minimum viable lab

1. Configure the mirror port for the lab VLAN uplink.
2. Install Suricata and Zeek on the sensor (capture interface without an IP address). Confirm
   with `tcpdump` that mirrored packets arrive.
3. Trigger Suricata's documented test alert (ET Open rule 2100498) from a lab host, and find the
   same connection in Zeek's `conn.log` and `http.log`.
4. Scan one lab host with Nmap and find the scan in both tools' logs.

At this stage the logs stay on the sensor. You review them with `jq` and `zeek-cut`.

### Stage 2: endpoint monitoring and central alerting

1. Deploy the Wazuh central components on the monitoring server (a recommended distribution or
   Docker, not the sensor).
2. Enable enrolment passwords, store the password in OpenBao (or, until Stage 3, in your password
   manager), and enrol agents on two lab hosts and on the sensor.
3. Configure the sensor's agent to read `eve.json` (flow 4). Repeat the Stage 1 test and confirm
   the Suricata alert appears in Wazuh.
4. Configure FIM on a lab host directory and confirm a file change raises an alert.

### Stage 3: vulnerability assessment and secrets

1. Deploy OpenBao with TLS, Raft storage, and a file audit device. Distribute unseal key shares
   and revoke the initial root token.
2. Deploy Greenbone in its own VM. Store its scan credentials in OpenBao, and read them with the
   `bao` CLI when you configure Greenbone.
3. Run a scheduled Greenbone scan of the lab VLAN during a defined window, and observe it in
   Suricata, Zeek, and Wazuh.

### Stage 4 (optional): web application testing

Run a deliberately vulnerable application bound to loopback or on an isolated Docker network, and
practise with ZAP as described in its entry.

## 10. Resource considerations

| Component | Figure | Source |
|---|---|---|
| Wazuh central (all-in-one, 1 to 25 agents, 90 days) | 4 vCPU, 8 GiB RAM, 50 GB | Wazuh quickstart (documented) |
| Wazuh Docker single-node | At least 4 cores, 8 GB RAM, 50 GB disk | Wazuh Docker guide (documented) |
| Wazuh agent | About 35 MB RAM on average | Wazuh documentation (documented) |
| Greenbone Community Edition | Minimum 2 cores, 4 GB RAM, 20 GB; recommended 4 cores, 8 GB, 60 GB | Greenbone documentation (documented) |
| Suricata and Zeek | No official minimum. Scales with traffic, rules, and scripts | Assumption: 4 cores and 8 to 16 GB is ample for a quiet lab link. Measure drops |
| OpenBao (single node) | No official minimum | Assumption: light. 1 to 2 vCPU and 1 to 2 GB is a starting point for a lab |
| Nmap, ZAP, Wireshark | Workstation tools | ZAP's Java runtime needs several GB during large scans (assumption) |

Lab tiers:

| Tier | What runs | Hardware (assumption) |
|---|---|---|
| **Minimum viable lab** | Stage 0 and 1: sensor with Suricata and Zeek, Nmap on the workstation | One mini PC with two NICs, a managed switch, and existing lab VMs |
| **Recommended expanded lab** | Stages 0 to 3: add Wazuh, OpenBao, and Greenbone | Sensor mini PC, plus a second host or VM server with 16 to 32 GB RAM for Wazuh (8 GiB), Greenbone (8 GB), OpenBao, and headroom |
| **Enterprise-oriented extensions** | See section 16 | Separate hosts per role, clustered components |

Time is a resource too. Expect to spend regular time on updates, triage, and tuning. A monitoring
stack that nobody reviews provides little security.

## 11. Security hardening

- **Management plane isolation.** Dashboards, APIs, and SSH listen on the management VLAN only.
  The Wazuh indexer (9200) and server API (55000) stay on loopback or the management VLAN. OpenBao
  listens with TLS on the management VLAN.
- **Credentials.** Change every default credential (especially Wazuh's Docker defaults) before a
  service is reachable. Keep lab credentials in OpenBao, and OpenBao's unseal key shares and root
  token offline and separate. Never reuse personal passwords in the lab.
- **Sensor hardening.** Capture NIC without an IP address. Suricata runs as the `suricata` user.
  Zeek uses capabilities rather than full root where practical. Sensor logs are readable only by
  you.
- **Scanning discipline.** Nmap, Greenbone, and ZAP target only the lab VLAN or isolated targets,
  never the home VLAN or the internet.
- **Vulnerable applications.** Bound to loopback or an internal-only network, and stopped when not
  in use.
- **Updates.** Subscribe to release announcements for every component. Several components had
  security releases in the weeks before this page was written.
- **Privacy.** Logs contain browsing and DNS history from lab hosts. Store them on encrypted disks,
  and set retention (`LogExpireInterval` in Zeek, indexer retention in Wazuh, logrotate for
  Suricata).

## 12. Backup and recovery

| Component | Back up | Documented method |
|---|---|---|
| Router and switch | Configuration exports | Vendor-specific |
| Sensor | `/etc/suricata`, `disable.conf` and local rules, `/opt/zeek/etc`, `/opt/zeek/share/zeek/site` | Configuration files (keep them in version control) |
| Wazuh | `/var/ossec/etc` (including `client.keys`, custom rules and decoders), certificates, indexer data | Wazuh backup guide; indexer snapshots |
| OpenBao | Raft snapshots (`bao operator raft snapshot save`), configuration, TLS material | OpenBao documentation. **Unseal key shares are stored separately and never with the snapshot** |
| Greenbone | Configuration and results in its PostgreSQL volume | **No official container backup procedure** is documented (see its entry) |

Test restores: rebuild the Wazuh server from backup on a spare VM, and restore an OpenBao snapshot
to an isolated instance and unseal it with the real key shares. A backup that has never been
restored is an assumption, not a backup.

## 13. Maintenance

| Task | Frequency (suggested) |
|---|---|
| `suricata-update` and reload | Daily (timer) |
| `zeekctl cron` | Every five minutes (cron), as the ZeekControl documentation suggests |
| OS and package updates on all hosts | Weekly, or sooner for security releases |
| Wazuh upgrades (central first, then agents, same versions) | Planned, following release notes |
| Greenbone feed synchronisation | As configured by its containers (check the entry) |
| OpenBao upgrades | Promptly. Only the latest release is supported |
| Review alerts and tune noisy rules | Weekly |
| Check sensor drops and disk space | Weekly |
| Test restores | Quarterly |

## 14. Troubleshooting

| Symptom | Where to look |
|---|---|
| Sensor sees only its own traffic | Mirror configuration, cabling to the capture NIC, `tcpdump -i <capture-nic>` |
| Suricata alerts missing in Wazuh | `localfile` entry on the sensor agent, agent status on the manager, `ossec.log` on the sensor |
| Agents disconnected | VLAN firewall rules for 1514/1515 from the lab to the monitoring server |
| Scans not visible to sensors | The scan path does not cross the mirrored uplink (for example, scanning within the same VLAN) |
| Monitoring server slow or unstable | RAM pressure from running Wazuh and Greenbone together. Move Greenbone to its own host or schedule it |
| OpenBao sealed after a power cut | Expected without auto-unseal. Unseal with the key holders |
| Disks fill | Zeek log expiry, Suricata logrotate, Wazuh indexer retention |

Each tool's entry has its own detailed troubleshooting table.

## 15. Limitations

- **Untested as a whole.** No part of this architecture has been executed for this page.
- **Partial visibility.** A single mirror port on the lab uplink misses traffic between hosts on the
  same switch ports unless they are mirrored too, and may drop packets under load.
- **Encrypted traffic.** Network sensors see metadata, not content, for TLS traffic.
- **Integration gaps.** Only Suricata to Wazuh (flow 4) is a documented integration among the
  monitoring tools here. Zeek to Wazuh and OpenBao audit to Wazuh are conceptual. Nmap and
  Greenbone results are not integrated with Wazuh.
- **Not production grade.** Single instances everywhere, no high availability, and a single
  administrator.
- **Resource contention.** The figures are documented minimums or assumptions, not benchmarks.
  Real usage depends on your traffic and workloads.

## 16. Expansion options

Enterprise-oriented extensions:

- **Network TAPs or a packet broker** instead of SPAN, and sensors at every zone boundary.
- **Clustered components:** a Zeek cluster with AF_PACKET workers, a multi-node Wazuh indexer and
  server cluster, and a three- or five-node OpenBao Raft cluster with auto-unseal through an HSM or
  KMS.
- **Dedicated log platform** for full Zeek and Suricata protocol logs, with retention tiers.
- **Identity integration:** SSO for dashboards, and OpenBao authentication through your identity
  provider.
- **Automated workflows:** alerts to ticketing, and scheduled vulnerability scans with results fed
  to remediation tracking. Each needs its own documented and tested integration.
- **Inline prevention:** Suricata IPS on a lab bridge, only after the IDS deployment is tuned and the
  failure behaviour is designed and tested.
- **Application security pipeline:** ZAP baseline scans in CI against a staging copy of a lab
  application.

See also the [personal and home-lab track](index.md) and the
[enterprise track](../enterprise/index.md).

## References

- [Suricata quickstart](https://docs.suricata.io/en/latest/quickstart.html) and
  [security considerations](https://docs.suricata.io/en/latest/security.html)
- [Zeek cluster setup](https://docs.zeek.org/en/current/cluster-setup.html) and
  [security considerations](https://docs.zeek.org/en/current/security-considerations.html)
- [Wazuh quickstart (requirements)](https://documentation.wazuh.com/current/quickstart.html),
  [architecture and ports](https://documentation.wazuh.com/current/getting-started/architecture.html),
  and [Suricata integration](https://documentation.wazuh.com/current/proof-of-concept-guide/integrate-network-ids-suricata.html)
- [Greenbone Community Edition container documentation](https://greenbone.github.io/docs/latest/22.4/container/index.html)
- [OpenBao storage backends](https://openbao.org/docs/configuration/storage/)
- [RFC 5737: IPv4 address blocks reserved for documentation](https://www.rfc-editor.org/info/rfc5737/)

Sources checked 2026-11-12. Tool-specific claims are traced in each linked entry's verification
notes.
