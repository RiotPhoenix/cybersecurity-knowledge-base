---
tool: Nmap
category: network-security
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://nmap.org
repository: https://github.com/nmap/nmap
requires_authorisation: true
---

# Nmap

!!! warning "Authorised use only"
    Scan only networks and hosts you own or have explicit written permission to scan.
    Unauthorised scanning may breach the law, your internet provider's acceptable-use policy,
    or your employer's rules, and it can disrupt fragile devices. The Nmap project's own
    [legal guidance](https://nmap.org/book/legal-issues.html) recommends securing written
    authorisation before scanning.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://nmap.org> |
| Source repository | <https://github.com/nmap/nmap> (official mirror; nmap.org also publishes source releases) |
| Licence | Nmap Public Source License (NPSL), a custom licence based on GPLv2 with additional terms. Not OSI-certified. |
| Supported operating systems | Linux, Windows, macOS, BSD, and other UNIX-like systems |
| Maintenance status | Active: 7.993 released 2026-10-23 according to the official changelog. Checked 2026-11-12 |
| Category | Network Security |
| Personal suitability | High: free, lightweight, and the standard tool for learning what is on your own network |
| Enterprise suitability | High for authorised discovery and validation; needs scope control, change management, and licence review for redistribution |
| Tested versions | Not lab-tested. Selected commands spot-checked; see [Verification notes](#verification-notes) |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

Nmap ("Network Mapper") discovers hosts on a network and identifies which ports are open,
which services and versions are listening, and, where possible, which operating system a host
runs. It was created by Gordon Lyon (Fyodor) and is maintained by the Nmap Project. The
distribution also includes:

| Program | Role |
|---|---|
| `nmap` | The scanner. |
| Zenmap | Official graphical front end, which can save and compare scans. |
| Ncat | General-purpose networking utility (a netcat replacement). |
| Nping | Packet generation and response analysis. |
| Ndiff | Compares two Nmap XML scan results and reports what changed. |

Defensive teams use Nmap for asset inventory, exposure checks, and validating firewall and
segmentation rules. Attackers use it for reconnaissance. That is why authorisation and scope
matter (see [Enterprise deployment considerations](#enterprise-deployment-considerations)).

## Features and capabilities

- **Host discovery** (`-sn`): finds live hosts without port scanning, using ARP on local
  Ethernet segments when privileged and ICMP/TCP probes otherwise.
- **Port scanning:** TCP SYN (`-sS`, the default when privileged), TCP connect (`-sT`, the
  default for unprivileged users), UDP (`-sU`), and others. Ports are reported as `open`,
  `closed`, `filtered`, `unfiltered`, `open|filtered`, or `closed|filtered`.
- **Service and version detection** (`-sV`), with adjustable intensity (0–9, default 7).
- **Operating-system detection** (`-O`) by TCP/IP stack fingerprinting.
- **Nmap Scripting Engine (NSE):** Lua scripts in categories such as `safe`, `default`,
  `discovery`, `vuln`, `intrusive`, `brute`, `exploit`, and `dos`.
- **Timing and rate control:** timing templates `-T0` to `-T5` (default `-T3`), plus explicit
  limits such as `--max-rate` and `--scan-delay`.
- **Output formats:** normal (`-oN`), XML (`-oX`), and grepable (`-oG`, documented as
  deprecated), or all three at once with `-oA`. XML is the format intended for other tools.

Limitations:

- Results are a point-in-time view from one vantage point. Firewalls, rate limiting, and
  intrusion prevention systems can make ports appear `filtered` or hosts appear down.
- Version and OS detection are inferences that can be wrong or incomplete.
- Nmap is not a vulnerability-management platform. The `vuln` NSE category checks for specific
  issues only. Use [Greenbone](../vulnerability-management/greenbone-community-edition.md) or
  similar for programmatic vulnerability assessment.
- NSE scripts are not sandboxed and run with Nmap's privileges.

## System requirements

- **Hardware:** modest. A typical laptop can scan a small network. Very large scans are
  limited mainly by network capacity and timing settings.
- **Operating systems** (from the [download page](https://nmap.org/download.html)): Windows 7
  and newer (the download page says Windows Server 2008 R2 and newer; the Windows install
  chapter says Server 2008 and newer), macOS (x86-64 disk image, "tested on Mac OS X 10.9 and
  later"), Linux (distribution packages, or x86-64 RPMs from nmap.org), and source builds for
  many UNIX systems.
- **Packet capture library:** Npcap on Windows (bundled with the installer). libpcap on
  Linux/macOS.
- **Privileges:** raw-packet features need root on UNIX-like systems, and an administrator
  account is recommended on Windows. Without them Nmap still works but is limited to
  connect scans and unprivileged host discovery. SYN, UDP, and OS-detection scans refuse to
  run (see [Troubleshooting](#troubleshooting)).

## Installation

Installing software system-wide needs administrator rights. Running Nmap afterwards does
not, unless you choose scan types that need raw packets.

### Fedora Linux

```bash
sudo dnf install nmap            # nmap and nping
sudo dnf install nmap-ncat       # optional: ncat
```

!!! note "Distribution version lag"
    On 2026-11-12 the Fedora 44 repositories provided **Nmap 7.92**, while the upstream
    stable release was **7.993**. Upstream notes that distribution packages "are necessarily
    behind" source releases. The distribution package receives Fedora's own security
    maintenance. Use it unless you need newer features or fingerprints.

**Newer upstream releases on Fedora.** nmap.org publishes x86-64 RPMs, but mixing them with
Fedora's package is not straightforward. The Fedora `nmap` and `nmap-ncat` packages carry
RPM **epoch 4** (observed on Fedora 44), and RPM compares the epoch before the version. An
upstream RPM with a lower epoch is therefore treated as *older* than Fedora's 7.92: dnf may
refuse to install it or replace it at the next upgrade. The upstream RPM's epoch was not
checked for this entry.

The cleaner route is the documented source build, installed under `/usr/local` alongside
(not over) the distribution package. Verify the tarball's signature first (see
[Verify the installation](#verify-the-installation)):

```bash
sudo dnf install gcc gcc-c++ make openssl-devel libpcap-devel   # build tools and headers
tar -xjf nmap-<VERSION>.tar.bz2 && cd nmap-<VERSION>
./configure            # installs under /usr/local by default
make
sudo make install      # root needed only to write to /usr/local
```

The build dependencies listed are a typical minimum, not an official list; `./configure`
reports anything missing. OpenSSL is optional: if its headers are absent, `configure` warns
and builds without OpenSSL support, which reduces SSL-related functionality. Afterwards,
`/usr/local/bin/nmap` takes precedence on Fedora's default `PATH`, so check `nmap --version`.
Such a build gets no automatic updates. Remove it with `sudo make uninstall` from the source
directory.

### Debian and Ubuntu

```bash
sudo apt update
sudo apt install nmap            # scanner
sudo apt install ndiff           # optional: scan comparison (separate package)
```

Debian stable (trixie) provided Nmap 7.95 at review time. The Nmap install guide notes Debian
packages can lag upstream significantly. It also describes converting upstream RPMs with
`alien`. That method is outside the distribution's package management, so prefer the
distribution package unless you have a specific need.

### Windows

1. Download `nmap-<version>-setup.exe` from the [download page](https://nmap.org/download.html).
2. Run it as an administrator. It installs Nmap, Zenmap, and **Npcap**, which raw-packet
   features need. The `/NPCAP=NO` option skips Npcap, but some Nmap features then do not
   work unless Npcap is installed separately.
3. Open a new terminal so that `nmap` is on the `PATH`.

### macOS

Download `nmap-<version>.dmg` from the [download page](https://nmap.org/download.html) and run
the installer. It installs Nmap, Zenmap, Ncat, and Ndiff. The download page describes an
x86-64 build. Native support for Apple Silicon was not stated on the pages reviewed.

### Verify the installation

```bash
nmap --version        # e.g. "Nmap version 7.92 ( https://nmap.org )"
nmap -sT -p 22 -n 127.0.0.1   # harmless self-test against your own loopback interface
```

The self-test should report `Host is up` and a state for port 22 (`open` if an SSH server is
running, otherwise `closed`).

**Verify downloads from nmap.org** before installing. Each release has a detached GPG
signature in <https://nmap.org/dist/sigs/>, and the
[integrity guide](https://nmap.org/book/install.html#inst-integrity) explains the procedure:

```bash
# Import the Nmap Project signing key (also available from major keyservers)
gpg --import nmap_gpgkeys.txt
gpg --fingerprint            # compare with the fingerprint published by the project
gpg --verify nmap-<VERSION>.tar.bz2.asc nmap-<VERSION>.tar.bz2
```

A `Good signature` from the Nmap Project Signing Key means the file was signed by the holder
of that key. That assurance is only as good as your check of the key's fingerprint.

### Updating and removal

- **Distribution packages:** `sudo dnf upgrade nmap` or `sudo apt upgrade nmap`.
- **Upstream installers and source builds:** download and verify the new release, then
  install it over the old one (or rebuild). On Windows the installer also offers to update
  Npcap.
- **Removal:** `sudo dnf remove nmap nmap-ncat`, `sudo apt remove nmap ndiff`, or the
  operating system's uninstaller (on Windows, uninstall Npcap separately if no other tool
  needs it). Keep or securely delete saved scan results under your retention policy, because
  they describe your network's exposure.

## Initial configuration

Nmap needs no configuration file to run. Before scanning:

1. **Write down your scope**: the exact addresses or ranges, allowed times, and allowed scan
   types. Keep it in a file and pass it with `-iL scope.txt`. Use `--exclude` or
   `--excludefile` for anything that must never be touched, such as fragile industrial
   devices or third-party systems.
2. **Decide on privileges.** Run unprivileged (`-sT`) where possible. Use `sudo` only for scan
   types that need raw packets (`-sS`, `-sU`, `-O`) and only when the scope justifies them.
3. **Choose conservative timing.** Keep the default `-T3` or use `-T2`, and add `--max-rate`
   on shared or production networks.
4. **Always save results** with `-oA <basename>` so you have XML for comparison and a
   readable record.
5. **Consider `-n`** (no reverse DNS) to avoid generating DNS queries for every address.

## Security hardening

Hardening for a scanner is mainly about using it safely and protecting what it produces.

| Measure | Why |
|---|---|
| Keep a written scope and pass it with `-iL` and `--excludefile`. | Typos in CIDR ranges are a common cause of scanning the wrong network. |
| Prefer unprivileged connect scans; avoid running Nmap as root routinely. | NSE scripts are not sandboxed, and root amplifies the impact of a malicious or buggy script. |
| Use only NSE scripts you have reviewed, from the official distribution. Avoid `--script all`. | Selecting all scripts includes exploits, brute-force crackers, and denial-of-service scripts. The project warns that some `default` scripts are intrusive. |
| Limit rate (`--max-rate`, `--scan-delay`) and avoid `-T5`. | Aggressive timing can overload fragile devices and trigger intrusion prevention. `-T5` also sacrifices accuracy. |
| Store scan output with restricted permissions and a retention limit. | Scan results are a map of your attack surface. |
| Verify upstream downloads with GPG. | Detects tampered installers. |
| Avoid categories that contact third parties (`external`) when scanning internal assets. | `external` scripts send data such as target addresses to outside services like whois servers. |

## Practical usage examples

The examples use `127.0.0.1` (your own machine) or documentation-reserved ranges
(`192.0.2.0/24`, `198.51.100.0/24`, RFC 5737). Replace reserved ranges only with networks
you own or are authorised to scan. Commands marked *spot-checked* were run on Fedora 44 with
Nmap 7.92 against loopback (see [Verification notes](#verification-notes)); the others are
illustrative.

### Personal and home-lab use

**Check exposed services on your own machine** (*spot-checked*). An unprivileged connect scan
of the loopback interface, showing why each port is in its state:

```bash
nmap -sT -p 22,631,9 --reason -n 127.0.0.1
```

Expected: each port with a state and a reason, for example `open ... syn-ack` for a listening
service and `closed ... conn-refused` for a port with nothing listening.

**Identify a service version on a lab machine** (*spot-checked* against loopback):

```bash
nmap -sT -sV --version-light -p 631 -n 127.0.0.1
```

`--version-light` (intensity 2) sends fewer probes than the default.

**Inventory devices on your own home network.** Host discovery only, no port scan. Replace
the reserved range with your own subnet, which is often shown in your router's settings:

```bash
sudo nmap -sn 192.0.2.0/24 -oA home-inventory
```

With `sudo` on a local Ethernet/Wi-Fi segment, Nmap uses ARP and reports MAC addresses and
vendors. Without `sudo` it falls back to TCP connection attempts to ports 80 and 443, which
can miss devices.

### Enterprise use

**Authorised asset discovery with safe settings.** Scope from a file, exclusions honoured,
moderate rate, and full output saved:

```bash
nmap -sT --top-ports 100 --open -n \
  -iL approved-scope.txt --excludefile do-not-scan.txt \
  --max-rate 100 --max-retries 2 \
  -oA discovery-$(date +%F)
```

**Validate network segmentation.** From a host inside segment A, confirm that management
ports in segment B are *not* reachable. A `filtered` result is the expected pass condition:

```bash
nmap -Pn -sT -p 22,445,3389 --reason -n 198.51.100.0/28 -oA segmentation-check
```

`-Pn` skips host discovery, because hosts behind a correctly configured firewall may not
answer pings. Run the same check from each segment that should be blocked, and record the
results as evidence for the control.

**Detect change between scans** with Ndiff, comparing two XML outputs:

```bash
ndiff discovery-2026-10-01.xml discovery-2026-11-01.xml
```

Ndiff reports hosts coming up or going down and ports opening or closing. That is useful for
spotting unapproved services.

**Run only low-risk scripts.** NSE boolean expressions let you exclude risky categories:

```bash
nmap -sT -sV --script "safe and not external" -p 443 -n 192.0.2.20
```

## Enterprise deployment considerations

- **Authorisation and scope.** Treat every scan as a change. Record who requested it, the
  approved scope (ranges, exclusions, time window), the permitted scan types, and contacts
  for stopping the scan. For third-party or cloud-hosted assets, confirm that the provider's
  terms permit scanning. Penetration tests need formal rules of engagement.
- **Operational impact.** Coordinate with network and security operations, because scans
  trigger IDS/IPS alerts and can affect fragile devices such as printers, industrial control
  systems, and medical equipment. Nmap's legal guidance suggests avoiding version detection,
  OS detection, and scripts against sensitive systems.
- **Dedicated scanner hosts.** Run scheduled scans from known, documented scanner addresses,
  so defenders can recognise them and firewall rules can permit them where intended.
- **Data handling.** Classify scan output as sensitive, store it centrally with access
  control, and feed XML into asset inventory or CMDB processes rather than ad-hoc
  spreadsheets.
- **Licensing.** End-user use is permitted under the NPSL. Redistributing Nmap inside a
  proprietary product, or embedding it in commercial software, requires an Nmap OEM licence.
  Have legal review the [NPSL](https://nmap.org/npsl/) before bundling Nmap in internal
  platforms that are distributed to others.
- **Support.** Commercial support is available through the Nmap OEM programme. Otherwise
  support is community-based.
- **Not a full vulnerability programme.** Use Nmap for discovery and validation, and pair it
  with an authenticated vulnerability scanner for patch-level findings.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| `You requested a scan type which requires root privileges. QUITTING!` | `-sS`, `-sU`, and similar need raw packets. Use `-sT`, or run with `sudo` if the scope permits. Observed on Fedora 44 for `-sS`. |
| `TCP/IP fingerprinting (for OS scan) requires root privileges. QUITTING!` | `-O` needs raw packets. Run with `sudo`, or omit OS detection. Observed on Fedora 44. |
| All hosts reported down, but you know they are up | Host discovery probes are blocked. Use `-Pn` (treat all hosts as up) for in-scope hosts. Expect slower scans. |
| Every port `filtered` | A firewall drops probes. This may be the correct, expected result (for example in a segmentation test). |
| Scan is very slow | UDP scans and `-Pn` against large ranges are inherently slow. Narrow the ports (`--top-ports`), scan fewer hosts, or relax timing carefully within the approved impact. |
| Results differ between runs | Rate limiting, packet loss, or IPS interference. Lower `--max-rate`, increase `--max-retries`, and scan from a closer vantage point. |
| Windows: raw scans fail | Npcap missing or not running. Reinstall Nmap with Npcap, or install Npcap separately. Use an administrator terminal. |
| `ndiff: command not found` | On Debian/Ubuntu, install the separate `ndiff` package. On Fedora 44, `ndiff` was not installed with the `nmap` package. |

## Alternatives and related tools

- **Masscan** and **ZMap:** very fast, stateless port scanners for large address spaces.
  They have less service detail and more potential for impact.
- [Greenbone Community Edition](../vulnerability-management/greenbone-community-edition.md):
  vulnerability assessment. It uses its own port scanning as part of a scan.
- [Nuclei](../vulnerability-management/nuclei.md): template-based checks against known
  services and web applications. It is often run against hosts that Nmap has discovered.
- [Wireshark](wireshark.md): shows on the wire what a scan sends and receives.
- **Zenmap:** the official Nmap GUI, included with the Windows and macOS installers.

## References

### Official documentation

- [Nmap website](https://nmap.org)
- [Nmap Reference Guide (man page)](https://nmap.org/book/man.html), including
  [host discovery](https://nmap.org/book/man-host-discovery.html),
  [port scanning techniques](https://nmap.org/book/man-port-scanning-techniques.html),
  [timing and performance](https://nmap.org/book/man-performance.html), and
  [output](https://nmap.org/book/man-output.html)
- [NSE usage and script categories](https://nmap.org/book/nse-usage.html)
- [Ndiff](https://nmap.org/ndiff/) and [Zenmap](https://nmap.org/zenmap/)
- Source repository: <https://github.com/nmap/nmap>
- [Changelog](https://nmap.org/changelog.html)

### Installation references

- [Download page](https://nmap.org/download.html)
- [Installation guide](https://nmap.org/book/install.html), including
  [Linux](https://nmap.org/book/inst-linux.html), [Windows](https://nmap.org/book/inst-windows.html),
  and [verifying integrity](https://nmap.org/book/install.html#inst-integrity)
- [Debian stable package: nmap](https://packages.debian.org/stable/nmap) and
  [ndiff](https://packages.debian.org/stable/ndiff)

### Security and deployment references

- [Legal issues](https://nmap.org/book/legal-issues.html)
- [Nmap Public Source License](https://nmap.org/npsl/)

### Verification notes

- **Sources checked:** 2026-11-12, against the pages listed above. The latest release (7.993,
  2026-10-23) was taken from the official changelog. The GitHub repository page did not
  show release tags.
- **Distribution versions:** Fedora 44 repositories provided 7.92 (checked with `dnf
  repoquery`), and Debian stable (trixie) provided 7.95 (packages.debian.org).
- **Spot-checked commands (not a full lab test):** on 2026-11-12, on Fedora 44 with Nmap 7.92
  from Fedora's repositories, run as an unprivileged user against `127.0.0.1` only:
  `nmap --version`, the `--reason` loopback example, the `-sV --version-light` loopback
  example, and the `-sS`/`-O` privilege errors quoted in Troubleshooting. All options used
  on this page appear in the 7.92 `nmap -h` output. Home-network, enterprise, segmentation, and
  Ndiff examples are illustrative and were not executed.
- **RPM epoch:** Fedora 44's `nmap` and `nmap-ncat` packages have epoch 4 (`rpm -q --qf
  '%{EPOCH}'`). The source-build commands were not executed. The `uninstall` make target and the
  optional OpenSSL handling were confirmed in the upstream `Makefile.in` and `configure.ac`.
- **Unresolved:** the Windows Server minimum (the download page and install chapter differ),
  Apple Silicon support for the macOS package, and whether Fedora packages `ndiff`
  separately.
