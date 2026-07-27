# OpsPilot Core Contracts Stabilization Review

## Status

Completed for the current read-only vertical slice.

## Scope

This stabilization reconciled the conflicting numbered Python and architecture drafts in the supplied project archive.

## Canonical Decisions

- `src/opspilot/core/plugin.py` is the only internal Plugin contract.
- Plugins expose `manifest` and `tools()`; Plugins do not execute Tool requests.
- Each Tool owns one typed executable capability.
- `src/opspilot/runtime/registry.py` owns Tool registration and duplicate rejection.
- Dispatcher is thin: resolve, validate input, invoke.
- Runtime owns Policy, Approval, Audit, and failure normalization.
- Policy returns structured decisions.
- Audit is event-based and records pre-execution failures as well as completed Tools.
- Workspace enforces root isolation, path traversal prevention, and symlink escape prevention.
- Transport performs I/O but never authorizes.
- The initial Filesystem plugin is read-only.

## Removed Conflicts

- numbered Python drafts under `src/opspilot/`
- duplicate Runtime Plugin contract
- generic `core/models.py` and `runtime/models.py` God-model drafts
- duplicate contract package under `src/opspilot/contracts/`
- direct `pathlib` access from Filesystem Tools
- numbered architecture drafts for Tool, Manifest, and Audit

## Validation

Executed in the review environment:

```text
PYTHONPATH=src python3 -m compileall -q src
PYTHONPATH=src python3 -m pytest -q
```

Result:

```text
9 passed
36 OpsPilot modules imported successfully
0 import failures
```

`uv run pytest`, Ruff, and Mypy could not be executed in the review environment because network access was unavailable for uv's requested Python download and Ruff/Mypy were not installed globally. They remain required validation steps on the development workstation.

## Next Phase

1. Run `uv run pytest`, `uv run ruff check .`, and `uv run mypy src` locally.
2. Fix any Python 3.11-specific typing or style findings.
3. Add CLI composition for the read-only Filesystem vertical slice.
4. Add MCP adapter only after CLI execution succeeds end-to-end.
5. Add workspace mutation only with preview, approval, atomic write, and audit coverage.
