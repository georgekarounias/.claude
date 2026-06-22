# Copilot Workspace Instructions

This workspace contains agent and skill definitions for a React + .NET stack and a Python FastAPI backend.

## Agent set

| Agent                              | Role                                                                |
| ---------------------------------- | ------------------------------------------------------------------- |
| `orchestrator`                     | End-to-end workflow driver — invokes all specialists autonomously   |
| `task-router`                      | Plans and sequences multi-specialist work, writes `task-routing.md` |
| `feature-intake-reviewer`          | Scope, cost-band estimation, and approval gate                      |
| `react-dotnet-solution-architect`  | Architecture plans and ADRs                                         |
| `dotnet-efcore-schema-designer`    | EF Core entity and schema design                                    |
| `dotnet-efcore-migrations`         | Migration generation and schema evolution                           |
| `dotnet-backend-developer`         | .NET Web API implementation                                         |
| `react-frontend-developer`         | React + TypeScript implementation                                   |
| `react-dotnet-refactor-specialist` | Behavior-preserving cleanup across both stacks                      |
| `dotnet-backend-unit-tester`       | .NET xUnit tests                                                    |
| `react-frontend-unit-tester`       | Vitest / React Testing Library tests                                |
| `dotnet-backend-code-reviewer`     | Backend code review                                                 |
| `react-frontend-code-reviewer`     | Frontend code review                                                |
| `python-fastapi-developer`         | Python FastAPI implementation                                       |
| `python-fastapi-unit-tester`       | pytest + httpx endpoint and service tests                           |
| `python-fastapi-code-reviewer`     | Python backend code review                                          |

## Skills

Skills live in `.claude/skills/` and are automatically discovered by both Claude and Copilot.
Add new skills there and reference them from agent bodies via relative paths.

## Coordination artifacts

For multi-agent runs, durable files are written at the repo root:

- `feature-intake.md`
- `task-routing.md`
- `architecture-plan.md`
- `task-handoff.md`
- `review-findings.md`
- `test-report.md`
- `orchestration-summary.md`
