import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture(scope="session")
def root() -> Path:
    return ROOT


@pytest.fixture(scope="session")
def mkdocs_config() -> dict:
    return yaml.safe_load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"))


VALID_RECORD_BODY = """
# Lab evidence: {tool} {version} on Fedora 44

## Environment

Single virtual machine on an isolated lab network (192.0.2.0/24), host name lab01.example.

## Hardware or virtual resources

VM with 2 vCPU, 4 GiB RAM, 40 GB disk, one virtio NIC.

## Installation method

Distribution package, following the entry's Fedora installation section.

## Configuration summary

Defaults, except the capture interface.

## Test objective

Show that the documented installation and verification steps work.

## Test procedure

1. Installed the package.
2. Ran the verification command from the entry.

## Expected result

The tool reports version {version}.

## Actual observed result

The tool reported version {version}.

## Outcome

{outcome}: the documented steps completed as described.

## Deviations from the documented procedure

None.

## Troubleshooting performed

None.

## Known limitations

Installation and version check only; no other features were exercised.

## Supporting evidence

Sanitised command output retained privately by the tester.
"""


@pytest.fixture
def lab_record():
    """Factory: write a valid lab evidence record (and index) into <docs_root>/lab-evidence/."""
    def make(docs_root, *, entry="network-security/sample.md", tool="Wireshark",
             version="4.6.8", outcome="pass", environment_type="lab", index=True,
             name="sample-2026-11-12.md", body=None, **meta):
        lab = docs_root / "lab-evidence"
        lab.mkdir(parents=True, exist_ok=True)
        front = {
            "record_type": "lab-evidence", "tool": tool, "tool_version": version,
            "entry": entry, "test_date": "2026-11-12", "environment_type": environment_type,
            "operating_system": "Fedora 44 (x86_64)",
            "installation_method": "Distribution package", "outcome": outcome,
            "tester": "anonymous", "sanitised": True,
        }
        front.update(meta)
        lines = ["---"]
        for k, v in front.items():
            if v is None:
                continue
            if isinstance(v, bool):
                v = "true" if v else "false"
            elif k == "test_date":
                v = str(v)
            else:
                v = f'"{v}"'
            lines.append(f"{k}: {v}")
        lines.append("---")
        text = "\n".join(lines) + (body if body is not None else
                                   VALID_RECORD_BODY.format(tool=tool, version=version,
                                                            outcome=outcome))
        p = lab / name
        p.write_text(text)
        idx = lab / "index.md"
        existing = idx.read_text() if idx.exists() else "# Lab Evidence Records\n\n"
        if index and f"({name})" not in existing:
            idx.write_text(existing + f"- [{name}]({name})\n")
        elif not idx.exists():
            idx.write_text(existing)
        return p
    return make
