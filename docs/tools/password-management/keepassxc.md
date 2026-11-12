---
tool: KeePassXC
category: password-management
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://keepassxc.org
repository: https://github.com/keepassxreboot/keepassxc
requires_authorisation: false
---

# KeePassXC

## At a glance

| Field | Value |
|---|---|
| Official website | <https://keepassxc.org> |
| Source repository | <https://github.com/keepassxreboot/keepassxc> |
| Licence | GPL-2.0 or GPL-3.0 (per the README; the website states GPLv3), with third-party files under other licences listed in `COPYING` |
| Supported operating systems | Windows 10/11 (x64, ARM64), macOS 12 and later, Linux; no official mobile apps |
| Maintenance status | Active: 2.8.0 released 2026-10-21. Checked 2026-11-12 |
| Category | Password and Secret Management |
| Personal suitability | High: free, offline, and well documented; you are responsible for backups and recovery |
| Enterprise suitability | Low to Medium: suitable for individual administrators or small teams with clear procedures; no central administration, policy enforcement, or audit logging |
| Tested versions | Not tested |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

KeePassXC is a cross-platform, offline password manager. It stores passwords, notes, TOTP
secrets, passkeys, SSH keys, and attachments in a single encrypted database file in the
**KDBX** format, compatible with other KeePass-family applications. There is no server or
account: the security of your data depends on your master key (password, plus optional key
file or hardware key) and on where you keep the file. It is a community project, a fork of
KeePassX, maintained by the KeePassXC team.

## Features and capabilities

- **Encrypted local database** in KDBX 4 (recommended) or KDBX 3.1. Older KeePass 1.x
  databases can be imported.
- **Key derivation:** Argon2 (recommended by the project, available in KDBX 4) or AES-KDF. The
  project recommends adjusting only the decryption-time slider, aiming for about one second.
- **Additional key factors:** a key file, and/or a YubiKey or OnlyKey in HMAC-SHA1
  challenge-response mode.
- **Password and passphrase generators**, with custom word lists.
- **Browser integration** through the KeePassXC-Browser extension for Firefox, Tor Browser,
  Chrome, Chromium, Edge, Vivaldi, and Brave, including passkeys.
- **Auto-Type**, **TOTP**, an **SSH agent** integration, and Freedesktop **Secret Service**
  support on Linux.
- **Merging and synchronisation:** merge two databases entry by entry, or run configured
  upload/download commands with *Remote Sync*. **KeeShare** shares groups between databases.
- **Command-line interface:** `keepassxc-cli`.

Limitations:

- **No account recovery.** Losing the master password, key file, or hardware-key secret means
  losing the data. The documentation warns this "might result in permanent locking of your
  database".
- **No built-in cloud sync or multi-user server.** Sharing and sync rely on files and
  external services.
- **No official mobile apps.** The FAQ points to separate projects (KeePassDX and
  KeePass2Android on Android; Strongbox and KeePassium on iOS), which have their own
  maintainers and security properties.
- **Endpoint trust:** like any local password manager, it cannot protect secrets on a device
  already compromised by malware running with your privileges or administrator rights.

## System requirements

- **Windows:** Windows 10 or 11, x64 or ARM64. The MSI requires the Microsoft Visual C++
  Redistributable. The download page states that the legacy installer for Windows 7/8/8.1 "is
  no longer supported after version 2.7.12".
- **macOS:** 12 or later (Apple Silicon and Intel disk images). MacPorts is suggested for
  macOS 11 and earlier.
- **Linux:** x86-64 (AArch64 AppImage experimental in 2.8.0). On Wayland, Auto-Type needs XDG
  Desktop Portal support (KDE Plasma 6.6+ and GNOME 51+ are listed in the current
  documentation).
- **Hardware:** modest. Higher KDF settings increase unlock time and memory use, so very
  low-powered devices may need lower settings.
- **Privileges:** installation needs administrator rights for system packages (MSI, `dnf`,
  `apt`). Flatpak `--user`, the portable ZIP, and AppImage do not.

## Installation

Use the official channels on the [download page](https://keepassxc.org/download/). Distribution
packages are maintained by the distributions and may lag the upstream release.

### Fedora Linux

```bash
sudo dnf install keepassxc
```

Fedora 44 repositories provided 2.7.12 on 2026-11-12, one release behind upstream 2.8.0.
For the current release, use the Flatpak, which the download page labels **"Recommended"**
for Linux:

```bash
flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo
flatpak install --user flathub org.keepassxc.KeePassXC
```

The `--user` installation needs no `sudo`.

### Debian and Ubuntu

```bash
sudo apt update
sudo apt install keepassxc
```

In Debian stable (trixie, 2.7.10 at review time), `keepassxc` is a transitional package that
depends on `keepassxc-full` or `keepassxc-minimal`. Check the package descriptions to see which
features each includes. For newer versions, the download page lists an Ubuntu PPA
(`ppa:phoerious/keepassxc`), the Flatpak, a Snap (`sudo snap install keepassxc`), and an
AppImage. The Snap cannot see files outside your home directory (except removable media), and
needs an extra interface connection for YubiKeys (see the FAQ).

### Windows

Use one of:

- The **MSI installer** from the download page (x64 or ARM64), run as an administrator.
- **winget:** `winget install -e --id KeePassXCTeam.KeePassXC`
- The portable ZIP, Microsoft Store, or Chocolatey (`choco install keepassxc`), all listed on
  the download page.

### macOS

Download the Apple Silicon or Intel `.dmg` from the download page and drag KeePassXC to
`/Applications`, or use Homebrew:

```bash
brew install --cask keepassxc
```

### Verify the installation

Verify downloaded files **before** installing them, as described on
[Verifying signatures](https://keepassxc.org/verifying-signatures/):

```bash
# Import the KeePassXC release key and check its fingerprint
gpg --keyserver keys.openpgp.org --recv-keys BF5A669F2272CF4324C1FDA8CFB4C2166397D0D2
gpg --verify KeePassXC-<VERSION>-<PLATFORM>.<EXT>.sig   # expect "Good signature"
shasum -a 256 -c KeePassXC-<VERSION>-<PLATFORM>.<EXT>.DIGEST   # expect "...: OK"
```

The expected primary key fingerprint is `BF5A 669F 2272 CF43 24C1 FDA8 CFB4 C216 6397 D0D2`.
The project stresses that the `.DIGEST` file only shows the download is intact, while the
signature shows it came from the KeePassXC team. On Windows, the MSI is also Authenticode-signed;
the project states the UAC prompt shows the publisher "DroidMonkey Apps, LLC". macOS builds are
signed with an Apple Developer ID.

After installation, start KeePassXC and confirm that the version shown in its About dialog
matches the release you verified.

### Updating and removal

- **Package managers:** `sudo dnf upgrade keepassxc`, `sudo apt upgrade`, `flatpak update`,
  `winget upgrade KeePassXCTeam.KeePassXC`, or `brew upgrade --cask keepassxc`.
- **MSI/DMG:** download, verify, and install the new version over the old one.
- **Back up your database before major upgrades** (for example 2.7 → 2.8), so you can return
  to the previous version with an unchanged copy if something goes wrong.
- **Removal** uninstalls the application but **does not delete your databases or key files**,
  wherever you stored them. Delete or keep them deliberately. Application settings live in
  your user profile.

## Initial configuration

1. **Create the database** from the *Database* menu. Choose **KDBX 4** with the recommended
   settings, and set the decryption time to around one second, as the project recommends.
2. **Choose a strong master password.** Use a long passphrase you can remember (the built-in
   passphrase generator helps). Write it down and keep it physically secure if you might
   forget it. There is no reset.
3. **Optional extra factor:** add a key file generated by KeePassXC (*Database settings →
   Security → Add Key File → Generate*) or a hardware key (*Add Challenge Response*). See
   hardening below for the backup implications.
4. **Set locking behaviour** in the application settings (*Tools → Settings*): lock after a period of
   inactivity and when the screen locks, and clear the clipboard after copying. Choose values
   that suit your environment; the defaults were not confirmed in the documentation reviewed.
5. **Configure backups** (see [Security hardening](#security-hardening)): set a backup
   destination in the save options, and plan an off-device copy.
6. **Browser integration (optional):** *Tools → Settings → Browser Integration → Enable browser
   integration*, select your browsers, install KeePassXC-Browser, and click **Connect** in the
   extension. Give each connection a unique name. Reusing a name overwrites the previous
   connection.

## Security hardening

| Measure | Why |
|---|---|
| Use KDBX 4 with Argon2 and about one second of decryption time. | Strengthens the master key against offline guessing if the file is stolen. |
| Use a long, unique master passphrase. Never reuse it. | The database file may end up in cloud storage or backups. Its strength is your main protection. |
| If you use a key file: let KeePassXC generate it, never modify it, keep it separate from the database, back it up, and always use it with a password. | The FAQ says the file must never change and must be unpredictable, and advises against using a key file without a password. Storing it next to the database removes its benefit. |
| If you use a YubiKey/OnlyKey: back up the challenge-response secret or program a second key with the same secret. | The FAQ warns that losing or breaking the key "you will permanently lose access". |
| Keep several dated backups in separate places, including one offline, and test that you can open them. | KeePassXC cannot recover a corrupted or deleted database. Its default "safe saves" mode reduces, but does not remove, corruption risk. |
| Enable auto-lock and clipboard clearing. | Limits exposure if you leave the device unattended or paste into the wrong window. The CLI's `clip` command clears after 10 seconds by default. |
| Grant browser access per site ("Confirm Access") and remove unused browser connections. | Each connection can request credentials from an unlocked database. |
| Be careful with Auto-Type, especially on Wayland, where window-title matching is not available. | Typing into the wrong window can disclose a password. |
| Keep screen-capture protection on. | On Windows and macOS, KeePassXC blocks screenshots and recordings by default. |
| Install only from official channels and verify signatures. | A trojanised password manager would expose every secret. |

The project had an independent code review (completed 19 January 2023), with the caveat in its
FAQ that an audit covers only a snapshot of the code. The project also reports a French ANSSI
first-level security certification (CSPN) for version 2.7.9.

## Practical usage examples

Illustrative examples, not executed for this entry. Paths and names are placeholders.
Passwords are always entered at interactive prompts, never on the command line, so they do
not end up in shell history.

### Personal and home-lab use

**Manage offline credentials.** Create a database from the command line. `--set-password`
prompts for the new password:

```bash
mkdir -p ~/Vaults
keepassxc-cli db-create --set-password ~/Vaults/personal.kdbx
keepassxc-cli generate                     # random password
keepassxc-cli diceware                     # passphrase
keepassxc-cli ls ~/Vaults/personal.kdbx    # prompts for the database password
```

**Add an entry with a generated password**, so the password is never typed:

```bash
keepassxc-cli add -g ~/Vaults/personal.kdbx "Example Service"
```

**Maintain encrypted backups.** Keep the database in a synced folder (Nextcloud, Dropbox, or
similar) for convenience *and* keep periodic offline copies. Before relying on a backup,
confirm it opens:

```bash
keepassxc-cli db-info /media/<BACKUP_DRIVE>/personal-2026-11-12.kdbx
```

**Check for leaked passwords offline** against a downloaded Have I Been Pwned SHA-1 hash list.
No passwords are sent anywhere:

```bash
keepassxc-cli analyze --hibp <PATH_TO_HIBP_SHA1_FILE> ~/Vaults/personal.kdbx
```

**Synchronise between two computers.** If a file-sync service creates a "conflicted copy",
use *Database → Merge From Database* to combine it into your main database. Entries are matched
by UUID, and the most recently modified version wins, with the older one kept in history.

### Enterprise use

**Individual administrator vault.** An administrator keeps break-glass or infrastructure
credentials in a KeePassXC database protected by a passphrase and hardware key, stored on
managed, encrypted storage, with a sealed recovery copy of the master key held under dual
control.

**Small team sharing with KeeShare.** A team lead exports a group (for example "Lab
infrastructure") to a shared file. Team members import or synchronise it into their own
databases. Everyone who holds the shared file and its password can read every secret in it.
There is no per-user revocation beyond rotating those secrets and re-sharing.

These patterns work only where the limitations below are explicitly accepted.

## Enterprise deployment considerations

- **No central management.** There is no administration console, user directory integration,
  role-based access control, policy enforcement, or central audit log of who viewed which
  secret. Many compliance regimes require these for shared credentials.
- **Offboarding.** Anyone who had a copy of a database and its key can keep it. Revoking access
  means rotating every secret they could see.
- **Recovery governance.** Define who holds recovery material (master password, key file,
  hardware-key secret), how it is stored (for example a sealed envelope in a safe), and how
  use is recorded.
- **Distribution and updates.** Deploy through your software-management tooling (MSI or winget
  on Windows, managed repositories on Linux) and keep it current. Decide whether browser
  integration is permitted.
- **Data location.** Decide where database files may be stored (managed file shares, endpoint
  encryption) and prohibit personal cloud storage for corporate secrets.
- **Support.** Community support only; there is no vendor support contract.
- **Better fit:** for organisation-wide password management, evaluate server-based managers with
  central administration and audit logging, such as [Vaultwarden](vaultwarden.md) (with its own
  limitations) or commercially supported products. For machine secrets, use a secrets vault.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| "Invalid credentials" or the database will not open | Wrong password, missing or changed key file, or wrong hardware-key slot. A modified key file cannot be repaired. Restore the original from backup. |
| Browser extension cannot connect | Browser integration not enabled for that browser, or the browser is a Flatpak/Snap build. The documentation says these are generally not supported on Linux, apart from Ubuntu's Firefox Snap. |
| Auto-Type does nothing on Linux | On Wayland, the desktop needs the Remote Desktop and Global Shortcuts portals (KDE Plasma 6.6+, GNOME 51+). Older desktops may need an X11 session. |
| YubiKey not detected with the Snap | Connect the interface as described in the FAQ (`sudo snap connect "keepassxc:raw-usb" "core:raw-usb"`). |
| Snap cannot open a database on another drive | Snap confinement limits access to your home directory and removable media under `/media`. |
| Sync service created conflicted copies | Two devices saved at once. Merge the copy (*Database → Merge From Database*) and delete it afterwards. |
| Remote Sync left an inconsistent state | The documentation warns that syncing "is not an atomic operation". Keep backups and avoid running it concurrently from several devices. |
| Windows 7/8 installation fails | Current releases require Windows 10 or later. 2.7.12 was the last legacy-installer version and is no longer supported. |

## Alternatives and related tools

- [Vaultwarden](vaultwarden.md): self-hosted, Bitwarden-compatible server for multi-device sync
  and sharing.
- **KeePass** (the original Windows application) and other KDBX-compatible clients.
- **Bitwarden**, **1Password**, and other hosted password managers: provider-run sync, sharing,
  and administration.
- **pass** (the standard UNIX password manager): GPG-encrypted files managed in Git, suited to
  command-line users.

## References

### Official documentation

- [KeePassXC website](https://keepassxc.org)
- [Documentation index](https://keepassxc.org/docs/), including the User Guide and Getting
  Started guide
- [FAQ](https://keepassxc.org/faq/) (key files, hardware keys, sync, mobile apps, audit)
- Source repository: <https://github.com/keepassxreboot/keepassxc>
- Maintainer-authored documentation sources:
  [database operations](https://github.com/keepassxreboot/keepassxc/blob/develop/docs/topics/DatabaseOperations.adoc),
  [browser integration](https://github.com/keepassxreboot/keepassxc/blob/develop/docs/topics/BrowserIntegration.adoc),
  [Auto-Type](https://github.com/keepassxreboot/keepassxc/blob/develop/docs/topics/AutoType.adoc),
  and the [keepassxc-cli manual](https://github.com/keepassxreboot/keepassxc/blob/develop/docs/man/keepassxc-cli.1.adoc)

### Installation references

- [Download page](https://keepassxc.org/download/)
- [Verifying signatures](https://keepassxc.org/verifying-signatures/)
- [Debian stable package: keepassxc](https://packages.debian.org/stable/keepassxc)

### Security and deployment references

- [Project blog (release notes, audit and certification announcements)](https://keepassxc.org/blog/)
- [KeePassXC-Browser extension source](https://github.com/keepassxreboot/keepassxc-browser)

### Verification notes

- **Sources checked:** 2026-11-12, against the pages listed above. The rendered User Guide
  could not be read in full, so the maintainer-authored AsciiDoc sources (develop branch) were
  used for database, browser, Auto-Type, and CLI details. Those sources may describe behaviour
  of the newest release only.
- **Release:** 2.8.0, published 2026-10-21 (blog and GitHub releases API).
- **Distribution versions:** Fedora 44 provided 2.7.12 (`dnf`). Debian stable provided 2.7.10
  (packages.debian.org).
- **Not executed:** KeePassXC was not installed or run for this entry. CLI commands and options
  were checked against the `keepassxc-cli` manual only.
- **Unresolved:** the default cipher and KDF parameters for new databases and the default
  lock/clipboard timeouts in the GUI (not stated in the documentation reviewed). The official
  FAQ states Auto-Type works only under X11 on Linux, which conflicts with the 2.8.0
  documentation and release notes on Wayland support.
