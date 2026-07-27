# Audit Contract Specification

## Status

Accepted for Contracts v1.

## Purpose

The Audit Service provides an immutable record of every significant Runtime decision and Tool execution.

Audit exists to support:

* accountability
* incident response
* forensic analysis
* debugging
* compliance
* reproducibility

Audit is a mandatory Core Platform Service.

It cannot be disabled by Plugins.

## Responsibilities

The Audit Service is responsible for:

* recording Runtime events
* recording Policy decisions
* recording Approval events
* recording Tool execution
* recording failures
* recording cancellations
* recording timeouts
* preserving event order
* providing immutable event history

## Non-Responsibilities

The Audit Service never:

* executes Tools
* evaluates Policy
* grants Approval
* stores raw secrets
* formats user-facing responses
* modifies Runtime behavior
* retries failed Tool executions

## Audit Principles

Audit must be:

* append-only
* immutable
* chronological
* deterministic
* structured
* machine-readable
* tamper-evident

Audit records are facts.

They must never contain assumptions.

## Audit Event

Each event contains:

* event_id
* timestamp
* session_id
* request_id
* runtime_id
* event_type
* user
* plugin
* tool
* target
* risk_class
* status
* duration_ms
* metadata

## Event Types

Contracts v1 defines:

```text
SESSION_STARTED
SESSION_FINISHED

REQUEST_RECEIVED
REQUEST_VALIDATED

POLICY_EVALUATED

APPROVAL_REQUESTED
APPROVAL_GRANTED
APPROVAL_REJECTED

TOOL_STARTED
TOOL_FINISHED
TOOL_FAILED

TIMEOUT
CANCELLED

RUNTIME_ERROR
PLUGIN_ERROR
```

Future versions may introduce additional events.

Existing event names remain stable.

## Ordering

Events must preserve causal ordering.

Example:

```text
SESSION_STARTED
REQUEST_RECEIVED
REQUEST_VALIDATED
POLICY_EVALUATED
APPROVAL_GRANTED
TOOL_STARTED
TOOL_FINISHED
SESSION_FINISHED
```

Out-of-order persistence is not permitted.

## Immutability

Existing events are never modified.

Corrections are represented by new events.

Deletion is not part of Contracts v1.

## Correlation

Every event references:

* request_id
* session_id

Tool events additionally reference:

* plugin
* tool

These identifiers allow complete reconstruction of execution history.

## Sensitive Data

Audit must never contain:

* passwords
* API keys
* SSH private keys
* bearer tokens
* raw secret values
* full environment dumps

Sensitive values must be redacted before auditing.

## Metadata

Metadata may include:

* hostname
* workspace identifier
* transport type
* execution duration
* retry count
* dry-run indicator

Metadata must remain structured.

Arbitrary log text is discouraged.

## Failure Recording

Every failure generates an audit event.

Examples:

* Policy denial
* timeout
* cancellation
* validation failure
* Plugin initialization failure
* Tool exception
* transport failure

Failures are first-class audit events.

## Approval Events

Approval events include:

* approver identity
* approval timestamp
* approval decision
* request identifier

Approval comments may be stored when available.

## Time

Timestamps use UTC.

Runtime clocks should be monotonic where appropriate for duration measurement.

## Storage

Contracts v1 does not mandate a storage backend.

Possible implementations:

* SQLite
* PostgreSQL
* OpenSearch
* object storage

The audit contract remains identical regardless of storage.

## Integrity

Future versions may support:

* cryptographic hashes
* signed audit chains
* append-only storage
* remote replication

Contracts v1 requires the interface to remain compatible with these enhancements.

## Querying

Consumers may query audit history.

Queries must never modify stored events.

Filtering may include:

* session
* request
* plugin
* tool
* event type
* time range

## Security

Plugins cannot:

* suppress audit events
* delete audit history
* modify existing events
* inject fabricated timestamps

Only the Runtime coordinates audit emission.

## Acceptance Criteria

The Audit contract is considered implemented when:

* every request produces correlated audit events
* event ordering is preserved
* events are immutable
* sensitive data is redacted
* failures are always recorded
* approval events are recorded
* Tool execution is traceable from start to finish
* Plugins cannot bypass auditing
* tests verify ordering, immutability, correlation, and redaction

