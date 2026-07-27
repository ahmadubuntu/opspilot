# Policy Model

## Purpose

The Policy Engine is a core security component of OpsPilot Runtime.

It decides whether a requested action can be:

- executed automatically
- rejected
- executed only after human approval
- executed only after dry-run validation

The Policy Engine is part of the Runtime Kernel.

It is NOT a plugin.

No plugin can bypass policy evaluation.


# Design Principles

## Fail Closed

If a policy decision cannot be determined:

Deny


The system must never assume permission.


## Least Privilege

Tools receive only the minimum permissions required for execution.


## Explicit Risk

Every operation has a risk classification.

Risk is determined by:

- tool type
- target system
- operation type
- affected scope
- mutation level


## Policy Before Execution

The execution flow is always:

Tool Request

|

Schema Validation

|

Policy Evaluation

|

Approval (if required)

|

Execution

|

Audit



# Policy Decision Model

Every request produces one of these results:


## ALLOW

The operation can execute immediately.


Example:


Read Kubernetes pod list


Requirements:

- valid schema
- permitted tool
- allowed target


---


## DENY

The operation must not execute.


Examples:


Accessing restricted secrets

Deleting protected resources

Unknown tool execution



---


## REQUIRE_APPROVAL

The operation requires human confirmation.


Examples:


kubectl delete pod

docker rm container

git push --force



---


## REQUIRE_DRY_RUN

The operation requires a preview before execution.


Examples:


terraform apply

kubernetes deployment changes

database migrations



# Risk Classes

## READ

Description:

Operations that only observe state.


Examples:

- list resources
- inspect configuration
- read logs


Default:


ALLOW



Requirements:

- audit event
- permission check


---


## WRITE_WORKSPACE

Description:

Operations modifying files inside the allowed workspace.


Examples:

- create configuration file
- update documentation
- generate reports


Default:


ALLOW



Requirements:

- workspace restriction
- audit event


---


## EXEC

Description:

Execution of commands or processes.


Examples:

- shell commands
- scripts
- local tools


Default:


REQUIRE_APPROVAL



Requirements:

- command inspection
- timeout
- audit


---


## CLUSTER_MUTATE

Description:

Changes to infrastructure resources.


Examples:

- scale deployment
- delete resources
- modify services


Default:


REQUIRE_APPROVAL

REQUIRE_DRY_RUN when supported


Requirements:

- target visibility
- impact summary
- audit


---


## REMOTE_EXEC

Description:

Execution on remote systems.


Examples:

- SSH commands
- remote agents


Default:


REQUIRE_APPROVAL



Requirements:

- explicit target host
- transport validation
- audit


# Policy Evaluation Input

The Policy Engine evaluates:


```yaml
request:

  session_id:

  user:

  tool:

  plugin:

  risk_class:

  target:

  arguments:

  permissions:

  transport:

  environment:
Policy Rules

Example:

rules:

  - name: deny-production-delete

    condition:

      environment: production

      operation: delete

    decision: DENY

Example:

rules:

  - name: require-confirmation-for-cluster-changes

    condition:

      risk_class: CLUSTER_MUTATE

    decision: REQUIRE_APPROVAL
Protected Resources

The Policy Engine must support protected resources.

Examples:

protected:

  namespaces:

    - kube-system

    - production

  paths:

    - ~/.ssh

    - ~/.kube

    - ~/.aws

Protected resources require stronger policies.

Approval Integration

Policy Engine does not perform approval itself.

It only requests approval.

Flow:

Policy Engine

        |

Approval Request

        |

Human Decision

        |

Runtime Execution

Approval payload must contain:

Action

Tool

Arguments

Target

Risk

Expected Impact

Dry Run Result
Policy and Plugins

Plugins:

declare required permissions
provide tool metadata
provide risk classification

Plugins cannot:

create policies
modify policies
approve themselves
bypass denied actions
Secrets Policy

Secrets are never available during policy evaluation.

Policy evaluates:

secret_ref

not:

secret_value

Example:

Allowed:

database-prod-password

Forbidden:

postgres://user:password@host
Audit Requirements

Every policy decision creates an audit event.

Example:

{
  "event": "policy_decision",
  "tool": "kubernetes.delete_pod",
  "decision": "REQUIRE_APPROVAL",
  "risk": "CLUSTER_MUTATE"
}
Future Extensions

The Policy Engine may support:

OPA integration
organization policies
team policies
environment-specific rules
compliance rules

The Runtime Kernel remains the final enforcement point.
