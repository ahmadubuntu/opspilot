## Development Workflow

Every architecture-sensitive change follows:

1. Read the applicable ADRs and specifications.
2. Define or review the public API.
3. Write acceptance tests.
4. Implement the smallest required behavior.
5. Refactor without changing the contract.
6. Update traceability.
7. Run all validation checks.
8. Commit one logical change.

## Branch Naming

Use one of these prefixes:

- `feature/`
- `fix/`
- `docs/`
- `refactor/`
- `test/`
- `chore/`

Examples:

- `feature/runtime-kernel-v1`
- `fix/workspace-symlink-validation`
- `docs/spec-baseline-v1`

## Commit Style

Use Conventional Commits.

Examples:

- `feat(runtime): add execution context`
- `fix(workspace): reject symlink escapes`
- `test(policy): cover fail-closed behavior`
- `docs: update architecture traceability`

Each commit must represent one coherent change.

## Specification Changes

Accepted specifications must not be changed silently.

A specification change requires:

- documented reason
- affected-contract review
- traceability update
- migration impact review
- ADR when the decision is architecturally significant

## ADR Requirement

Create an ADR when a decision:

- has meaningful alternatives
- affects multiple subsystems
- changes a trust boundary
- has significant reversal cost
- changes architectural ownership
- changes extension or integration mechanisms

Routine implementation details do not require an ADR.

## Definition of Ready

A task is ready when:

- the governing specification is accepted
- the public API is known
- acceptance behavior is identified
- affected files are known
- security boundaries are understood

## Definition of Done

A change is complete when:

- required tests exist
- implementation matches accepted specifications
- Ruff passes
- Mypy passes
- Pytest passes
- traceability is updated when applicable
- no numbered duplicate files are introduced
- no unresolved `TODO`, `FIXME`, or `HACK` remains in production code
- the change is committed with a focused Conventional Commit

## Required Validation

```bash
uv run pytest
uv run ruff check .
uv run mypy src
git diff --check
