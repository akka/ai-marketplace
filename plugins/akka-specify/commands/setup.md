---
description: Set up a complete Akka SDK development environment from scratch. Installs Java, Maven, Akka CLI, configures tokens, scaffolds a project, and downloads context documentation. Idempotent — safe to rerun for repair/upgrade.
handoffs:
  - label: Start Building a Feature
    agent: akka.specify
    prompt: I want to build a feature for my new Akka project
    send: true
  - label: Run Local Development
    agent: akka.build
    prompt: Build, test, and run the service locally
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

`/akka.setup` detects the user's environment, installs all missing dependencies,
scaffolds an Akka project, and leaves the user ready to develop — with **zero
prerequisites** beyond having an AI coding agent installed.

The skill is **idempotent and re-runnable**. On first run it performs full setup.
On subsequent runs it operates in repair/upgrade mode.

## Execution Instructions

**FIRST:** Test if you have shell access by executing `echo "bash-ok"` using the Bash tool.

**If Bash is available:** Execute all commands yourself. Do NOT ask the user to run
commands or paste output. The only exceptions are commands requiring `sudo` (show the
command and ask permission first) and `akka code token` (which opens a browser).

**If Bash is NOT available (plugin permission limitation):** This skill was loaded from
a plugin, which currently does not grant shell access. Tell the user:

*"The setup skill needs shell access to install dependencies and scaffold your project.
Due to a Claude Code plugin limitation, I can't run commands directly from a plugin-installed skill.

To get the full automated setup, run this in your terminal:*

```
akka specify init . --agent claude-code
```

*If you don't have the Akka CLI yet, install it first:*
- *macOS:* `brew install akka/brew/akka`
- *Other platforms:* https://doc.akka.io/operations/cli/installation.html

*After running `akka specify init .`, restart Claude Code. The setup skill will be
installed natively at `.claude/commands/akka.setup.md` with full shell access.
Then run `/akka.setup` to complete the environment setup.*"

**STOP HERE if Bash is not available.** Do not proceed with the phases below.

---

**Phases 1–4 use only bash commands** — the Akka CLI is not yet installed, so MCP tools
are unavailable. After Phase 4, delegate to `akka` CLI commands.

Work through each phase sequentially. Skip phases where the check shows the dependency
is already satisfied. Report progress to the user after each phase.

---

## Phase 1: Environment Detection

Execute the following to detect the platform:

1. Run `uname -s` and `uname -m` to determine OS and architecture.
2. Run `echo $SHELL` to determine the shell.
3. On Linux, run `cat /etc/os-release 2>/dev/null | grep -E '^(ID|ID_LIKE)='` for the distro.
4. Check which package managers are available by running `command -v brew`, `command -v apt`, `command -v dnf`, `command -v pacman`, `command -v winget`, `command -v scoop`, `command -v sdk`.

Then check for an existing project by running `ls pom.xml .akka/ .claude/commands/ akka-context/ .mcp.json 2>/dev/null`.

- If `pom.xml` exists → **existing project**, enter repair/upgrade mode (Phase 7B).
- If no `pom.xml` → **new project**, proceed with full setup.

Check for an enterprise manifest by reading `.akka/enterprise.yaml`, `~/.akka/enterprise.yaml`, or fetching from `$AKKA_ENTERPRISE_CONFIG_URL` if set. If found, inform the user and apply overrides in subsequent phases.

Report: *"Detected: [OS] [ARCH] with [PACKAGE_MANAGER]. [New project / Existing project]."*

---

## Phase 2: Java Installation

Execute `java -version 2>&1` and parse the major version.

- If Java 21+ is present: report *"Java [version] — already installed"* and skip to Phase 3.
- If missing or below 21: install it.

**Enterprise override:** If the enterprise manifest has `tooling.java.install-command`, execute that command instead of the defaults below.

Install based on the platform detected in Phase 1:
- **macOS:** Execute `brew install --cask temurin@21`
- **Linux (preferred):** If SDKMAN is not available, install it with `curl -s "https://get.sdkman.io" | bash` then `source "$HOME/.sdkman/bin/sdkman-init.sh"`. Then execute `sdk install java 21-tem`.
- **Linux (apt fallback):** Show `sudo apt install openjdk-21-jdk` to the user and ask permission before executing.
- **Linux (dnf fallback):** Show `sudo dnf install java-21-openjdk-devel` to the user and ask permission before executing.
- **Linux (pacman fallback):** Show `sudo pacman -S jdk-openjdk` to the user and ask permission before executing.
- **Windows:** Execute `winget install EclipseAdoptium.Temurin.21.JDK`

After installation, verify by executing `java -version 2>&1`. Confirm Java 21+. If verification fails, stop and ask the user for guidance.

**PRIVILEGE POLICY:** Prefer user-space installs (SDKMAN, Homebrew, winget). For `sudo` commands, always show the exact command and ask before executing.

---

## Phase 3: Maven Installation

Execute `mvn --version 2>&1`. Also check for a Maven wrapper with `ls ./mvnw 2>/dev/null`.

- If Maven 3.9+ is present (or `./mvnw` exists): report *"Maven [version] — already installed"* and skip to Phase 4.
- If missing or below 3.9: install it.

**Enterprise override:** If the enterprise manifest has `tooling.maven.install-command`, execute that instead.

Install based on the platform:
- **macOS:** Execute `brew install maven`
- **Linux (preferred):** Execute `sdk install maven` (requires SDKMAN from Phase 2)
- **Linux (apt fallback):** Show `sudo apt install maven` and ask permission.
- **Linux (dnf fallback):** Show `sudo dnf install maven` and ask permission.
- **Windows:** Execute `winget install Apache.Maven`

Verify by executing `mvn --version 2>&1`. Confirm Maven 3.9+.

---

## Phase 4: Akka CLI Installation

Execute `akka version 2>&1`.

- If the Akka CLI is present: report *"Akka CLI [version] — already installed"* and skip to Phase 5.
- If missing: install it.

**Enterprise override:** If the enterprise manifest has `tooling.akka-cli.install-command`, execute that instead.

Install based on the platform:
- **macOS:** Execute `brew install akka/brew/akka`
- **Linux/Windows:** Refer the user to https://doc.akka.io/operations/cli/installation.html for download instructions.

Verify by executing `akka version`. If this fails, stop and ask the user for guidance.

---

## Phase 5: Akka Download Token

Execute `grep -q "akka-repository" ~/.m2/settings.xml 2>/dev/null && echo "configured" || echo "not configured"` and `grep -q "akka-plugin-repository" ~/.m2/settings.xml 2>/dev/null && echo "configured" || echo "not configured"`.

- If both are configured: report *"Akka download token — already configured"* and skip to Phase 6.
- If missing: provision the token.

**Enterprise override:** If the enterprise manifest has `tooling.maven.settings-overlay`, download that settings file and merge it into `~/.m2/settings.xml` instead.

Tell the user: *"I need to run `akka code token` which will open a browser window for you to log in to your Akka account. This is a free account needed to download Akka SDK dependencies."*

Execute `akka code token`. Wait for the user to complete the browser flow.

After completion, verify by executing `grep -c "akka-repository" ~/.m2/settings.xml` and `grep -c "akka-plugin-repository" ~/.m2/settings.xml`. Both should return 1 or more.

---

## Phase 6: Docker (Optional)

Execute `docker info 2>/dev/null | head -5`.

- If Docker is running: report *"Docker — available"* and continue to Phase 7.
- If not available: inform the user:

*"Docker is only needed for running local clusters and building container images for deployment. You can develop and test without it."*

Ask: *"Would you like to install Docker now, or skip it? You can always rerun `/akka.setup` later."*

If the user wants to install:
- **macOS:** Execute `brew install --cask docker`
- **Linux:** Show Docker CE install commands and ask permission (requires sudo).
- **Windows:** Execute `winget install Docker.DockerDesktop`
- Verify with `docker info`.

If the user defers: record it as skipped and continue.

**Enterprise override:** If `tooling.docker.runtime` is set (e.g., `podman`), check for that runtime instead.

---

## Phase 7: Project Scaffolding

### 7A. New Project (no existing `pom.xml`)

1. **Project identity:** Execute `basename "$(pwd)"` to get the directory name. Derive:
   - **artifactId**: lowercase, hyphens only (e.g., `My Shopping Cart` → `my-shopping-cart`)
   - **groupId**: default `com.example`

   Present to the user for confirmation. Apply changes if requested.

2. **Scaffold:** Execute `akka specify init . --agent claude-code`. This clones the empty project, customizes pom.xml, downloads akka-context/, CLAUDE.md, AGENTS.md, constitution, installs slash commands, templates, and .mcp.json.

3. **Git init:** If git is not already initialized, execute `git init`, `git add .`, `git commit -m "Initial Akka project setup via /akka.setup"`.

4. **Enterprise post-scaffolding** (if manifest detected in Phase 1):
   - Download additional context sources from `context.additional-sources`
   - Apply custom constitutions from `governance.constitutions` (merge or replace)
   - Apply custom templates from `governance.templates` (replace or add)
   - Append governance rules from `governance.rules` to the constitution
   - Install skill overrides from `sdlc.skill-overrides`
   - Apply Maven mirror settings from `tooling.maven.mirrors`

### 7B. Existing Project (repair/upgrade mode)

1. **Check SDK version:** Execute `curl -s https://doc.akka.io/sdk/_attachments/latest-version.txt` to get the latest version. Execute `grep -A1 '<parent>' pom.xml | grep '<version>' | sed 's/.*<version>\(.*\)<\/version>.*/\1/'` to get the current version. If behind, ask if the user wants to upgrade.

2. **Check for missing artifacts:** Execute `test -f .mcp.json && echo "OK" || echo "MISSING"` for each expected file (.mcp.json, .akka/constitution/, .akka/templates/, .claude/commands/, akka-context/, CLAUDE.md, AGENTS.md). For any missing, execute `akka specify init . --agent claude-code` to regenerate.

3. **Update context:** Execute `akka code context-update . --assistant claude-code --force`.

4. **Enterprise repair:** If manifest detected, apply the same customizations as 7A.4.

---

## Phase 8: Akka Context Documentation

For new projects: already handled by `akka specify init .` in Phase 7A.

For existing projects: already handled by `akka code context-update` in Phase 7B.

Verify by executing `ls akka-context/ | wc -l`. Should show ~161 files. If empty or missing, execute `akka code context-update . --assistant claude-code --force`.

---

## Phase 9: AI Key Configuration (Optional)

Execute these checks:
- `[ -n "$ANTHROPIC_API_KEY" ] && echo "set" || echo "not set"`
- `[ -n "$OPENAI_API_KEY" ] && echo "set" || echo "not set"`
- `[ -n "$GOOGLE_AI_API_KEY" ] && echo "set" || echo "not set"`

Inform the user: *"AI API keys are only needed for building Akka services that call LLM providers (agent development). They are NOT needed for standard Akka service development."*

Ask: *"Would you like to configure AI API keys now, or skip?"*

If the user defers: record as skipped and continue.

If configuring: ask which provider(s), get the key value, and ask where to store it:
- **Environment variable (recommended):** Execute `export KEY_NAME="value"` and remind the user to add it to their shell profile for persistence.
- **application.conf:** Write the key to `src/main/resources/application.conf`. Warn that keys in config files are visible in the repo.

---

## Phase 10: Validation

Execute all checks and build the summary:

1. Execute `java -version 2>&1 | head -1`
2. Execute `mvn --version 2>&1 | head -1`
3. Execute `akka version 2>&1`
4. Execute `grep -q "akka-repository" ~/.m2/settings.xml 2>/dev/null && echo "configured" || echo "not configured"`
5. Execute `docker info 2>/dev/null | head -1 || echo "not available"`
6. If `pom.xml` exists, execute `mvn compile -q 2>&1` to verify the build. Report errors but do not block.

Output a summary:

```
/akka.setup — Complete

  Java 21 (Temurin)      ✓ installed
  Maven 3.9.6            ✓ installed
  Akka CLI 3.x.x         ✓ installed
  Akka download token    ✓ configured
  Docker                 ✓ installed        (or: ⏭ deferred)
  SDK version            ✓ latest
  Project scaffolded     ✓ com.example:my-cart
  Akka context docs      ✓ 161 files
  AI keys                ⏭ deferred         (or: ✓ configured)

IMPORTANT: Please restart Claude Code now. The MCP server configuration
(.mcp.json) was created during setup, but Claude Code only loads MCP
servers at session start. After restarting, the Akka MCP tools will be
available and /akka.specify will work with full functionality.

Ready to go! After restarting, run /akka.specify to start building your first feature.
```

If enterprise customizations were applied, add them to the summary.

**Enterprise post-setup hooks** (`tooling.post-setup-hooks`): For each hook, show the command and description, ask for confirmation, execute, and report success/failure. Substitute `${artifact_id}`, `${group_id}`, `${project_dir}`, `${team}` in command strings.

---

## Enterprise Customization Reference

| Manifest Section | Phase | Action |
|-----------------|-------|--------|
| `tooling.java.install-command` | 2 | Replace default Java install |
| `tooling.maven.install-command` | 3 | Replace default Maven install |
| `tooling.akka-cli.install-command` | 4 | Replace default CLI install |
| `tooling.maven.settings-overlay` | 5 | Download and merge Maven settings |
| `tooling.maven.mirrors` | 5 | Add mirror config to Maven settings |
| `tooling.docker.install-command` | 6 | Replace default Docker install |
| `tooling.docker.runtime` | 6 | Check for alternative runtime |
| `context.additional-sources` | 7 | Download additional context |
| `governance.constitutions` | 7 | Merge or replace constitution |
| `governance.templates` | 7 | Replace or add templates |
| `governance.rules` | 7 | Append rules to constitution |
| `sdlc.skill-overrides` | 7 | Replace default slash commands |
| `sdlc.gates` | 7 | Document gates in project |
| `sdlc.environments` | 7 | Document environments in project |
| `tooling.post-setup-hooks` | 10 | Execute post-setup commands |

---

## Error Handling

1. Report errors clearly with the specific error message.
2. Do not retry blindly — if the same error persists, ask the user.
3. Suggest alternatives: Homebrew fails → suggest SDKMAN; apt fails → suggest SDKMAN.
4. Docker (Phase 6) and AI keys (Phase 9) failures are non-blocking — record as deferred.
5. Build failures in Phase 10 are non-blocking — report but don't block the summary.

## Key Rules

- EXECUTE COMMANDS YOURSELF — do not ask the user to run them or paste output
- IDEMPOTENT — check before acting; skip already-satisfied phases
- ASK BEFORE SUDO — show the exact command and get permission first
- USER CHOOSES — optional phases (Docker, AI keys) are offered, never forced
- DELEGATE TO CLI — after Phase 4, use `akka` CLI commands
- ENTERPRISE EXTENSIBLE — check the manifest and apply overrides at each phase
