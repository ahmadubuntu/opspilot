# OpsPilot Architecture Review — Critical Assessment

**Date:** 2026-07-18  
**Scope:** Bootstrap design (principles, layout, roadmap, empty architecture docs, stated stack)  
**Verdict:** The *product idea* is sound. The *architecture* is not yet an architecture — it is a slogans + folder layout. You are about to spend hundreds of hours implementing against empty contracts. That is the highest-risk state a project can be in.

Architecture docs under `docs/architecture/` are empty. ADRs are one-liners. No plugin contract, no trust boundary, no execution model, no confirmation protocol. Writing more code now freezes ambiguity into the codebase.

---

## Idea summary (positive / negative)

### Positive

- **Local-first DevOps agent** addresses a real problem; teams that will not send infra data/credentials externally are a real market.
- **Plugin-first + MCP** is the right direction for extensibility — *if* the contract is correct.
- **Safety-over-convenience** is non-negotiable for tools that touch kube/SSH/terminal.
- **Model-independent** is correct; UI and runtime must not lock to Gemma/LM Studio.
- **Python + uv + Typer + Pydantic** is a reasonable stack for this domain.
- **Keeping Open WebUI free of business logic** is excellent.
- **Requiring future remote ops without assuming local filesystem** is correctly identified — if it lands in the API now, it avoids a later redesign.

### Negative / dangerous

- **“Everything is a plugin” without boundaries** is abstraction theater. Core without minimal capabilities (policy, approval, audit, session, transport) does not exist.
- **Open WebUI → Runtime** has no defined protocol. That is an integration gap, not an implementation detail.
- **Roadmap is tool-ordered** (filesystem → k8s → kafka…) instead of **capability-layered** (observe → plan → confirm → execute → audit).
- **AI memory (`.ai/`)** currently repeats the README; it is not structured memory with schema and freshness guarantees.
- **Docker-first for everything** tensions with local-first and local GPU/LLM; for a workstation agent, a daemon inside a container is often pain, not benefit.
- **No threat model, no plugin ABI, no execution sandbox model** — and the architecture docs are empty.

---

## 1. Architectural mistakes already visible

**A. Architecture by aspiration**  
Clean Architecture diagram in principles (`Runtime → Loader → Plugins → Infra`) is a dependency-rule slogan. There is no:

- port/adapter map
- domain model
- application services
- failure taxonomy
- concurrency model

Without those, “Clean Architecture” is cargo cult.

**B. Plugin-everything fallacy**  
If filesystem, terminal, docker, git, *and* policy/approval/audit are all plugins, the core becomes a dumb loader. Loaders do not make platforms. Platforms need **invariants** that plugins cannot violate. Those invariants belong in core, not plugins.

**C. UI coupling risk is unacknowledged**  
“Open WebUI is UI only” is good. But Open WebUI owns chat state, tool calling UX, and often MCP client behavior. You have not defined whether OpsPilot is:

1. an MCP server that Open WebUI calls, or
2. a custom backend with its own agent loop, or
3. a sidecar that Open WebUI never truly controls.

Those three produce **different** runtimes. Choosing none is choosing accidental architecture.

**D. Empty architecture docs with full directory claims**  
`runtime.md`, `plugin-system.md`, `security-model.md`, `mcp.md`, `memory.md` exist and are empty. Documentation-first + empty contracts = false confidence. Future AI agents will invent incompatible designs from slogans.

**E. ADR theater**  
`DECISIONS.md` lists “Python”, “plugins”, “Docker” as decisions without alternatives considered, consequences, or reversal cost. That is a changelog of preferences, not ADRs.

**F. Roadmap inverted**  
Phases are tool catalogs. The hard problems are: **tool schema**, **confirmation**, **idempotency**, **blast radius**, **observability of agent actions**, **partial failure**, **multi-host identity**. Shipping Kafka before a real approval bus is feature theater.

**G. “Remote via SSH later without redesign” is asserted, not designed**  
Avoiding `pathlib.Path` in the API is necessary but nowhere near sufficient. You need:

- Host identity / inventory
- Transport abstraction (local exec vs SSH vs future agent)
- Credential providers
- Workspace roots per host
- Latency and partial connectivity semantics

None of that is in the layout.

---

## 2. Decisions that are excellent

| Decision | Why it holds |
|---|---|
| Local-first | Correct trust model for DevOps data and credentials |
| Model-independent backends | Avoids vendor lock-in; OpenAI-compatible is the right interchange |
| Open WebUI ≠ business logic | Prevents the classic “logic trapped in a chat UI” dead end |
| Python + Pydantic + Typer + structlog + uv | Fits MCP/AI ecosystem; good operational ergonomics |
| Safety / least privilege / explicit confirmation | Non-negotiable for anything that can `rm`, `kubectl delete`, SSH |
| Explicit future remote requirement now | Timing is right — before filesystem plugin freezes local assumptions |
| Conventional commits + small commits | Keeps history usable when agents also commit |
| Treating docs as product surface | Correct for an AI-maintained codebase — *if* docs have schemas |

Keep these. They are the load-bearing walls.

---

## 3. Decisions to reconsider before implementation grows

**1. Plugin granularity**  
Do not make `filesystem`, `git`, `terminal` three independent security domains with three loaders if they share the same host and same blast radius. Prefer **capability packages** behind a single **HostExecutor** / **Workspace** abstraction, with plugins as *tool providers*, not *mini-runtimes*.

**2. Docker-first as a principle for the agent itself**  
Docker-first for *optional services* (Open WebUI, later observability) is fine. Docker-first for the agent that must talk to host Docker socket, kubeconfig, SSH agent, and local GPU LLM is a footgun. Prefer: **agent on host (or privileged thin runner)**, UI/services in Compose.

**3. MCP as the internal plugin ABI**  
MCP is an excellent *external* protocol. As the *only* internal plugin interface it is chatty, process-heavy, and awkward for in-process typed Python plugins. Dual surface is better:

- **Internal:** typed Python Plugin Protocol (fast, testable)
- **External:** MCP adapter (interop with Open WebUI / other clients)

**4. “Every capability is a plugin”**  
Reclassify:

- **Core platform services** (config, policy, approval, audit, secrets, sessions, event bus)
- **Tool plugins** (k8s, kafka, …)
- **Optional extension plugins**

If approval is a plugin, a malicious or buggy plugin bypasses safety by not loading it.

**5. Open WebUI as the long-term agent UX**  
Fine for Stage 1. Do not let its tool-calling semantics define your runtime. Own the agent loop early, even if UX stays Open WebUI via MCP.

**6. Documentation volume without schemas**  
Stop proliferating markdown. Introduce **machine-checkable** contracts (JSON Schema / Pydantic models for plugin manifest, tool defs, policy, ADR frontmatter). Unstructured AI memory diverges.

---

## 4. Important components still missing

These are not “nice to have”; they are foundation:

1. **Agent runtime loop** — plan/act/observe, cancellation, timeouts, budget limits
2. **Tool registry + schema** — namespacing, versioning, deprecation
3. **Policy engine** — allow/deny/confirm by tool, arg shape, host, environment
4. **Approval / confirmation bus** — human-in-the-loop with durable pending actions
5. **Audit log** — append-only, who/what/when/args/result/diff
6. **Secrets provider** — never in prompts, never in plugin config plaintext
7. **Host / transport model** — `Local` | `SSH` | `RemoteAgent`
8. **Workspace / root scoping** — path jail per session
9. **Session & memory model** — episodic vs semantic vs project memory (distinct from `.ai/` docs)
10. **Observability** — traces of tool calls, token usage, plugin latency
11. **Error model** — retryable vs fatal vs needs-human
12. **Plugin manifest + signing/trust** — at least checksum + declared permissions
13. **Idempotency / dry-run / diff preview** — especially for mutate tools
14. **MCP adapter boundary** — explicit, thin, versioned
15. **Threat model document** — assets, attackers, trust boundaries

Without 3–7 and 12, “secure by default” is fiction.

---

## 5. Future scaling problems

- **Plugin count explosion** → tool namespace collisions, context window saturation, conflicting tools (`delete` × N)
- **Context bloat** — dumping kube/kafka schemas into every prompt destroys local small models (Gemma-class)
- **Process sprawl** — one MCP server process per plugin becomes operationally painful
- **State inconsistency** — agent believes cluster state from stale tool output
- **Multi-host fan-out** — N hosts × M tools without job/orchestration primitives
- **Test matrix** — every plugin × every backend × every policy mode
- **Doc drift** — `.ai/` and `docs/` diverge from code; AI agents amplify the lie
- **Open WebUI upgrades** changing MCP/tool behavior under you

Local LLM reality check: small models need **narrow tool sets per turn**, retrieval of runbooks, and strong guardrails — not 40 plugins registered globally.

---

## 6. Underestimated security issues

| Risk | Why it's worse than you think |
|---|---|
| Prompt injection via cluster logs / ticket text / README | Tool-using agents will follow malicious instructions in retrieved content |
| Docker socket = root | “Docker plugin” is often privilege escalation with extra steps |
| kubeconfig / cloud creds in agent environment | One filesystem read tool = full cluster |
| Confirmation UX fatigue | Users approve blindly; need risk-ranked, summarized diffs |
| Audit without integrity | Logs that plugins can skip are useless after incidents |
| Workspace path escape | Symlinks, `..`, `/proc`, soft links out of jail |
| SSH agent forwarding / jump hosts | Credential confusion across hosts |
| Supply chain of plugins | Unsigned plugins executing terminal is RCE-as-a-feature |
| Secrets in LLM context | Structlog redaction ≠ prompt redaction |
| Open WebUI as trusted client | If anyone can hit the MCP port, they own the host |

“Explicit confirmation” without **policy + argument inspection + dry-run + audit** is a checkbox, not a control.

---

## 7. Would you redesign the plugin system?

**Yes — partially.**

Keep plugin-*provided tools*. Redesign the contract:

```
PluginManifest
  id, version, permissions[], requires_transport[]
PluginContext
  host, workspace, secrets, policy, audit, logger  # injected, not imported globally
Tool
  name, input_model, output_model, risk_class, mutate?, dry_run?
HostTransport
  exec / read / write / port_forward  # local or SSH later
```

Hard rules:

- Plugins never open raw SSH/Docker without going through transport + policy.
- Permissions are **declared and enforced by core**, not honored by convention.
- Prefer in-process Python plugins for Stage 1; MCP wrappers for external exposure.
- Risk classes: `read`, `write_workspace`, `exec`, `cluster_mutate`, `remote_exec` — different default policies.

Do **not** redesign into microservices-per-plugin. That is premature distribution.

---

## 8. Would you redesign the runtime?

**Yes — define it before coding it.**

Current diagram:

`LLM → Open WebUI → Runtime → Loader → Plugins → Tools`

Missing the real control plane:

```
Client (Open WebUI / CLI)
    ↓
Gateway (authn, session)
    ↓
Agent Runtime (loop, budgets, memory retrieval)
    ↓
Policy + Approval
    ↓
Tool Dispatcher
    ↓
Plugin Tools → Host Transport → Systems
    ↓
Audit + Event Log
```

Own the agent loop. Treat Open WebUI as one client. CLI should use the same runtime API — that forces clean boundaries early.

---

## 9. Would you redesign the project layout?

**Mildly.** Layout is premature scaffolding, not wrong.

Problems:

- Empty top-level dirs (`plugins/`, `memory/`, `mcp/`, `prompts/`, …) invite conflicting conventions.
- Architecture docs empty while tree looks “complete.”
- Ambiguity: are plugins in-repo packages, entry points, or separate distributions?

Recommendation:

- `src/opspilot/{runtime,plugins_api,policy,audit,mcp_server}/`
- `plugins/` only for first-party plugins with a **required** manifest schema
- Delete or stub-with-README any empty architecture file that pretends to be done
- Keep `workspace/` as **runtime data**, not source — and gitignore secrets aggressively

Layout is not the crisis. **Contracts** are.

---

## 10. Would you redesign the AI memory structure?

**Yes.**

Today it duplicates marketing status. At 100k LOC it becomes a second buggy README.

Better model:

| File | Role | Constraint |
|---|---|---|
| `PROJECT.md` | Stable north star | Rarely changes |
| `STATUS.yaml` | Machine-readable truth | Schema + CI check vs code |
| `ROADMAP.yaml` | Capability roadmap, not tool wishlist | Risk-ordered |
| `DECISIONS.md` → `docs/adr/NNNN-*.md` | Real ADRs | Context/decision/consequences |
| `CONTEXT.md` | *Volatile* working memory | Size-capped; dated |
| `TASKS.md` | Generated or linked to issues | Don't dual-maintain forever |

Add: `ARCHITECTURE_INDEX.md` pointing to non-empty specs. Add freshness: `last_reviewed`, owners, “if conflicting, code wins.”

---

## 11. What a Principal Engineer (Google/OpenAI/Anthropic) would change

1. Stop coding features; write **threat model + plugin ABI + runtime state machine** first.
2. Separate **product vision** (DevOps platform) from **MVP execution system** (safe local tools + approval).
3. Make **policy/approval/audit** non-optional core.
4. Treat MCP as **interop**, not identity.
5. Design for **small local models**: tool retrieval, short schemas, strong system prompts, fewer tools per turn.
6. Require **dry-run / diff** for mutating tools from day one.
7. Replace vibe ADRs with real ones; delete empty architecture files or fill them.
8. Define SLOs for the agent: max blast radius, max unattended actions = 0 until Stage 5.
9. Build **CLI-first** runtime tests; UI is last.
10. Instrument everything; an unobservable agent is undebuggable.

---

## 12. What should absolutely be fixed BEFORE writing more code?

Absolute blockers:

1. **Fill or remove** empty architecture docs — no hollow authority.
2. **Write Plugin ABI + Manifest** (Pydantic models + examples).
3. **Write Security model + threat model** (trust boundaries, confirmation protocol).
4. **Decide OpsPilot↔Open WebUI integration mode** (MCP server vs other) in an ADR with consequences.
5. **Define Host/Transport + Workspace** so filesystem doesn't hardcode local disk.
6. **Define core vs plugin responsibility matrix** — what may *never* be a plugin.
7. **Risk taxonomy for tools** + default policies for Stage 1.
8. **Replace DECISIONS.md one-liners** with real ADR-0001… for the above.

Until then, every line of plugin code is speculative.

---

## 13. If this project reaches 100k lines, what decisions made today will hurt?

- Unversioned plugin interfaces → forever breaking changes or forever `if plugin_id == ...`
- Secrets and host access via ambient env → incident waiting to happen
- God-runtime that imports plugins directly → untestable
- Prompt/stringly-typed tools without Pydantic I/O → silent tool misuse
- Open WebUI-shaped session state inside core → can't go multi-client
- Markdown-only architecture → five AIs, five architectures
- Per-tool confirmation without policy aggregation → UX death / rubber-stamp approvals
- No audit integrity → can't do RCA on the agent itself
- Global tool registration without retrieval → local LLM collapse

---

## 14. Prioritized roadmap by risk reduction (not feature count)

1. **Contracts:** Plugin ABI, Tool schema, Manifest, permissions
2. **Security spine:** Policy engine + Approval + Audit (even if only filesystem)
3. **Host/Workspace/Transport** (local only implementation, SSH-shaped interface)
4. **Runtime loop + CLI driver** (testable without UI)
5. **MCP adapter** exposing the same tools to Open WebUI
6. **Filesystem plugin** (read-only default, jail, symlink defenses)
7. **Git plugin** (read + explicit write)
8. **Terminal plugin** with allowlist / deny patterns / confirmation
9. **Docker plugin** with explicit socket risk warnings + policy
10. **Dry-run/diff framework** for mutators
11. **Memory v0** (session transcript + structured action log — not RAG cosplay)
12. Then Kubernetes/Postgres/etc. as plugins on the stable spine
13. SSH transport implementation of existing interface
14. Planning / multi-step / semi-autonomy **only after** audit+policy proven

Notice: Kafka does not appear until the spine exists. Correct.

---

## 15. If you had only ONE chance to redesign the foundation today, what would you change?

**Make the foundation a sealed execution kernel, not a plugin loader.**

The kernel owns:

- session
- policy
- approval
- audit
- secrets
- host transport
- tool dispatch

Plugins only **register tools** into that kernel under declared permissions.

Everything else — Open WebUI, MCP, LM Studio, Gemma, future vLLM — is a client or a model backend behind a thin interface.

That single change prevents the failure mode this design is currently sleepwalking into: a pile of powerful plugins with no enforceable safety substrate, glued together by markdown aspirations and an empty `runtime.md`.

---

## Bottom line

The vision is worth building. The current “architecture” is a **bootstrap narrative**, not a platform design. The expensive mistake would be implementing filesystem/terminal/docker plugins before the **kernel contracts** exist — you would then retrofit safety onto code that already assumes trust.

Painful truth: you do not need more folders, more planned plugins, or more principle statements. You need five real specs and one ADR that chooses how Open WebUI talks to OpsPilot. After that, code. Not before.
