"""Tests for data/editions.yml, the single source of edition facts."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import pytest

STATUSES = {"planned", "confirmed", "delivered"}
PROGRAM_STATUSES = {"proposed", "approved", "tbc"}
REGISTRATION_STATUSES = {"open", "closed", "upcoming", None}

# A confirmed or delivered edition must publish these facts.
REQUIRED_WHEN_CONFIRMED = (
    "date",
    "start",
    "end",
    "venue",
    "address",
    "map_url",
    "organizer",
    "contact",
    "official_url",
)

# These values identify one edition. Two editions never share them, so an
# equal value means that someone copied it from another edition.
EDITION_SPECIFIC = (
    "date",
    "registration_opens",
    "registration_deadline",
    "official_url",
    "evaluation_url",
    "assessment_deadline",
)

TIME = re.compile(r"^\d{2}:\d{2}$")


def test_featured_edition_exists(editions_data):
    assert editions_data["featured_edition"] in editions_data["editions"]


def test_all_editions_have_the_same_keys(editions_data):
    keys = {eid: set(e) for eid, e in editions_data["editions"].items()}
    union = set().union(*keys.values())
    for eid, k in keys.items():
        assert k == union, f"{eid} lacks {sorted(union - k)}. Add them as null."


@pytest.mark.parametrize(
    "field", ["status", "detailed_program_status", "registration_status"]
)
def test_vocabularies(editions_data, field):
    allowed = {
        "status": STATUSES,
        "detailed_program_status": PROGRAM_STATUSES,
        "registration_status": REGISTRATION_STATUSES,
    }[field]
    for eid, e in editions_data["editions"].items():
        assert e[field] in allowed, f"{eid}.{field} = {e[field]!r}"


def test_dates_and_times_are_valid(editions_data):
    for eid, e in editions_data["editions"].items():
        for key in ("date", "assessment_deadline"):
            if e[key] is not None:
                date.fromisoformat(str(e[key]))
        for key in ("start", "end"):
            if e[key] is not None:
                assert TIME.match(str(e[key])), f"{eid}.{key} must be HH:MM"
        if e["start"] and e["end"]:
            assert e["start"] < e["end"], f"{eid}: start must come before end"
        for key in ("registration_opens", "registration_deadline"):
            if e[key] is not None:
                ts = datetime.fromisoformat(str(e[key]))
                assert ts.tzinfo is not None, f"{eid}.{key} needs a UTC offset"


def test_urls_use_https(editions_data):
    for eid, e in editions_data["editions"].items():
        for key, value in e.items():
            if key.endswith("_url") and value is not None:
                assert str(value).startswith("https://"), f"{eid}.{key}"


def test_confirmed_editions_publish_the_essential_facts(editions_data):
    for eid, e in editions_data["editions"].items():
        if e["status"] in {"confirmed", "delivered"}:
            missing = [k for k in REQUIRED_WHEN_CONFIRMED if e[k] is None]
            assert not missing, f"{eid} is {e['status']} but lacks {missing}"


def test_no_edition_copies_another_edition(editions_data):
    eds = editions_data["editions"]
    for key in EDITION_SPECIFIC:
        seen: dict[str, str] = {}
        for eid, e in eds.items():
            value = e[key]
            if value is None:
                continue
            assert str(value) not in seen, (
                f"{eid}.{key} repeats the value of {seen[str(value)]}. "
                "Use null until a public source confirms the value."
            )
            seen[str(value)] = eid


def test_planned_edition_has_no_confirmed_logistics(editions_data):
    for eid, e in editions_data["editions"].items():
        if e["status"] == "planned":
            assert e["detailed_program_status"] != "approved", eid
            assert e["evaluation_url"] is None, eid


def test_each_edition_has_a_page_and_each_page_an_edition(
    editions_data, repo_root: Path
):
    pages = {p.stem for p in (repo_root / "contents" / "editions").glob("*.qmd")}
    ids = set(editions_data["editions"])
    assert ids == pages, (
        f"pages without data: {pages - ids}; data without page: {ids - pages}"
    )
