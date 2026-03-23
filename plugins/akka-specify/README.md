# akka-specify Plugin

Complete Akka SDK development workflow — from environment setup to production deployment.

## Quick Start

```
/akka-specify:setup
```

This single command handles everything: dependency installation, project scaffolding, and configuration.

## Workflow

```
/akka-specify:setup     → Environment + project setup (one-time, re-runnable)
/akka-specify:specify   → Design your feature (spec)
/akka-specify:clarify   → Resolve open questions
/akka-specify:plan      → Create implementation plan
/akka-specify:tasks     → Break plan into tasks
/akka-specify:implement → Execute tasks
/akka-specify:build     → Build, test, run locally
/akka-specify:deploy    → Deploy to Akka platform
/akka-specify:review    → Review against spec and constitution
```

## Enterprise Support

Place an `enterprise.yaml` manifest at `.akka/enterprise.yaml` (project-level), `~/.akka/enterprise.yaml` (user-level), or set `AKKA_ENTERPRISE_CONFIG_URL` to customize:

- Dependency installation methods
- Custom context documentation sources
- Governance rules and constitutions
- SDLC gates and deployment overrides
