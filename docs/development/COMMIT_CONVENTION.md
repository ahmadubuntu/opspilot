# Commit Message Convention

## Goal

This project follows the Conventional Commits specification to keep the Git history clean, searchable, and automation-friendly.

Benefits:

- Consistent commit history
- Easier code reviews
- Automatic changelog generation
- Semantic versioning support
- Better AI-assisted development

---

## Format

<type>: <short description>

Example:

feat: add Docker plugin
fix: handle missing kubeconfig
docs: update installation guide

---

## Commit Types

### feat

A new feature.

Examples:

feat: add filesystem plugin
feat: support MCP server discovery

---

### fix

Bug fixes.

Examples:

fix: resolve plugin loading issue
fix: handle empty workspace

---

### build

Build system, packaging, Docker, dependencies.

Examples:

build: bootstrap OpsPilot project
build: update Docker image
build: migrate to uv

---

### docs

Documentation only.

Examples:

docs: add architecture overview
docs: improve README

---

### refactor

Code restructuring without changing behavior.

Examples:

refactor: simplify plugin loader
refactor: split runtime module

---

### test

Tests only.

Examples:

test: add filesystem plugin tests
test: improve CLI coverage

---

### perf

Performance improvements.

Examples:

perf: reduce plugin startup latency
perf: optimize directory scanning

---

### security

Security improvements.

Examples:

security: restrict filesystem access
security: validate plugin permissions

---

### ci

Continuous Integration / GitHub Actions / automation.

Examples:

ci: add GitHub workflow
ci: run pytest on pull requests

---

### chore

Repository maintenance that doesn't fit other categories.

Examples:

chore: update .gitignore
chore: reorganize project folders

---

## Rules

- Use the imperative mood.

Good:

feat: add terminal plugin

Bad:

feat: added terminal plugin

---

Keep the first line under 72 characters.

---

One logical change per commit.

Avoid mixing unrelated changes.

Good:

feat: add git plugin

Separate commit:

docs: document git plugin

---

## Examples

build: bootstrap OpsPilot project

feat: add Docker plugin

feat: add Kubernetes plugin

fix: handle invalid YAML configuration

docs: update MCP architecture

test: add plugin loader tests

refactor: simplify configuration manager

perf: cache plugin metadata

security: prevent path traversal

ci: add release workflow

chore: update development dependencies

---

## Version

Current standard: v1
