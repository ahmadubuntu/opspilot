# Runtime Execution Contract Specification

## Status

Accepted for Contracts v1.

## Purpose

The Runtime Execution Kernel is the single authoritative execution path for every OpsPilot Tool request.

It coordinates:

* request validation
* session validation
* Tool resolution
* Policy evaluation
* Approval
* dry-run handling
* dispatch
* timeout
* cancellation
* result validation
* error normalization
* Audit emission

No client, Plugin, Tool, adapter, or Transport may bypass the Execution Kernel.

## Responsibilities

The Execution Kernel is responsible for:

* accepting structured Tool requests
* validating request identity and session state
* resolving registered Tools
* validating Tool input
* creating immutable execution context
* invoking Policy
* pausing for Approval when required
* enforcing dry-run requirements
* dispatching the Tool
* enforcing timeout and cancellation
* validating Tool output
* normalizing failures
* emitting ordered Audit events
* returning structured execution results

## Non-Responsibilities

The Execution Kernel never:

* implements domain-specific Tool behavior
* contains Kubernetes logic
* contains Docker logic
* contains Git logic
* contains Kafka logic
* contains PostgreSQL logic
* renders Open WebUI interfaces
* implements MCP protocol details
* stores raw Secrets
* opens raw SSH connections
* directly executes subprocesses
* directly manipulates host files

Those responsibilities belong to Tools, adapters, Workspace, Transport, or SecretProvider.

## Canonical Execution Flow

Every request follows this sequence:

```text
Request Received
    |
    v
Session Validation
    |
    v
Request Validation
    |
    v
Tool Resolution
    |
    v
Input Validation
    |
    v
Policy Evaluation
    |
    +-----------------------------+
    |             |               |
    v             v               v
  Deny      Require Approval   Require Dry Run
    |             |               |
    |             v               v
    |       Approval Result    Dry-Run Execution
    |             |               |
    |             +-------+-------+
    |                     |
    v                     v
Structured Failure    Final Policy Evaluation
                              |
                              v
                         Tool Dispatch
                              |
                              v
                       Output Validation
                              |
                              v
                         Audit Completion
                              |
                              v
                       Structured Result
```

No stage may be skipped.

## Request Model

Every execution begins with a structured request containing:

* request ID
* session ID
* user identity
* Tool name
* validated argument payload
* target identity when applicable
* environment
* requested timeout
* optional client metadata
* creation timestamp

The request must not contain:

* raw Secrets
* unrestricted Transport objects
* executable Python callbacks
* client-specific UI state
* unvalidated shell strings

## Request Identity

Every request has a globally unique request ID.

The request ID is used for:

* Audit correlation
* Approval correlation
* cancellation
* timeout tracking
* result correlation
* debugging

Request IDs must never be reused.

## Session Validation

Every request belongs to exactly one active session.

Runtime validates:

* session exists
* session is active
* user identity matches session rules
* Workspace is available
* target host is available
* session limits are not exceeded

An invalid or expired session produces a structured failure.

The request does not reach Policy or Dispatcher.

## Tool Resolution

Runtime resolves the Tool through ToolRegistry.

Tool resolution verifies:

* Tool exists
* Tool is registered
* owning Plugin is active
* Tool name is unique
* Tool is declared by the Plugin manifest
* Tool API version is compatible
* required capabilities are available

Unknown Tools fail closed.

## Input Validation

Tool arguments are validated using the Tool input Pydantic model.

Raw dictionaries must not reach Tool implementations.

Validation occurs before:

* Policy evaluation
* Approval
* Audit of executable arguments
* dispatch

Validation failures produce structured errors and Audit events.

## Execution Context

Runtime creates an immutable execution context.

The context contains:

* request identity
* session identity
* user identity
* Workspace capability
* approved target identity
* approved Transport capabilities
* cancellation state
* deadline
* environment
* redacted metadata
* SecretProvider reference when required

The context must not expose:

* mutable Runtime internals
* raw Audit storage
* raw Policy configuration
* unrestricted filesystem access
* unrestricted subprocess access
* raw Secrets
* arbitrary host selection

Tools and Plugins never create their own execution context.

## Policy Evaluation

Every validated request is evaluated by Policy.

Policy returns one of:

* `ALLOW`
* `DENY`
* `REQUIRE_APPROVAL`
* `REQUIRE_DRY_RUN`

Runtime is responsible for enforcing the decision.

A Policy exception, timeout, unknown result, or missing context produces `DENY`.

## Denied Requests

When Policy returns `DENY`:

* no Tool execution occurs
* no Transport operation occurs
* no Approval is requested
* the reason is returned as a structured failure
* the decision is audited

Denied requests must never reach Dispatcher.

## Approval Flow

When Policy returns `REQUIRE_APPROVAL`, Runtime creates an Approval request containing:

* request ID
* session ID
* user
* Tool
* Plugin
* target
* validated arguments
* risk class
* expected impact
* dry-run result when available
* expiration time

Runtime pauses execution until the Approval Service returns:

* approved
* rejected
* expired
* cancelled

Only explicit approval permits continuation.

Approval is valid only for the exact request payload presented.

Changing arguments, target, Tool, or impact invalidates the Approval.

## Approval Rejection

When Approval is rejected or expires:

* no Tool execution occurs
* the result is structured
* the event is audited
* the request reaches a terminal state

Runtime must not retry or request repeated Approval automatically.

## Dry-Run Flow

When Policy returns `REQUIRE_DRY_RUN`:

1. Runtime verifies that the Tool supports dry-run.
2. Runtime invokes only the dry-run behavior.
3. The dry-run result is validated.
4. The result is audited.
5. Policy is evaluated again using preview metadata.
6. Approval may then be required.
7. Mutation occurs only after the complete flow succeeds.

If dry-run is required but unsupported, execution is denied.

A dry-run result never grants implicit authorization.

## Dispatcher

Dispatcher is a thin Runtime service.

Dispatcher is responsible for:

* receiving a resolved Tool
* receiving validated typed input
* invoking the Tool
* returning the Tool output
* isolating unexpected Tool exceptions
* normalizing Tool execution failures

Dispatcher does not:

* evaluate Policy
* request Approval
* persist Audit events
* resolve Sessions
* retry operations
* select arbitrary Transports
* render client responses

## Tool Execution

Tool execution receives:

* immutable execution context
* validated input model

Tool execution returns:

* validated output model

Tools do not return:

* raw tracebacks
* client-formatted Markdown
* MCP payloads
* CLI-specific output
* unstructured exception strings as normal success responses

## Output Validation

Runtime validates Tool output against the declared output model.

Invalid output is treated as a Tool contract violation.

The request fails even when the underlying operation may have completed.

The ambiguity must be recorded in Audit.

Invalid output must not be silently returned to clients.

## Execution States

Contracts v1 defines these states:

```text
CREATED
VALIDATING
POLICY_EVALUATION
WAITING_FOR_APPROVAL
DRY_RUN_EXECUTING
EXECUTING
COMPLETED
DENIED
REJECTED
FAILED
TIMED_OUT
CANCELLED
```

Every request begins in `CREATED`.

Every request ends in exactly one terminal state:

* `COMPLETED`
* `DENIED`
* `REJECTED`
* `FAILED`
* `TIMED_OUT`
* `CANCELLED`

## State Transitions

Valid conceptual transitions include:

```text
CREATED
  -> VALIDATING

VALIDATING
  -> POLICY_EVALUATION
  -> FAILED

POLICY_EVALUATION
  -> EXECUTING
  -> WAITING_FOR_APPROVAL
  -> DRY_RUN_EXECUTING
  -> DENIED
  -> FAILED

WAITING_FOR_APPROVAL
  -> EXECUTING
  -> REJECTED
  -> CANCELLED
  -> TIMED_OUT

DRY_RUN_EXECUTING
  -> POLICY_EVALUATION
  -> FAILED
  -> CANCELLED
  -> TIMED_OUT

EXECUTING
  -> COMPLETED
  -> FAILED
  -> CANCELLED
  -> TIMED_OUT
```

Invalid transitions are Runtime errors.

## Timeout

Every request has a bounded deadline.

Timeout may apply to:

* validation
* Policy evaluation
* Approval wait
* dry-run
* Tool execution
* Transport operation
* shutdown cleanup

Runtime owns the overall deadline.

Plugins and Tools cannot disable it.

A timed-out request enters `TIMED_OUT`.

Mutating operations with ambiguous completion state must report that ambiguity.

## Cancellation

Runtime supports explicit cancellation.

Cancellation may be requested by:

* user
* client
* session shutdown
* Runtime shutdown
* policy change
* deadline enforcement

Cancellation propagates to:

* Dispatcher
* Tool
* Workspace
* Transport

Cancellation must not be reported as success.

## Retry

Contracts v1 performs no automatic retry for mutating operations.

Read-only operations may be retried only when:

* the failure is explicitly retryable
* the Tool is safe to retry
* Policy still permits execution
* the request deadline allows it
* retry limits are not exceeded

Retry decisions belong to Runtime.

Tools and Transports do not retry independently.

## Idempotency

Tools declare whether their behavior is idempotent or retry-safe.

Runtime must not infer idempotency from Tool names.

For ambiguous remote or mutating execution states, Runtime must:

* stop automatic recovery
* return an ambiguous result
* preserve Audit evidence
* require human review

## Concurrency

Contracts v1 executes one ToolRequest at a time per Runtime invocation.

The architecture may later support concurrent independent requests.

Therefore:

* Runtime services should avoid unsafe global state
* Tools should remain stateless where practical
* Registries must be safe for read access
* shared Transports must define concurrency behavior
* Audit ordering must remain deterministic per request

Concurrency scheduling is outside Contracts v1.

## Error Normalization

Runtime converts failures into structured OpsPilot errors.

Primary categories include:

* validation error
* session error
* Tool not found
* Policy denied
* Approval rejected
* Approval expired
* dry-run unsupported
* Tool execution failure
* Transport failure
* timeout
* cancellation
* Plugin failure
* output validation failure
* internal Runtime failure
* ambiguous execution state

Raw Python tracebacks must not reach clients.

Original causes may be preserved internally for diagnostics.

## Audit Events

Every execution emits ordered Audit events.

Minimum event sequence for an allowed read:

```text
REQUEST_RECEIVED
REQUEST_VALIDATED
POLICY_EVALUATED
TOOL_STARTED
TOOL_FINISHED
```

Minimum event sequence for denial:

```text
REQUEST_RECEIVED
REQUEST_VALIDATED
POLICY_EVALUATED
REQUEST_DENIED
```

Minimum event sequence for Approval:

```text
REQUEST_RECEIVED
REQUEST_VALIDATED
POLICY_EVALUATED
APPROVAL_REQUESTED
APPROVAL_GRANTED or APPROVAL_REJECTED
TOOL_STARTED
TOOL_FINISHED
```

Failures, timeout, and cancellation must always be recorded.

## Audit Failure

Audit is mandatory.

If Audit cannot record a required pre-execution event, execution fails closed.

A Tool must not execute when the Runtime cannot establish the required Audit trail.

Post-execution Audit failure is a critical Runtime failure and must be surfaced explicitly.

## Secret Handling

Raw Secrets must never enter:

* Tool requests
* Policy logs
* Approval payloads
* Audit events
* Runtime exceptions
* client responses

Secret resolution occurs only at the controlled execution boundary.

Tools receive only scoped capabilities or opaque references.

## Memory Relationship

Memory may help planning or provide previous context.

Memory cannot:

* authorize execution
* replace Tool resolution
* replace Policy evaluation
* prove current target state
* prove current filesystem state
* bypass Approval
* bypass Audit

Runtime verifies current reality using Tools.

## Client Boundary

All clients use the same Runtime API.

Supported clients may include:

* CLI
* MCP adapter
* Open WebUI
* future Web API
* future IDE integration

Clients cannot:

* call Tools directly
* call Transport directly
* bypass Policy
* forge Approval
* suppress Audit
* change Runtime state transitions

MCP is an adapter, not the Runtime.

## Plugin Boundary

Plugins provide Tools and lifecycle metadata.

Plugins do not:

* own sessions
* receive raw requests before validation
* evaluate Policy
* request user Approval
* control Audit
* create arbitrary Transports
* retry mutations
* override timeouts
* change terminal execution state

## Shutdown

Runtime shutdown must:

* stop accepting new requests
* cancel or complete active requests according to policy
* flush required Audit events
* invoke Plugin shutdown
* close shared Transports
* release owned resources
* terminate within a bounded deadline

Shutdown must remain safe after partial initialization.

## Observability

Runtime may emit structured operational telemetry including:

* request duration
* Policy latency
* Approval wait time
* Tool latency
* Transport latency
* failure category
* cancellation count
* timeout count

Observability data does not replace Audit.

Sensitive values must be redacted.

## Security Invariants

The Runtime Execution Kernel must always enforce:

* one canonical execution path
* validated requests
* active session
* registered Tool
* typed Tool input
* mandatory Policy evaluation
* explicit Approval when required
* mandatory dry-run when required
* immutable execution context
* bounded timeout
* cancellation propagation
* validated Tool output
* structured errors
* mandatory Audit
* no raw Secret exposure
* no client or Plugin bypass

When safe execution cannot be proven, execution fails closed.

## Acceptance Criteria

The Runtime Execution contract is considered implemented when:

* every request follows the canonical execution path
* invalid sessions are rejected
* unknown Tools are rejected
* Tool input is validated before Policy and execution
* Policy is evaluated for every request
* denied requests never reach Dispatcher
* Approval pauses execution
* rejected or expired Approval prevents execution
* dry-run requirements are enforced
* Tool output is validated
* timeout produces a terminal timed-out state
* cancellation propagates to Tool and Transport
* mutating operations are not automatically retried
* ambiguous execution states are surfaced
* Audit events are ordered and correlated
* Audit failure prevents unsafe execution
* raw Secrets do not enter execution records
* CLI and MCP use the same Runtime API
* tests cover success, denial, Approval, dry-run, failure, timeout, cancellation, invalid transition, invalid output, and Audit failure

