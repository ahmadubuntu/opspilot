# Host Transport Contract Specification

## Status

Accepted for Contracts v1.

## Purpose

HostTransport provides the controlled execution and I/O boundary between OpsPilot and a target host.

It abstracts whether operations are performed on:

* the local workstation
* a remote SSH host
* a future remote agent
* another approved execution environment

Tools and Plugins must not depend on concrete transport implementations.

HostTransport is a mandatory Core Platform Service.

It is not a Plugin.

## Responsibilities

HostTransport is responsible for:

* executing bounded host operations
* reading files through approved Workspace paths
* writing files through approved Workspace paths
* listing directories
* retrieving path metadata
* starting approved processes
* enforcing execution timeouts
* supporting cancellation where technically possible
* capturing structured stdout and stderr
* reporting transport-level failures
* identifying the target host
* providing consistent behavior across transport implementations

## Non-Responsibilities

HostTransport never:

* evaluates Policy
* grants permissions
* requests Approval
* writes Audit events directly
* selects which Tool to run
* resolves user intent
* exposes raw Secrets
* chooses the active Workspace
* modifies Tool risk classification
* retries mutating operations automatically
* communicates directly with users

## Core Boundary

The mandatory execution path is:

```text
Runtime
    |
    v
Policy
    |
    v
Approval
    |
    v
Dispatcher
    |
    v
Tool
    |
    v
Workspace
    |
    v
HostTransport
    |
    v
Target Host
```

Transport is an execution mechanism.

Transport is not an authorization mechanism.

## Transport Interface

Contracts v1 defines a transport capability conceptually containing:

```python
class HostTransport(Protocol):
    @property
    def host(self) -> HostIdentity:
        ...

    async def read_file(
        self,
        path: WorkspacePath,
        *,
        max_bytes: int,
    ) -> ReadFileResult:
        ...

    async def list_directory(
        self,
        path: WorkspacePath,
        *,
        max_entries: int,
    ) -> DirectoryListResult:
        ...

    async def stat(
        self,
        path: WorkspacePath,
    ) -> PathMetadata:
        ...

    async def execute(
        self,
        request: ProcessRequest,
    ) -> ProcessResult:
        ...
```

The exact Python implementation is defined during Contracts v1 implementation.

## Transport Types

Initial and future transport types include:

### LocalTransport

Runs operations on the current machine.

### SSHTransport

Runs operations through an authenticated SSH connection.

SSHTransport is not implemented in the initial vertical slice.

### RemoteAgentTransport

Runs operations through a future authenticated remote OpsPilot agent.

RemoteAgentTransport is outside Contracts v1 implementation but must remain compatible with the interface.

## Host Identity

Every Transport has an immutable HostIdentity.

Host identity contains at least:

* stable host identifier
* display name
* transport type
* operating-system metadata when available
* environment label
* optional address metadata

Host identity must not contain raw credentials.

Examples:

```text
local-workstation
staging-app-01
production-kafka-02
```

The target host must always be explicit.

Implicit remote execution is forbidden.

## Capability-Based Access

Tools receive only the transport capabilities required for their operation.

A filesystem Tool should not automatically receive unrestricted process execution.

A read-only Tool should not automatically receive write capability.

Future implementations may expose narrower interfaces such as:

* FileReader
* FileWriter
* DirectoryReader
* ProcessExecutor
* PortForwarder

Contracts v1 may use a combined interface internally, but Policy must still restrict actual capabilities.

## LocalTransport

LocalTransport performs operations on the current machine.

LocalTransport must:

* execute without an interactive shell by default
* use explicit argument lists
* enforce configured working directory
* enforce timeouts
* capture stdout and stderr separately
* return structured results
* avoid inheriting unrestricted environment variables
* support cancellation where possible
* avoid detached background processes

LocalTransport must not assume that all local resources are authorized.

Local execution still passes through Policy, Approval, Workspace, and Audit.

## Process Request

A process execution request contains:

* executable
* argument list
* working directory
* environment references
* timeout
* stdin behavior
* output size limits
* cancellation token
* target host
* risk metadata
* dry-run indicator when supported

The request must use structured arguments.

## Shell Execution

Direct shell-string execution is forbidden by default.

Forbidden:

```python
subprocess.run(
    "rm -rf " + user_input,
    shell=True,
)
```

Preferred:

```python
subprocess.run(
    ["git", "status", "--short"],
    shell=False,
)
```

A future explicit shell Tool may exist, but it requires:

* dedicated Policy rules
* explicit Approval
* argument visibility
* strict quoting
* timeout
* output limits
* mandatory Audit

## Environment Variables

Transport must not inherit the complete host environment by default.

Allowed environment variables must be explicit.

Forbidden behavior includes:

* forwarding all environment variables
* exposing tokens to unrelated processes
* logging environment dumps
* passing raw Secrets in request metadata

Secrets may be injected only through approved SecretProvider capabilities at the execution boundary.

## Working Directory

Every process execution has an explicit working directory.

For project operations, the working directory must be resolved through Workspace.

Tools must not supply arbitrary absolute working directories.

An invalid or out-of-scope working directory is rejected.

## Timeout

Every transport operation has a bounded timeout.

Timeout behavior must:

* stop or terminate the operation where technically possible
* return a structured timeout error
* preserve partial stdout and stderr when safe
* produce an Audit event through Runtime
* avoid leaving unmanaged child processes

Plugins and Tools cannot disable Runtime timeout enforcement.

## Cancellation

Transport operations receive cancellation state.

When cancellation is requested, Transport should:

1. stop accepting additional work
2. signal the active operation
3. terminate child processes when safe
4. wait for bounded cleanup
5. return a structured cancellation result

Cancellation must not silently report success.

## Process Trees

For local process execution, cancellation and timeout handling must consider child processes.

Transport should avoid leaving orphaned processes.

Future platform-specific implementations may use:

* process groups
* job objects
* cgroups
* remote-agent task identifiers

## Output Capture

Process output is captured as structured fields:

* stdout
* stderr
* exit code
* started time
* finished time
* duration
* truncation indicator
* encoding information

Output limits are mandatory.

Unbounded output capture is forbidden.

## Output Limits

Transport may enforce:

* maximum stdout bytes
* maximum stderr bytes
* maximum combined output
* maximum streamed event count

When output is truncated, the result must state that truncation occurred.

Truncation must not turn a failed command into a successful result.

## Streaming

Contracts v1 does not require end-user streaming.

The interface should remain compatible with future:

* progress events
* stdout streaming
* stderr streaming
* cancellation during streaming

Streaming APIs must not bypass Audit or output limits.

## Exit Codes

A completed process returns an explicit exit code.

Transport does not automatically treat every non-zero exit code as an internal error.

Domain-specific Tools interpret expected command exit codes.

Examples:

* `git diff --quiet` may return a non-zero status to indicate differences
* a command-not-found result is a Transport or execution failure
* a Tool must distinguish operational state from infrastructure failure

## File Operations

File operations must use Workspace-approved paths.

Transport must not accept unrestricted Tool-provided host paths.

Supported read-only operations include:

* read text file
* read bounded binary content
* list directory
* stat path
* check existence

Future mutating operations may include:

* write file
* atomic replace
* create directory
* rename
* copy
* delete

All mutating operations remain subject to Policy and Approval.

## Workspace Relationship

Workspace owns safe path resolution and root isolation.

Transport performs the actual operation.

Transport must not weaken Workspace validation.

Conceptual flow:

```text
Tool relative path
    |
    v
Workspace validation
    |
    v
Transport-safe target path
    |
    v
Host operation
```

Transport implementations must not allow a Plugin to skip Workspace by passing a raw path.

## Remote Transport

Future SSHTransport and RemoteAgentTransport must preserve the same contracts as LocalTransport.

Remote implementations must additionally support:

* explicit host identity
* authentication through SecretProvider
* connection timeout
* operation timeout
* host-key or agent-identity verification
* structured connectivity errors
* bounded reconnection behavior
* partial-connectivity handling

Remote transport does not imply authorization.

## SSH Security

Future SSHTransport must not:

* disable host-key checking by default
* expose private keys to Plugins
* forward SSH agents implicitly
* reuse credentials across unrelated hosts
* hide jump-host routing
* accept ambiguous host identities
* execute unstructured shell commands by default

Credentials are resolved by trusted Runtime services.

## Remote Agent Security

A future RemoteAgentTransport must include:

* mutual authentication
* encrypted communication
* host identity verification
* request correlation
* bounded capabilities
* replay protection
* protocol versioning
* remote Audit correlation
* cancellation support

The remote agent must not become an unrestricted root daemon by default.

## Retry Rules

Transport may retry only operations classified as safe and retryable.

Potentially retryable:

* transient connection establishment
* read-only metadata requests
* temporary network failures

Never automatically retry:

* mutating operations
* process execution with side effects
* partially completed remote commands
* destructive filesystem operations
* cluster mutations

Retry policy belongs to Runtime, not Transport.

Transport reports retryability metadata.

## Idempotency

Transport itself does not assume idempotency.

Tools declare whether operations are idempotent or safe to retry.

A connection retry must not cause duplicate execution.

For remote execution, Runtime and Transport must distinguish:

* request not delivered
* request delivered but not started
* request started
* request completed but response lost

Ambiguous execution state must be surfaced to the user and Audit.

## Error Model

Expected Transport errors include:

* host unavailable
* connection refused
* authentication failure
* host identity mismatch
* operation timeout
* cancellation
* executable not found
* working directory invalid
* output limit exceeded
* encoding failure
* transport protocol mismatch
* connection lost during execution
* ambiguous remote execution state
* unsupported capability

Transport errors are structured and preserve the original technical cause internally.

Raw exceptions and raw tracebacks must not reach clients.

## Error Classification

Transport errors should identify whether they are:

* retryable
* non-retryable
* ambiguous
* caused by cancellation
* caused by timeout
* caused by authentication
* caused by target state
* caused by local Runtime failure

Runtime decides the final recovery behavior.

## Audit Integration

Transport does not persist Audit events directly.

Runtime records transport-related information including:

* host identity
* transport type
* operation type
* executable without raw Secrets
* redacted arguments
* working directory identifier
* start and finish times
* exit code
* timeout
* cancellation
* output truncation
* failure category

Raw sensitive output should not be copied into Audit automatically.

## Logging

Transport may emit structured diagnostic logs through an injected logger.

Logs must not contain:

* private keys
* tokens
* passwords
* full environment variables
* unredacted connection strings
* raw secret values

Diagnostic logs are not a replacement for Audit.

## Concurrency

Transport implementations may support concurrent read-only operations in future.

Contracts v1 Runtime executes one ToolRequest at a time per invocation.

Transport implementations must remain safe if reused concurrently later.

Shared clients and connection pools must be explicitly synchronized.

## Resource Ownership

Transport owns resources it creates, such as:

* local child processes
* SSH connections
* remote-agent sessions
* streams
* temporary transport buffers

Transport must release owned resources during shutdown.

Plugins do not own or close shared Runtime transports.

## Lifecycle

Transport lifecycle is:

```text
Created
    |
    v
Configured
    |
    v
Validated
    |
    v
Ready
    |
    v
Executing Operations
    |
    v
Closing
    |
    v
Closed
```

Operations on a closed Transport must fail predictably.

## Configuration

Transport configuration must be:

* explicit
* validated
* free of raw Secrets
* versionable
* bounded
* target-specific

Configuration may include:

* host identifier
* connection endpoint
* timeout defaults
* output limits
* allowed capabilities
* environment label
* Secret references

## SecretProvider Relationship

Transport may request approved credentials through SecretProvider.

Transport receives only the credentials required for the specific target and operation.

Transport must not expose resolved credentials to Plugins or Tools.

Credentials must be released or invalidated when appropriate.

## Memory Relationship

Memory may remember previous host state or connectivity.

Memory is not authoritative.

Transport must perform current operations against the real target.

Cached success does not prove current connectivity.

Reality overrides Memory.

## Plugin Relationship

Plugins and Tools must not:

* instantiate concrete Transports directly
* open raw SSH connections
* call `subprocess` directly
* select arbitrary remote hosts
* access Transport credentials
* disable timeout
* disable output limits
* bypass Workspace
* retry mutations independently

They receive approved capabilities through Runtime context.

## Client Relationship

Clients cannot directly invoke Transport methods.

CLI, MCP, Open WebUI, and future clients submit Runtime requests.

Runtime remains the single execution authority.

## Security Invariants

Transport must enforce these invariants:

* explicit target identity
* no authorization decisions
* no raw Secret exposure
* bounded timeouts
* bounded output
* structured arguments
* explicit working directory
* no unmanaged background processes
* no implicit shell execution
* Workspace-controlled paths
* structured errors
* safe resource cleanup

If execution safety cannot be established, the operation fails closed.

## Acceptance Criteria

The Transport contract is considered implemented when:

* LocalTransport executes structured argument lists
* shell execution is disabled by default
* working directory is explicit and Workspace-bound
* stdout and stderr are captured separately
* output limits are enforced
* timeouts terminate bounded operations
* cancellation returns a structured result
* environment inheritance is restricted
* raw Secrets are not exposed
* file operations use Workspace-approved paths
* Transport does not evaluate Policy
* Tools cannot instantiate unrestricted Transports
* mutating operations are not automatically retried
* host identity is included in results
* errors expose retryability and ambiguity
* tests cover success, non-zero exit, timeout, cancellation, output truncation, invalid working directory, restricted environment, and cleanup

