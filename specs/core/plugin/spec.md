# Plugin Contract Specification

## Status

Accepted for Contracts v1.

## Purpose

A Plugin is a versioned provider of OpsPilot Tools.

Plugins extend OpsPilot with domain-specific capabilities while remaining subordinate to the Execution Kernel.

Examples include:

* Filesystem
* Git
* Terminal
* Docker
* Kubernetes
* Kafka
* PostgreSQL
* Sentry

A Plugin does not own execution, authorization, approval, audit, sessions, memory, secrets, or transport policy.

## Responsibilities

A Plugin is responsible for:

* declaring its identity
* declaring its version
* providing a validated manifest
* declaring required permissions
* declaring supported transport capabilities
* exposing one or more Tools
* validating its own initialization requirements
* releasing owned resources during shutdown
* remaining compatible with the supported Plugin API version

## Non-Responsibilities

A Plugin never:

* executes a user request directly
* evaluates Policy
* grants permissions
* approves an operation
* writes directly to audit storage
* communicates directly with users
* reads raw secrets
* imports Runtime implementation internals
* accesses another Plugin directly
* creates unmanaged transports
* opens raw SSH sessions
* invokes subprocesses outside HostTransport
* bypasses Workspace boundaries
* modifies global Runtime state

## Core Boundary

The Execution Kernel owns:

* session lifecycle
* request validation
* Tool registration
* Policy evaluation
* Approval
* Audit coordination
* Tool dispatch
* timeout enforcement
* cancellation
* error normalization
* transport selection

Plugins own:

* domain-specific Tool implementations
* Tool input and output models
* Plugin metadata
* Plugin-specific initialization
* domain-specific error interpretation

## Plugin Interface

Every internal Python Plugin implements the canonical Plugin interface.

Conceptually:

```python
class Plugin(Protocol):
    @property
    def manifest(self) -> PluginManifest:
        ...

    def tools(self) -> tuple[Tool, ...]:
        ...

    async def initialize(self, context: PluginContext) -> None:
        ...

    async def shutdown(self) -> None:
        ...
```

The exact Python interface is defined in the Contracts v1 implementation.

## Execution Rule

Plugins do not expose a generic `execute()` method.

Each capability is represented by an individual Tool.

The Runtime execution flow is:

```text
ToolRequest
    |
    v
Execution Kernel
    |
    v
Tool Registry
    |
    v
Selected Tool
    |
    v
Workspace / Transport
    |
    v
Target System
```

The Plugin acts as the provider and lifecycle owner of its Tools.

## Plugin Manifest

Every Plugin provides a `PluginManifest`.

The manifest contains at least:

* Plugin identifier
* display name
* semantic version
* Plugin API version
* description
* required permissions
* required transport capabilities
* exposed Tool names
* minimum supported OpsPilot version

The manifest describes what the Plugin requests.

The manifest does not grant authority.

Policy remains the final authority.

## Plugin Identity

Plugin identifiers must:

* be globally unique
* use lowercase characters
* remain stable across releases
* never be reused for an unrelated Plugin
* use a predictable namespace

Examples:

```text
filesystem
git
docker
kubernetes
kafka
postgres
sentry
```

## Tool Ownership

A Plugin exposes immutable collections of Tool instances.

Tool names must be namespaced by Plugin identifier.

Examples:

```text
filesystem.read_file
filesystem.list_directory
git.status
docker.list_containers
kubernetes.list_pods
```

Duplicate Tool names cause Plugin registration to fail.

A Plugin cannot replace a previously registered Tool silently.

## Plugin Context

Runtime creates and injects a restricted `PluginContext`.

The context may provide:

* structured logger
* Workspace capability
* approved HostTransport capability
* SecretProvider reference
* Plugin configuration
* cancellation facilities
* Runtime compatibility metadata

The context must not expose:

* mutable Runtime internals
* raw audit storage
* raw Policy configuration
* raw approval state
* raw secrets
* unrestricted filesystem access
* unrestricted subprocess access

## Secrets

Plugins never receive raw secret values during initialization.

Plugins may receive:

* secret references
* opaque secret handles
* short-lived credentials
* capability-scoped credential providers

Secret resolution occurs only at the controlled execution boundary.

Secrets must never appear in:

* Plugin manifests
* Tool schemas
* prompts
* logs
* audit payloads
* exceptions
* configuration committed to Git

## Lifecycle

The Plugin lifecycle is:

```text
Discovered
    |
    v
Manifest Loaded
    |
    v
Manifest Validated
    |
    v
Compatibility Checked
    |
    v
Permissions Evaluated
    |
    v
Plugin Loaded
    |
    v
Plugin Initialized
    |
    v
Tools Registered
    |
    v
Ready
    |
    v
Shutdown
    |
    v
Unloaded
```

A Plugin that fails any lifecycle stage must not become available.

Partial Tool registration must be rolled back.

## Initialization

Plugin initialization must:

* be explicit
* be bounded by a timeout
* avoid global side effects
* avoid Tool execution
* avoid user interaction
* validate required dependencies
* fail closed when requirements are not met

Initialization must not perform infrastructure mutations.

## Shutdown

Plugin shutdown must:

* release owned resources
* stop managed background tasks
* close owned clients
* respect Runtime timeout
* remain safe when called after partial initialization
* avoid infrastructure mutation unless explicitly designed and approved

Shutdown failures must be recorded but must not crash the Runtime.

## Isolation

A Plugin failure must not crash the Execution Kernel.

Unexpected Plugin exceptions are converted into structured Plugin errors.

The Runtime may disable a failed Plugin while keeping other Plugins available.

Plugins must avoid shared mutable global state.

Tools should be stateless whenever practical.

## Dependency Injection

Plugins receive dependencies through explicit context injection.

Plugins must not import concrete implementations of:

* Audit backends
* Policy engines
* Approval providers
* Secret stores
* Runtime session managers
* transport implementations

Plugins depend only on stable contracts.

## Plugin Discovery

Contracts v1 supports deterministic built-in Plugin registration.

Future discovery may use Python entry points.

Directory scanning and arbitrary module importing are not allowed as the primary discovery mechanism.

Discovery strategy must not affect Runtime or Tool APIs.

## Versioning

Plugins follow Semantic Versioning.

### Major

Required for:

* breaking Tool schema changes
* removed Tools
* incompatible manifest changes
* incompatible behavior changes

### Minor

Used for:

* new backward-compatible Tools
* new optional capabilities
* backward-compatible schema extensions

### Patch

Used for:

* bug fixes
* internal improvements
* documentation updates
* compatible security fixes

Plugin API compatibility must be checked before initialization.

## Third-Party Plugins

Third-party Plugins are treated as untrusted code.

Installation does not imply authorization.

Third-party Plugins must still pass:

* manifest validation
* compatibility validation
* permission evaluation
* Tool schema validation
* duplicate-name checks
* lifecycle controls

Future versions may add:

* Plugin checksums
* package signing
* trusted publisher metadata
* isolated execution
* allowlisted distributions

## External MCP Providers

MCP is not the internal Plugin ABI.

An external MCP provider may be integrated through an adapter.

The adapter translates external schemas and execution requests into Runtime contracts.

External MCP providers must not bypass:

* Policy
* Approval
* Audit
* Workspace
* Transport restrictions

## Errors

Expected Plugin lifecycle failures use structured errors.

Examples:

* invalid manifest
* incompatible API version
* missing dependency
* initialization timeout
* duplicate Tool
* unsupported transport
* undeclared permission
* shutdown failure

Raw exceptions must not be returned to clients.

## Security Invariants

A Plugin cannot:

* authorize itself
* expand its declared permissions at runtime
* access capabilities it was not granted
* override Runtime timeout
* disable Audit
* disable Approval
* replace Policy
* escape Workspace
* retrieve raw secrets without an approved capability
* register undeclared Tools

Unknown or ambiguous Plugin behavior is denied by default.

## Acceptance Criteria

The Plugin contract is considered implemented when:

* a valid Plugin can be registered
* invalid manifests are rejected
* incompatible Plugin API versions are rejected
* duplicate Plugin identifiers are rejected
* duplicate Tool names are rejected
* undeclared Tools are rejected
* Plugin initialization failures do not crash Runtime
* partially registered Plugins are rolled back
* Plugin shutdown is invoked predictably
* Plugins cannot access raw Runtime internals
* Plugins expose Tools rather than a generic execution switch
* tests cover lifecycle, registration, compatibility, and failure isolation

