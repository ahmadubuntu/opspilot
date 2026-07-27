# Host Transport

## Purpose

HostTransport abstracts execution against different execution environments.

The Runtime never interacts directly with the operating system.

Instead, every operation is performed through a HostTransport implementation.

---

## Supported Transports

Current:

- LocalHostTransport

Future:

- SSHHostTransport
- RemoteAgentTransport
- KubernetesExecTransport
- DockerTransport

---

## Responsibilities

A transport may provide:

- execute commands
- read files
- write files
- create directories
- remove files
- list directories
- upload files
- download files
- port forwarding

---

## Design Rules

Runtime depends only on the HostTransport interface.

Plugins never instantiate transports.

Plugins receive a transport from Runtime.

---

## Security

Transport never performs authorization.

Authorization belongs to Policy Engine.

Transport executes only approved requests.

---

## Future

Future transports must implement exactly the same interface.

No plugin should know whether execution is local or remote.
