from __future__ import annotations

from enum import StrEnum


class RiskClass(StrEnum):
    READ = "read"
    WRITE_WORKSPACE = "write_workspace"
    EXEC = "exec"
    CLUSTER_MUTATE = "cluster_mutate"
    REMOTE_EXEC = "remote_exec"
    SYSTEM = "system"
