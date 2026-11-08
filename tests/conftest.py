"""pytest configuration: put the repository root (and scripts/) on sys.path.

Tests import the library as ``src`` (``from src.schema_parser import ...``) and the
reproduction script as ``reproduce_tables``.  No /data absolute imports are required for the
parser / normalization / metrics tests; dataset and reproducibility tests skip (or fail
loudly where noted) if the on-disk artefacts are absent.
"""
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "scripts"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return ROOT
