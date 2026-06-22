# Copilot Workspace Instructions

This workspace contains agent and skill definitions for a React + .NET stack and a Python FastAPI backend.
Agents are **stack-agnostic** — each agent detects the project's technology from the codebase and loads the appropriate skills automatically.

## Agent set

| Agent | Role | Stack detection |
| --- | --- | --- |
| `orchestrator` | End-to-end workflow driver — invokes all specialists autonomously | n/a |
| `task-router` | Plans and sequences multi-specialist work, writes `task-routing.md` | n/a |
| `feature-intake-reviewer` | Scope, cost-band estimation, and approval gate | n/a |
| `solution-architect` | Architecture plans and ADRs | .NET · FastAPI · React |
| `schema-designer` | Database entity and schema design | EF Core · SQLAlchemy |
| `migrations` | Migration generation and schema evolution | EF Core · Alembic |
| `backend-developer` | Backend API implementation | .NET · Python FastAPI |
| `frontend-developer` | Frontend UI implementation | React (· Vue TBD) |
| `refactor-specialist` | Behavior-preserving cleanup across any stack | any |
| `backend-unit-tester` | Backend tests | xUnit · pytest+httpx |
| `frontend-unit-tester` | Frontend component tests | Vitest + RTL |
| `backend-code-reviewer` | Backend code review | .NET · Python FastAPI |
| `frontend-code-reviewer` | Frontend code review | React |

## Skills

Skills live in `.claude/skills/` and are automatically discovered by both Claude and Copilot.
Agents load skills on demand based on detected stack — they do not pre-load everything.

## Coordination artifacts

For multi-agent runs, durable files are written at the repo root:

- `feature-intake.md`
- `task-routing.md`
- `architecture-plan.md`
- `task-handoff.md`
- `review-findings.md`
- `test-report.md`
- `orchestration-summary.md`
