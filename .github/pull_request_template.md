## Summary

<!-- What does this change and why? -->

## Type of change

- [ ] New tool entry
- [ ] Update or correction to existing content
- [ ] Site, tooling, or workflow change
- [ ] Governance or documentation standards

## Checklist

- [ ] `python -m mkdocs build --strict` passes
- [ ] `python scripts/check_links.py` passes
- [ ] `python scripts/validate_entries.py` passes
- [ ] `python scripts/check_quality.py` passes
- [ ] `python scripts/check_lab_evidence.py` passes
- [ ] `python scripts/scan_secrets.py` passes
- [ ] `python -m pytest` passes
- [ ] New pages are added to `nav` in `mkdocs.yml`
- [ ] Factual claims cite official sources; verification notes record the check date
- [ ] New or re-reviewed entries have a row in `docs/contributing/quality-review-log.md`
- [ ] Status raised to `lab-tested` or above only with linked, sanitised lab evidence records
- [ ] No credentials, private keys, internal hostnames, or private network details
- [ ] Offensive-tool content includes an *Authorised use only* warning and lab-only examples
- [ ] Verification status is supported by the evidence below
- [ ] `CHANGELOG.md` updated (for notable changes)

## Verification evidence

<!-- Versions tested, platform, date, and what was executed. Write "Not tested" if none. -->
