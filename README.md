# Akka AI Marketplace

Plugin marketplace for AI-assisted Akka SDK development.

## Installation

### Claude Code (plugin)

```
/plugin marketplace add akka/ai-marketplace
/plugin install akka-specify@ai-marketplace
/reload-plugins
/akka-specify:setup
```

### Akka CLI (any AI agent)

If you're using Cursor, Windsurf, or another AI coding agent — or prefer to set up
manually — use the [Akka CLI](https://doc.akka.io/operations/cli/installation.html):

```bash
# Install the Akka CLI (see link above for all platforms)
brew install akka/brew/akka      # macOS

# Initialize your project with skills, templates, and MCP config
akka specify init .
```

This produces the same result as the Claude Code plugin: skills, templates,
documentation, and MCP server configuration installed in your project directory.
The CLI detects your agent type and writes to the appropriate location
(`.claude/commands/` for Claude Code, `.cursor/rules/` for Cursor).

## Getting Started

After installing via either path, run the setup command in your project directory:
- **Plugin:** `/akka-specify:setup`
- **CLI-installed:** `/akka.setup`

It will:

1. Detect your OS and install any missing dependencies (Java 21+, Maven 3.9+, Akka CLI)
2. Configure the Akka download token for Maven
3. Scaffold a new Akka project (or repair/upgrade an existing one)
4. Download SDK documentation and AI context
5. Optionally configure Docker and AI API keys

Zero prerequisites beyond having Claude Code installed.

## Commands

| Plugin (Claude Code) | CLI-installed | Description |
|---------------------|---------------|-------------|
| `/akka-specify:setup` | `/akka.setup` | Set up a complete Akka development environment |
| `/akka-specify:specify` | `/akka.specify` | Create or update a feature specification |
| `/akka-specify:plan` | `/akka.plan` | Generate an implementation plan from a spec |
| `/akka-specify:tasks` | `/akka.tasks` | Break a plan into ordered, testable tasks |
| `/akka-specify:implement` | `/akka.implement` | Execute tasks from the task list |
| `/akka-specify:build` | `/akka.build` | Build, test, and run the service locally |
| `/akka-specify:deploy` | `/akka.deploy` | Deploy to the Akka platform |
| `/akka-specify:review` | `/akka.review` | Review code against spec and constitution |
| `/akka-specify:clarify` | `/akka.clarify` | Resolve open questions in specs or plans |
| `/akka-specify:analyze` | `/akka.analyze` | Analyze codebase for patterns and issues |
| `/akka-specify:checklist` | `/akka.checklist` | Generate implementation or review checklists |
| `/akka-specify:issues` | `/akka.issues` | Track and manage issues |
| `/akka-specify:constitution` | — | Edit the project constitution |

## Attribution

The spec-driven development workflow (specify, plan, tasks, clarify, analyze, checklist,
issues) is built on [SpecKit](https://github.com/github/spec-kit), adapted for the
Akka SDK with MCP tool integration. The build, deploy, implement, review, setup, and
constitution skills are original to Akka.

## License

See [LICENSE](LICENSE) for details.
