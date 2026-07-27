# Project Principles

These principles are mandatory.

## 1. AI First

The repository must be understandable by both humans and AI.

Documentation is considered part of the source code.

---

## 2. Plugin Based

Every capability belongs inside a plugin.

The runtime must not depend on any specific plugin.

---

## 3. Docker First

Every service must be executable through Docker.

---

## 4. Open WebUI Is Only UI

No business logic may exist inside Open WebUI.

---

## 5. Secure By Default

Least privilege.

Read-only access whenever possible.

Explicit approval for dangerous actions.

---

## 6. Test Everything

Every feature requires automated tests.

---

## 7. Documentation First

Architecture decisions must be documented.

Every sprint updates the documentation.

---

## 8. AI Documentation

The .ai directory must always reflect the current state of the project.

---

## 9. Clean Architecture

Runtime

↓

Plugin Loader

↓

Plugins

↓

Infrastructure

Dependencies always point downward.

---

## 10. Backward Compatibility

Breaking changes require an Architecture Decision Record (ADR).
