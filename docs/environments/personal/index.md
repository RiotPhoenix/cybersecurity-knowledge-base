# Personal and Home Lab

Guidance for individuals securing their own devices and accounts, and for learners building
labs to practise safely.

## Principles

- **Isolate your lab.** Keep vulnerable or experimental systems on a separate network segment
  or virtual network with no route to your personal devices or the internet unless required.
- **Test only what you own.** Scanning, exploitation, and interception tools must only be used
  against systems you own or have written permission to test.
- **Snapshot before you change.** Use virtual-machine snapshots or backups so experiments can
  be rolled back.
- **Keep it patched.** Lab hosts are easy to forget and can become an attacker's foothold.
- **Protect your accounts first.** A password manager and multi-factor authentication give the
  largest improvement for most individuals.

## Where to start

Choose tools by the problem you actually have, not by popularity. A sensible order for most
people:

| Step | Need | Start with | Why this first |
|---|---|---|---|
| 1 | Stop reusing passwords | [KeePassXC](../../tools/password-management/keepassxc.md) | Local application, nothing to host, very low running cost. |
| 2 | See what is on your network | [Nmap](../../tools/network-security/nmap.md) (`-sn` host discovery, then connect scans of your own devices) | Lightweight, runs on a laptop, teaches how services are exposed. |
| 3 | Understand traffic and troubleshoot | [Wireshark](../../tools/network-security/wireshark.md) | Shows what your devices actually send, which makes DNS and connectivity problems visible. |
| 4 | Find known vulnerabilities on lab hosts | [Nuclei](../../tools/vulnerability-management/nuclei.md) for targeted checks, then [Greenbone](../../tools/vulnerability-management/greenbone-community-edition.md) for full assessments | Nuclei is a single binary; Greenbone is heavier but broader. |
| 5 | Share passwords across devices and family | [Vaultwarden](../../tools/password-management/vaultwarden.md), only if you will run it properly | A self-hosted server is a commitment (see below). |
| 6 | Learn network security monitoring | [Zeek](../../tools/network-security/zeek.md) on capture files, then [Suricata](../../tools/network-security/suricata.md) and Zeek on a mirrored lab segment | Offline analysis needs no extra hardware. Live monitoring needs a mirror port or TAP. |
| 7 | Monitor lab hosts and centralise alerts | [Wazuh](../../tools/siem/wazuh.md) | Endpoint monitoring and FIM, but the central stack needs 4 vCPU and 8 GiB RAM. |
| 8 | Practise web application testing | [ZAP](../../tools/penetration-testing/zap.md) against a deliberately vulnerable application on loopback | Teaches the difference between passive analysis and active attacks safely. |
| 9 | Keep lab service credentials out of config files | [OpenBao](../../tools/password-management/openbao.md) | Teaches policy-based access, but unseal keys and TLS need care. |

For a worked design that combines steps 2, 4, 6, 7, and 9, see the
[security monitoring lab reference architecture](security-monitoring-lab.md).

## Hardware and resources

| Tool | Typical footprint |
|---|---|
| KeePassXC, Nmap, Wireshark, Nuclei | Runs on an ordinary laptop or desktop. |
| Vaultwarden | Very light: a small VM or single-board computer is enough for a household. The real requirements are HTTPS, backups, and updates. |
| Greenbone Community Edition | Minimum 2 CPU cores, 4 GB RAM, 20 GB disk; 4 cores, 8 GB, and 60 GB recommended. Plan a dedicated VM. |
| ZAP | Runs on a workstation (Java 17 or later). Active scans of large applications use significant memory. |
| Suricata and Zeek | No official minimum. A sensor with two NICs and a mirror port is needed for live monitoring. Disk use grows with logged traffic. |
| Wazuh (central stack) | 4 vCPU, 8 GiB RAM, and 50 GB for 1 to 25 agents with 90 days of alerts (official quickstart). Agents need about 35 MB RAM. |
| OpenBao | Light for a single node, but needs TLS, unseal-key custody, and backups. |

A single mini PC cannot comfortably run Wazuh, Greenbone, the sensors, and lab VMs together. The
[security monitoring lab](security-monitoring-lab.md) describes a staged deployment.

## Local tools versus self-hosted services

- **Local tools** (KeePassXC, Nmap, Wireshark, Nuclei) run when you start them and store data in
  files you control. Your responsibilities are keeping them updated and protecting their output:
  capture files, scan results, and the password database.
- **Self-hosted services** (Vaultwarden, Greenbone, Suricata, Zeek, Wazuh, OpenBao) run
  continuously, and you become the
  operator. You must handle TLS certificates, updates (including security fixes, sometimes
  urgently), backups and restore tests, monitoring, and access control. If you cannot commit
  to that, prefer a local tool or a reputable hosted service.

## Backup and maintenance responsibilities

- **Password databases and vaults:** there is no account recovery. Keep several dated backups,
  including one offline. Store key files and hardware-key secrets separately, and test that
  backups open. See [KeePassXC](../../tools/password-management/keepassxc.md#security-hardening)
  and [Vaultwarden](../../tools/password-management/vaultwarden.md#personal-and-home-lab-use).
- **Scanners:** update the scanner and its data (Nmap fingerprints, Nuclei templates, the
  Greenbone feed). Outdated data finds less.
- **Captures and scan results** describe your network and may contain personal data. Store
  them in a private directory and delete them when you no longer need them.

## Safe practice environments

- Use **loopback** (`127.0.0.1`) or your own virtual machines for first experiments. Several
  entries include loopback examples.
- Run deliberately vulnerable applications **only** on an isolated virtual network or bound to
  `127.0.0.1`, never exposed to your home LAN or the internet.
- Use conservative rate limits even in a lab. Home routers and IoT devices can crash under
  aggressive scans.
- Remember that your internet provider's terms may prohibit scanning beyond your own network.

## Planned coverage

!!! note "Planned"
    - Further reference architectures (the first is the
      [security monitoring lab](security-monitoring-lab.md)).
    - Baseline hardening for personal Linux, Windows, and macOS systems.
    - Learning paths that link tool entries in a sensible order.
    - Resource-constrained deployment notes for further tool entries.
