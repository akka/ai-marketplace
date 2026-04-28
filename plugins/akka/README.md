# akka Plugin

Complete Akka SDK development workflow — from environment setup to production deployment.

## Quick Start

```
/akka:setup
```

This single command handles everything: dependency installation, project scaffolding, and configuration.

## Workflow

```
/akka:setup     → Environment + project setup (one-time, re-runnable)
/akka:specify   → Design your feature (spec)
/akka:clarify   → Resolve open questions
/akka:plan      → Create implementation plan
/akka:tasks     → Break plan into tasks
/akka:implement → Execute tasks
/akka:build     → Build, test, run locally
/akka:deploy    → Deploy to Akka platform
/akka:review    → Review against spec and constitution
```

## Codex

Codex users can load the same workflow from the `plugins/akka` directory.
The Codex variant includes:

- `.codex-plugin/plugin.json`
- `.mcp.json` pointing at `akka mcp serve --disable-prompt`
- Codex skill aliases for the Akka workflows

Use the canonical `akka-sdd` skill when you want the full workflow guidance,
or one of the alias skills when you want a task-specific entry point:

- `akka-specify`
- `akka-plan`
- `akka-tasks`
- `akka-implement`
- `akka-review`
- `akka-build`
- `akka-deploy`
- `akka-analyze`
- `akka-clarify`
- `akka-checklist`
- `akka-issues`

## Enterprise Support

Place an `enterprise.yaml` manifest at `.akka/enterprise.yaml` (project-level), `~/.akka/enterprise.yaml` (user-level), or set `AKKA_ENTERPRISE_CONFIG_URL` to customize:

- Dependency installation methods
- Custom context documentation sources
- Governance rules and constitutions
- SDLC gates and deployment overrides
