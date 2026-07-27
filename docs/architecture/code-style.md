# Code Style

Python >= 3.14

Type hints are mandatory.

Public functions require docstrings.

Business logic must be testable.

Avoid global state.

Avoid singleton patterns.

Prefer composition over inheritance.

Use dataclasses only for immutable internal objects.

Use Pydantic for public contracts.

Raise typed exceptions.

Never return None to indicate failure.

Never catch broad Exception unless re-raising with additional context.
