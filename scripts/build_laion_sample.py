"""Build the public metadata of the LAION sample.

Reads the raw sample (JSON files named by key) from the folder given as the
first argument. Writes `assets/cases/laion-sample/sample.json`. The file holds
the summary numbers of the whole sample, the full LAION record of a small
selection, and the full record of every image that the LAION label flags.
The repository stores no image: the pages load the selected images live from
their original URLs. The raw folder stays outside Git.

The script then writes the HTML fragments that the gallery page and the slides
include, all from `sample.json`. Without an argument, it writes only the
fragments.

Run: `uv run python scripts/build_laion_sample.py [RAW_DIR]`
"""

from __future__ import annotations

import html
import json
import statistics
import sys
import textwrap
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "assets" / "cases" / "laion-sample"

# Entries with an HTTPS URL that loaded on 2026-10-18. No face, no private name.
SELECTED = [324, 1328, 2326, 3256, 1322, 3220, 3250, 3246]
# Flagged entries that join the slide strip. The label is wrong for both.
SELECTED_FLAGGED = [3212, 6320]
# Flagged entries whose source did not load on 2026-10-18. The record drops the URL.
NOT_LOADING = {4325: "The source no longer loads. The record shows no URL."}
# Flagged entries that show private people. The record stays, the URL goes.
WITHHELD = {
    3217: (
        "Photo of two adults at a fitness event, with faces visible. "
        "The people are private individuals, not models. "
        "The course shows no photo of such people."
    )
}
# Slides: the strip shows four harmless entries and two flagged ones.
STRIP = [324, 3256, 1322, 3220]
STRIP_FLAGGED = [3212, 6320]
# The slide "One entry, in full" shows one of the strip entries. Drawn at random
# from STRIP on 2026-10-19.
EXAMPLE = 3256
# The fields that the speaker notes read aloud.
SLIDE_FIELDS = ("url", "NSFW", "similarity", "LICENSE", "caption")
CAPTION_MAX = 60
GONE_LABEL = {
    "withheld": "Image withheld: private people",
    "gone": "Source no longer loads",
}


def build_sample(raw: Path) -> dict:
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
            image = "live"
            if m["key"] in WITHHELD:
                del rec["url"]
                rec["withheld"] = WITHHELD[m["key"]]
                image = "withheld"
            elif m["key"] in NOT_LOADING:
                del rec["url"]
                rec["withheld"] = NOT_LOADING[m["key"]]
                image = "gone"
            flagged.append({**rec, "image": image})
    return {"summary": summary, "entries": entries, "flagged": flagged}


def esc(text: object) -> str:
    return html.escape(str(text), quote=True)


def dump(rec: dict, fields: tuple[str, ...] | None = None) -> str:
    """The record as the pages show it: JSON, without the build-only fields."""
    shown = {k: v for k, v in rec.items() if k != "image"}
    if fields:
        shown = {k: v for k, v in shown.items() if k in fields}
    return html.escape(json.dumps(shown, ensure_ascii=False, indent=2), quote=False)


def slot(rec: dict) -> str:
    """The image cell: a grey placeholder until the visitor loads the image."""
    image = rec.get("image", "live")
    if image != "live":
        return f'<div class="slot gone" role="img" aria-label="{GONE_LABEL[image]}">{GONE_LABEL[image]}</div>'
    return (
        f'<div class="slot"><img data-src="{esc(rec["url"])}" alt="{esc(rec["caption"])}" '
        'referrerpolicy="no-referrer"><span class="ph">Image not loaded</span></div>'
    )


def table(recs: list[dict]) -> str:
    rows = [
        f"<tr>\n<td>{slot(r)}</td>\n<td><pre>{dump(r)}</pre></td>\n</tr>" for r in recs
    ]
    return '<table class="laion-table">\n' + "\n".join(rows) + "\n</table>\n"


def figure(rec: dict, label: bool = False) -> str:
    short = textwrap.shorten(rec["caption"], CAPTION_MAX, placeholder="…")
    note = (
        f'<br><span class="fragment"><strong>LAION label: {esc(rec["NSFW"])}</strong></span>'
        if label
        else ""
    )
    return (
        f'<figure>\n<img data-src="{esc(rec["url"])}" alt="{esc(rec["caption"])}" '
        f'referrerpolicy="no-referrer">\n<figcaption>{esc(short)}{note}</figcaption>\n</figure>'
    )


def entry(rec: dict) -> str:
    return (
        f'<img data-src="{esc(rec["url"])}" alt="{esc(rec["caption"])}" '
        f'referrerpolicy="no-referrer">\n<pre>{dump(rec, SLIDE_FIELDS)}</pre>\n'
    )


def render(sample: dict) -> dict[str, str]:
    by_key = {e["key"]: e for e in sample["entries"]}
    harmless = [e for e in sample["entries"] if e["NSFW"] == "UNLIKELY"]
    strip = [figure(by_key[k]) for k in STRIP]
    strip += [figure(by_key[k], label=True) for k in STRIP_FLAGGED]
    return {
        "gallery.html": table(harmless),
        "flagged.html": table(sample["flagged"]),
        "strip.html": "\n".join(strip) + "\n",
        "entry-example.html": entry(by_key[EXAMPLE]),
        "entry-flagged.html": entry(by_key[STRIP_FLAGGED[0]]),
    }


def main(raw: Path | None) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    if raw:
        sample = build_sample(raw)
        (OUT / "sample.json").write_text(
            json.dumps(sample, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(sample["summary"])
    else:
        sample = json.loads((OUT / "sample.json").read_text(encoding="utf-8"))
    for name, text in render(sample).items():
        (OUT / name).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main(Path(sys.argv[1]) if len(sys.argv) > 1 else None)
