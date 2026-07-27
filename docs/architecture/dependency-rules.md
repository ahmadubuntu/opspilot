# Dependency Rules

Dependencies point inward.

Runtime knows plugins.

Plugins do not know Runtime internals.

Policy knows nothing about plugins.

Audit knows nothing about transport.

Transport knows nothing about Kubernetes, Docker, Git, or PostgreSQL.

LLM providers never call plugins directly.

Only the Dispatcher may invoke tools.

Circular dependencies are prohibited.
