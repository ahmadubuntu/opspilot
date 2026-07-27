# Testing Strategy

Testing pyramid:

1. Unit Tests

Core logic.

2. Integration Tests

Plugin + Runtime.

3. End-to-End Tests

CLI → Runtime → Plugin.

Mutating tools must support dry-run tests.

Every plugin must provide:

- success case
- failure case
- permission denied case

Production bugs require regression tests before fixes are merged.
