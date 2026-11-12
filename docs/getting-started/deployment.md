# GitHub Pages Deployment

The site is published to
<https://riotphoenix.github.io/cybersecurity-knowledge-base/> by the
`.github/workflows/deploy-pages.yml` workflow using GitHub's official Pages Actions.

## How it works

1. A push to `main` (or a manual *Run workflow*) starts the **Deploy documentation** workflow.
2. The **build** job installs pinned dependencies, runs `mkdocs build --strict`, and uploads
   the `site/` directory as a Pages artifact.
3. The **deploy** job publishes the artifact to the `github-pages` environment.

Pull requests never deploy. They run the separate **Documentation checks** workflow, which
has read-only permissions.

## One-time repository settings

A repository administrator must configure these once:

| Setting | Location | Value |
|---|---|---|
| Pages source | *Settings → Pages → Build and deployment → Source* | **GitHub Actions** |
| Environment branch rule | *Settings → Environments → github-pages* | Deployment branches: `main` only (created automatically on first deploy; verify afterwards) |
| Workflow permissions | *Settings → Actions → General → Workflow permissions* | **Read repository contents** (workflows request extra permissions explicitly) |
| Private vulnerability reporting | *Settings → Security → Private vulnerability reporting* | **Enabled** (used by `SECURITY.md`) |

## Base path

The site is served from the `/cybersecurity-knowledge-base/` sub-path. `site_url` in
`mkdocs.yml` is set accordingly and MkDocs generates relative links, so the same build works
both locally and on GitHub Pages.

## Verifying a deployment

1. Open the **Actions** tab and confirm both jobs of **Deploy documentation** succeeded.
2. Visit the deployment URL shown on the deploy job.
3. Check the homepage, search, and one deep page (for example a tool category).

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Deploy job fails with a permissions or environment error | Pages source is not set to **GitHub Actions**, or the environment branch rule excludes `main`. |
| Site loads without styling | `site_url` does not match the Pages URL. |
| 404 at the Pages URL right after the first deploy | Propagation delay; wait a few minutes and retry. |
