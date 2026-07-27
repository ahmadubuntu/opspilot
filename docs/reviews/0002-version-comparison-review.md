# OpsPilot Review 0002 — Versioned Files Comparison

**Date:** 2026-07-19  
**Scope:** Compare multi-version docs and Python spikes; judge whether the highest-numbered file is an improvement or a regression.  
**Constraint:** Read-only review. No existing project files were modified when this review was produced.  
**Canonicalization rule (project owner):** When multiple versions exist, the highest number is the intended winner; older numbered copies will be deleted and numbers removed from filenames.

**Related:** `docs/reviews/0001-bootstrap-review.md` (bootstrap / empty-architecture critique).

---

## Executive summary

Keeping numbered spikes for comparison is reasonable. Blindly promoting “highest number = full replacement” is **not** always safe.

- Several latest docs (`runtime3`, `plugin-system3`, `security-model3`, `mcp2`) improve depth but **drop sharp boundary rules** from earlier versions.
- Two clear problems if latest is taken wholesale: **`error-model2` is a taxonomy regression**; **`models2` alone is incomplete** (must merge with `models`, not replace).
- **`memory2` leans regressive** on the critical “memory never bypasses reality” rule.
- On code: **`plugin4` is the right direction** for the current Dispatcher path but is **broken at import** today; **`loader2` is a clean improvement**.

ADR-0002 (`docs/adr/0002-plugin-discovery.md`) was rechecked after the user’s fix: it now looks like a real ADR (Status, Context, Decision, Consequences, Alternatives).

---

## ADR-0002 status

`docs/adr/0002-plugin-discovery.md` appears corrected:

- Status / Date
- Context → Decision → Consequences
- Rejected Alternatives (with reasons)
- Migration path / Decision Drivers

Two-stage discovery (explicit imports → entry points) is clear and actionable.

---

## Parallel unnumbered pair: transport

| File | Strength |
|---|---|
| `docs/architecture/host-transport.md` | Stronger: OS isolation, DI, “transport never authorizes”, broader ops surface |
| `docs/architecture/transport.md` | Weaker overall; useful bits: `subprocess.run` anti-pattern, `stream()`, jump hosts |

**Recommendation:** Treat `host-transport.md` as canonical; fold in the subprocess example and `stream()` from `transport.md` when consolidating. Not a numbered pair, but the same “duplicate drafts” problem.

---

## Docs comparison

### 1. Runtime: `runtime.md` → `runtime2.md` → `runtime3.md`

**Latest:** `runtime3.md`  
**Score:** MIXED  
**Promote highest as-is?** No — use as base, merge back v1/v2 strengths.

**Gains in v3**

- Clearer mission: safely execute while enforcing policy, approval, audit, transport
- Gateway restored in the pipeline (dropped in v2)
- Execution state machine: `Created → Planning → WaitingForApproval → Executing → Completed|Rejected|Failed`
- Soft/hard timeouts; plugins cannot disable them
- Retry rule: never auto-retry mutating operations
- Cancellation, budget enforcement, request/session IDs
- Plugins intentionally stateless

**Losses / regressions in v3**

- v1 hard exclusions gone: Runtime does NOT own UI / Open WebUI / MCP / tool implementation
- v1 domain rule gone: Runtime NEVER contains K8s/Docker/Git implementation details
- v2 Tool Registry section (discover, validate manifests, reject duplicates)
- v2 policy outcomes: Allow / Deny / Require Confirmation / Require Dry Run
- v2 error taxonomy under Runtime
- Mandatory linear order softened into a fan-out diagram

**Critical contradiction**

- v2: execute one tool at a time  
- v3: runtime may execute multiple tools concurrently  
- Unresolved; must be decided before rename-to-canonical.

**Prefer:** `runtime3` + restore v1 ownership boundaries + v2 policy/registry detail + resolve concurrency.

---

### 2. Plugin system: `plugin-system.md` → `plugin-system2.md` → `plugin-system3.md`

**Latest:** `plugin-system3.md`  
**Score:** MIXED (closest to IMPROVED among the triples)  
**Promote highest as-is?** Almost — restore a few v1/v2 items first.

**Gains in v3**

- Richer lifecycle: Discover → Validate Manifest → Load → Initialize → Register Tools → Ready
- Tool contract adds risk, dry-run, cancellation
- DI restored (lost in v2): logger, transport, audit, policy, workspace, secrets
- Isolation: plugin failures must not crash the runtime
- Concrete YAML manifest example restored
- Future types: Python / External MCP / Remote Agent

**Losses / regressions in v3**

- v1 concrete layout gone: `manifest.yaml`, `plugin.py`, `tools.py`, `models.py`
- v2 “Plugins never communicate directly with users”
- v2 Unload step removed from lifecycle
- v2 sharp checklist (“Cannot write audit logs”, “Cannot approve actions”) diluted
- “never call subprocess directly” less sharp than earlier wording

**Critical tension**

- v3 injects `secrets` into plugins; security docs say plugins must not access secrets directly. Clarify: opaque handles only, never raw secret material.

**Prefer:** `plugin-system3` + v1 file layout + v2 user-boundary / Unload.

---

### 3. Security model: `security-model.md` → `security-model2.md` → `security-model3.md`

**Latest:** `security-model3.md`  
**Score:** MIXED  
**Promote highest as-is?** No — restore hardened defaults from v1/v2.

**Gains in v3**

- Best structural merge: Trust Boundaries + Principles + Risk Classes
- “Convenience never overrides safety”
- Approval payload: command, arguments, target, risk, estimated impact
- Workspace hardening: path traversal + symlink escapes
- Audit richer: session, plugin; append-only
- `WRITE` → `WRITE_WORKSPACE` (clearer scope)

**Losses / regressions in v3**

- v1 “Never Execute Unknown Intent”
- v1 `CLUSTER_MUTATE` = Strong Confirmation + Dry Run if available → v3 only “Approval Required”
- v1 `REMOTE_EXEC` = Always Confirm → softer wording
- v2 Threats list gone (prompt injection, privilege escalation, path traversal, …)
- v2 Fail Closed / Defense in Depth named principles
- v2 concrete secret-path bans (`~/.ssh`, `~/.kube`, `~/.aws`, env vars)
- v2 future OPA / concrete confirm examples (`rm -rf`, `terraform apply`)

**Prefer:** `security-model3` + v2 threats/Fail Closed + v1 dry-run/strong confirm for high-risk classes.

---

### 4. MCP: `mcp.md` → `mcp2.md`

**Latest:** `mcp2.md`  
**Score:** MIXED  
**Promote highest as-is?** Prefer merge.

**Gains in mcp2**

- Critical: “Runtime must never depend on MCP.”
- “CLI and MCP use the same Runtime API.”
- Future: Streaming, Progress, Cancellation, Remote Runtime

**Losses / regressions in mcp2**

- “It is NOT the internal plugin API” (important fence)
- Explicit MCP-is-NOT list: security, policy, approval, audit, planning
- Richer Open WebUI → MCP Client → Server → Runtime diagram
- MCP responsibilities: tool discovery, session forwarding

**Prefer:** mcp2 dependency rule + restore mcp1 “not internal plugin API” and responsibility split.

---

### 5. Memory: `memory.md` → `memory2.md`

**Latest:** `memory2.md`  
**Score:** MIXED (leans REGRESSED on operational safety)  
**Promote highest as-is?** No.

**Gains in memory2**

- Runtime decides which memories are retrieved; plugins never query memory directly
- Knowledge reframed as optional indexed external docs / runbooks
- Future backends: SQLite, ChromaDB, PostgreSQL, OpenSearch

**Losses / regressions in memory2**

- **Critical lost rule:** “Memory never bypasses reality. When uncertain, Runtime must execute tools again.”
- Entire Runtime Cache layer gone (kubectl/git/docker cache; never source of truth)
- Concrete homes (`.ai/` project memory, `docs/` knowledge) gone / redefined

**Prefer:** `memory.md` as base + memory2 retrieval ownership + backend futures. Do not replace v1 wholesale.

---

### 6. Workspace: `workspace.md` → `workspace2.md`

**Latest:** `workspace2.md`  
**Score:** MIXED  
**Promote highest as-is?** Prefer merge.

**Gains in workspace2**

- Exactly one workspace per session
- Isolation + mandatory validation before file ops
- Path traversal rejected; symlink escapes denied
- Contents framing: project root, temp, cache, notes, artifacts

**Losses / regressions in workspace2**

- “Plugins receive a Workspace object”
- “Plugins never manipulate absolute paths directly”
- Named responsibilities: relative path resolution, sandbox enforcement
- Future specificity for SSH / containers / remote agents (v1) replaced by vaguer remote/shared/ephemeral

**Prefer:** workspace2 isolation/security + v1 Workspace object / relative-path rule.

---

### 7. Error model: `error-model.md` → `error-model2.md`

**Latest:** `error-model2.md`  
**Score:** REGRESSED (taxonomy) / MIXED only if counting retry hints  
**Promote highest as-is?** **No. Prefer v1.**

**Gains in error-model2**

- Per-category retry guidance
- Extra structured fields: plugin, tool, timestamp
- “Exactly one category” rule

**Losses / regressions in error-model2**

- Distinct `ApprovalRequired` category removed
- `PolicyDenied` → `PermissionDenied` (blurs policy deny vs authz)
- `PluginError` vs `ToolError` collapsed
- “Errors are part of the public API” gone
- Optional `details` / `cause` gone
- “Every error generates an audit event” gone
- “Retry behavior belongs to Runtime” gone
- Blanket TransportError “Retry: Yes” is dangerous for non-idempotent ops

**Critical contradiction**

- “PermissionDenied: Retry only after approval” conflates hard policy deny with approval-gated flows that v1 separated.

**Prefer:** `error-model.md` (v1); graft v2 retry fields / plugin/tool/timestamp only.

---

## Docs summary table

| Set | Latest | Score | Prefer |
|---|---|---|---|
| runtime 1/2/3 | runtime3 | MIXED | v3 + v1 boundaries + v2 policy/errors; resolve concurrency |
| plugin-system 1/2/3 | plugin-system3 | MIXED (~improved) | v3 + v1 layout + v2 user-boundary/Unload |
| security-model 1/2/3 | security-model3 | MIXED | v3 + v2 threats/Fail Closed + v1 dry-run/strong confirm |
| mcp 1/2 | mcp2 | MIXED | merge; keep mcp2 dependency rule |
| memory 1/2 | memory2 | MIXED (safety lean regress) | v1 reality rule + cache; + memory2 retrieval |
| workspace 1/2 | workspace2 | MIXED | v2 isolation + v1 Workspace object/paths |
| error-model 1/2 | error-model2 | **REGRESSED** | **v1**, add v2 retry fields |
| host-transport vs transport | (unnumbered) | duplicates | **host-transport** (+ subprocess example) |

---

## Code comparison

### 1. Plugin ABI: `plugin.py` → `plugin2.py` → `plugin3.py` → `plugin4.py`

(+ note: `core/plugin.py` aligns with Path A)

**Latest:** `plugin4.py`  
**Score:** MIXED (right direction for current runtime consumers)  
**Promote highest as-is?** Not until import/models fix; consider adding `manifest`.

#### Signatures

| File | Surface |
|---|---|
| plugin.py | `id`; `tools() -> list[str]`; `execute(request) -> ToolResult` |
| plugin2.py | `manifest -> PluginManifest`; `tools() -> list[Tool]`; **no execute** |
| plugin3.py | Same as plugin2 (docstrings only) |
| plugin4.py | `id`; `version`; `tools() -> Iterable[ToolDefinition]`; `execute(context, request) -> ToolResult` |
| core/plugin.py | `id/version/description`; `tools() -> list[Tool]`; no execute, no manifest |

#### Architectural fork (not a linear ladder)

- **Path A (plugin2/3 + core/plugin + core/tool.Tool):** Plugin registers tools; Tool owns `async execute`. Matches “plugins only register tools” docs.
- **Path B (plugin → plugin4 + Dispatcher + filesystem):** Plugin owns `execute`; tools are `ToolDefinition` data.

**plugin2 → plugin3:** not an improvement — nearly identical APIs.

**Gains in plugin4 (for Path B)**

- `execute(context, request)` matches Dispatcher / filesystem plugin
- `tools() -> Iterable[ToolDefinition]` richer than `list[str]`
- Explicit `version`; documents policy/approval/audit preconditions

**Losses / problems**

- No `manifest` property (plugin2/3 had it)
- Drops Path A
- **Broken import today:** imports `ToolDefinition` from `opspilot.runtime.models`, but that symbol lives only in `models2.py` → ImportError

**Prefer:** plugin4 as winner for Path B after fixing models import and adding manifest; do not promote plugin2/3 unless Dispatcher/filesystem are rewritten onto Tool.execute.

---

### 2. Models: `models.py` vs `models2.py`

**Latest:** `models2.py`  
**Score:** MIXED — highest number is **not** a clean successor  
**Promote highest as-is?** **No. Merge required.**

| | models.py | models2.py |
|---|---|---|
| Enums | `RiskClass` (`WRITE`), `PolicyDecision` | `RiskClass` (`WRITE_WORKSPACE`), `Permission` |
| Types | `ToolRequest`, `ToolResult`, `AuditRecord` | `PluginManifest`, `ToolDefinition`, `ToolRequest`, `ToolResult` |
| Missing vs other | No `ToolDefinition`, `Permission`, `PluginManifest` | No `PolicyDecision`, `AuditRecord` |

**Incompatible shared shapes**

- `RiskClass.WRITE` vs `WRITE_WORKSPACE` (policy code still checks `WRITE`; filesystem uses `WRITE_WORKSPACE`)
- `ToolRequest`: `plugin` + `arguments: dict` vs no `plugin` + `arguments: BaseModel`
- `ToolResult`: `output`/`error` vs `data`/`message`

**Gains in models2**

- Types the rest of the tree already assumes
- Stronger tool metadata (`input_model`, `mutating`, `dry_run`)
- Typed arguments; clearer result shape for filesystem

**Losses in models2**

- Drops audit/policy types used by `runtime/audit.py` and `runtime/policy.py`
- Risk rename breaks policy
- Required `input_model` ahead of some filesystem spikes that omit it

**Prefer:** Merged canonical `models.py` containing the union of both, with one agreed RiskClass / ToolRequest / ToolResult shape. models2 alone regresses audit/policy.

---

### 3. Plugin loader: `loader.py` vs `loader2.py`

**Latest:** `loader2.py`  
**Score:** IMPROVED  
**Promote highest as-is?** Yes, with Runtime API alignment.

| | loader.py | loader2.py |
|---|---|---|
| API | `load() -> list[Plugin]` → always `[]` | `register` / `get` / `all` / `exists` |
| State | none | `dict[str, Plugin]` + duplicate check |
| Honesty | stub | stage-1 manual instantiate; future discovery noted |

**Gains**

- Real registry behavior
- Duplicate `plugin.id` → `ValueError`

**Cost**

- No `load()` — breaks current `Runtime.initialize()` until updated

**Prefer:** loader2 as canonical `loader.py`; update Runtime to `register`/`all`, or keep a thin `load()` that returns `list(self.all())`.

---

## Code summary table

| Set | Winner | Score | Promote highest → unnumbered? |
|---|---|---|---|
| plugin* | plugin4 (Path B) | MIXED | Only after import/models fix; add `manifest` |
| models* | **merge** (not models2 alone) | MIXED | **No** — merge types/shapes first |
| loader* | loader2 | IMPROVED | **Yes**, with Runtime API alignment |

---

## Practical rename checklist (when owner consolidates)

Use highest number as the **starting point**, then merge back listed losses before deleting older versions.

| Final filename | Start from | Before rename / delete extras |
|---|---|---|
| `runtime.md` | runtime3 | Restore “Runtime does not own UI/MCP/tools”; resolve concurrency |
| `plugin-system.md` | plugin-system3 | Restore plugin file layout; Unload; no direct user comms |
| `security-model.md` | security-model3 | Restore threats, Fail Closed, dry-run/strong confirm for high risk |
| `mcp.md` | mcp2 | Keep “not internal plugin API” from mcp1 |
| `memory.md` | **memory (v1) as base** | Add memory2 retrieval ownership; keep reality + cache rules |
| `workspace.md` | workspace2 | Restore Workspace object / relative paths from v1 |
| `error-model.md` | **error-model (v1)** | Do not replace with error-model2; graft retry fields only |
| `plugin.py` | plugin4 | Fix ToolDefinition import; add manifest |
| `models.py` | **merge models + models2** | Do not promote models2 alone |
| `loader.py` | loader2 | Align Runtime (`register`/`all` vs `load`) |
| Host transport | host-transport.md | Fold subprocess anti-pattern / stream from transport.md |

---

## Bottom line

1. **Highest number is a good cleanup rule, not a quality guarantee.**
2. Latest docs usually add operational depth and sometimes delete the sharpest safety/boundary sentences — merge, don’t blind-replace.
3. Do **not** take `error-model2` or `models2` as sole winners.
4. `plugin4` + merged models + `loader2` is the coherent code consolidation path for the Dispatcher/filesystem design.
5. Until Path A vs Path B (Tool.execute vs Plugin.execute) is explicitly chosen in one ADR/doc, numbered plugin spikes will keep reappearing as “new improvements.”

---

## One-line verdict

Latest versions of **runtime / plugin-system / security / mcp / plugin4 / loader2** are mostly directional improvements with missing pieces; **error-model2 is weaker**; **models2 must be merged, not crowned**; **memory2 must not erase the reality/cache rules**.
