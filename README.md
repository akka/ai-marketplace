# Akka AI Marketplace

Claude Code plugin marketplace for Akka SDK development tools.

## Installation

```
/plugin marketplace add akka/akka-ai-marketplace
/plugin install akka-specify@akka-ai-marketplace
```

## Available Plugins

### akka-specify

Complete Akka SDK development workflow — from environment setup to production deployment.

**Commands:**

| Command | Description |
|---------|-------------|
| `/akka.setup` | Set up a complete Akka development environment from scratch |
| `/akka.specify` | Create or update a feature specification |
| `/akka.plan` | Generate an implementation plan from a spec |
| `/akka.tasks` | Break a plan into ordered, testable tasks |
| `/akka.implement` | Execute tasks from the task list |
| `/akka.build` | Build, test, and run the service locally |
| `/akka.deploy` | Build a container image and deploy to the Akka platform |
| `/akka.review` | Review implemented code against spec, plan, and constitution |
| `/akka.clarify` | Resolve open questions in specs or plans |
| `/akka.analyze` | Analyze codebase for Akka SDK patterns and issues |
| `/akka.checklist` | Generate implementation or review checklists |
| `/akka.issues` | Track and manage issues found during development |

## Getting Started

After installing the plugin, run `/akka.setup` in your project directory. It will:

1. Detect your OS and install any missing dependencies (Java 21+, Maven 3.9+, Akka CLI)
2. Configure the Akka download token for Maven
3. Scaffold a new Akka project (or repair/upgrade an existing one)
4. Download SDK documentation and AI context
5. Optionally configure Docker and AI API keys

Zero prerequisites beyond having Claude Code installed.

## Prerequisites

The workflow skills (`/akka.specify`, `/akka.plan`, `/akka.build`, etc.) require the
[Akka CLI](https://doc.akka.io/reference/cli/installation.html) and its MCP server
(`akka mcp serve`) to be installed and configured. The `/akka.setup` skill handles
this automatically — always run it first.

If you installed the plugin without running `/akka.setup`, you can install the Akka CLI
manually and run `akka specify init .` in your project directory.

## Attribution

The spec-driven development workflow (specify, plan, tasks, clarify, analyze, checklist,
issues) is built on [SpecKit](https://github.com/github/spec-kit), adapted for the
Akka SDK with MCP tool integration. The build, deploy, implement, review, setup, and
constitution skills are original to Akka.

## License

See [LICENSE](LICENSE) for details.
