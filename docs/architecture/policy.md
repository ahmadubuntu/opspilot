# Policy Engine

Policy decides whether a tool may execute.

Plugins never make security decisions.

---

## Decision Flow

Tool Request

↓

Policy Evaluation

↓

Allowed

Denied

Confirmation Required

↓

Runtime

---

## Policy Inputs

Tool

Arguments

Risk Class

Transport

Workspace

Current Session

---

## Policy Outputs

ALLOW

DENY

CONFIRM

---

## Examples

Filesystem Read

ALLOW

Git Commit

CONFIRM

kubectl delete

CONFIRM

rm -rf /

DENY

---

## Rule

Policy decisions are deterministic.

No LLM is involved in policy evaluation.
