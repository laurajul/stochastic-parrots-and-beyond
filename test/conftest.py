from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def editions_data() -> dict:
    with (REPO_ROOT / "data" / "editions.yml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def site_sources() -> list[Path]:
    """Return every page that Quarto renders into the website."""
    pages = [REPO_ROOT / "index.qmd"]
    for folder in ("contents", "documentation"):
        pages += sorted((REPO_ROOT / folder).rglob("*.qmd"))
    return [p for p in pages if p.exists()]


def tracked_files() -> list[Path] | None:
    """Return the files that Git tracks, or None outside a Git checkout."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=True,
        ).stdout
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
    return [REPO_ROOT / p for p in out.decode().split("\0") if p]
