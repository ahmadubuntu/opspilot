# API Guidelines

Public APIs must use Pydantic models.

Never expose dictionaries.

Never expose tuples.

Never expose raw subprocess output.

Every public API must define:

- Input model
- Output model
- Exceptions

Avoid boolean arguments.

Prefer enums.

Prefer explicit method names.

APIs should be deterministic whenever possible.
