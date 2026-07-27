#!/usr/bin/env python3

from __future__ import annotations

import difflib
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".idea",
    ".vscode",
    "build",
    "dist",
    "node_modules",
}

TEXT_EXTENSIONS = {
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
    ".py",
}


def ignored(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def canonical_name(path: Path) -> str:
    """
    security-model3.md -> security-model.md
    plugin2.py -> plugin.py
    """

    stem = re.sub(r"\d+$", "", path.stem)
    return str(path.with_name(stem + path.suffix).relative_to(ROOT))


def read_text(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return []


def print_inventory(files: list[Path]):
    print("=" * 80)
    print("PROJECT FILES")
    print("=" * 80)

    for f in sorted(files):
        print(f.relative_to(ROOT))


def print_duplicates(groups):
    print()
    print("=" * 80)
    print("VERSIONED FILES")
    print("=" * 80)

    found = False

    for key in sorted(groups):
        versions = sorted(groups[key])

        if len(versions) < 2:
            continue

        found = True

        print()
        print(key)

        for v in versions:
            print("   ", v.relative_to(ROOT))

    if not found:
        print("No versioned files found.")


def print_diffs(groups):
    print()
    print("=" * 80)
    print("DIFFS")
    print("=" * 80)

    for key in sorted(groups):
        versions = sorted(groups[key])

        if len(versions) < 2:
            continue

        print()
        print("#", key)

        for old, new in zip(versions, versions[1:]):

            old_lines = read_text(old)
            new_lines = read_text(new)

            diff = list(
                difflib.unified_diff(
                    old_lines,
                    new_lines,
                    fromfile=str(old.relative_to(ROOT)),
                    tofile=str(new.relative_to(ROOT)),
                    lineterm="",
                )
            )

            print()
            print(f"---- {old.name} -> {new.name}")

            if not diff:
                print("No differences.")
                continue

            for line in diff[:250]:
                print(line)

            if len(diff) > 250:
                print("... diff truncated ...")


def main():

    files = []

    for p in ROOT.rglob("*"):

        if p.is_dir():
            continue

        if ignored(p):
            continue

        if p.suffix not in TEXT_EXTENSIONS:
            continue

        files.append(p)

    groups = defaultdict(list)

    for f in files:
        groups[canonical_name(f)].append(f)

    print_inventory(files)
    print_duplicates(groups)
    print_diffs(groups)


if __name__ == "__main__":
    main()
