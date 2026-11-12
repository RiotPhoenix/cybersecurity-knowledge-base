# ADR 0001: Static documentation site with MkDocs and GitHub Pages

- **Status:** Accepted
- **Date:** 2026-11-11

## Context

The project needs a public, searchable, low-maintenance documentation website sourced from
Markdown in Git. It must be reproducible by any contributor, secure, and free to host.
Server-side components, databases, and authentication are unnecessary for a read-only
reference.

## Decision

- Use **MkDocs 1.6** with the **standard `mkdocs` theme** and its built-in search plugin.
- Apply project styling through a single CSS layer (`docs/assets/css/riotphoenix.css`)
  built on CSS custom properties, without forking theme templates.
- Disable the theme's CDN-loaded highlight.js and use **Pygments** with a local stylesheet,
  so the site loads no third-party assets.
- Build and deploy with **GitHub Actions** and the **official GitHub Pages actions**
  (artifact-based deployment, not a `gh-pages` branch).
- Pin Python dependencies fully in `requirements.txt` / `requirements-dev.txt`, and pin
  GitHub Actions to full commit SHAs.
- Build in **strict mode** with MkDocs link, anchor, and navigation validation enabled.

## Consequences

- Content is portable Markdown with YAML front matter; migrating to another static
  generator would mainly require navigation and theme changes, not content rewrites.
- The standard theme has fewer features than third-party themes (no tabs or content tabs),
  which keeps the dependency surface small. A theme change would warrant a new ADR.
- Pinned dependencies require periodic, deliberate updates (documented in the local
  development guide).
