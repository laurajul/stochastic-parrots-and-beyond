"""Tests for the LAION sample: its generated fragments and its public record."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SAMPLE_DIR = Path(__file__).resolve().parents[1] / "assets" / "cases" / "laion-sample"
SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "build_laion_sample.py"


@pytest.fixture(scope="module")
def builder():
    spec = importlib.util.spec_from_file_location("build_laion_sample", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def sample() -> dict:
    return json.loads((SAMPLE_DIR / "sample.json").read_text(encoding="utf-8"))


def test_fragments_match_sample(builder, sample):
    """A fragment that differs from sample.json means: run the build script."""
    for name, text in builder.render(sample).items():
        assert (SAMPLE_DIR / name).read_text(encoding="utf-8") == text, name


def test_public_urls_use_https(sample):
    for rec in sample["entries"] + sample["flagged"]:
        assert rec.get("url", "https://").startswith("https://"), rec["key"]


def test_withheld_records_show_no_url(sample):
    for rec in sample["flagged"]:
        if rec["image"] != "live":
            assert "url" not in rec, rec["key"]
            assert rec["withheld"], rec["key"]


def test_slide_record_shows_only_the_read_aloud_fields(builder, sample):
    text = builder.render(sample)["entry-example.html"]
    assert "original_width" not in text
    assert "&quot;key&quot;" not in text and '"key"' not in text
