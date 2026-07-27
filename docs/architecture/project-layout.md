# Project Layout

src/opspilot/

Runtime implementation.

plugins/

First-party plugins.

tests/

Automated tests.

docs/

Architecture and ADRs.

workspace/

Runtime data only.

.agent/

AI development rules.

No business logic may exist outside src/.

Runtime data must never be imported by application code.
