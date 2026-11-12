---
tool: Wireshark
category: network-security
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://www.wireshark.org
repository: https://gitlab.com/wireshark/wireshark
requires_authorisation: true
---

# Wireshark

!!! warning "Authorised use only"
    Capturing network traffic can expose other people's communications, credentials, and
    personal data. Capture only on networks and systems you own or are explicitly authorised
    to monitor, and handle capture files as sensitive data. Interception laws and workplace
    monitoring rules differ by jurisdiction.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://www.wireshark.org> |
| Source repository | <https://gitlab.com/wireshark/wireshark> |
| Licence | GPL-2.0-or-later |
| Supported operating systems | Windows, macOS, Linux and other UNIX-like systems (see [System requirements](#system-requirements)) |
| Maintenance status | Active: stable branch 4.6, old-stable branch 4.4, 5.0 in release-candidate testing. Checked 2026-11-12 |
| Category | Network Security |
| Personal suitability | High: free, well documented, and invaluable for learning how networks behave |
| Enterprise suitability | High as an analyst tool; it is not a continuous monitoring platform and needs data-handling controls |
| Tested versions | Not lab-tested. Selected commands spot-checked; see [Verification notes](#verification-notes) |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

Wireshark is a network protocol analyser. It captures packets from a network interface, or
opens previously saved capture files, and decodes them protocol by protocol so you can see
exactly what was sent, by whom, and in what order. It is maintained by the Wireshark
development community under the Wireshark Foundation, with source code on GitLab.

The suite includes several programs:

| Program | Role |
|---|---|
| `wireshark` | Graphical analyser (Qt). |
| `tshark` | Terminal analyser with the same dissectors; suited to scripting and remote hosts. |
| `dumpcap` | Capture-only engine. Wireshark and TShark call it to do the actual capture, which lets the privileged part stay small. |
| `capinfos`, `editcap`, `mergecap` | Summarise, convert, split, trim, and merge capture files. |

Wireshark shows what is on the wire. It does not decrypt encrypted traffic unless you supply
the session keys, and it does not block or alter traffic.

## Features and capabilities

- **Live capture** from Ethernet, Wi-Fi, loopback, and other interfaces supported by
  libpcap (Linux/macOS) or Npcap (Windows).
- **Offline analysis** of capture files. The native format is **pcapng**; classic **pcap**
  and many other formats can also be read. TShark and dumpcap write pcapng by default.
- **Protocol dissection** for a very large set of protocols, with expert information that
  flags retransmissions, malformed packets, and similar anomalies.
- **Two filter languages:**
    - *Capture filters* use the libpcap/BPF syntax (for example `udp port 53`). They decide
      what is recorded, and anything they exclude is lost.
    - *Display filters* use Wireshark's own field syntax (for example `dns.flags.rcode != 0`).
      They only hide or show packets that have already been captured.
- **Statistics:** conversations, endpoints, protocol hierarchy, I/O graphs, and stream
  reassembly ("Follow TCP Stream").
- **Ring-buffer and autostop capture**, so long captures do not fill the disk.

Limitations:

- It is an analysis tool, not an intrusion detection system or long-term traffic store.
- Visibility depends on where you capture. On a switched network you normally see only your
  own host's traffic, broadcast, and multicast. Seeing other hosts requires a SPAN/mirror
  port or a network tap.
- Large captures (gigabytes) are slow in the GUI; filter at capture time or split files.
- Dissectors parse untrusted input and regularly receive security fixes (see
  [Security hardening](#security-hardening)).

## System requirements

From the official [platform requirements](https://www.wireshark.org/docs/wsug_html_chunked/ChIntroPlatforms.html):

| Platform | Requirement (as documented on 2026-11-12) |
|---|---|
| Windows | Windows versions within Microsoft's extended support lifetime. At the time of writing that is Windows 11, 10, Server 2022, 2019, and 2016. 64-bit Intel or Arm processor, Universal C Runtime, 500 MB RAM and 500 MB disk as a baseline. The 4.6 branch is the last to support Windows 10 1809 and Server 2019. |
| macOS | Signed `.dmg` installer. The platform page was internally inconsistent about the minimum macOS version during this review, so check the page before installing on older releases. |
| Linux / UNIX | Distribution packages (Debian, Ubuntu, Fedora, RHEL, Arch, Alpine, and others). No minimum hardware is stated. |

The documented memory and disk figures suit small-to-medium capture files (up to a few
hundred MB). Larger files need more RAM.

**Privileges:** capturing needs raw access to network interfaces. On Linux that means the
`CAP_NET_RAW` and `CAP_NET_ADMIN` capabilities, granted only to `dumpcap`. On Windows it
means the Npcap driver, and on macOS the ChmodBPF launch daemon. Reading existing capture
files needs no special privileges.

## Installation

Use the operating system's package manager or the official installers from the
[download page](https://www.wireshark.org/download.html). Installing software system-wide
requires administrator rights (`sudo` on Linux, an administrator account on Windows and macOS).
The privilege is needed only for installation and capture-permission setup. Wireshark itself
should then run as a normal user.

### Fedora Linux

Fedora splits the suite into two packages: `wireshark` (the Qt GUI) and `wireshark-cli`
(TShark, dumpcap, and the file utilities). Installing `wireshark` pulls in `wireshark-cli`.

```bash
sudo dnf install wireshark          # GUI and command-line tools
# or, for servers without a desktop:
sudo dnf install wireshark-cli
```

The Fedora packages create a `wireshark` group and install `dumpcap` so that only `root` and
members of that group can run it. To capture as your normal user, add yourself to the group,
then log out and back in so the new membership takes effect:

```bash
sudo usermod -aG wireshark "$USER"
```

The upstream user guide's RPM instructions mention a `wireshark-qt` package. That is not the
Fedora package name; on Fedora use the names above.

### Debian and Ubuntu

```bash
sudo apt update
sudo apt install wireshark          # GUI; pulls in the shared libraries
# or the terminal analyser only:
sudo apt install tshark
```

During installation Debian asks *"Should non-superusers be able to capture packets?"*. The
default answer, **No**, means only root can capture. Answering **Yes** lets members of the
`wireshark` group capture. Change the answer later and add your user to the group:

```bash
sudo dpkg-reconfigure wireshark-common
sudo usermod -aG wireshark "$USER"   # then log out and back in
```

Debian stable (trixie) shipped the 4.4 old-stable branch at review time. Ubuntu users who need
the current stable branch can use the Wireshark developers'
[stable PPA](https://launchpad.net/~wireshark-dev/+archive/ubuntu/stable), which the download
page links to. A PPA adds a third-party package source, so weigh that against staying on the
distribution's version.

### Windows

1. Download the 64-bit installer from the [download page](https://www.wireshark.org/download.html).
2. Run it from an administrator account. The installer includes **Npcap**, which is required
   for live capture, and installs it by default. A silent install (`/S`) does **not** install
   Npcap; install it separately from <https://npcap.com/> in that case.
3. In the Npcap installer, consider **"Restrict Npcap driver's access to Administrators
   only"** on shared machines, so that ordinary users cannot sniff traffic.

### macOS

1. Download the `.dmg` for your processor and drag Wireshark to `/Applications`. The
   application is signed by the Wireshark Foundation.
2. To capture, install the **ChmodBPF** launch daemon. Use *Install ChmodBPF.pkg* in the disk
   image, or *About Wireshark → Folders → macOS Extras*. ChmodBPF adjusts the permissions of
   the packet-capture devices so that Wireshark does not need to run as root.

### Containers and sandboxed packages

Wireshark is not usually deployed as a service container. If you run `tshark` in a container,
it needs the `NET_RAW` and `NET_ADMIN` capabilities and sees only the network namespace it is
attached to. The wiki notes that the Flatpak build cannot capture on network adapters. It is
suitable for analysing existing files only.

### Verify the installation

```bash
tshark --version          # prints the version, e.g. "TShark (Wireshark) 4.x.y"
tshark -D                 # lists capture interfaces you are allowed to use
```

If `tshark -D` lists interfaces as your normal user, capture permissions are correct. If it
reports no interfaces or a permission error, see [Troubleshooting](#troubleshooting). On
Linux you can also confirm the capability assignment:

```bash
getcap /usr/bin/dumpcap   # expect cap_net_admin and cap_net_raw (path may be /usr/sbin)
```

For downloaded installers, the download page links to a signatures file containing the
release hashes, signed with GPG key ID `0xE6FEAEEA`. Compare the hash of your download with
that file before installing.

### Updating and removal

- **Linux:** updates arrive through the package manager (`sudo dnf upgrade`,
  `sudo apt upgrade`). Distribution packages receive security backports on the distribution's
  schedule, which may lag the upstream release.
- **Windows and macOS:** Wireshark can check for updates. Otherwise download and install the
  new release over the existing one. Keep Npcap current too.
- **Removal:** `sudo dnf remove wireshark wireshark-cli` or `sudo apt remove wireshark tshark`,
  or the operating system's uninstaller. Remove users from the `wireshark` group, and on
  Windows uninstall Npcap separately if nothing else needs it. Capture files you created are
  not removed; delete or archive them under your data-retention rules.

Keep to a supported release branch. The [lifecycle table](https://www.wireshark.org/docs/wsug_html_chunked/ChIntroReleaseLifeCycle.html)
shows when each branch stops receiving fixes.

## Initial configuration

1. **Capture as a normal user.** Use group membership (Linux), ChmodBPF (macOS), or Npcap
   (Windows) as above. Do not start the GUI as root or Administrator.
2. **Choose the right interface.** `tshark -D` lists them. Use the loopback interface for
   local-only experiments and the physical interface for real traffic.
3. **Decide on capture filters before long captures.** A capture filter such as
   `host 192.0.2.10 and tcp port 443` keeps files small and limits collection of unrelated
   traffic.
4. **Turn off name resolution you do not need.** Resolving every address causes extra DNS
   lookups from the analysis machine, which can leak what you are investigating. It also
   slows analysis. Disable it in the GUI's name-resolution preferences, or use `-n` with
   TShark.
5. **Store captures in a restricted directory.** On Fedora 44, capture files written by
   TShark were created readable only by their owner (mode `0600`). Keep them that way.

## Security hardening

| Measure | Why |
|---|---|
| Never run the Wireshark GUI or TShark as root/Administrator; grant capture rights only to `dumpcap`. | Dissectors parse attacker-controllable data. Privilege separation limits the damage if a dissector bug is exploited. The project's capture-privileges guidance calls running as Administrator on Windows "very insecure". |
| Restrict who can capture: membership of the `wireshark` group (Linux) or Npcap "Administrators only" (Windows). | Anyone who can capture can read unencrypted traffic on that interface. |
| Keep Wireshark on a supported, patched branch. | Advisories (`wnpa-sec-*`) are published frequently, mostly for dissector and file-parser crashes. See the [security page](https://www.wireshark.org/security/). |
| Open captures from untrusted sources in a disposable VM or sandbox. | A crafted capture file can trigger the same parser bugs as live traffic. |
| Treat capture files as sensitive data: encrypt at rest, limit retention, and log who has copies. | Captures can contain credentials, session cookies, personal data, and internal addressing. |
| Remember that pcapng files carry metadata. | On Fedora 44, `capinfos` showed that a TShark capture recorded the CPU model, operating system and kernel version, and capture application. Interface names and comments may also be stored. |
| Use capture filters and snap lengths to minimise collection. | `-s` (snapshot length) on TShark/dumpcap captures only packet headers when payloads are not needed. `editcap -s` truncates existing files. |
| Protect TLS key material. | Decrypting TLS needs session secrets. Anyone with those secrets and the capture can read the traffic. |
| Verify installers against the signed hash list. | Detects tampered downloads. |

Sanitising: truncation (`editcap -s`) and filtering out unrelated packets reduce exposure but
do **not** anonymise IP or MAC addresses. Wireshark's own documentation reviewed for this entry
does not provide a full anonymisation procedure, so before sharing captures outside your
organisation, review them packet by packet or use a dedicated, vetted anonymisation tool.

## Practical usage examples

The commands below use your own machine or documentation-reserved addresses (`192.0.2.0/24`,
`example.com`). Replace them only with systems you are authorised to monitor. Commands marked
*spot-checked* were run on Fedora 44 with Wireshark 4.6.8 as described in
[Verification notes](#verification-notes); the others are illustrative.

### Personal and home-lab use

**Investigate unexpected traffic from a device on your own network.** Capture briefly on your
computer's interface with a time limit, then summarise who it talked to:

```bash
mkdir -p -m 700 ~/captures          # private directory for capture files
# Capture for 5 minutes (300 s) into a file; stops automatically
tshark -i <INTERFACE> -a duration:300 -w ~/captures/home.pcapng

# Summarise conversations by IP address (statistics only, no packet output)
tshark -r ~/captures/home.pcapng -q -z conv,ip
```

On a switched home network this shows only your own computer's traffic plus
broadcast/multicast. To see another device, capture on the router (if it supports it) or on a
mirror port.

**Troubleshoot DNS resolution.** Capture DNS only, then show failed lookups:

```bash
tshark -i <INTERFACE> -f "udp port 53" -a duration:60 -w ~/captures/dns.pcapng
tshark -r ~/captures/dns.pcapng -Y "dns.flags.rcode != 0" \
  -T fields -e frame.time -e ip.src -e dns.qry.name -e dns.flags.rcode
```

A non-zero response code (`rcode`) indicates errors such as NXDOMAIN (3) or SERVFAIL (2).
Encrypted DNS (DNS over HTTPS/TLS) will not appear as `dns` traffic.

**Learn safely on loopback** (*spot-checked*). Generate a connection to a closed local port
and capture the TCP reset:

```bash
tshark -q -i lo -f "tcp port 9" -a duration:4 -w /tmp/lo9.pcapng &
sleep 1                                     # give the capture time to start
nmap -sT -p 9 -n 127.0.0.1 > /dev/null      # or any local client
wait
tshark -r /tmp/lo9.pcapng -Y "tcp.flags.reset == 1" \
  -T fields -e frame.number -e ip.src -e ip.dst -e tcp.srcport -e tcp.dstport
```

Expected: one line showing a reset sent from port 9 on `127.0.0.1` back to the client's
ephemeral port.

### Enterprise use

**Packet capture during incident response.** Use a ring buffer so the capture can run for
hours without filling the disk, capture on a designated monitoring interface fed by a SPAN
port or tap, and record chain-of-custody details:

```bash
# 10 files x 100 MB (filesize is in kB); oldest file overwritten when full
dumpcap -i <MONITOR_INTERFACE> -f "host 192.0.2.50" \
  -b filesize:100000 -b files:10 -w /srv/captures/ir-case-0001.pcapng
sha256sum /srv/captures/ir-case-0001_*.pcapng > /srv/captures/ir-case-0001.sha256
```

The capture directory must be writable by the analyst account running `dumpcap` and
readable only by authorised staff. Hashing the files at collection time lets you show later that the evidence was not altered.

**Investigate application connectivity.** A capture taken next to the client usually
answers whether the server responded at all, whether the TCP handshake completed, and
whether TLS negotiation failed:

```bash
tshark -r app-issue.pcapng -Y "tcp.flags.syn == 1 && tcp.flags.ack == 0" -T fields \
  -e frame.time -e ip.dst -e tcp.dstport                       # connection attempts
tshark -r app-issue.pcapng -Y "tcp.analysis.retransmission"      # packet loss symptoms
tshark -r app-issue.pcapng -Y "tls.handshake.type == 1" -T fields \
  -e ip.dst -e tls.handshake.extensions_server_name             # TLS ClientHello / SNI
```

**Convert for tools that need classic pcap** (*spot-checked*):

```bash
editcap -F pcap input.pcapng output.pcap
```

## Enterprise deployment considerations

- **Authorisation and scope.** Packet capture is monitoring of communications. Base it on a
  written policy or change/incident record that states the purpose, scope (interfaces,
  hosts, time window), who is authorised, and retention. Legal and HR review may be needed
  where captures can include employee or customer personal data.
- **Placement and visibility.** Analysts usually need SPAN/mirror ports or network taps
  provisioned by the network team. Changes to switch configuration should go through change
  management.
- **Data protection.** Store captures in an access-controlled, encrypted location with a
  defined retention period. Avoid copying captures to personal devices or ticket
  attachments. Captures may be subject to legal hold.
- **Workstation control.** Restrict capture rights (group membership, Npcap
  Administrators-only) to named analysts. Endpoint management should keep Wireshark patched,
  because outdated dissectors are a realistic attack surface on analyst machines.
- **Scale.** Wireshark is for focused investigations. Continuous full-packet capture,
  indexing, and retention at scale need purpose-built platforms. Use Wireshark to analyse
  extracts from them.
- **Support.** The open-source project has no commercial support contract. Organisations rely
  on community resources, internal expertise, or third-party training.
- **Auditability.** Wireshark itself does not log who opened which capture. Use file-system
  auditing or a controlled evidence store if you need that trail.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| No interfaces listed, or "You don't have permission to capture on that device" (Linux) | User is not in the `wireshark` group, or the session predates the group change. Log out and in, or run `newgrp wireshark` for the current shell. Check `getcap` on `dumpcap`. On Debian, re-run `sudo dpkg-reconfigure wireshark-common`. |
| Permissions on `dumpcap` stopped working after a manual change | Changing the file's group or owner clears file capabilities. Re-apply them as described on the [capture privileges](https://wiki.wireshark.org/CaptureSetup/CapturePrivileges) page, or reinstall the package. |
| No interfaces on Windows | Npcap missing (for example after a silent install) or restricted to Administrators. Install or repair Npcap. |
| No interfaces on macOS | ChmodBPF not installed. Install it from the disk image (or *About Wireshark → Folders → macOS Extras*) and log in again. |
| You see only your own traffic | Expected on switched networks. Use a mirror port or tap. |
| Capture filter rejected | Capture filters use libpcap syntax (`tcp port 443`), not display-filter syntax (`tcp.port == 443`). |
| GUI becomes unresponsive with large files | Split with `editcap -c <packets-per-file>`, filter with TShark first, or use capture filters and ring buffers next time. |
| Flatpak build cannot capture | Documented limitation. Use the distribution package for capture. |
| Wi-Fi capture shows no other stations' traffic | Monitor mode is hardware- and driver-dependent and not always available. See the Wireshark wiki for your platform. |

## Alternatives and related tools

- **tcpdump:** the classic command-line capture tool using the same libpcap filters. It is
  lighter for headless capture; analyse the resulting file in Wireshark.
- **TShark and dumpcap** (part of Wireshark): headless capture and scripted analysis.
- **Zeek** and **Suricata:** continuous network monitoring and detection, rather than
  interactive analysis. Planned for this knowledge base.
- [Nmap](nmap.md): active discovery of hosts and services. It is often used alongside
  Wireshark to see how a scan looks on the wire.

## References

### Official documentation

- [Wireshark website](https://www.wireshark.org)
- [Wireshark User's Guide](https://www.wireshark.org/docs/wsug_html_chunked/)
- [Capture filters](https://www.wireshark.org/docs/wsug_html_chunked/ChCapCaptureFilterSection.html)
  and [display filters](https://www.wireshark.org/docs/wsug_html_chunked/ChWorkBuildDisplayFilterSection.html)
- Manual pages: [tshark](https://www.wireshark.org/docs/man-pages/tshark.html) and
  [dumpcap](https://www.wireshark.org/docs/man-pages/dumpcap.html)
- Source repository: <https://gitlab.com/wireshark/wireshark>

### Installation references

- [Download page](https://www.wireshark.org/download.html) (current releases, signatures file, PPA link)
- [Supported platforms and requirements](https://www.wireshark.org/docs/wsug_html_chunked/ChIntroPlatforms.html)
- [Installing on Windows](https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallWinInstall.html),
  [macOS](https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallOSXInstall.html), and
  [UNIX/Linux](https://www.wireshark.org/docs/wsug_html_chunked/ChBuildInstallUnixInstallBins.html)
- [Debian packaging notes (README.Debian)](https://gitlab.com/wireshark/wireshark/-/raw/master/packaging/debian/README.Debian)
- [Debian stable packages: wireshark](https://packages.debian.org/stable/wireshark) and
  [tshark](https://packages.debian.org/stable/tshark)

### Security and deployment references

- [Security advisories](https://www.wireshark.org/security/)
- [Capture privileges](https://wiki.wireshark.org/CaptureSetup/CapturePrivileges)
- [Release life cycle](https://www.wireshark.org/docs/wsug_html_chunked/ChIntroReleaseLifeCycle.html)
- [Npcap](https://npcap.com/)

### Verification notes

- **Sources checked:** 2026-11-12, against the pages listed above. At that date the download
  page listed 4.6.9 as stable and 4.4.19 as old stable, with 5.0 in release-candidate
  testing. The GitLab project page already labelled 5.0 as stable; the discrepancy was not
  resolved. Re-check the download page before relying on a branch name.
- **Package names:** Fedora names (`wireshark`, `wireshark-cli`) and the Fedora 44 dumpcap
  permissions (owner `root`, group `wireshark`, mode `0750`, capabilities
  `cap_net_admin,cap_net_raw=ep`) were observed on a Fedora 44 system with wireshark 4.6.8
  from the Fedora repositories. Debian names were checked on packages.debian.org (trixie).
- **Spot-checked commands (not a full lab test):** on 2026-11-12, on Fedora 44 with
  Wireshark 4.6.8 from Fedora's repositories: `tshark --version`, `tshark -D`, the loopback
  capture and reset-filter example (output written to a scratch directory instead of `/tmp`),
  `tshark -q -z conv,ip`, `capinfos`, and `editcap -F pcap`. The observed results were as
  described above. All display-filter field names used on this page were confirmed with
  `tshark -G fields`. Installation procedures were not executed on any platform; the
  installation was pre-existing.
- **Unresolved:** minimum supported macOS version for the 4.6 branch; the exact signatures-file
  URL (linked from the download page).
