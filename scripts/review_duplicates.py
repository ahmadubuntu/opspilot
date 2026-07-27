#!/usr/bin/env python3

from pathlib import Path
import difflib
import re
from datetime import datetime


ROOT = Path(".")
OUTPUT = Path("docs/reviews/file-version-review.md")


IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    "node_modules",
    ".cache",
}


VERSION_PATTERN = re.compile(
    r"""
    (?P<base>
        .+?
    )
    (?:
        [-_]?v?\d+
    )?
    (?P<ext>
        \.[^.]+$
    )
    """,
    re.VERBOSE,
)


def normalize_filename(path: Path):
    """
    Convert:
        security-model3.md
        security-model2.md
        security-model.md

    into:
        security-model.md
    """

    name = path.name

    match = VERSION_PATTERN.match(name)

    if not match:
        return name

    return (
        match.group("base")
        + match.group("ext")
    )


def collect_files():

    files = []

    for p in ROOT.rglob("*"):

        if not p.is_file():
            continue

        if any(
            part in IGNORE_DIRS
            for part in p.parts
        ):
            continue

        files.append(p)

    return files


def group_versions(files):

    groups = {}

    for file in files:

        key = (
            str(file.parent)
            + "/"
            + normalize_filename(file)
        )

        groups.setdefault(key, []).append(file)

    return {
        k: sorted(v)
        for k, v in groups.items()
        if len(v) > 1
    }


def read_file(path):

    try:
        return path.read_text(
            encoding="utf-8"
        ).splitlines()

    except Exception:

        return [
            "[binary or unreadable file]"
        ]


def make_diff(a, b):

    return "\n".join(
        difflib.unified_diff(
            read_file(a),
            read_file(b),
            fromfile=str(a),
            tofile=str(b),
            lineterm=""
        )
    )


def generate_report(groups):

    lines = []

    lines.append(
        "# OpsPilot File Version Review"
    )

    lines.append("")

    lines.append(
        f"Generated: {datetime.now()}"
    )

    lines.append("")

    lines.append(
        f"Duplicate groups found: {len(groups)}"
    )

    lines.append("\n---\n")


    for name, files in groups.items():

        lines.append(
            f"## {name}"
        )

        lines.append("")

        for f in files:

            size = len(read_file(f))

            lines.append(
                f"- `{f}` ({size} lines)"
            )

        lines.append("")

        if len(files) >= 2:

            latest = files[-1]

            previous = files[-2]


            lines.append(
                "### Diff: previous → latest"
            )

            lines.append("")

            lines.append(
                "```diff"
            )

            lines.append(
                make_diff(
                    previous,
                    latest
                )
            )

            lines.append(
                "```"
            )

        lines.append("\n---\n")


    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    OUTPUT.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


def main():

    files = collect_files()

    groups = group_versions(files)

    generate_report(groups)

    print(
        f"Report created: {OUTPUT}"
    )

    print(
        f"Groups: {len(groups)}"
    )


if __name__ == "__main__":
    main()
