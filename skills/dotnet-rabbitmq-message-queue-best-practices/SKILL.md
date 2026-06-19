---
name: dotnet-rabbitmq-message-queue-best-practices
description: Skill for .NET and RabbitMQ messaging guidance covering delivery guarantees, idempotent consumers, acknowledgements, retries, dead-lettering, message contracts, durability, ordering, backpressure, and the transactional outbox. Use this when adding or reviewing async messaging, introducing RabbitMQ, designing producers or consumers, or debugging lost, duplicated, stuck, or out-of-order messages.
---

# Message Queue & RabbitMQ Best Practices

Async messaging decouples producers from consumers and smooths load, but it replaces an in-process method call's guarantees with a distributed system's realities: messages can be delayed, duplicated, reordered, or redelivered, and either end can crash mid-operation. Design every consumer to be safe under **at-least-once delivery** — that single assumption prevents most messaging bugs.

## Core principles

- **Assume at-least-once delivery; make consumers idempotent.** A message will sometimes be delivered more than once (redelivery after a crash, retry after a timeout). "Exactly-once delivery" does not really exist end-to-end; you achieve effectively-once by making processing idempotent. This is the single most important rule.
- **The broker is infrastructure, not your database.** Use it to move messages, not as a system of record. Don't rely on queue contents as durable application state.
- **Producers and consumers evolve independently.** That's the point of decoupling — so message contracts must be explicit and versioned, and both sides must tolerate the other being down or slow.
- **Acknowledge only after successful processing.** An ack means "I'm done and it's safe to forget this message." Acking on receive (before doing the work) loses messages on a crash.
- **Plan for failure first.** Decide up front what happens to a message that can't be processed — retried how, how many times, then where. Messaging without a dead-letter/poison strategy will eventually wedge a queue.

---

## When to use a queue

Good fits: decoupling services, leveling spiky load (buffer bursts, process at a steady rate), offloading slow/expensive work from a request, fan-out to multiple consumers, and reliable retries. If you need a synchronous answer right now, or strict global ordering, or transactional reads across data — a queue is usually the wrong tool (or needs careful extra design).

## Messaging patterns

- **Work queue / competing consumers** — one queue, multiple consumers sharing the load. The default for background jobs; scale throughput by adding consumers.
- **Publish/subscribe** — producers publish to an **exchange**; multiple queues bound to it each get a copy. Use for events that several services care about (`OrderPlaced`).
- **Routing / topic** — consumers subscribe to subsets of messages via routing keys/patterns (`order.*.eu`). Use direct/topic exchanges to route without the producer knowing the consumers.
- **Avoid request/reply (RPC) over the broker** unless you really need it — it reintroduces synchronous coupling and timeouts. Prefer a real RPC/HTTP call for synchronous needs.

In RabbitMQ, **producers publish to exchanges, never directly to queues**; bindings + routing keys decide which queues receive the message. This indirection is what lets you add consumers without touching producers.

## Delivery, acknowledgement & idempotency

- **Use manual acknowledgements.** Process the message, then ack. On failure, `nack`/`reject` (with or without requeue, deliberately). Disable auto-ack for anything that matters.
- **Set a sensible prefetch (QoS).** Limit unacknowledged messages per consumer (e.g. prefetch 10–50) so one consumer doesn't grab the whole queue, work is balanced, and memory is bounded. Too high hurts fairness; too low hurts throughput.
- **Make the consumer idempotent.** Carry a stable `MessageId`/idempotency key on every message and track processed ids (a dedupe table/set, or a natural idempotent operation like an upsert). Reprocessing the same message must produce the same result with no double side-effects.
- **Beware redelivery after partial work.** If processing has multiple side effects, design so a crash between them is recoverable (idempotent steps, or transactional handling) — the message will be redelivered.

## Retries, dead-lettering & poison messages

- **Retry transient failures with backoff** (and jitter), not in a tight loop. Immediate infinite requeue of a failing message is a hot loop that starves the queue.
- **Cap retries**, then route the message to a **dead-letter exchange/queue (DLX/DLQ)** instead of dropping it or requeuing forever. A poison message (one that can never succeed) must leave the main queue so it doesn't block others.
- **Use a delayed-retry mechanism** for backoff (e.g. per-attempt delay queues with TTL → DLX, or a delayed-message plugin) rather than `Thread.Sleep` in the consumer.
- **Keep a parking lot / DLQ you actually monitor.** Dead-lettered messages need alerting and a way to inspect, fix, and replay them. A DLQ no one watches is silent data loss.
- Distinguish **transient** (retry) from **permanent** (don't retry — bad message, send straight to DLQ) failures in your handler.

## Message design

- **Keep messages small**; carry ids and let consumers fetch detail if needed, rather than embedding large payloads. Large messages strain the broker.
- **Define an explicit, versioned schema.** Include a message type and a version; make consumers tolerant of unknown/extra fields (forward compatible) and never break existing fields — add, don't repurpose.
- **Include metadata:** a unique `MessageId`, a `CorrelationId` for tracing across services, timestamp, and content type. Correlation ids are what make distributed flows debuggable.
- Treat the message contract as a **public API** between services — changing it carelessly breaks consumers you may not control.

## Durability & reliable publishing

- **Make queues durable and messages persistent** for anything that must survive a broker restart. (Persistence costs throughput — non-critical, high-volume telemetry may accept transient.)
- **Use publisher confirms** so the producer knows the broker actually accepted a message; without confirms, a publish can be silently lost. Don't treat "I called publish" as "it's safely stored."
- **Prefer quorum queues** (replicated, raft-based) over classic mirrored queues for high-availability data safety in modern RabbitMQ.
- **Solve the dual-write problem with the transactional outbox pattern.** Don't write to the database and publish to the broker as two independent steps — a crash between them loses or fabricates events. Instead, write the message into an _outbox_ table in the same DB transaction as your state change, and a separate relay publishes it (and marks it sent). This guarantees the event is published if and only if the state change committed.

## Ordering

- **Don't assume global ordering.** With competing consumers and redelivery, messages can arrive out of order. If order matters for a given entity, route related messages to a single queue/consumer (e.g. by a partition/routing key on the entity id) or include sequence/version info so consumers can detect and handle reordering.

## Backpressure & flow control

- Use **prefetch limits** and **consumer scaling** to match consumption to production.
- Set **queue length limits and message TTLs** where appropriate so a stuck/slow consumer doesn't let a queue grow unbounded and exhaust broker memory (overflow can dead-letter or drop per policy).
- Consider **lazy queues** (disk-backed) for queues expected to hold large backlogs, to protect broker memory.
- Watch for the producer outpacing consumers — growing queue depth is the early warning.

## Connections & channels (RabbitMQ specifics)

- **Reuse long-lived connections; don't open a connection per message or per request** — connections are expensive. Open a small number and keep them.
- **Use one channel per thread/consumer**; channels are not thread-safe and are cheap to create relative to connections.
- **Enable automatic connection recovery and heartbeats**, and make publishing resilient to a dropped connection.
- **Don't run `KEYS`-equivalent expensive admin operations** or poll aggressively; use the management API/metrics for monitoring.

## Observability

- Propagate a **correlation id** through messages and logs so a flow can be traced across services; integrate distributed tracing where possible.
- Monitor **queue depth, consumer count, redelivery rate, DLQ depth, and consumer lag/processing time**, and alert on growth. A rising DLQ or queue depth is usually the first sign of trouble.

## Security

- **Enable TLS** for broker connections; never send credentials or messages in plaintext over untrusted networks.
- **Use per-service users with least privilege** and separate **vhosts** to isolate environments/teams.
- **Don't put secrets or unnecessary PII in messages** — they sit in queues, logs, and DLQs. Scope and minimize sensitive payloads.

## .NET specifics

- The low-level `RabbitMQ.Client` works, but for most apps a higher-level abstraction like **MassTransit** (or NServiceBus) is worth it — it gives you idempotency helpers, retry/backoff policies, dead-lettering, the outbox, serialization, and consumer lifecycle out of the box, so you don't hand-roll the hard parts.
- Reuse a single connection (or a small pool); register consumers via DI; keep handlers `async` and non-blocking.
- Implement consumers to ack after success and to surface transient vs permanent failures so the framework's retry/DLQ policy can act correctly.

---

## Review checklist

1. Is the consumer idempotent (safe under redelivery / duplicate messages)?
2. Are acknowledgements manual and sent only after successful processing?
3. Is prefetch/QoS set so load is balanced and memory bounded?
4. Do transient failures retry with backoff, capped, then dead-letter (not requeue forever)?
5. Is there a monitored DLQ/parking lot with a replay path?
6. Are queues durable and critical messages persistent, with publisher confirms?
7. Is reliable publishing handled (transactional outbox) instead of a naive dual write?
8. Does the message carry id, version, correlation id, and a versioned schema?
9. Is ordering either not assumed or explicitly handled where it matters?
10. Are connections long-lived, channels per-thread, with recovery and TLS enabled?

## Anti-patterns to reject

- Auto-ack (or acking before processing) — loses messages on crash.
- Non-idempotent consumers that double-charge / double-send on redelivery.
- Infinite immediate requeue of a failing (poison) message, blocking the queue.
- No DLQ, or a DLQ nobody monitors.
- Treating "publish was called" as durability (no publisher confirms).
- Dual-writing to DB and broker as separate steps (no outbox) — lost or phantom events.
- Assuming global message ordering with competing consumers.
- Giant messages, or secrets/PII embedded in messages.
- Opening a connection per message/request; sharing one channel across threads.
- Unbounded queues with no length/TTL limits or backpressure.

When in doubt, ask: what happens if this message is delivered twice, delivered late, or the consumer crashes halfway through? Design so the answer is always "the system stays correct."
