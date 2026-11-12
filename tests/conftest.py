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
