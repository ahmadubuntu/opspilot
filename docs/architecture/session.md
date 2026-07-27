# Session Model

Every interaction belongs to a session.

A session contains:

- user
- workspace
- transport
- model
- memory
- audit log

Sessions are isolated.

Plugins never share state directly.

Long-running operations belong to the originating session.

Session IDs are UUIDv7.
