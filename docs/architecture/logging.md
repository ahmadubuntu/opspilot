# Logging Strategy

OpsPilot uses structured logging only.

Format:

JSON

Every log includes:

- timestamp
- level
- session_id
- plugin
- tool
- duration
- host
- workspace

Never log:

- passwords
- tokens
- kubeconfig
- SSH keys
- secrets

Logs are immutable.

Audit logs are append-only.

Business logs and audit logs are separated.
