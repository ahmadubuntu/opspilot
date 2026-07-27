# Audit System

## Purpose

Audit provides an append-only record of every security-relevant Runtime decision and Tool execution. An action that bypasses Audit is considered invalid execution.

## Event Types

Initial events:

- `request_received`
- `policy_decided`
- `approval_resolved`
- `tool_started`
- `tool_completed`
- `tool_failed`

Future events may include cancellation, timeout, transport connection, and session lifecycle events.

## Required Fields

Every event includes:

- event ID
- event type
- timestamp
- session ID
- request ID
- Tool name
- structured payload

Payloads may include policy decisions, approval status, duration, result summary, and sanitized error details.

## Rules

- Audit is a mandatory Core service.
- Plugins never write directly to audit storage.
- Policy denials and approval rejections are audited.
- Failures before Tool execution are audited.
- Records are append-only and immutable.
- Secrets, credentials, and sensitive raw outputs must be redacted.

## Storage

Stage 1 uses an in-memory sink for contract and integration tests. Future sinks may include SQLite, OpenTelemetry, Loki, Elasticsearch, or SIEM systems without changing Runtime APIs.
