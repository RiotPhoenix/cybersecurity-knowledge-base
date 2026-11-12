---
tool: ZAP
category: penetration-testing
status: research-complete
last_reviewed: 2026-11-12
tested_versions: []
website: https://www.zaproxy.org/
repository: https://github.com/zaproxy/zaproxy
requires_authorisation: true
---

# ZAP (Zed Attack Proxy)

!!! warning "Authorised use only"
    ZAP's active scanner sends attack payloads that can modify or delete data, create junk
    records, lock accounts, and degrade services. Even its spider can follow links that change
    state. Test only applications you own or have **explicit written authorisation** to test,
    within an agreed scope and time window. Practise against deliberately vulnerable
    applications in an isolated lab.

## At a glance

| Field | Value |
|---|---|
| Official website | <https://www.zaproxy.org/> |
| Source repository | <https://github.com/zaproxy/zaproxy> |
| Licence | Apache-2.0 |
| Supported operating systems | Windows, Linux, macOS (Java 17 or later; bundled on macOS), official Docker images |
| Maintenance status | Active: 2.17.0 (latest full release, 2025-12-15), with weekly releases (latest 2026-11-11). Checked 2026-11-12 |
| Category | Penetration Testing |
| Personal suitability | High: free, well documented, and ideal for learning web security against lab applications |
| Enterprise suitability | Medium to High: widely used for dynamic application testing and CI automation, if governed by scope, authorisation, and triage processes |
| Tested versions | Not yet tested |
| Verification status | Research complete |
| Last reviewed | 2026-11-12 |

## Overview

ZAP is an open-source web application security scanner and intercepting proxy, previously
known as **OWASP ZAP**. Its website now presents it as "ZAP by Checkmarx". It sits between a
browser (or other client) and a web application, records the traffic, analyses it for security
weaknesses, and can actively probe the application for vulnerabilities such as injection flaws
and cross-site scripting.

ZAP's checks fall into two fundamentally different groups:

| | Passive analysis | Active testing |
|---|---|---|
| What it does | Inspects requests and responses that pass through ZAP, without sending anything extra | Sends crafted requests (attacks) to find vulnerabilities |
| Typical findings | Missing security headers, insecure cookies, information disclosure | SQL injection, cross-site scripting, path traversal, and similar |
| Risk to the target | Low (the traffic is whatever you or the spider generated) | **High**: can change or destroy data and disrupt service |
| Authorisation | Still required for the target, because spidering sends requests | **Always required, in writing, with an agreed scope** |

**Spidering is not passive.** Crawlers send requests and submit forms (the traditional spider
posts forms by default). On an application where a link means "delete", the spider can delete.
Only spider applications you are authorised to test.

## Features and capabilities

- **Intercepting proxy** (listening on `localhost:8080` by default) with breakpoints to pause,
  inspect, and modify requests and responses.
- **Browser integration.** *Manual Explore* launches Firefox or Chrome preconfigured to proxy
  through ZAP. ZAP generates its own root certificate so it can decrypt HTTPS traffic for the
  browser it launches.
- **Passive scan rules** that run automatically on proxied traffic.
- **Spiders:** the traditional spider (fast, HTML-based) and browser-based crawling (AJAX spider
  and client spider) for JavaScript-heavy applications.
- **Active scanner** with configurable scan policies, attack strength, and alert thresholds.
- **Contexts** define an application: its URLs, inclusion and exclusion patterns, technologies,
  authentication method, session management, and users.
- **Authentication handling:** manual, HTTP, form-based, JSON, script-based, browser-based, and
  auto-detection methods, with logged-in and logged-out verification.
- **API scanning** of OpenAPI, SOAP, and GraphQL definitions.
- **Automation Framework:** a YAML plan describing the environment and an ordered list of jobs
  (spider, passive-scan wait, active scan, reports, and more), run with `zap.sh -cmd -autorun`.
- **Packaged Docker scans:** baseline (spider plus passive scan), full (adds active scanning), and
  API scans.
- **Reports** in HTML, Markdown, XML, JSON, and other templates.
- **Modes:** *Safe*, *Protected*, *Standard*, and *ATTACK*. The documentation recommends
  **Protected** mode, which allows potentially dangerous actions only on URLs in scope.
- **Marketplace** of add-ons, including alpha and beta scan rules.

Limitations:

- **False positives and negatives.** Automated scanners miss business-logic flaws and
  authorisation problems, and report some issues that are not exploitable. Findings need manual
  verification.
- **Authentication is often the hard part.** Unauthenticated scans see little of most
  applications, and fragile authentication configuration silently produces incomplete scans.
- **Unsigned releases.** The download page states that ZAP releases are currently unsigned.
  Verify downloads against the published SHA-256 checksums.

## System requirements

- **Java:** Windows and Linux packages require Java 17 or later. The macOS installers include
  Java 17. Fedora 44 provides Java 25 (`java-25-openjdk`), and Debian 13's `default-jre` is
  Java 21. Both meet "17 or later", but neither combination was tested for this entry.
- **Hardware:** no official minimum is published. The desktop is a Java application, and active
  scans of large applications consume CPU and memory for hours. A workstation with several GB
  of free RAM is a practical starting point (assumption, not an official figure).
- **Privileges:** no administrator rights are needed to run ZAP. Installers need them to install
  system-wide.
- **Network:** access to the target application. The ZAP API listens on the same port as the
  proxy. Keep it on loopback.

## Installation

All official options are listed on the download page. Choose one:

| Platform | Method | Maintained by |
|---|---|---|
| Fedora and other Linux | Flathub (`org.zaproxy.ZAP`), Snapcraft (`zaproxy`), Linux installer, Linux package (`.tar.gz`), or the ZAP Linux repositories | ZAP team |
| Debian and Ubuntu | Linux installer or package with a Java 17+ runtime; Flathub or Snapcraft | ZAP team |
| Windows | Windows installer, or `winget install --id=ZAP.ZAP -e` | ZAP team |
| macOS | macOS installer (`.dmg`, Intel or Apple Silicon), or `brew install --cask zap` | ZAP team (Homebrew cask "updated by the ZAP team") |
| Containers | `ghcr.io/zaproxy/zaproxy:stable` (also `zaproxy/zap-stable` on Docker Hub); `:bare`, `:weekly`, `:nightly` | ZAP team |

Chocolatey and FreeBSD packages are listed as unsupported third-party packages.

### Fedora (Flathub)

Prerequisite: Flatpak with the Flathub remote enabled (Fedora includes Flatpak):

```bash
flatpak install flathub org.zaproxy.ZAP
flatpak run org.zaproxy.ZAP
```

### Debian and Ubuntu (Linux package)

Install a Java runtime, download the Linux package from the download page, verify its checksum
against the value on the GitHub release page, and run it from your home directory:

```bash
sudo apt install default-jre
cd ~/Downloads
sha256sum ZAP_2.17.0_Linux.tar.gz        # compare with the SHA-256 on the v2.17.0 release page
tar -xzf ZAP_2.17.0_Linux.tar.gz
./ZAP_2.17.0/zap.sh
```

`sudo` is only needed to install Java. ZAP itself runs as your normal user. Do not run it as
root.

### Windows and macOS

Download the installer, check its SHA-256 checksum (`Get-FileHash .\ZAP_2_17_0_windows.exe` in
PowerShell, or `shasum -a 256` on macOS), and run it. Because releases are unsigned, Windows
SmartScreen and macOS Gatekeeper show warnings. The download page documents how to proceed.
Only do so after the checksum matches.

### Containers

```bash
docker pull ghcr.io/zaproxy/zaproxy:stable
docker run --rm -t ghcr.io/zaproxy/zaproxy:stable zap.sh -version
```

Mount a working directory at `/zap/wrk` for plans and reports. The images run as the `zap`
user. The `stable` image is updated on each full release and regenerated monthly with updated
add-ons, so pin by digest in CI if you need reproducibility. The documentation warns that the
packaged scans **expose the unauthenticated ZAP API** to the host they run on: do not publish the
API port to untrusted systems.

### Verify the installation

- **Desktop:** ZAP starts and asks whether to persist the session. *Help > About* shows the
  version.
- **Command line:** `./zap.sh -cmd -version` (or `zap.sh -version` in the container) prints the
  version and exits.
- **Proxy:** with ZAP running, `curl -x http://127.0.0.1:8080 http://localhost:3000/` against a lab
  application should appear in ZAP's *History* tab.

### Updating and removal

- **Core:** install the new full release from the same channel (Flathub, Snap, winget, Homebrew,
  or a new download). Read the release notes first.
- **Add-ons:** *Help > Check for Updates* in the desktop, or `zap.sh -cmd -addonupdate`. In
  containers, the documentation recommends `zap.sh -cmd -addonupdate` before running a plan if you
  need the latest add-ons.
- **Weekly releases** contain the latest features but "things may be broken or only partially
  implemented". Use full releases for routine work.
- **Rollback:** reinstall the previous release from the GitHub releases page. Keep plans and
  context files under version control so they survive reinstallation.
- **Removal:** uninstall through the platform's package manager or installer. User settings and
  the generated root certificate remain in the ZAP home directory (for example `~/.ZAP` on Linux)
  until you delete it.

## Initial configuration

1. **Set the mode to Protected** (toolbar). Dangerous actions are then possible only on URLs in
   scope.
2. **Create a context** for your lab application (for example `http://localhost:3000`). Add an
   inclusion regex such as `http://localhost:3000.*` and mark the context *In Scope*. Add
   exclusions for logout and destructive endpoints.
3. **Use the browser ZAP launches** (*Manual Explore*) instead of importing ZAP's root certificate
   into your everyday browser profile. A trusted interception CA in your normal browser lets anyone
   who obtains ZAP's key intercept your HTTPS traffic.
4. **Keep the API on loopback** and leave the API key requirement enabled (the default since
   2.6.0). Never use API options that accept connections from any address on a shared network.
5. **Persist sessions** for real assessments, and store session files and reports in a protected
   directory: they contain requests, responses, cookies, and possibly credentials.

## Security hardening

| Measure | Why |
|---|---|
| Work in Protected mode, with explicit contexts and scope. | Prevents spidering or attacking sites you did not intend to test. |
| Keep the proxy and API bound to `127.0.0.1`, require the API key, and never publish the API port from containers to untrusted networks. | The API controls ZAP fully. The packaged Docker scans expose it without authentication. |
| Do not trust ZAP's root CA in your daily browser profile. Use the browser launched by ZAP, or a separate profile. | ZAP's CA can decrypt any HTTPS traffic for browsers that trust it. |
| Verify download checksums against the release page. | Releases are unsigned, so the checksum is your integrity check. |
| Supply credentials through environment variables in automation plans (`${VAR}`), not literal values in YAML. | Plans are stored in repositories and CI logs. |
| Use dedicated test accounts with no real data, and test against non-production environments. | Active scans create junk data and can trigger account lockouts or notifications. |
| Treat sessions, reports, and logs as confidential, and delete them at the end of the engagement. | They contain application data and authentication material. |
| Install add-ons only from the official marketplace, and prefer release-quality rules for routine work. | Add-ons run inside ZAP. Alpha rules are less mature and noisier. |
| Throttle active scans (`delayInMs`, thread limits) on fragile targets. | Reduces the risk of a denial of service on the application under test. |

## Practical usage examples

All examples target **OWASP Juice Shop**, a deliberately vulnerable application, running on your
own machine. Never point these commands at a system you are not authorised to test. Not executed
for this entry.

### Personal and home-lab use

**Run a deliberately vulnerable local application.** Bind it to loopback so nothing else on your
network can reach it (command from the Juice Shop README):

```bash
docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop
```

**Explore it manually through ZAP.** In the desktop, open *Manual Explore*, enter
`http://localhost:3000`, launch the browser, and use the application: register a test account,
search, and add items to the basket. Watch the *History* and *Alerts* tabs fill with passively
detected issues. Use breakpoints to modify a request (for example a basket quantity) and observe
how the application responds.

**Run a baseline (spider plus passive) scan in containers.** Put both containers on an internal
Docker network with no route out, and generate an HTML report in the current directory:

```bash
docker network create --internal zap-lab
docker run -d --rm --name juice-shop --network zap-lab bkimminich/juice-shop
docker run --rm --network zap-lab -v "$(pwd)":/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable \
  zap-baseline.py -t http://juice-shop:3000 -r baseline-report.html
```

The baseline scan "doesn't perform any actual 'attacks'". It spiders for one minute by default
and then reports passive findings. Exit codes are non-zero when warnings or failures are found,
which matters in CI.

**Active scan the lab application.** Only against your own Juice Shop instance:

<!-- quality-allow: active-web-scan -- deliberately vulnerable app on an internal-only Docker network -->
```bash
docker run --rm --network zap-lab -v "$(pwd)":/zap/wrk/:rw -t ghcr.io/zaproxy/zaproxy:stable \
  zap-full-scan.py -t http://juice-shop:3000 -m 5 -r full-report.html
```

Then verify each high-risk alert by hand. Reproduce the request, read the evidence ZAP recorded,
and decide whether it is exploitable. Clean up with `docker stop juice-shop` and
`docker network rm zap-lab`.

### Enterprise use

**Authorised application security testing.** Within an approved engagement, model each
application as a context with authentication, session management, and test users. Agree the scope
(hostnames, paths, excluded functions such as payments or account deletion), the time window, the
rate limits, and the emergency contact. Run passive analysis and spidering first, review coverage,
then run active scans with a scan policy appropriate to the environment. Report verified
findings, not raw scanner output.

**Controlled integration into CI pipelines.** Run passive baseline scans on every build of a
review or staging environment, and scheduled active scans against a dedicated test environment.
An Automation Framework plan kept in the repository makes the scan reviewable:

<!-- quality-allow: active-web-scan -- illustrates an approved staging-only plan; see the scope rules above -->
```yaml
env:
  contexts:
    - name: staging-app
      urls:
        - https://staging.example.com
      includePaths:
        - "https://staging.example.com.*"
      excludePaths:
        - "https://staging.example.com/logout.*"
  parameters:
    failOnError: true
    failOnWarning: false
    progressToStdout: true
jobs:
  - type: spider
    parameters:
      maxDuration: 5
  - type: passiveScan-wait
    parameters:
      maxDuration: 10
  - type: activeScan
    parameters:
      maxScanDurationInMins: 30
      delayInMs: 100
  - type: report
    parameters:
      template: risk-confidence-html
      reportDir: /zap/wrk
      reportFile: zap-staging-report
```

Run it with `zap.sh -cmd -autorun /zap/wrk/zap.yaml`. With `-cmd`, the exit code is 0 for success,
1 for errors, and 2 for warnings, unless an `exitStatus` job overrides it. Remove the
`activeScan` job for pipelines that run against shared or production-like environments. Store
test-account passwords in the CI secret store and reference them as `${VARIABLE}` in the plan's
user definitions.

## Enterprise deployment considerations

- **Authorisation and scope.** Every active test needs written authorisation from the application
  owner, an agreed scope (hosts, paths, excluded functions), a time window, rate limits, and
  contacts. Notify operations and monitoring teams, because ZAP traffic looks like an attack. Keep
  the authorisation record with the results.
- **Environment selection.** Prefer dedicated test environments with synthetic data. Baseline
  scans are described as suitable "even against production sites". Treat that as a decision for
  the application owner, because spidering still submits forms by default.
- **Pipeline governance.** Version plans in the repository, pin container images, fail builds only
  on agreed rule IDs (baseline scans support a configuration file that sets rules to `IGNORE`,
  `WARN`, or `FAIL`), and route new findings to the owning team's backlog.
- **Credential handling.** Use dedicated test identities, never real user accounts, and rotate them.
  Supply them from a secrets store at run time.
- **Triage capacity.** Automated DAST output needs triage by people who understand the application.
  Budget for it, or the findings will be ignored.
- **Data handling.** Session files and reports contain application data. Store them with access
  controls and retention limits.
- **Support.** ZAP is open source with community support. Check commercial support options and
  whether a commercial DAST product is required for your compliance programme.

## Troubleshooting

| Symptom | Likely cause and fix |
|---|---|
| Browser shows certificate errors through ZAP | The browser does not trust ZAP's root CA. Use the browser launched by *Manual Explore*, or a separate test profile that trusts the CA. |
| Nothing appears in *History* | The client is not using the proxy, or ZAP listens on a different address or port. Check *Options > Network > Local Servers/Proxies*. |
| Spider or active scan refuses to run | Protected or Safe mode, and the target is not in scope. Add the URL to an in-scope context. |
| Scan finds almost nothing behind the login | Authentication not configured or not verified. Configure the context's authentication, users, and logged-in or logged-out indicators, and check the authentication report. |
| Baseline scan in Docker cannot reach `localhost` | `localhost` inside the container is the container itself. Put the target and ZAP on the same Docker network, as in the examples. |
| ZAP will not start | Java older than 17, or not on `PATH`. Install a current Java runtime, or use the macOS installer, Flatpak, or containers. |
| Very slow scans, or the target falls over | Too many threads or no delay. Reduce threads, set `delayInMs`, and limit scan duration. |
| Docker healthcheck fails | ZAP running on a port other than 8080 without `ZAP_PORT` set. Set the variable. |
| Antivirus flags the download | Documented on the download page as a known false positive pattern. Verify the checksum before trusting it. |

## Alternatives and related tools

- [Nuclei](../vulnerability-management/nuclei.md): template-based checks for known
  vulnerabilities, complementary to ZAP's crawling and active scanning.
- [Nmap](../network-security/nmap.md): finds the web services to test in the first place.
- **Burp Suite**: commercial (with a free Community Edition) intercepting proxy and scanner
  (not yet documented here).
- [Wireshark](../network-security/wireshark.md): lower-level traffic analysis when HTTP-level
  views are not enough.

## References

### Official documentation

- [ZAP website](https://www.zaproxy.org/)
- [ZAP documentation](https://www.zaproxy.org/docs/)
- [Modes](https://www.zaproxy.org/docs/desktop/start/features/modes/)
- [Automation Framework](https://www.zaproxy.org/docs/desktop/addons/automation-framework/)
- [Automation Framework environment](https://www.zaproxy.org/docs/desktop/addons/automation-framework/environment/)
- [Source repository](https://github.com/zaproxy/zaproxy)

### Installation references

- [Download page](https://www.zaproxy.org/download/)
- [ZAP 2.17.0 release and checksums](https://github.com/zaproxy/zaproxy/releases/tag/v2.17.0)
- [Docker images and usage](https://www.zaproxy.org/docs/docker/about/)
- [Flathub: org.zaproxy.ZAP](https://flathub.org/en/apps/org.zaproxy.ZAP)

### Security and deployment references

- [Baseline scan](https://www.zaproxy.org/docs/docker/baseline-scan/)
- [Full scan](https://www.zaproxy.org/docs/docker/full-scan/)
- [API scan](https://www.zaproxy.org/docs/docker/api-scan/)
- [Why an API key is required by default](https://www.zaproxy.org/faq/why-is-an-api-key-required-by-default/)
- [OWASP Juice Shop](https://github.com/juice-shop/juice-shop)

### Verification notes

- **Sources checked:** 2026-11-12. Documentation was read on the website and from its Markdown
  sources in the `zaproxy-website` repository (Automation Framework add-on 0.62.0 pages).
- **Releases:** 2.17.0 is the latest full release (published 2025-12-15, GitHub `releases/latest`).
  Weekly releases continue (latest `w2026-11-11`). The download page lists 2.17.0 and states that
  releases are unsigned and that Windows and Linux need Java 17 or later.
- **Java on distributions:** Fedora 44 offered `java-25-openjdk-headless` 25.0.5 (`dnf
  repoquery`). Debian 13's `default-jre` depends on Java 21 (Debian archive query).
- **Automation plan:** keys (`env.contexts`, `includePaths`, `excludePaths`, `parameters`,
  `spider.maxDuration`, `passiveScan-wait.maxDuration`, `activeScan.maxScanDurationInMins`,
  `delayInMs`, `report.template`, `reportDir`, `reportFile`) and the exit codes were checked against
  the add-on documentation. The plan itself is illustrative and was not run.
- **Juice Shop:** the `docker run --rm -p 127.0.0.1:3000:3000 bkimminich/juice-shop` command is from
  the Juice Shop README. The internal-network variant is an adaptation.
- **Not executed:** ZAP was not installed or run for this entry.
- **Unresolved:** an official hardware recommendation for ZAP; the history and dates of the
  project's move from OWASP (not researched for this entry).
