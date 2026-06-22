---
description: "Autonomous multi-agent orchestrator. Use instead of task-router when you want Copilot to drive the entire workflow end-to-end without manual handoffs between specialists. Decomposes a request, invokes subagents in the correct sequence (or in parallel where safe), collects their outputs, and synthesises a final result. Suitable for features that touch schema, backend, frontend, tests, and review in a single run."
name: orchestrator
tools: [agent, read, edit, search]
---

# TODO: Add orchestrator instructions

Port from `.claude/agents/orchestrator.md`, replacing Claude `Task` tool usage
with the Copilot `agent` tool alias for subagent invocation.
