---
name: agent-handoff-evidence-best-practices
description: Route multi-agent work with durable handoff, review, and test artifacts. Use when a task spans specialists or needs reusable execution evidence beyond chat.
---

# Agent Handoff And Evidence Best Practices

Multi-agent systems fail when context lives only in chat. Durable artifacts reduce
re-discovery, improve routing quality, and make validation and review auditable.

Use the following task-level files at the repo root unless the repo already has a
better established convention:

- `task-routing.md`
- `task-handoff.md`
- `review-findings.md`
- `test-report.md`
- `architecture-plan.md` or an ADR when architecture work is required

## Example triggers

- "Plan the agent sequence for this API and UI change and leave a durable handoff."
- "Persist the review findings so another agent can fix them later."
- "Write a test report for the coverage added in this task."

## Read Order

When these artifacts exist, read them in this order before doing significant work:

1. `task-routing.md`
2. `architecture-plan.md` or the relevant ADR
3. `task-handoff.md`
4. `review-findings.md`
5. `test-report.md`

Do not reread every artifact blindly. Read the smallest relevant set for the task.

## Artifact Contracts

### `task-routing.md`

Created by the router or intake agent before specialist work begins.

Structure:

- Request summary
- Task classification
- Risk level
- Required artifacts
- Ordered agent sequence
- Entry criteria and exit criteria per step
- Validation gates
- Open questions or blockers
- Immediate next agent

### `task-handoff.md`

Created or updated when one agent finishes and another is expected to continue.

Structure:

- Current objective
- Files touched or planned
- Decisions already made
- Invariants that must hold
- Work completed
- Remaining work
- Validation already run
- Known risks or blockers
- Recommended next agent

### `review-findings.md`

Created or updated when review findings need to survive beyond the current chat.

Structure:

- Scope reviewed
- Critical findings
- Warning findings
- Nit findings
- Files and lines affected
- Suggested fixes
- Recommended next agent

### `test-report.md`

Created or updated when test work or validation results should be durable.

Structure:

- Scope tested
- Commands run
- Pass/fail results
- Coverage added or gaps left intentionally
- Blockers or production defects found
- Recommended next agent

## Evidence Rules

- Distinguish observed facts from assumptions.
- Record exact commands run whenever validation matters.
- Never imply a build, test, lint, or review happened if it did not.
- Update the existing artifact instead of creating duplicates when the task is ongoing.
- Keep artifacts concise and execution-focused.
- If a file is no longer current, replace outdated sections explicitly rather than letting contradictory notes accumulate.

## When To Write Artifacts

- Always write `task-routing.md` for non-trivial tasks.
- Write or refresh `task-handoff.md` whenever another agent should continue.
- Write `review-findings.md` when findings are non-trivial or another agent must fix them.
- Write `test-report.md` when tests were added, validation was important, or failures/gaps must be preserved.

For truly trivial one-step tasks, a durable artifact can be skipped unless the user asks for one.

## Completion Standard

When you create or update one of these files, mention it in your summary. The next
agent should be able to continue from the artifact without reconstructing the task
from chat history.
