# OpsPilot File Version Review

Generated: 2026-07-25 13:39:22.730838

Duplicate groups found: 15

---

## src/opspilot/core/tool.py

- `src/opspilot/core/tool.py` (35 lines)
- `src/opspilot/core/tool2.py` (124 lines)

### Diff: previous → latest

```diff
--- src/opspilot/core/tool.py
+++ src/opspilot/core/tool2.py
@@ -1,35 +1,124 @@
 from __future__ import annotations
 
 from abc import ABC, abstractmethod
-from typing import Any
+from typing import Any, Type
 
-from pydantic import BaseModel
+from pydantic import BaseModel, Field
 
-from opspilot.core.models import RiskClass, ToolPermission, ToolResult
+from opspilot.core.models import (
+    RiskLevel,
+    ToolRequest,
+    ToolResult,
+)
+
+
+class ToolDefinition(BaseModel):
+    """
+    Metadata describing a tool exposed by a plugin.
+
+    Runtime uses this information for:
+    - discovery
+    - validation
+    - policy checks
+    - approval decisions
+    - audit
+    """
+
+    name: str = Field(
+        description="Unique tool name"
+    )
+
+    description: str
+
+    input_model: str = Field(
+        description="Qualified input model name"
+    )
+
+    output_model: str = Field(
+        description="Qualified output model name"
+    )
+
+    risk_level: RiskLevel
+
+    mutates: bool = False
+
+    requires_confirmation: bool = False
+
+    permissions: list[str] = Field(
+        default_factory=list
+    )
 
 
 class Tool(ABC):
     """
-    Base class for every executable tool.
+    Base contract for executable tools.
+
+    Tools are owned by plugins.
+    Execution is controlled by Runtime.
     """
 
-    name: str
-    description: str
-
-    permission: ToolPermission
-    risk: RiskClass
-
-    input_model: type[BaseModel]
-    output_model: type[BaseModel] = ToolResult
-
-    requires_confirmation: bool = False
-    supports_dry_run: bool = False
+    definition: ToolDefinition
 
     @abstractmethod
     async def execute(
         self,
-        arguments: BaseModel,
-        *,
-        dry_run: bool = False,
+        request: ToolRequest,
     ) -> ToolResult:
+        """
+        Execute the tool.
+
+        Tool implementations must not:
+        - bypass policy
+        - bypass approval
+        - access secrets directly
+        - write audit records directly
+        """
         raise NotImplementedError
+
+
+class ToolRegistry:
+    """
+    Central registry of available tools.
+
+    Runtime owns the registry.
+    Plugins only register tools.
+    """
+
+    def __init__(self) -> None:
+        self._tools: dict[str, Tool] = {}
+
+    def register(
+        self,
+        tool: Tool,
+    ) -> None:
+
+        name = tool.definition.name
+
+        if name in self._tools:
+            raise ValueError(
+                f"Tool already registered: {name}"
+            )
+
+        self._tools[name] = tool
+
+    def get(
+        self,
+        name: str,
+    ) -> Tool:
+
+        try:
+            return self._tools[name]
+
+        except KeyError:
+            raise KeyError(
+                f"Unknown tool: {name}"
+            )
+
+    def list(
+        self,
+    ) -> list[ToolDefinition]:
+
+        return [
+            tool.definition
+            for tool in self._tools.values()
+        ]
```

---

## src/opspilot/core/models.py

- `src/opspilot/core/models.py` (44 lines)
- `src/opspilot/core/models2.py` (88 lines)

### Diff: previous → latest

```diff
--- src/opspilot/core/models.py
+++ src/opspilot/core/models2.py
@@ -1,44 +1,88 @@
 from __future__ import annotations
 
-from datetime import UTC, datetime
+from datetime import datetime
 from enum import Enum
-from uuid import uuid4
+from typing import Any
+from uuid import UUID, uuid4
 
 from pydantic import BaseModel, Field
 
 
-class RiskClass(str, Enum):
+class RiskLevel(str, Enum):
     READ = "read"
-    WRITE = "write"
+    WRITE_WORKSPACE = "write_workspace"
     EXEC = "exec"
     CLUSTER_MUTATE = "cluster_mutate"
     REMOTE_EXEC = "remote_exec"
 
 
-class ToolPermission(str, Enum):
-    FILESYSTEM = "filesystem"
-    TERMINAL = "terminal"
-    GIT = "git"
-    DOCKER = "docker"
-    KUBERNETES = "kubernetes"
-    KAFKA = "kafka"
-    POSTGRES = "postgres"
-    SENTRY = "sentry"
+class ExecutionStatus(str, Enum):
+    CREATED = "created"
+    PLANNING = "planning"
+    WAITING_FOR_APPROVAL = "waiting_for_approval"
+    EXECUTING = "executing"
+    COMPLETED = "completed"
+    FAILED = "failed"
+    REJECTED = "rejected"
+    CANCELLED = "cancelled"
 
 
-class Session(BaseModel):
-    id: str = Field(default_factory=lambda: str(uuid4()))
-    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
-    user: str = "local"
+class ToolRequest(BaseModel):
+    """
+    Immutable request entering runtime.
+    """
+
+    request_id: UUID = Field(default_factory=uuid4)
+
+    session_id: str
+
+    user: str
+
+    tool_name: str
+
+    arguments: dict[str, Any] = Field(default_factory=dict)
+
+    target: str | None = None
+
+    created_at: datetime = Field(
+        default_factory=datetime.utcnow
+    )
 
 
 class ToolResult(BaseModel):
+    """
+    Standard output from every tool execution.
+    """
+
+    request_id: UUID
+
     success: bool
-    message: str | None = None
-    data: dict | list | str | None = None
+
+    output: Any | None = None
+
+    error: str | None = None
+
+    finished_at: datetime = Field(
+        default_factory=datetime.utcnow
+    )
 
 
-class ApprovalDecision(str, Enum):
-    APPROVED = "approved"
-    DENIED = "denied"
-    NOT_REQUIRED = "not_required"
+class ExecutionContext(BaseModel):
+    """
+    Context passed during execution.
+
+    Plugins receive context.
+    They do not create their own.
+    """
+
+    session_id: str
+
+    user: str
+
+    workspace: str
+
+    host: str | None = None
+
+    metadata: dict[str, Any] = Field(
+        default_factory=dict
+    )
```

---

## src/opspilot/plugin_loader/loader.py

- `src/opspilot/plugin_loader/loader.py` (18 lines)
- `src/opspilot/plugin_loader/loader2.py` (40 lines)

### Diff: previous → latest

```diff
--- src/opspilot/plugin_loader/loader.py
+++ src/opspilot/plugin_loader/loader2.py
@@ -1,18 +1,40 @@
 from __future__ import annotations
+
+from collections.abc import Iterable
 
 from opspilot.core.plugin import Plugin
 
 
 class PluginLoader:
     """
-    Responsible for loading plugins.
+    Loads and manages plugins.
+
+    Stage-1:
+        Plugins are instantiated manually.
+
+    Future:
+        entry_points()
+        manifest validation
+        signature verification
+        dependency resolution
     """
 
-    def load(self) -> list[Plugin]:
-        """
-        Load all enabled plugins.
+    def __init__(self) -> None:
+        self._plugins: dict[str, Plugin] = {}
 
-        Dynamic discovery will be implemented later.
-        """
+    def register(self, plugin: Plugin) -> None:
+        if plugin.id in self._plugins:
+            raise ValueError(
+                f"Plugin '{plugin.id}' already registered."
+            )
 
-        return []
+        self._plugins[plugin.id] = plugin
+
+    def get(self, plugin_id: str) -> Plugin:
+        return self._plugins[plugin_id]
+
+    def all(self) -> Iterable[Plugin]:
+        return self._plugins.values()
+
+    def exists(self, plugin_id: str) -> bool:
+        return plugin_id in self._plugins
```

---

## src/opspilot/runtime/plugin.py

- `src/opspilot/runtime/plugin.py` (27 lines)
- `src/opspilot/runtime/plugin2.py` (21 lines)
- `src/opspilot/runtime/plugin3.py` (31 lines)
- `src/opspilot/runtime/plugin4.py` (38 lines)

### Diff: previous → latest

```diff
--- src/opspilot/runtime/plugin3.py
+++ src/opspilot/runtime/plugin4.py
@@ -1,31 +1,38 @@
 from __future__ import annotations
 
 from abc import ABC, abstractmethod
+from typing import Iterable
 
-from opspilot.core.plugin_manifest import PluginManifest
-from opspilot.core.tool import Tool
+from opspilot.runtime.context import RuntimeContext
+from opspilot.runtime.models import ToolDefinition, ToolRequest, ToolResult
 
 
 class Plugin(ABC):
     """
-    Base interface for every OpsPilot plugin.
-
-    A plugin is only responsible for registering tools.
-
-    Execution is handled by the Runtime.
+    Base class for every first-party and third-party plugin.
     """
 
-    @property
-    @abstractmethod
-    def manifest(self) -> PluginManifest:
-        """
-        Plugin metadata.
-        """
-        ...
+    id: str
+    version: str = "0.1.0"
 
     @abstractmethod
-    def tools(self) -> list[Tool]:
+    def tools(self) -> Iterable[ToolDefinition]:
         """
         Return all tools exposed by this plugin.
         """
-        ...
+
+    @abstractmethod
+    def execute(
+        self,
+        context: RuntimeContext,
+        request: ToolRequest,
+    ) -> ToolResult:
+        """
+        Execute a tool request.
+
+        The runtime guarantees that:
+
+        - policy has already been evaluated
+        - approval (if required) has completed
+        - audit has started
+        """
```

---

## src/opspilot/runtime/dispatcher.py

- `src/opspilot/runtime/dispatcher.py` (67 lines)
- `src/opspilot/runtime/dispatcher2.py` (26 lines)

### Diff: previous → latest

```diff
--- src/opspilot/runtime/dispatcher.py
+++ src/opspilot/runtime/dispatcher2.py
@@ -1,67 +1,26 @@
 from __future__ import annotations
 
-from opspilot.core.audit import AuditLogger
-from opspilot.core.policy import PolicyEngine
-from opspilot.runtime.context import RuntimeContext
 from opspilot.runtime.models import ToolRequest, ToolResult
 from opspilot.runtime.registry import ToolRegistry
 
 
 class Dispatcher:
     """
-    Central execution pipeline.
+    Dispatches validated requests to registered tools.
 
-    Flow:
+    Dispatcher does not perform:
 
-        Request
-            ↓
-        Registry
-            ↓
-        Policy
-            ↓
-        Plugin
-            ↓
-        Audit
-            ↓
-        Result
+    - authorization
+    - approval
+    - auditing
+
+    Those belong to Runtime.
     """
 
-    def __init__(
-        self,
-        registry: ToolRegistry,
-        policy: PolicyEngine,
-        audit: AuditLogger,
-    ) -> None:
-        self.registry = registry
-        self.policy = policy
-        self.audit = audit
+    def __init__(self, registry: ToolRegistry):
+        self._registry = registry
 
-    def dispatch(
-        self,
-        context: RuntimeContext,
-        request: ToolRequest,
-    ) -> ToolResult:
-        plugin, tool = self.registry.get(request.tool)
+    def dispatch(self, request: ToolRequest) -> ToolResult:
+        tool = self._registry.get(request.tool)
 
-        self.policy.authorize(
-            context,
-            tool,
-            request,
-        )
-
-        event = self.audit.start(
-            context,
-            request,
-        )
-
-        result = plugin.execute(
-            context,
-            request,
-        )
-
-        self.audit.finish(
-            event,
-            result,
-        )
-
-        return result
+        return tool.execute(request)
```

---

## src/opspilot/runtime/models.py

- `src/opspilot/runtime/models.py` (44 lines)
- `src/opspilot/runtime/models2.py` (54 lines)

### Diff: previous → latest

```diff
--- src/opspilot/runtime/models.py
+++ src/opspilot/runtime/models2.py
@@ -3,42 +3,52 @@
 from enum import Enum
 from typing import Any
 
-from pydantic import BaseModel, Field
+from pydantic import BaseModel
 
 
 class RiskClass(str, Enum):
     READ = "read"
-    WRITE = "write"
+    WRITE_WORKSPACE = "write_workspace"
     EXEC = "exec"
     CLUSTER_MUTATE = "cluster_mutate"
     REMOTE_EXEC = "remote_exec"
 
 
-class PolicyDecision(str, Enum):
-    ALLOW = "allow"
-    DENY = "deny"
-    CONFIRM = "confirm"
+class Permission(str, Enum):
+    READ_FILES = "read_files"
+    WRITE_FILES = "write_files"
+    EXEC_TERMINAL = "exec_terminal"
+    SSH = "ssh"
+
+
+class PluginManifest(BaseModel):
+    id: str
+    version: str
+    permissions: list[Permission]
+
+
+class ToolDefinition(BaseModel):
+    name: str
+    description: str
+
+    input_model: type[BaseModel]
+
+    risk: RiskClass
+
+    mutating: bool = False
+
+    dry_run: bool = False
 
 
 class ToolRequest(BaseModel):
-    plugin: str
     tool: str
-    arguments: dict[str, Any] = Field(default_factory=dict)
+
+    arguments: BaseModel
 
 
 class ToolResult(BaseModel):
     success: bool
-    output: Any = None
-    error: str | None = None
 
+    data: dict[str, Any] | None = None
 
-class AuditRecord(BaseModel):
-    plugin: str
-    tool: str
-    arguments: dict[str, Any]
-
-    decision: PolicyDecision
-
-    success: bool
-
-    duration_ms: int
+    message: str | None = None
```

---

## src/opspilot/runtime/runtime.py

- `src/opspilot/runtime/runtime.py` (21 lines)
- `src/opspilot/runtime/runtime2.py` (58 lines)

### Diff: previous → latest

```diff
--- src/opspilot/runtime/runtime.py
+++ src/opspilot/runtime/runtime2.py
@@ -1,21 +1,58 @@
 from __future__ import annotations
 
-from opspilot.core.registry import ToolRegistry
-from opspilot.plugin_loader.loader import PluginLoader
+from opspilot.runtime.approval import ApprovalProvider
+from opspilot.runtime.audit import AuditLogger
+from opspilot.runtime.dispatcher import Dispatcher
+from opspilot.runtime.models import ToolRequest, ToolResult
+from opspilot.runtime.policy import PolicyEngine
 
 
 class Runtime:
     """
-    Main execution runtime.
+    Central execution kernel.
+
+    Responsibilities
+
+    - validate request
+    - evaluate policy
+    - request approval
+    - dispatch tool
+    - audit result
+
+    Runtime never contains tool implementations.
     """
 
-    def __init__(self) -> None:
-        self.registry = ToolRegistry()
-        self.loader = PluginLoader()
+    def __init__(
+        self,
+        *,
+        dispatcher: Dispatcher,
+        policy: PolicyEngine,
+        approval: ApprovalProvider,
+        audit: AuditLogger,
+    ):
+        self._dispatcher = dispatcher
+        self._policy = policy
+        self._approval = approval
+        self._audit = audit
 
-    def initialize(self) -> None:
-        plugins = self.loader.load()
+    def execute(
+        self,
+        request: ToolRequest,
+    ) -> ToolResult:
+        """
+        Execute a single tool request.
+        """
 
-        for plugin in plugins:
-            for tool in plugin.tools():
-                self.registry.register(tool)
+        self._policy.evaluate(request)
+
+        if request.requires_confirmation:
+            approved = self._approval.approve(request)
+
+            if not approved:
+                raise PermissionError("Execution rejected by user.")
+
+        result = self._dispatcher.dispatch(request)
+
+        self._audit.log(request, result)
+
+        return result
```

---

## src/opspilot/runtime/policy.py

- `src/opspilot/runtime/policy.py` (33 lines)
- `src/opspilot/runtime/policy2.py` (18 lines)

### Diff: previous → latest

```diff
--- src/opspilot/runtime/policy.py
+++ src/opspilot/runtime/policy2.py
@@ -1,33 +1,18 @@
 from __future__ import annotations
 
-from opspilot.runtime.models import (
-    PolicyDecision,
-    RiskClass,
-)
+from abc import ABC, abstractmethod
+
+from opspilot.runtime.models import ToolRequest
 
 
-class PolicyEngine:
+class PolicyEngine(ABC):
     """
-    Stage-1 implementation.
-
-    Later this will become configurable.
+    Decides whether a tool may execute.
     """
 
-    def evaluate(self, risk: RiskClass) -> PolicyDecision:
-
-        if risk == RiskClass.READ:
-            return PolicyDecision.ALLOW
-
-        if risk == RiskClass.WRITE:
-            return PolicyDecision.CONFIRM
-
-        if risk == RiskClass.EXEC:
-            return PolicyDecision.CONFIRM
-
-        if risk == RiskClass.CLUSTER_MUTATE:
-            return PolicyDecision.CONFIRM
-
-        if risk == RiskClass.REMOTE_EXEC:
-            return PolicyDecision.CONFIRM
-
-        return PolicyDecision.DENY
+    @abstractmethod
+    def evaluate(self, request: ToolRequest) -> None:
+        """
+        Raise an exception if execution is not allowed.
+        """
+        raise NotImplementedError
```

---

## src/opspilot/runtime/audit.py

- `src/opspilot/runtime/audit.py` (18 lines)
- `src/opspilot/runtime/audit2.py` (19 lines)

### Diff: previous → latest

```diff
--- src/opspilot/runtime/audit.py
+++ src/opspilot/runtime/audit2.py
@@ -1,18 +1,19 @@
 from __future__ import annotations
 
-from opspilot.runtime.models import AuditRecord
+from abc import ABC, abstractmethod
+
+from opspilot.runtime.models import ToolRequest, ToolResult
 
 
-class AuditLogger:
+class AuditLogger(ABC):
     """
-    Stage-1 in-memory audit logger.
+    Append-only audit log.
     """
 
-    def __init__(self) -> None:
-        self.records: list[AuditRecord] = []
-
-    def append(self, record: AuditRecord) -> None:
-        self.records.append(record)
-
-    def all(self) -> list[AuditRecord]:
-        return list(self.records)
+    @abstractmethod
+    def log(
+        self,
+        request: ToolRequest,
+        result: ToolResult,
+    ) -> None:
+        raise NotImplementedError
```

---

## open-webui/cache/embedding/models/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/onnx/model_O.onnx

- `open-webui/cache/embedding/models/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/onnx/model_O1.onnx` (1 lines)
- `open-webui/cache/embedding/models/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/onnx/model_O2.onnx` (1 lines)
- `open-webui/cache/embedding/models/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/onnx/model_O3.onnx` (1 lines)
- `open-webui/cache/embedding/models/models--sentence-transformers--all-MiniLM-L6-v2/snapshots/1110a243fdf4706b3f48f1d95db1a4f5529b4d41/onnx/model_O4.onnx` (1 lines)

### Diff: previous → latest

```diff

```

---

## docs/architecture/plugin-manifest.md

- `docs/architecture/plugin-manifest.md` (60 lines)
- `docs/architecture/plugin-manifest2.md` (337 lines)

### Diff: previous → latest

```diff
--- docs/architecture/plugin-manifest.md
+++ docs/architecture/plugin-manifest2.md
@@ -1,60 +1,337 @@
-# Plugin Manifest
-
-Every plugin must provide a manifest.
-
-Example
+# Plugin Manifest Contract
+
+## Purpose
+
+A Plugin Manifest is the declaration of identity, capabilities, permissions, and compatibility requirements of an OpsPilot plugin.
+
+The Runtime Kernel uses the manifest before loading any plugin.
+
+A plugin MUST declare its capabilities explicitly.
+
+The manifest is not trusted input.
+
+The Runtime MUST validate it before registration.
+
+
+# Design Principles
+
+- Plugins declare permissions; they do not grant themselves permissions.
+- Runtime decides whether permissions are acceptable.
+- Missing declarations are treated as denied.
+- Unknown fields are rejected.
+- Plugin metadata must be versioned.
+- Plugin loading must fail closed.
+
+
+# Plugin Lifecycle
+
+Discovered
+|
+Manifest Loaded
+|
+Manifest Validated
+|
+Permission Check
+|
+Plugin Loaded
+|
+Tools Registered
+|
+Plugin Ready
+
+
+A plugin that fails any stage MUST NOT become available.
+
+
+# Manifest Location
+
+Each plugin MUST contain:
+
+
+plugin/
+├── manifest.yaml
+├── plugin.py
+├── tools.py
+└── models.py
+
+
+
+Example:
 
 ```yaml
 id: kubernetes
 
-name: Kubernetes
-
-version: 1.0.0
-
-description: Kubernetes operations
+name: Kubernetes Plugin
+
+version: 0.1.0
+
+description: >
+  Kubernetes operational tools.
+
+runtime:
+  min_version: 0.1.0
+
 
 permissions:
 
-  - cluster_read
-
-transport:
+  - CLUSTER_READ
+
+  - CLUSTER_MUTATE
+
+
+transports:
 
   - local
 
-  - ssh
+  - kubernetes
+
 
 tools:
 
-  - get_pods
-
-  - logs
-
-  - describe
-```
-
----
-
-## Required Fields
-
-- id
-- version
-- description
-- permissions
-- transport
-- tools
-
----
-
-## Validation
-
-Manifest is validated by Runtime before loading.
-
-Invalid plugins are rejected.
-
----
-
-## Rule
-
-Plugins declare capabilities.
-
-Runtime decides whether they may execute.
+  - kubernetes.list_pods
+
+  - kubernetes.restart_deployment
+
+
+security:
+
+  requires_confirmation:
+    - kubernetes.restart_deployment
+
+  supports_dry_run:
+    - kubernetes.restart_deployment
+Required Fields
+
+Every manifest MUST define:
+
+id
+
+Unique plugin identifier.
+
+Rules:
+
+lowercase
+stable
+never reused
+
+Example:
+
+kubernetes
+postgres
+docker
+version
+
+Semantic version.
+
+Example:
+
+1.2.0
+
+Version changes:
+
+MAJOR
+Breaking contract change
+
+MINOR
+New capability
+
+PATCH
+Bug fix
+description
+
+Human readable explanation.
+
+Used for:
+
+UI display
+AI context
+audit records
+permissions
+
+Declared capabilities required by plugin.
+
+Examples:
+
+FILE_READ
+
+FILE_WRITE
+
+WORKSPACE_WRITE
+
+PROCESS_EXEC
+
+DOCKER_ACCESS
+
+KUBERNETES_READ
+
+KUBERNETES_MUTATE
+
+REMOTE_EXEC
+
+A plugin MUST NOT receive permissions it did not declare.
+
+Permission Model
+
+Permissions are evaluated by Runtime.
+
+Flow:
+
+Plugin Manifest
+
+        |
+
+Requested Permissions
+
+        |
+
+Policy Engine
+
+        |
+
+Allowed / Denied
+
+The plugin cannot override policy decisions.
+
+Transport Requirements
+
+Plugins MUST declare required transports.
+
+Supported transports:
+
+local
+
+Operations on current machine.
+
+Example:
+
+filesystem
+git
+docker
+ssh
+
+Operations on remote machines.
+
+Example:
+
+remote filesystem
+remote docker
+kubernetes
+
+Operations through Kubernetes API.
+
+Example:
+
+kubectl
+API clients
+Tool Registration
+
+Plugins declare tools.
+
+Example:
+
+tools:
+
+  - git.status
+
+  - git.diff
+
+  - git.commit
+
+Runtime validates:
+
+tool name uniqueness
+schema availability
+permissions
+risk classification
+
+Duplicate tool names MUST fail registration.
+
+Plugin Isolation Rules
+
+Plugins MUST NOT:
+
+import Runtime internals
+access other plugins directly
+modify global state
+bypass Policy Engine
+write audit logs directly
+access secrets directly
+
+Plugins receive dependencies through:
+
+PluginContext
+
+Example:
+
+PluginContext(
+    logger,
+    audit,
+    policy,
+    transport,
+    workspace
+)
+Secrets Handling
+
+Plugins never receive raw secrets.
+
+Forbidden:
+
+password = context.secrets.get("db_password")
+
+Allowed:
+
+credential = context.secret_ref(
+    "database-prod"
+)
+
+Runtime resolves secrets only at execution boundary.
+
+Trust Model
+
+Plugins are considered:
+
+Untrusted code
+
+Even first-party plugins must follow:
+
+permission declaration
+audit rules
+policy enforcement
+Future External Plugins
+
+The manifest format supports future:
+
+Python plugins
+MCP tools
+Remote agents
+Signed extensions
+
+Example future:
+
+type: external_mcp
+
+endpoint:
+  transport: stdio
+Validation Rules
+
+Runtime MUST reject:
+
+missing id
+invalid version
+unknown permission
+duplicate tools
+unsupported transport
+invalid schema references
+Security Requirement
+
+The manifest describes what a plugin wants.
+
+It does NOT describe what a plugin is allowed to do.
+
+Final authority:
+
+Runtime Kernel
+        |
+Policy Engine
+        |
+Approval System
```

---

## docs/architecture/audit.md

- `docs/architecture/audit.md` (63 lines)
- `docs/architecture/audit2.md` (69 lines)

### Diff: previous → latest

```diff
--- docs/architecture/audit.md
+++ docs/architecture/audit2.md
@@ -1,63 +1,69 @@
-# Audit System
+# Approval System
 
-Every tool execution is recorded.
+## Purpose
 
-Audit cannot be disabled.
+The Approval System prevents dangerous operations from executing without explicit user consent.
 
 ---
 
-## Audit Record
+## Principles
 
-Timestamp
+Approval is determined by Policy.
 
-Session ID
-
-Plugin
-
-Tool
-
-Arguments
-
-Duration
-
-Result
-
-Status
-
-User
-
-Host
-
-Transport
+Approval is never decided by plugins.
 
 ---
 
-## Status
+## Approval Request
 
-SUCCESS
+An approval request contains:
 
-FAILED
-
-DENIED
-
-CANCELLED
-
-TIMEOUT
+- operation
+- plugin
+- tool
+- target
+- arguments
+- risk class
+- estimated impact
+- dry-run result (if available)
+- diff preview (if available)
 
 ---
 
-## Goals
+## Approval Result
 
-Traceability
+Possible outcomes:
 
-Debugging
-
-Security
-
-Compliance
+- Approved
+- Rejected
+- Expired
 
 ---
 
-## Rule
+## Rules
 
-A tool that is not audited is considered not executed.
+READ operations should not require approval.
+
+WRITE operations may require approval.
+
+EXEC operations usually require approval.
+
+REMOTE_EXEC always requires approval.
+
+CLUSTER_MUTATE always requires approval.
+
+---
+
+## Timeout
+
+Approval requests expire after a configurable timeout.
+
+Expired requests never execute automatically.
+
+---
+
+## Audit
+
+Every approval decision is recorded.
+
+Approved or rejected actions are both auditable.
```

---

## docs/architecture/tool-contract.md

- `docs/architecture/tool-contract.md` (65 lines)
- `docs/architecture/tool-contract2.md` (292 lines)

### Diff: previous → latest

```diff
--- docs/architecture/tool-contract.md
+++ docs/architecture/tool-contract2.md
@@ -1,65 +1,292 @@
 # Tool Contract
 
-Every tool exposed by OpsPilot follows the same contract.
-
----
-
-## Required Fields
-
-Every tool has:
-
-- id
-- name
-- description
-- version
-- input schema
-- output schema
-- risk class
-
----
-
-## Input
-
-Inputs are validated using Pydantic models.
-
-Invalid requests never reach plugins.
-
----
-
-## Output
-
-Tools return structured objects.
-
-Tools never return formatted markdown.
-
-Formatting belongs to the client.
-
----
-
-## Error Handling
-
-Tools never raise raw exceptions.
-
-Expected failures are returned as structured errors.
-
-Unexpected failures are converted into Runtime errors.
-
----
-
-## Dry Run
-
-Mutating tools should support dry-run whenever technically possible.
-
----
-
-## Idempotency
-
-Read operations should always be idempotent.
-
-Mutating operations should document idempotency guarantees.
-
----
-
-## Versioning
-
-Breaking changes require a new major version.
+## Purpose
+
+A Tool is the smallest executable capability exposed by OpsPilot.
+
+Tools are provided by plugins but are controlled by the Runtime Kernel.
+
+A Tool is NOT allowed to bypass:
+
+- Policy Engine
+- Approval System
+- Audit System
+- Host Transport
+- Session Context
+
+
+## Design Principles
+
+- Tools must have explicit input and output schemas.
+- Tools must declare their risk level.
+- Tools must support dry-run when mutation is possible.
+- Tools must be deterministic whenever possible.
+- Tools must never access credentials directly.
+- Tools must never execute outside the provided execution context.
+
+
+# Tool Lifecycle
+
+Registered
+|
+Validated
+|
+Available
+|
+Requested
+|
+Policy Evaluation
+|
+Approval (if required)
+|
+Execution
+|
+Audit
+|
+Completed / Failed
+
+
+
+# Tool Definition
+
+Every tool MUST define:
+
+
+Tool
+├── name
+├── description
+├── input_model
+├── output_model
+├── risk_class
+├── mutating
+├── supports_dry_run
+├── timeout
+└── required_permissions
+
+
+
+# Risk Classification
+
+## READ
+
+Examples:
+
+- list pods
+- get kafka topic metadata
+- read git status
+
+
+Default:
+
+
+Allowed
+Audit required
+
+
+
+---
+
+## WRITE_WORKSPACE
+
+Examples:
+
+- create file
+- modify configuration
+- generate report
+
+
+Default:
+
+
+Allowed with workspace restriction
+Audit required
+
+
+
+---
+
+## EXEC
+
+Examples:
+
+- run shell command
+- execute docker command
+
+
+Default:
+
+
+Confirmation required
+
+
+
+---
+
+## CLUSTER_MUTATE
+
+Examples:
+
+- kubectl delete
+- scale deployment
+- modify resources
+
+
+Default:
+
+
+Dry-run required when supported
+
+Strong confirmation required
+
+Audit mandatory
+
+
+
+---
+
+## REMOTE_EXEC
+
+Examples:
+
+- SSH command execution
+- remote agent execution
+
+
+Default:
+
+
+Always confirmation required
+
+
+
+# Input Model
+
+Tools MUST use typed schemas.
+
+Example:
+
+```python
+class DeletePodInput(BaseModel):
+
+    namespace: str
+
+    pod_name: str
+
+    dry_run: bool = True
+
+Never:
+
+dict[str, Any]
+
+because:
+
+validation is impossible
+security inspection is impossible
+UI generation is impossible
+Output Model
+
+Every tool returns:
+
+class ToolResult(BaseModel):
+
+    success: bool
+
+    summary: str
+
+    data: dict
+
+    error: str | None
+
+    execution_time_ms: int
+Mutation Rules
+
+Mutating tools MUST:
+
+Support dry-run if possible.
+Return planned changes before execution.
+Include target resource.
+Include affected scope.
+Generate audit events.
+
+Example:
+
+Bad:
+
+delete(namespace,pod)
+
+Good:
+
+delete_pod(
+ namespace="prod",
+ pod="api-123",
+ dry_run=True
+)
+Cancellation
+
+Tools MUST:
+
+respect cancellation signals
+stop long operations
+report partial execution
+
+Tools MUST NOT:
+
+ignore timeout
+create background jobs without registration
+Error Handling
+
+Tools return typed errors.
+
+Examples:
+
+ValidationError
+
+PermissionDenied
+
+PolicyRejected
+
+ApprovalRequired
+
+TransportError
+
+ExecutionFailed
+
+Timeout
+Tool Ownership
+
+Plugins own:
+
+implementation
+domain knowledge
+schemas
+
+Runtime owns:
+
+execution order
+authorization
+approval
+timeout
+audit
+lifecycle
+Forbidden Behavior
+
+A Tool MUST NOT:
+
+call another plugin directly
+access secrets directly
+modify audit records
+bypass policy
+ask user directly
+use global configuration
+open raw SSH sessions
+call subprocess without HostTransport
+Future Compatibility
+
+The contract supports:
+
+Python plugins
+MCP adapters
+Remote agents
+External tool providers
+
+The Runtime API remains stable regardless of tool implementation.
```

---

## plugins/filesystem/tools.py

- `plugins/filesystem/tools.py` (26 lines)
- `plugins/filesystem/tools2.py` (96 lines)

### Diff: previous → latest

```diff
--- plugins/filesystem/tools.py
+++ plugins/filesystem/tools2.py
@@ -1,26 +1,96 @@
 from __future__ import annotations
 
-from opspilot.plugins.filesystem.models import (
-    ReadFileInput,
-    WriteFileInput,
-)
-from opspilot.runtime.models import (
-    RiskClass,
-    ToolDefinition,
-)
+from pathlib import Path
 
-TOOLS = [
-    ToolDefinition(
-        name="filesystem.read_file",
-        description="Read a UTF-8 text file.",
-        input_model=ReadFileInput,
-        risk=RiskClass.READ,
-    ),
-    ToolDefinition(
-        name="filesystem.write_file",
-        description="Write a UTF-8 text file.",
-        input_model=WriteFileInput,
-        risk=RiskClass.WRITE_WORKSPACE,
-        mutating=True,
-    ),
-]
+from opspilot.runtime.models import ToolRequest, ToolResult
+from opspilot.runtime.tool import Tool
+
+
+class ReadFileTool(Tool):
+
+    name = "filesystem.read_file"
+
+    description = "Read a text file."
+
+    risk = "READ"
+
+    mutating = False
+
+    supports_dry_run = False
+
+    def execute(
+        self,
+        request: ToolRequest,
+    ) -> ToolResult:
+
+        path = Path(request.arguments["path"])
+
+        return ToolResult(
+            success=True,
+            data={
+                "content": path.read_text(),
+            },
+        )
+
+
+class WriteFileTool(Tool):
+
+    name = "filesystem.write_file"
+
+    description = "Write a text file."
+
+    risk = "WRITE_WORKSPACE"
+
+    mutating = True
+
+    supports_dry_run = True
+
+    def execute(
+        self,
+        request: ToolRequest,
+    ) -> ToolResult:
+
+        path = Path(request.arguments["path"])
+
+        path.write_text(request.arguments["content"])
+
+        return ToolResult(
+            success=True,
+        )
+
+
+class ListDirectoryTool(Tool):
+
+    name = "filesystem.list_directory"
+
+    description = "List directory."
+
+    risk = "READ"
+
+    mutating = False
+
+    supports_dry_run = False
+
+    def execute(
+        self,
+        request: ToolRequest,
+    ) -> ToolResult:
+
+        path = Path(request.arguments["path"])
+
+        entries = []
+
+        for item in path.iterdir():
+            entries.append(
+                {
+                    "name": item.name,
+                    "is_dir": item.is_dir(),
+                }
+            )
+
+        return ToolResult(
+            success=True,
+            data={
+                "entries": entries,
+            },
+        )
```

---

## plugins/filesystem/plugin.py

- `plugins/filesystem/plugin.py` (62 lines)
- `plugins/filesystem/plugin2.py` (28 lines)

### Diff: previous → latest

```diff
--- plugins/filesystem/plugin.py
+++ plugins/filesystem/plugin2.py
@@ -1,17 +1,10 @@
 from __future__ import annotations
 
 from opspilot.core.plugin import Plugin
-from opspilot.plugins.filesystem.models import (
-    ReadFileInput,
-    WriteFileInput,
-)
-from opspilot.plugins.filesystem.service import FilesystemService
-from opspilot.plugins.filesystem.tools import TOOLS
-from opspilot.runtime.context import RuntimeContext
-from opspilot.runtime.models import (
-    ToolDefinition,
-    ToolRequest,
-    ToolResult,
+from .tools import (
+    ListDirectoryTool,
+    ReadFileTool,
+    WriteFileTool,
 )
 
 
@@ -19,44 +12,17 @@
 
     id = "filesystem"
 
-    def __init__(self) -> None:
-        self.service = FilesystemService()
+    version = "0.1.0"
 
-    def tools(self) -> list[ToolDefinition]:
-        return TOOLS
+    def initialize(self) -> None:
+        pass
 
-    def execute(
-        self,
-        context: RuntimeContext,
-        request: ToolRequest,
-    ) -> ToolResult:
+    def shutdown(self) -> None:
+        pass
 
-        match request.tool:
-
-            case "filesystem.read_file":
-
-                args = request.arguments
-                assert isinstance(args, ReadFileInput)
-
-                content = self.service.read(args.path)
-
-                return ToolResult(
-                    success=True,
-                    data={"content": content},
-                )
-
-            case "filesystem.write_file":
-
-                args = request.arguments
-                assert isinstance(args, WriteFileInput)
-
-                self.service.write(
-                    args.path,
-                    args.content,
-                )
-
-                return ToolResult(success=True)
-
-        raise ValueError(
-            f"Unknown tool '{request.tool}'."
-        )
+    def tools(self):
+        return [
+            ReadFileTool(),
+            WriteFileTool(),
+            ListDirectoryTool(),
+        ]
```

---
