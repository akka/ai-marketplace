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

## Enterprise Support

Place an `enterprise.yaml` manifest at `.akka/enterprise.yaml` (project-level), `~/.akka/enterprise.yaml` (user-level), or set `AKKA_ENTERPRISE_CONFIG_URL` to customize:

- Dependency installation methods
- Custom context documentation sources
- Governance rules and constitutions
- SDLC gates and deployment overrides
