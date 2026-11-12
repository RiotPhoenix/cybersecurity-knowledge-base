# Contributing

Thank you for your interest in improving the Cybersecurity Knowledge Base.

## Before you start

- Read the [authoring standards](docs/contributing/authoring-standards.md) and
  [verification statuses](docs/contributing/verification-statuses.md).
- For new tools, open a **New tool entry** issue first to avoid duplicated effort.

## Making a change

1. Fork the repository and create a branch from `main` (for example `entry/<tool-slug>` or
   `fix/<short-description>`).
2. Set up the environment ([Local Development](docs/getting-started/local-development.md)).
3. For a new tool, copy [`templates/tool-entry.md`](templates/tool-entry.md) to
   `docs/tools/<category>/<tool-slug>.md`, add it to `nav` in `mkdocs.yml`, link it from
   the category index, and record its review in the
   [quality review log](docs/contributing/quality-review-log.md) (see the
   [quality framework](docs/contributing/quality-framework.md)).
4. Run all checks:

   ```bash
   python -m mkdocs build --strict
   python scripts/check_links.py
   python scripts/scan_secrets.py
   python scripts/validate_entries.py
   python scripts/check_quality.py
   python -m pytest
   ```

5. Open a pull request and complete the checklist.

## Commit messages

Use short, imperative subject lines (≤ 72 characters), optionally prefixed with a scope:

```text
docs(network-security): add entry for <tool>
fix(links): correct anchor in deployment guide
ci: pin action versions
```

## Content rules

- Cite official sources. Mark untested steps as untested.
- Never include credentials, private keys, internal hostnames, or private network details.
- Offensive tools require an *Authorised use only* warning and lab-only examples.
- Do not raise verification status without recorded evidence.
- Do not copy third-party documentation, screenshots, or logos unless licensing permits.

## Licensing of contributions

By contributing, you agree that documentation contributions are licensed under
[CC BY 4.0](LICENSE-DOCS.md) and code contributions under the [MIT licence](LICENSE).

## Conduct

Be respectful and constructive. Critique content, not people. Maintainers may close
contributions that are abusive, off-topic, or promote unauthorised activity.
