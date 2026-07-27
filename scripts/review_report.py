#!/usr/bin/env python3

from __future__ import annotations

import datetime
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REPORT_DIR = ROOT / "docs" / "reviews"
REPORT_DIR.mkdir(parents=True, exist_ok=True)


def git(cmd: list[str]) -> str:
    try:
        return (
            subprocess.check_output(cmd, cwd=ROOT)
            .decode()
            .strip()
        )
    except Exception:
        return "unknown"


commit = git(["git", "rev-parse", "--short", "HEAD"])
branch = git(["git", "branch", "--show-current"])
status = git(["git", "status", "--short"])

existing = sorted(REPORT_DIR.glob("*.md"))

next_id = len(existing) + 1

filename = REPORT_DIR / f"{next_id:04d}-review.md"

today = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


with filename.open("w", encoding="utf8") as f:

    f.write(f"# OpsPilot Review {next_id:04d}\n\n")

    f.write(f"Generated: {today}\n\n")

    f.write("## Git\n\n")

    f.write(f"- Branch: `{branch}`\n")
    f.write(f"- Commit: `{commit}`\n\n")

    f.write("### Working Tree\n\n")

    if status.strip():
        f.write("```text\n")
        f.write(status)
        f.write("\n```\n")
    else:
        f.write("Clean\n")

    f.write("\n---\n")

    f.write("# Current Architecture\n\n")

    for p in sorted((ROOT / "docs" / "architecture").glob("*.md")):
        f.write(f"- {p.name}\n")

    f.write("\n---\n")

    f.write("# ADRs\n\n")

    for p in sorted((ROOT / "docs" / "adr").glob("*.md")):
        f.write(f"- {p.name}\n")

    f.write("\n---\n")

    f.write("# Runtime Modules\n\n")

    for folder in [
        "src/opspilot/runtime",
        "src/opspilot/core",
        "src/opspilot/plugin_loader",
    ]:

        p = ROOT / folder

        if not p.exists():
            continue

        f.write(f"## {folder}\n\n")

        for py in sorted(p.glob("*.py")):
            f.write(f"- {py.name}\n")

        f.write("\n")

    f.write("---\n\n")

    f.write("# Review Checklist\n\n")

    checklist = [
        "Architecture consistency",
        "Plugin ABI",
        "Transport abstraction",
        "Workspace isolation",
        "Security model",
        "Threat model",
        "Policy engine",
        "Approval flow",
        "Audit trail",
        "Memory model",
        "Tool registry",
        "Error model",
        "Dependency direction",
        "Future extensibility",
    ]

    for item in checklist:
        f.write(f"- [ ] {item}\n")

    f.write("\n---\n\n")

    f.write("# Questions For Reviewer\n\n")

    questions = [
        "What architectural risks remain?",
        "What contradictions exist?",
        "Which files should be merged?",
        "Which docs are obsolete?",
        "Which contracts are still missing?",
        "What should be implemented before more plugins?",
        "Will this scale to 100k LOC?",
        "What would a Principal Engineer redesign?",
    ]

    for q in questions:
        f.write(f"1. {q}\n")

print()
print(f"Review created:\n\n{filename}")
