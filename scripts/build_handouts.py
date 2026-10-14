#!/usr/bin/env python3
"""Build the printable and editable handout files.

Each handout source is a page in ``contents/handouts/``. The website shows it
as accessible HTML. This script renders the same source to a tagged PDF with
Typst and, when the front matter asks for it, to DOCX. It then moves the files
to ``assets/handouts/``, where the site links them.

CI renders HTML only, so the generated files are committed. The
``check-handouts`` job in ``.github/workflows/quarto-publish.yml`` fails when a
generated file is older than its source.

Usage:
    uv run python scripts/build_handouts.py            # all handouts
    uv run python scripts/build_handouts.py NAME ...   # selected handouts
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = REPO_ROOT / "contents" / "handouts"
OUTPUT_DIR = REPO_ROOT / "assets" / "handouts"
SITE_DIR = REPO_ROOT / "_site" / "contents" / "handouts"

# Front-matter format key -> file extension of the rendered output.
FORMATS = {"typst": "pdf", "docx": "docx"}


def front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    data = yaml.safe_load(text[3:end])
    return data if isinstance(data, dict) else {}


def targets(path: Path) -> list[str]:
    fmt = front_matter(path).get("format", {})
    if isinstance(fmt, str):
        fmt = {fmt: None}
    return [key for key in FORMATS if key in fmt]


def render(path: Path, fmt: str) -> Path:
    subprocess.run(
        ["quarto", "render", str(path.relative_to(REPO_ROOT)), "--to", fmt],
        cwd=REPO_ROOT,
        check=True,
    )
    built = SITE_DIR / f"{path.stem}.{FORMATS[fmt]}"
    if not built.exists():
        sys.exit(f"Quarto did not write {built.relative_to(REPO_ROOT)}.")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final = OUTPUT_DIR / built.name
    shutil.move(built, final)
    return final


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("names", nargs="*", help="Handout file stems to build.")
    args = parser.parse_args()

    sources = sorted(p for p in SOURCE_DIR.glob("*.qmd") if p.stem != "index")
    if args.names:
        wanted = set(args.names)
        sources = [p for p in sources if p.stem in wanted]
        missing = wanted - {p.stem for p in sources}
        if missing:
            sys.exit(f"Unknown handout: {', '.join(sorted(missing))}")

    for source in sources:
        for fmt in targets(source):
            final = render(source, fmt)
            print(f"{source.relative_to(REPO_ROOT)} -> {final.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
