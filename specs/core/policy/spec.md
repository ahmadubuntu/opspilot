# Policy Contract Specification

## Status

Accepted for Contracts v1.

## Purpose

The Policy Engine is the authoritative decision component that determines whether an OpsPilot operation may proceed.

Every Tool execution must pass through Policy evaluation before execution.

Policy is a mandatory Core Platform Service.

Policy is not a Plugin and cannot be disabled by a Plugin.

## Responsibilities

The Policy Engine is responsible for:

* evaluating Tool execution requests
* enforcing least privilege
* validating declared permissions
* evaluating operation risk
* evaluating target scope
* applying environment-specific restrictions
* requiring approval when necessary
* requiring dry-run when necessary
* denying unknown or ambiguous operations
* producing an explicit structured decision
* explaining why a decision was made

## Non-Responsibilities

The Policy Engine never:

* executes Tools
* invokes Plugins
* communicates directly with users
* performs Approval itself
* writes directly to audit storage
* resolves raw secrets
* opens transports
* modifies Workspace state
* retries operations
* formats responses for CLI, MCP, or UI clients

## Enforcement Point

Policy evaluation occurs inside the Execution Kernel.

The mandatory flow is:

```text
ToolRequest
    |
    v
Request Validation
    |
    v
Tool Resolution
    |
    v
Policy Evaluation
    |
    +-------------------+
    |                   |
    v                   v
Allow              Deny / Approval / Dry Run
    |
    v
Execution
```

No client, adapter, Plugin, or Tool may bypass this step.

## Policy Inputs

Policy evaluation receives a structured input containing:

* session identity
* user identity
* request identity
* Tool definition
* Plugin identity
* Tool risk class
* required permissions
* target host
* target environment
* Workspace
* transport type
* validated Tool arguments
* mutation indicator
* dry-run support
* execution context metadata
* applicable organization or project policy

Policy input must not contain raw secret values.

## Policy Decision

Every evaluation returns exactly one primary decision:

```text
ALLOW
DENY
REQUIRE_APPROVAL
REQUIRE_DRY_RUN
```

The decision must be explicit.

Policy must never return an ambiguous or implicit result.

## Policy Evaluation Model

Conceptually:

```python
class PolicyDecision(StrEnum):
    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"
    REQUIRE_DRY_RUN = "require_dry_run"


class PolicyEvaluation(BaseModel):
    decision: PolicyDecision
    reason: str
    matched_policy: str | None
    required_approvals: tuple[str, ...]
    constraints: tuple[str, ...]
```

The exact implementation is defined in Contracts v1.

## Decision: ALLOW

`ALLOW` means the request may proceed without additional human approval.

Typical examples:

* reading a file inside the active Workspace
* listing a directory inside the active Workspace
* reading Git status
* listing Kubernetes Pods in an allowed non-production environment

An allowed request must still be audited.

`ALLOW` does not disable:

* timeouts
* cancellation
* result validation
* Workspace isolation
* Transport restrictions
* audit events

## Decision: DENY

`DENY` means the operation must not execute.

Examples:

* access outside Workspace
* undeclared Plugin permission
* unknown Tool
* unsupported target
* forbidden production mutation
* use of an unauthorized transport
* attempts to read protected secret paths
* ambiguous or malformed requests

Denied operations are not sent to Dispatcher.

Every denial must be auditable.

## Decision: REQUIRE_APPROVAL

`REQUIRE_APPROVAL` means execution must pause until an authorized human explicitly approves the operation.

Examples:

* command execution
* remote execution
* destructive Git operations
* Docker mutation
* Kubernetes mutation
* production configuration changes
* credential-scoped actions

Approval is handled by the Approval Service, not by Policy.

Policy only declares that Approval is required.

## Decision: REQUIRE_DRY_RUN

`REQUIRE_DRY_RUN` means the operation cannot proceed directly to mutation.

The Runtime must first produce a dry-run, preview, or expected-impact result.

Examples:

* Kubernetes resource changes
* Terraform operations
* database migrations
* filesystem overwrite
* bulk configuration updates

After dry-run, Policy may be evaluated again using preview information.

A dry-run result does not itself authorize execution.

## Dry-Run and Approval Sequencing

Contracts v1 returns one primary Policy decision at a time.

An operation that requires both dry-run and human Approval follows this sequence:

```text
REQUIRE_DRY_RUN
    |
    v
Dry-run execution
    |
    v
Preview validation and Audit
    |
    v
Policy re-evaluation
    |
    v
REQUIRE_APPROVAL

Policy does not return simultaneous REQUIRE_DRY_RUN and REQUIRE_APPROVAL primary decisions.

Dry-run does not authorize mutation.

Mutation may proceed only after the subsequent Policy evaluation and required Approval succeed.

## Fail Closed

Policy always fails closed.

If evaluation cannot be completed:

```text
DENY
```

Examples:

* Policy configuration unavailable
* unknown risk class
* missing target metadata
* Plugin permission mismatch
* Policy Engine exception
* unsupported decision state

Runtime must never assume permission.

## Least Privilege

Policy grants only the minimum capability required for the requested operation.

A Plugin declaring a permission does not automatically receive that permission.

The final granted capability may be narrower than the declared permission.

Example:

```text
Declared:
workspace.write

Granted:
write only under docs/generated/
```

## Permission Evaluation

Each Tool declares required permissions.

Policy checks:

* whether the Plugin declared the permission
* whether the Tool declares the permission
* whether the user may exercise the permission
* whether the target permits the permission
* whether the environment permits the permission
* whether the active session grants the permission

A missing or undeclared permission results in `DENY`.

## Risk Evaluation

Initial risk classes are:

* `READ`
* `WRITE_WORKSPACE`
* `EXEC`
* `CLUSTER_MUTATE`
* `REMOTE_EXEC`

Risk classification informs Policy but does not replace Policy.

The same Tool may receive different decisions depending on:

* environment
* target
* arguments
* user
* Workspace
* scope
* current runtime mode

## Default Risk Policy

### READ

Default:

```text
ALLOW
```

Subject to:

* Workspace restrictions
* target access
* permission checks
* protected resource rules
* mandatory audit

### WRITE_WORKSPACE

Default:

```text
ALLOW or REQUIRE_APPROVAL
```

Depending on:

* destination path
* overwrite behavior
* file sensitivity
* scope
* project policy

Writes outside Workspace are denied.

### EXEC

Default:

```text
REQUIRE_APPROVAL
```

Command arguments must be visible to Policy.

Unknown or shell-composed commands may be denied.

### CLUSTER_MUTATE

Default:

```text
REQUIRE_DRY_RUN
```

Then:

```text
REQUIRE_APPROVAL
```

Dry-run is mandatory when technically supported.

The approval payload must include expected impact.

### REMOTE_EXEC

Default:

```text
REQUIRE_APPROVAL
```

Remote target identity must be explicit.

Implicit or ambiguous remote targets are denied.

## Protected Resources

Policy supports protected resources.

Examples:

```text
~/.ssh
~/.kube
~/.aws
/etc
/proc
/sys
production namespaces
system databases
critical Kafka topics
protected Git branches
```

Protected resources may be:

* denied entirely
* read-only
* approval-gated
* restricted to specific identities

Plugins must not hardcode or override protected-resource policy.

## Environment Awareness

Policy may consider environment labels such as:

* local
* development
* staging
* production
* disaster-recovery
* restricted

Production defaults must be stricter than development defaults.

Environment must be explicit for infrastructure mutations.

Unknown environment defaults to the strictest applicable policy.

## Argument Inspection

Policy evaluates validated Tool arguments.

Examples:

* command and arguments
* target namespace
* Git branch
* filesystem path
* Docker container
* database name
* Kafka topic
* remote host

Policy must not evaluate unvalidated raw input.

Sensitive values must be redacted before policy logging.

## Policy Rules

Conceptual rule:

```yaml
id: deny-production-delete

match:
  environment: production
  operation: delete

decision: deny

reason: destructive production deletion is prohibited
```

Another example:

```yaml
id: require-approval-for-remote-exec

match:
  risk: remote_exec

decision: require_approval

reason: remote command execution requires explicit human approval
```

## Rule Precedence

Contracts v1 uses deterministic rule precedence.

The strictest matching decision wins.

Recommended precedence:

```text
DENY
REQUIRE_DRY_RUN
REQUIRE_APPROVAL
ALLOW
```

A broader `ALLOW` rule cannot override a matching `DENY`.

Conflicting rules must be detectable and reported.

## Unknown Intent

OpsPilot never executes unknown intent.

If the requested outcome or target is ambiguous:

```text
DENY
```

or:

```text
REQUIRE_APPROVAL
```

depending on configured policy.

Policy must never infer destructive intent silently.

## Approval Integration

Policy emits an approval requirement.

The Approval request must contain:

* Tool name
* Plugin identity
* operation summary
* validated arguments
* target
* risk class
* expected impact
* dry-run result when available
* expiration time
* request identity
* session identity

Approval result is returned to Runtime.

Policy does not communicate with the user directly.

## Dry-Run Integration

When `REQUIRE_DRY_RUN` is returned:

1. Runtime verifies that the Tool supports dry-run.
2. Runtime executes only the dry-run path.
3. The preview is audited.
4. Policy is re-evaluated with preview metadata.
5. Approval may then be requested.
6. Mutation occurs only after the complete flow succeeds.

If required dry-run is unsupported, the default result is `DENY`.

An explicit policy exception would require a separate reviewed rule.

## Audit Integration

Every Policy evaluation produces an audit event.

Required fields include:

* request ID
* session ID
* user
* Tool
* Plugin
* target
* risk
* decision
* reason
* matched rule
* timestamp

Policy must not write directly to storage.

Runtime forwards the structured Policy event to Audit.

## Policy Configuration

Policy configuration must be:

* explicit
* validated
* versionable
* reviewable
* fail-closed
* free of raw secrets

Policy configuration must not be embedded inside Plugin code.

## Policy Sources

Contracts v1 may use built-in Python policy rules.

Future policy sources may include:

* project policy files
* organization policy bundles
* OPA
* Cedar
* RBAC
* ABAC
* signed remote policy bundles

External policy sources must still produce the canonical Policy evaluation model.

## Plugin Relationship

Plugins declare:

* required permissions
* Tool risk
* Tool mutation behavior
* Tool dry-run support

Plugins cannot:

* define the final Policy decision
* modify Policy
* approve themselves
* bypass denied actions
* downgrade Tool risk dynamically
* hide arguments from Policy
* expand permissions at runtime

## Client Relationship

Clients may display Policy decisions.

Clients cannot override Policy.

The following clients all use the same Policy path:

* CLI
* MCP
* Open WebUI
* future Web API
* future IDE integrations

## Errors

Expected Policy failures use structured errors.

Examples:

* invalid policy configuration
* unsupported Policy version
* missing required context
* conflicting rules
* undeclared permission
* unknown target
* evaluation timeout

Policy evaluation errors default to denial.

Raw exceptions must not reach clients.

## Timeouts

Policy evaluation must have a bounded timeout.

A timed-out evaluation results in `DENY`.

Policy timeout cannot be overridden by Plugins.

## Determinism

Given the same:

* validated request
* identity
* target
* environment
* Policy version
* Runtime context

Policy should return the same decision.

Non-deterministic policy behavior is not allowed in Contracts v1.

## Security Invariants

Policy cannot be:

* disabled by a Plugin
* bypassed by a client
* skipped for read operations
* overridden by memory
* replaced by Tool metadata
* weakened because audit is unavailable
* bypassed due to Policy errors

Memory and cached state are advisory only.

Current validated context is authoritative.

## Acceptance Criteria

The Policy contract is considered implemented when:

* every Tool request is evaluated before execution
* Policy returns a structured decision
* unknown decisions are denied
* missing permissions are denied
* conflicting rules are detected
* strictest-rule precedence is enforced
* Policy errors fail closed
* Policy timeouts fail closed
* approval requirements pause execution
* dry-run requirements prevent direct mutation
* denied requests never reach Dispatcher
* every decision produces an audit event
* Plugins cannot override Policy
* clients cannot bypass Policy
* tests cover Allow, Deny, Approval, Dry Run, conflict, timeout, and failure behavior

