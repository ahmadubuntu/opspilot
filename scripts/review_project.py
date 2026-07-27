#!/usr/bin/env python3

from __future__ import annotations

import difflib
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IGNORE = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "build",
    "dist",
}


def should_ignore(path: Path) -> bool:
    return any(part in IGNORE for part in path.parts)


def canonical_name(path: Path) -> str:
    """
    security-model3.md
    ->
    security-model.md
    """

    return re.sub(r"(\d+)(\.[^.]+)$", r"\2", path.name)


groups = defaultdict(list)

all_files = []

for f in ROOT.rglob("*"):

    if not f.is_file():
        continue

    if should_ignore(f):
        continue

    all_files.append(f)

    key = (
        str(f.parent.relative_to(ROOT)),
        canonical_name(f),
    )

    groups[key].append(f)

report = []

report.append("# Project Review\n")

report.append("## Files\n")

for f in sorted(all_files):
    report.append(f"- {f.relative_to(ROOT)}")

report.append("\n")

for (_, name), files in sorted(groups.items()):

    if len(files) == 1:
        continue

    report.append(f"# {name}\n")

    files = sorted(files)

    report.append("Versions:\n")

    for f in files:
        report.append(f"- {f.relative_to(ROOT)}")

    report.append("")

    for a, b in zip(files, files[1:]):

        report.append(
            f"## Diff\n{a.name} -> {b.name}\n"
        )

        try:
            old = a.read_text().splitlines()
            new = b.read_text().splitlines()

            diff = difflib.unified_diff(
                old,
                new,
                fromfile=a.name,
                tofile=b.name,
                lineterm="",
            )

            report.append("```diff")

            report.extend(diff)

            report.append("```")

        except Exception as ex:
            report.append(str(ex))

        report.append("")

output = ROOT / "reports"

output.mkdir(exist_ok=True)

report_file = output / "project_review.md"

report_file.write_text("\n".join(report))

print(report_file)
