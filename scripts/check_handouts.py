#!/usr/bin/env python3
"""Check that every generated handout file is current.

``scripts/build_handouts.py`` renders each handout source in
``contents/handouts/`` to a PDF and, if the front matter asks for it, to a
DOCX. CI renders HTML only, so the generated files are committed. This check
fails when a generated file is missing, or when its last commit is older than
the last commit of its source or of an asset that the source embeds.

Run it in a clone with the full history: ``git log -- <path>`` needs it.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_handouts import FORMATS, OUTPUT_DIR, REPO_ROOT, SOURCE_DIR, targets

ASSET_REF = re.compile(r"\]\(([^)\s]+\.(?:svg|png|jpg|jpeg))[^)]*\)")


def last_commit(path: Path) -> int | None:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", str(path.relative_to(REPO_ROOT))],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()
    return int(out) if out else None


def dependencies(source: Path) -> list[Path]:
    deps = [source]
    for ref in ASSET_REF.findall(source.read_text(encoding="utf-8")):
        if ref.startswith(("http://", "https://")):
            continue
        dep = (source.parent / ref).resolve()
        if dep.exists():
            deps.append(dep)
    return deps


def main() -> int:
    errors: list[str] = []
    for source in sorted(SOURCE_DIR.glob("*.qmd")):
        if source.stem == "index":
            continue
        newest_input = max((last_commit(d) or 0) for d in dependencies(source))
        for fmt in targets(source):
            output = OUTPUT_DIR / f"{source.stem}.{FORMATS[fmt]}"
            rel = output.relative_to(REPO_ROOT)
            if not output.exists():
                errors.append(f"{rel} is missing. Run npm run handouts:build.")
                continue
            built = last_commit(output)
            if built is None:
                errors.append(f"{rel} is not committed.")
            elif built < newest_input:
                errors.append(
                    f"{rel} is older than its sources. "
                    f"Run npm run handouts:build -- {source.stem} and commit the result."
                )
    for error in errors:
        print(f"::error::{error}")
    if not errors:
        print("Every handout file is current.")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
