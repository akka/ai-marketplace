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

### Antigravity (`agy`)

```bash
agy plugin install https://github.com/akka/ai-marketplace
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

## Repository layout — one repo, multiple manifests

The repo root carries several manifests side by side so a single source of
truth ships to every harness. Each harness reads only its own files;
[HARNESSES.md](HARNESSES.md) is the authoritative mapping and this table
must stay in sync with it.

| Root manifest files | Read by |
| --- | --- |
| `.claude-plugin/marketplace.json` + `plugins/akka/` | Claude Code (and Claude Tag) |
| `.agents/plugins/marketplace.json` + `.codex-plugin/plugin.json` | Codex CLI |
| `gemini-extension.json` | Gemini CLI |
| `plugin.json` + `mcp_config.json` | Antigravity CLI (`agy`) |
| `plugin.json` + `mcp.json` ([Agent Plugins 1.0](https://agent-plugins.org/specification)) | **No harness reads these today.** Present so the plugin is indexable by any future AP 1.0 client without a second copy of the skill content — the `skills/<name>/SKILL.md` tree is the same one the Codex target emits. Commands are out of scope in AP 1.0 v1, so an AP 1.0 client that ships would reach the workflow through the 22 skills and the MCP toolset, not through `/akka:*` slash commands. |

`plugin.json` at the root does double duty: it is the Antigravity manifest
*and* the AP 1.0 manifest (the two schemas are compatible). `mcp_config.json`
and `mcp.json` are distinct files — Antigravity reads the former, AP 1.0
reads the latter.

The canonical location for the `/akka:setup` skill is
[`skills/setup/SKILL.md`](skills/setup/SKILL.md). `akka.ai/setup` aliases
this path, so link to the repo file rather than copying the content.

## Version pinning — install pins to `@stable`, never `main`

Every downstream install command references the `stable` tag (a floating
pointer advanced on each release cut) or a specific `vX.Y.Z` tag:

```
akka/ai-marketplace@stable
akka/ai-marketplace@vX.Y.Z
```

`main` moves ahead of what has been validated end-to-end, so an install
that resolves against `main` can pull an unreleased marketplace against a
released CLI. `stable` and every released `vX.Y.Z` tag are the only refs
safe to install from. The tag-cutting workflow and the `stable`-tag
contract are in [RELEASING.md](RELEASING.md); the CLI mechanism that
consumes them (`akka specify init --channel stable` vs `--channel edge`)
is documented in the Akka CLI docs.

The install snippets at the top of this README omit the tag pin for
brevity. The AI-install playbook at `akka.ai/` (which AI coding assistants
read to install Akka on the user's behalf) always emits the `@stable`
form; a follow-up will pin the top-of-README snippets to match.

## Attribution

The spec-driven development workflow (specify, plan, tasks, clarify, analyze, checklist,
issues) is built on [SpecKit](https://github.com/github/spec-kit), adapted for the
Akka SDK with MCP tool integration. The build, conform, constitution, converge, deploy,
docs, harnesses, implement, inspect, mode, reliability, review, setup, ship, and status
skills are original to Akka.

## License

See [LICENSE](LICENSE) for details.
