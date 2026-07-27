# Tool Lifecycle

Every tool execution MUST follow the same lifecycle.

## 1. Discovery

The runtime selects candidate tools based on:

- capability
- permissions
- current transport
- current workspace

## 2. Planning

The LLM generates an execution plan.

The runtime validates:

- tool exists
- arguments match schema
- permissions are satisfied

No tool executes during planning.

---

## 3. Approval

If tool.risk != READ

runtime creates a pending approval.

The user must explicitly approve.

---

## 4. Execution

Dispatcher invokes plugin.

Plugin receives:

- PluginContext
- validated input

Plugin returns structured output.

Never markdown.

---

## 5. Audit

Audit entry is written.

Includes:

- user
- session
- tool
- arguments
- execution time
- result
- errors

---

## 6. Memory

Only successful executions are eligible for memory.

Memory is optional.

Audit is mandatory.
