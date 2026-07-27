from __future__ import annotations

from enum import StrEnum


class Permission(StrEnum):
    WORKSPACE_READ = "workspace.read"
    WORKSPACE_WRITE = "workspace.write"
    TERMINAL_EXEC = "terminal.exec"
    GIT_READ = "git.read"
    GIT_WRITE = "git.write"
    DOCKER_READ = "docker.read"
    DOCKER_WRITE = "docker.write"
    KUBERNETES_READ = "kubernetes.read"
    KUBERNETES_WRITE = "kubernetes.write"
    POSTGRES_READ = "postgres.read"
    POSTGRES_WRITE = "postgres.write"
    KAFKA_READ = "kafka.read"
    KAFKA_WRITE = "kafka.write"
    NETWORK_CONNECT = "network.connect"
    REMOTE_EXEC = "remote.exec"
