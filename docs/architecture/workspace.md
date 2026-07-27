# Workspace Architecture

## Purpose

Workspace defines the filesystem scope available to OpsPilot.

Every tool operates inside a Workspace.

Workspace is independent of transport.

The same Workspace API works for:

- Local machine
- SSH host
- Future Remote Agent

---

# Workspace Responsibilities

Workspace is responsible for:

- path resolution
- root enforcement
- file discovery
- safe relative paths

Workspace is NOT responsible for:

- authorization
- approvals
- transport
- auditing

---

# Root

Every session has exactly one workspace root.

Examples:

```

~/projects/opspilot

```

or

```

/srv/project

```

or

```

remote:/home/dev/project

```

---

# Path Rules

Allowed:

```

README.md

docs/runtime.md

src/main.py

```

Rejected:

```

../../etc/passwd

/etc/shadow

~/.ssh

```

Symlink escapes must also be rejected.

---

# Isolation

Workspace must prevent access outside its root.

No plugin may bypass Workspace.

All filesystem operations pass through Workspace.

---

# Remote Support

Workspace APIs never assume local files.

Examples:

```

workspace.read(...)

workspace.write(...)

workspace.list(...)

```

Runtime decides whether requests are executed locally or remotely.

Plugins do not know.

---

# Multiple Workspaces

Future versions may support multiple workspaces.

Current Runtime supports exactly one active workspace per session.

---

# Interaction

```

Plugin
↓
Workspace
↓
Transport
↓
Host Filesystem

```

---

# Principles

- One root per session
- No path traversal
- No absolute paths
- Remote-first API
- Transport-independent
- Workspace never performs authorization
