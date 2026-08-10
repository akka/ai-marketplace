# Akka AI Marketplace

Plugin marketplace for AI-assisted Akka SDK development.

## Installation

### Claude Code (plugin)

```
/plugin marketplace add akka/ai-marketplace
/plugin install akka@ai-marketplace
/reload-plugins
/akka:setup
```

### Codex

Codex can use the same Akka workflow from the `plugins/akka` directory.
That plugin package includes a Codex manifest, an Akka MCP config using
`akka mcp serve --disable-prompt`, and Codex skill aliases for the Akka
workflows.

### Akka CLI (any AI agent)

If you're using Cursor, Windsurf, VS Code Copilot, or another AI coding agent — or
prefer to set up manually — use the
[Akka CLI](https://doc.akka.io/operations/cli/installation.html):

```bash
# Install the Akka CLI (see link above for all platform)
brew install akka/brew/akka      # macOS

# Initialize your project — use the --agent flag for your editor
akka specify init . --agent cursor
akka specify init . --agent vscode-copilot
akka specify init . --agent claude-code
```

The `--agent` flag controls where commands are installed:

| Agent           | Flag                     | Commands installed to |
| --------------- | ------------------------ | --------------------- |
| Claude Code     | `--agent claude-code`    | `.claude/commands/`   |
| Cursor          | `--agent cursor`         | `.cursor/rules/`      |
| VS Code Copilot | `--agent vscode-copilot` | `.github/prompts/`    |

This produces the same result as the Claude Code plugin: skills, templates,
documentation, and MCP server configuration installed in your project directory.
For Codex, use the repo-local plugin files under `plugins/akka`.

## Getting Started

After installing via either path, run the setup command in your project directory:

- **Plugin:** `/akka:setup`
- **CLI-installed:** `/akka.setup`

It will:

1. Detect your OS and install any missing dependencies (Java 21+, Maven 3.9+, Akka CLI)
2. Configure the Akka download token for Maven
3. Scaffold a new Akka project (or repair/upgrade an existing one)
4. Download SDK documentation and AI context
5. Optionally configure Docker and AI API keys

Zero prerequisites beyond having a supported AI coding agent installed.

## Commands

| Plugin (Claude Code) | CLI-installed        | Description                                            |
| -------------------- | -------------------- | ------------------------------------------------------ |
| `/akka:setup`        | `/akka.setup`        | Set up a complete Akka development environment         |
| `/akka:constitution` | `/akka.constitution` | Create or update the project constitution              |
| `/akka:specify`      | `/akka.specify`      | Create or update a feature specification               |
| `/akka:clarify`      | `/akka.clarify`      | Resolve open questions in specs or plans               |
| `/akka:plan`         | `/akka.plan`         | Generate an implementation plan from a spec            |
| `/akka:tasks`        | `/akka.tasks`        | Break a plan into ordered, testable tasks              |
| `/akka:analyze`      | `/akka.analyze`      | Analyze codebase for patterns and issues               |
| `/akka:checklist`    | `/akka.checklist`    | Generate implementation or review checklists           |
| `/akka:implement`    | `/akka.implement`    | Execute tasks from the task list                       |
| `/akka:harnesses`    | `/akka.harnesses`    | Generate the enterprise-configuration assets required  |
| `/akka:converge`     | `/akka.converge`     | Queue remaining work the spec and plan still require   |
| `/akka:review`       | `/akka.review`       | Review code against spec and constitution              |
| `/akka:build`        | `/akka.build`        | Build, test, and run the service locally               |
| `/akka:inspect`      | `/akka.inspect`      | Inspect a deployed service                             |
| `/akka:reliability`  | `/akka.reliability`  | Add or remove resilience-testing instrumentation       |
| `/akka:deploy`       | `/akka.deploy`       | Deploy to the Akka platform                            |
| `/akka:issues`       | `/akka.issues`       | Track and manage issues                                |
| `/akka:status`       | `/akka.status`       | Show the definition-of-done rollup, read-only          |
| `/akka:conform`      | `/akka.conform`      | Run the auditors and return the ship-readiness verdict |
| `/akka:ship`         | `/akka.ship`         | Run the auditors and, on pass, run the ship steps      |
| `/akka:mode`         | `/akka.mode`         | Switch between Enforced and À la carte modes           |
| `/akka:docs`         | `/akka.docs`         | Generate rendered project documentation into `docs/`   |

> **Migrating from `akka-specify`?** The `akka-specify` plugin is still available but deprecated. Uninstall it and install `akka` instead.

## Attribution

The spec-driven development workflow (specify, plan, tasks, clarify, analyze, checklist,
issues) is built on [SpecKit](https://github.com/github/spec-kit), adapted for the
Akka SDK with MCP tool integration. The build, conform, constitution, converge, deploy,
docs, harnesses, implement, inspect, mode, reliability, review, setup, ship, and status
skills are original to Akka.

## License

See [LICENSE](LICENSE) for details.
