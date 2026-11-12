# Authoring Standards

## Sources and verification

| Section | How to research and verify it |
|---|---|
| Overview, features | Official website, official documentation, and project README. Avoid marketing superlatives; describe what the tool does. |
| Official website, source repository | Link only to the project's own domains and repositories. Confirm the repository is the canonical upstream. |
| Licence | The licence file in the source repository or the vendor's licensing page. Use SPDX identifiers where available. |
| Supported operating systems | Official installation or system-requirements documentation. |
| Maintenance status | Recent releases and commit activity in the canonical repository; vendor lifecycle or end-of-life pages. Record the date you checked. |
| System requirements | Official documentation only. |
| Installation, initial configuration | Official installation guides. Prefer distribution packages or signed official releases; document signature or checksum verification where provided. |
| Security hardening | Vendor hardening guides and recognised benchmarks. Explain *why* each setting matters. |
| Usage examples | Execute every example in a lab before marking the entry `lab-tested`. Use placeholder targets. |
| Enterprise considerations | Official architecture, scaling, and high-availability documentation. |
| Troubleshooting | Official documentation, issue trackers, and your own lab results. |
| Alternatives | Link to other entries in this knowledge base where they exist. |
| Tested versions | Exact version strings you executed, with platform. |

## Writing style

- Use clear, neutral, technical language and UK or US spelling consistently within a page.
- State limitations as plainly as capabilities.
- Prefer tables for structured facts and numbered lists for procedures.
- Use admonitions for safety information:

```markdown
!!! warning "Authorised use only"
    Explain the risk here.
```

## Commands and examples

- Put commands in fenced code blocks with a language (`bash`, `powershell`, `yaml`, …).
- Show the prompt context (for example, whether `sudo` is required) in surrounding text.
- Use documentation-reserved placeholders only:
    - IPv4: `192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24` (RFC 5737)
    - IPv6: `2001:db8::/32` (RFC 3849)
    - Domains: `example.com`, `example.org`, `example.net` (RFC 2606)
- Never include real credentials, API keys, tokens, private keys, or internal infrastructure
  details. Use clearly fake placeholders such as `<YOUR_API_KEY>`.

## Offensive security tools

Entries for tools capable of attacking systems (scanners, exploitation frameworks, credential
attacks, interception tools) must:

1. Begin with an **Authorised use only** warning admonition.
2. Use examples that target only lab systems or documentation-reserved addresses.
3. Describe legal and authorisation prerequisites in the *Enterprise deployment
   considerations* section (rules of engagement, scope, written approval).
4. Avoid step-by-step guidance aimed at evading detection or attacking third parties.

## Third-party material

Do not copy vendor documentation, screenshots, or logos unless the licence clearly permits
redistribution; link to the original instead. Short quotations must be attributed.

## File layout and naming

- One file per tool: `docs/tools/<category>/<tool-slug>.md`, lowercase, hyphen-separated.
- Add the page to the `nav` in `mkdocs.yml` under its category and link it from the
  category's index page.
- Start from [`templates/tool-entry.md`](tool-template.md).
