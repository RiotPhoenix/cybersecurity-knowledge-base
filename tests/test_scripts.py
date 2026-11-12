"""Behaviour of the public validation scripts."""
import check_links
import scan_secrets


def test_secret_scanner_detects_token():
    fake = "gh" + "p_" + "A" * 36           # assembled at runtime; not a literal secret
    assert scan_secrets.scan_text("f", f"token = {fake}")


def test_secret_scanner_detects_private_key_header():
    header = "-----BEGIN " + "OPENSSH PRIVATE KEY-----"
    assert scan_secrets.scan_text("f", header)


def test_secret_scanner_detects_credential_url():
    assert scan_secrets.scan_text("f", "https://" + "admin:hunter2pass" + "@db.internal")


def test_secret_scanner_allows_placeholders():
    assert not scan_secrets.scan_text("f", 'api_key = "<YOUR_API_KEY>"')
    assert not scan_secrets.scan_text("f", "https://" + "<user>:<password>" + "@example.com")


def test_secret_scanner_sensitive_filenames():
    rx = scan_secrets.SENSITIVE_FILENAMES
    assert rx.search(".env") and rx.search("keys/id_ed25519") and rx.search("a/b.pem")
    assert not rx.search("docs/index.md")


def test_slugify_matches_markdown_toc():
    assert check_links.slugify("Validate before opening a pull request") == \
        "validate-before-opening-a-pull-request"
    assert check_links.slugify("ADR 0001: Static site") == "adr-0001-static-site"


def test_repository_links_clean():
    errs = [e for f in check_links.markdown_files() for e in check_links.check(f)]
    assert errs == []


def test_repository_has_no_secrets():
    assert scan_secrets.main(["scan_secrets.py"]) == 0
