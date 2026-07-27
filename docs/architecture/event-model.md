# Event Model

OpsPilot is event-driven internally.

Every significant action emits an event.

Events are immutable.

## Standard Events

SessionStarted

SessionEnded

PlanCreated

PlanApproved

ToolStarted

ToolCompleted

ToolFailed

PolicyDenied

TransportConnected

TransportDisconnected

MemoryStored

AuditWritten

## Event Structure

Every event contains:

- event_id
- event_type
- timestamp
- session_id
- correlation_id
- payload

Events may be written to:

- audit log
- metrics
- future event bus

Plugins never emit events directly.

Plugins report execution results.

Runtime generates events.
