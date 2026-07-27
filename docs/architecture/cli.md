# CLI Architecture

The CLI is a thin client.

Responsibilities:

- Parse arguments
- Initialize Runtime
- Render output
- Handle exit codes

The CLI never contains business logic.

All operations are delegated to the Runtime.

Supported output formats:

- text
- json

Future:

- yaml
- streaming

Exit codes:

0 Success

1 User error

2 Validation error

3 Permission denied

4 Tool failure

5 Internal runtime failure
