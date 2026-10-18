"""Build the public metadata of the LAION sample.

Reads the raw sample (JSON files named by key) from the folder given as the
first argument. Writes `assets/cases/laion-sample/sample.json`. The file holds
the summary numbers of the whole sample, the full LAION record of a small
selection, and the full record of every image that the LAION label flags.
The repository stores no image: the pages load the selected images live from
their original URLs. The raw folder stays outside Git.

Run: `uv run python scripts/build_laion_sample.py RAW_DIR`
"""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "cases" / "laion-sample"

# Entries with an HTTPS URL that loaded on 2026-10-18. No face, no private name.
SELECTED = [324, 1328, 2326, 3256, 1322, 3220, 3250, 3246]
# Flagged entries that join the slide strip. The label is wrong for both.
SELECTED_FLAGGED = [3212, 6320]
# Flagged entries whose source did not load on 2026-10-18.
NOT_LOADING = {4325}
# Flagged entries that show private people. The record stays, the URL goes.
WITHHELD = {
    3217: (
        "Photo of two adults at a fitness event, with faces visible. "
        "The people are private individuals, not models. "
        "The course shows no photo of such people."
    )
}


def main(raw: Path) -> None:
    metas = [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(raw.glob("*.json"), key=lambda p: int(p.stem))
    ]
    scores = [m["similarity"] for m in metas]
    summary = {
        "entries": len(metas),
        "similarity_min": round(min(scores), 3),
        "similarity_max": round(max(scores), 3),
        "similarity_median": round(statistics.median(scores), 3),
        "license_unknown": sum(m["LICENSE"] in ("?", "") for m in metas),
        "flagged_nsfw_or_unsure": sum(m["NSFW"] != "UNLIKELY" for m in metas),
    }
    by_key = {m["key"]: m for m in metas}

    def record(m: dict) -> dict:
        return dict(m)

    entries = []
    for key in SELECTED + SELECTED_FLAGGED:
        m = by_key[key]
        assert m["url"].startswith("https://")
        entries.append(record(m))
    flagged = []
    for m in metas:
        if m["NSFW"] != "UNLIKELY":
            rec = record(m)
            if m["key"] in WITHHELD:
                del rec["url"]
                rec["withheld"] = WITHHELD[m["key"]]
            flagged.append(
                {**rec, "loads": m["key"] not in NOT_LOADING | WITHHELD.keys()}
            )
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "sample.json").write_text(
        json.dumps(
            {"summary": summary, "entries": entries, "flagged": flagged},
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
        encoding="utf-8",
    )
    print(summary)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
