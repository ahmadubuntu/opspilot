# Next Steps

## Current Phase

Phase 1.5 — Architecture Governance

## Remaining Tasks Before Merge

* Review ADR coverage
* Verify all specifications are internally consistent
* Update architecture indexes
* Update implementation contracts
* Pass the Merge Gate
* Merge `docs/spec-baseline-v1` into `main`

## Phase 2

After the Merge Gate passes:

1. Create:

```text
feature/runtime-kernel-v1
```

2. Implement:

```text
src/opspilot/core/errors.py
src/opspilot/core/models.py
src/opspilot/runtime/context.py
src/opspilot/runtime/dispatcher.py
src/opspilot/runtime/kernel.py
```

3. Add unit tests.

4. Keep implementation aligned with:

* Accepted ADRs
* Accepted Specifications
* Traceability Matrix

5. Do not introduce architectural shortcuts.

## Development Rule

Every significant feature follows:

```text
ADR (if required)

↓

Specification

↓

Tests

↓

Implementation

↓

Review

↓

Merge
```

## Initial Vertical Slice

Target:

```text
CLI
    ↓
Runtime
    ↓
Policy
    ↓
Dispatcher
    ↓
Filesystem Plugin
    ↓
Workspace
    ↓
LocalTransport
```

Supported Tools:

* filesystem.read_file
* filesystem.list_directory
* filesystem.stat

Mutating filesystem operations remain outside the first implementation slice.


# Next Steps

## Current Work

Complete the final Merge Gate for `docs/spec-baseline-v1`.

## Before Merge

Run:

```bash
uv run pytest
uv run ruff check .
uv run mypy src
git diff --check
git status


Update .ai/STATUS.yaml with the results.

Merge

Merge docs/spec-baseline-v1 into main using a non-fast-forward merge.

Create the architecture-v1 annotated tag.

Next Branch
chore/development-infrastructure-v1
Sprint 0

Implement only:

pre-commit
GitHub Actions
Makefile
EditorConfig
coverage reporting without an enforced threshold
Phase 2 Branch

After Sprint 0 is merged:

feature/runtime-kernel-v1
Phase 2 Objective

Implement the Runtime contracts required for the read-only filesystem vertical slice.

Initial Vertical Slice
CLI
  -> Runtime Execution Kernel
  -> Session
  -> Policy
  -> Audit
  -> Dispatcher
  -> Filesystem Tool
  -> Workspace
  -> LocalTransport
