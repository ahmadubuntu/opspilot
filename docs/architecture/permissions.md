# Permission Model

Every tool declares permissions.

Permissions are enforced by the Runtime.

Plugins cannot bypass permission checks.

## Standard Permissions

filesystem.read

filesystem.write

terminal.exec

docker.read

docker.write

git.read

git.write

kubernetes.read

kubernetes.write

postgres.read

postgres.write

network.connect

remote.exec

memory.read

memory.write

audit.read

policy.override

Permissions are additive.

No wildcard permissions are allowed.
