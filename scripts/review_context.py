#!/usr/bin/env python3

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

IGNORE = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    ".mypy_cache",
    "node_modules",
    "dist",
    "build",
}

TEXT = {
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".toml",
    ".json",
}


# ---------------------------------------------------------


def ignored(path: Path) -> bool:
    return any(part in IGNORE for part in path.parts)


def version_key(path: Path) -> str:
    """
    runtime3.md -> runtime.md
    plugin2.py -> plugin.py
    """

    stem = re.sub(r"\d+$", "", path.stem)
    return str(path.with_name(stem + path.suffix).relative_to(ROOT))


def sha(path: Path) -> str:
    h = hashlib.sha1()
    h.update(path.read_bytes())
    return h.hexdigest()[:8]


# ---------------------------------------------------------


files: list[Path] = []

for f in ROOT.rglob("*"):

    if f.is_dir():
        continue

    if ignored(f):
        continue

    if f.suffix not in TEXT:
        continue

    files.append(f)

groups = defaultdict(list)

for f in files:
    groups[version_key(f)].append(f)


# ---------------------------------------------------------

print("=" * 80)
print("OpsPilot Review Context")
print("=" * 80)

print()
print("Project Root")
print("------------")
print(ROOT)

print()
print(f"Text Files : {len(files)}")
print()

# ---------------------------------------------------------

print("=" * 80)
print("Architecture Specs")
print("=" * 80)

for f in sorted(ROOT.glob("docs/architecture/*.md")):
    print("-", f.relative_to(ROOT))

# ---------------------------------------------------------

print()
print("=" * 80)
print("ADRs")
print("=" * 80)

for f in sorted(ROOT.glob("docs/adr/*.md")):
    print("-", f.relative_to(ROOT))

# ---------------------------------------------------------

print()
print("=" * 80)
print("Python Runtime")
print("=" * 80)

for folder in [
    "src/opspilot/runtime",
    "src/opspilot/core",
    "src/opspilot/plugin_loader",
]:
    p = ROOT / folder
    if not p.exists():
        continue

    print()
    print(folder)

    for f in sorted(p.rglob("*.py")):
        print("   ", f.relative_to(ROOT))

# ---------------------------------------------------------

print()
print("=" * 80)
print("Versioned Files")
print("=" * 80)

duplicate_found = False

for key in sorted(groups):

    versions = sorted(groups[key])

    if len(versions) < 2:
        continue

    duplicate_found = True

    print()
    print(key)

    for f in versions:
        print(
            "   ",
            f.relative_to(ROOT),
            f"[{sha(f)}]",
        )

if not duplicate_found:
    print("No versioned files.")

# ---------------------------------------------------------

print()
print("=" * 80)
print("Empty Files")
print("=" * 80)

empty = False

for f in sorted(files):

    if f.stat().st_size == 0:
        empty = True
        print("-", f.relative_to(ROOT))

if not empty:
    print("None")

# ---------------------------------------------------------

print()
print("=" * 80)
print("Architecture Coverage")
print("=" * 80)

required = [
    "runtime.md",
    "plugin-system.md",
    "security-model.md",
    "host-transport.md",
    "workspace.md",
    "memory.md",
    "tool-registry.md",
    "approval.md",
    "audit.md",
    "error-model.md",
    "policy-engine.md",
    "mcp.md",
]

existing = {
    p.name
    for p in (ROOT / "docs/architecture").glob("*.md")
}

for name in required:

    if name in existing:
        print(f"[ OK ] {name}")
    else:
        print(f"[MISS] {name}")

# ---------------------------------------------------------

print()
print("=" * 80)
print("Architecture Review Checklist")
print("=" * 80)

items = [
    "Runtime owns execution loop",
    "Policy is in Core",
    "Approval is mandatory",
    "Audit is append-only",
    "Plugins are stateless",
    "Transport never authorizes",
    "Workspace is sandboxed",
    "CLI uses Runtime",
    "MCP uses Runtime",
    "No plugin bypasses Policy",
    "No plugin writes Audit directly",
    "No plugin owns Secrets",
]

for item in items:
    print("[ ]", item)

# ---------------------------------------------------------

print()
print("=" * 80)
print("Questions For AI Reviewer")
print("=" * 80)

questions = [
    "Which architectural contracts are still missing?",
    "Do any docs contradict each other?",
    "Are runtime responsibilities clearly separated?",
    "Does any plugin bypass policy?",
    "Does any plugin bypass transport?",
    "Are trust boundaries explicit?",
    "Is the approval protocol complete?",
    "Is the plugin ABI stable?",
    "Are there hidden coupling points?",
    "What would break at 100k LOC?",
]

for q in questions:
    print("-", q)

print()
print("=" * 80)
print("End of Review Context")
print("=" * 80)
