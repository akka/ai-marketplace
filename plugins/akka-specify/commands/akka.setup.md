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

`/akka.setup` replaces the manual `akka specify init` workflow. It detects the user's
environment, installs all missing dependencies, scaffolds an Akka project, and leaves
the user ready to develop — with **zero prerequisites** beyond having Claude Code installed.

The skill is **idempotent and re-runnable**. On first run it performs full setup. On
subsequent runs it operates in repair/upgrade mode — checking dependencies, updating
context docs, filling in missing pieces, and offering SDK version upgrades.

## Important Constraint

**Phases 1–4 use only bash commands** — the Akka CLI is not yet installed, so MCP tools
are unavailable. After Phase 4 installs the CLI, subsequent phases can delegate to
`akka` CLI commands.

---

## Phase 1: Environment Detection

Detect the platform, check for an existing project, and check for enterprise customization.

### 1.1 Platform Detection

Run these commands to determine the environment:

```bash
uname -s    # Darwin, Linux, MINGW64_NT-*, MSYS_NT-*
uname -m    # x86_64, arm64, aarch64
echo $SHELL # /bin/bash, /bin/zsh, /usr/bin/fish, etc.
```

On Linux, also detect the distro and package manager:

```bash
cat /etc/os-release 2>/dev/null | grep -E '^(ID|ID_LIKE)='
```

Detect available package managers:

```bash
command -v brew && echo "brew available"
command -v apt && echo "apt available"
command -v dnf && echo "dnf available"
command -v pacman && echo "pacman available"
command -v winget && echo "winget available"
command -v scoop && echo "scoop available"
command -v sdk && echo "sdkman available"
```

Store the results mentally for use in subsequent phases. Report to the user:
*"Detected: [OS] [ARCH] with [PACKAGE_MANAGER]"*

### 1.2 Existing Project Detection

Check for existing project artifacts:

```bash
ls pom.xml .akka/ .claude/commands/ akka-context/ .mcp.json 2>/dev/null
```

- If `pom.xml` exists → this is an **existing project**. Enter **repair/upgrade mode** (see Phase 7).
- If no `pom.xml` → this is a **new project**. Proceed with full setup.

### 1.3 Enterprise Manifest Detection

Check for an enterprise customization manifest at three locations (in precedence order):

1. **Project-level**: Read `.akka/enterprise.yaml` if it exists
2. **User-level**: Read `~/.akka/enterprise.yaml` if it exists
3. **URL-fetched**: If `$AKKA_ENTERPRISE_CONFIG_URL` is set, fetch and read the YAML from that URL

If a manifest is found, read its contents. The manifest sections will be applied during
the relevant phases (see the Enterprise Customization section at the end of this document).

If a manifest is found, inform the user:
*"Enterprise manifest detected at [location]. Enterprise customizations will be applied."*

---

## Phase 2: Java Installation

**Depends on:** Phase 1

### 2.1 Check Current Java Version

```bash
java -version 2>&1
```

Parse the output to extract the major version. Java 21+ is required.

- If Java 21+ is present: report *"Java [version] — already installed"* and **skip to Phase 3**.
- If Java is missing or below 21: proceed with installation.

**Enterprise override:** If the enterprise manifest has `tooling.java.install-command`,
use that command instead of the platform defaults below.

### 2.2 Install Java

Choose the installation method based on the platform detected in Phase 1:

**macOS:**
```bash
brew install --cask temurin@21
```

**Linux (SDKMAN preferred — no sudo required):**

If SDKMAN is not already installed:
```bash
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"
```

Then install Java:
```bash
sdk install java 21-tem
```

**Linux (apt fallback):** Show the command and ask the user to confirm before running:
```bash
sudo apt install openjdk-21-jdk
```

**Linux (dnf fallback):** Show the command and ask the user to confirm before running:
```bash
sudo dnf install java-21-openjdk-devel
```

**Linux (pacman fallback):** Show the command and ask the user to confirm before running:
```bash
sudo pacman -S jdk-openjdk
```

**Windows:**
```powershell
winget install EclipseAdoptium.Temurin.21.JDK
```

Fallback: `scoop install temurin21-jdk` or `choco install temurin21`

### 2.3 Verify Installation

```bash
java -version 2>&1
```

Confirm the output shows Java 21+. If verification fails, stop and ask the user
for guidance — do not retry the same install.

**PRIVILEGE POLICY:** Prefer user-space installs (SDKMAN, Homebrew, winget).
If system-level install is required (apt/dnf/pacman with sudo), display the exact
command and ask for explicit confirmation before executing. Never run privileged
commands silently.

---

## Phase 3: Maven Installation

**Depends on:** Phase 2 (Java must be installed first)

### 3.1 Check Current Maven Version

```bash
mvn --version 2>&1
```

Also check for a Maven wrapper in the project:
```bash
ls ./mvnw 2>/dev/null
```

- If Maven 3.9+ is present (or `./mvnw` exists): report *"Maven [version] — already installed"* and **skip to Phase 4**.
- If Maven is missing or below 3.9: proceed with installation.

**Enterprise override:** If the enterprise manifest has `tooling.maven.install-command`,
use that command instead.

### 3.2 Install Maven

**macOS:**
```bash
brew install maven
```

**Linux (SDKMAN preferred):**
```bash
sdk install maven
```

**Linux (apt fallback):**
```bash
sudo apt install maven
```

**Linux (dnf fallback):**
```bash
sudo dnf install maven
```

**Windows:**
```powershell
winget install Apache.Maven
```

Fallback: `scoop install maven` or `choco install maven`

### 3.3 Verify Installation

```bash
mvn --version 2>&1
```

Confirm Maven 3.9+ is available. Same privilege policy as Phase 2.

---

## Phase 4: Akka CLI Installation

**Depends on:** Phase 2, Phase 3

### 4.1 Check Current Installation

```bash
akka version 2>&1
```

- If the Akka CLI is present: report *"Akka CLI [version] — already installed"* and **skip to Phase 5**.
- If missing: proceed with installation.

**Enterprise override:** If the enterprise manifest has `tooling.akka-cli.install-command`,
use that command instead.

### 4.2 Install Akka CLI

**macOS:**
```bash
brew install akka/brew/akka
```

**Linux:**
Download the binary from the Akka releases. The exact URL should be determined from
the Akka installation documentation at `https://doc.akka.io/reference/cli/installation.html`.

**Windows:**
Download the binary from the Akka releases page.

### 4.3 Verify Installation

```bash
akka version
```

Confirm the CLI is operational. If this fails, stop and ask the user for guidance.

---

## Phase 5: Akka Download Token

**Depends on:** Phase 4 (Akka CLI must be installed)

### 5.1 Check Maven Settings

Check if the Akka resolver is already configured in Maven settings:

```bash
grep -q "akka-repository" ~/.m2/settings.xml 2>/dev/null && echo "configured" || echo "not configured"
```

Also check for the plugin repository:
```bash
grep -q "akka-plugin-repository" ~/.m2/settings.xml 2>/dev/null && echo "configured" || echo "not configured"
```

- If both are configured: report *"Akka download token — already configured"* and **skip to Phase 6**.
- If missing: proceed with token provisioning.

**Enterprise override:** If the enterprise manifest has `tooling.maven.settings-overlay`,
download that settings file and merge it into `~/.m2/settings.xml` instead of running
the token flow. Inform the user which settings were applied.

### 5.2 Provision Token

Run the Akka CLI token command, which opens a browser for OAuth authentication:

```bash
akka code token
```

This will:
1. Open a browser window to `https://account.akka.io`
2. Ask the user to log in (or create a free account)
3. Automatically configure `~/.m2/settings.xml` with the Akka resolver

Tell the user: *"A browser window will open for you to log in to your Akka account.
This is a free account needed to download Akka SDK dependencies."*

### 5.3 Verify Token

After the token flow completes, verify:

```bash
grep -c "akka-repository" ~/.m2/settings.xml
grep -c "akka-plugin-repository" ~/.m2/settings.xml
```

Both should return 1 or more. If verification fails, inform the user and suggest
running `akka code token` manually.

---

## Phase 6: Docker (Optional)

### 6.1 Check Docker

```bash
docker info 2>/dev/null
```

- If Docker is running: report *"Docker [version] — available"* and continue.
- If Docker is not installed or not running: proceed to 6.2.

### 6.2 Ask the User

Inform the user:
*"Docker (or an equivalent container runtime) is only needed for:
- Running local clusters (`/akka.build` with multi-service setups)
- Building container images for deployment (`/akka.deploy`)

You can develop and test individual services without Docker."*

Ask: *"Would you like to install Docker now, or skip and install it later?
You can always rerun `/akka.setup` to install it."*

- **If the user wants to install now:** Use the appropriate command for their platform:
  - macOS: `brew install --cask docker`
  - Linux (apt): Follow Docker CE official install instructions (requires sudo — show commands and confirm)
  - Windows: `winget install Docker.DockerDesktop`
  - Verify with `docker info`

- **If the user defers:** Record that Docker was skipped. Continue to Phase 7.

**Enterprise override:** If the enterprise manifest has `tooling.docker.install-command`,
use that command. If `tooling.docker.runtime` is set (e.g., `podman`), check for that
runtime instead of Docker.

---

## Phase 7: Project Scaffolding

**Depends on:** Phases 2–5 (all core dependencies must be installed)

### 7A. New Project (no existing `pom.xml`)

#### 7A.1 Project Identity

Infer project identity from the current directory name:

```bash
basename "$(pwd)"
```

Apply naming rules:
- **artifactId**: lowercase, hyphens only, strip invalid characters
  - Example: `My Shopping Cart` → `my-shopping-cart`
- **groupId**: default to `com.example`
- **package**: derived from groupId (e.g., `com.example`)

Present to the user for confirmation:
*"Project identity:
  - artifactId: my-shopping-cart
  - groupId: com.example
  - package: com.example

Would you like to change any of these?"*

If the user wants changes, apply them.

#### 7A.2 Scaffold via Akka CLI

Run the Akka CLI init command in the current directory:

```bash
akka specify init . --agent claude-code
```

This command handles:
1. Cloning the empty project from `https://github.com/akka-samples/empty`
2. Customizing `pom.xml` with the user's artifactId and groupId
3. Downloading `akka-context/` documentation (~161 markdown files)
4. Downloading `CLAUDE.md` and `AGENTS.md`
5. Downloading the Akka SDK constitution
6. Installing 11 slash commands to `.claude/commands/`
7. Installing 4 SDD templates to `.akka/templates/`
8. Writing `.mcp.json` for the MCP server

If the init command detects that Maven is not configured, it will prompt for token
setup — this should already be done in Phase 5, so it will skip automatically.

#### 7A.3 Initialize Git

If git is not already initialized:

```bash
git init
git add .
git commit -m "Initial Akka project setup via /akka.setup"
```

#### 7A.4 Enterprise Post-Scaffolding

If an enterprise manifest was detected in Phase 1, apply these customizations AFTER
the standard scaffolding:

**Custom context extensions** (`context.additional-sources`):
For each additional source, download the content and place it at the specified path.
- Git repos: clone into the target directory
- Zip/tar URLs: download and extract
- Single files: download directly

**Custom constitutions** (`governance.constitutions`):
- If `mode: "merge"`: append the custom constitution content to `.akka/constitution/akka-sdk-constitution.md`
- If `mode: "replace"`: overwrite `.akka/constitution/akka-sdk-constitution.md` entirely

**Custom templates** (`governance.templates`):
- If `mode: "replace"`: download and overwrite the template in `.akka/templates/`
- If `mode: "add"`: download to `.akka/templates/` as a new template

**Governance rules** (`governance.rules`):
Append the rules to the constitution file as an "Enterprise Rules" section:
```markdown

## Enterprise Rules

The following rules are mandated by your organization:

- [rule 1]
- [rule 2]
...
```

**Skill overrides** (`sdlc.skill-overrides`):
For each override, download the custom skill and write it to `.claude/commands/[skill].md`,
replacing the default version.

**Maven settings** (`tooling.maven.mirrors`):
If Maven mirror configuration is specified, update `~/.m2/settings.xml` to include
the enterprise mirrors.

### 7B. Existing Project (repair/upgrade mode)

If `pom.xml` was detected in Phase 1, enter repair/upgrade mode.

#### 7B.1 Check SDK Version

Fetch the latest Akka SDK version:

```bash
curl -s https://doc.akka.io/sdk/_attachments/latest-version.txt
```

Read the current version from `pom.xml`:

```bash
grep -A1 '<parent>' pom.xml | grep '<version>' | sed 's/.*<version>\(.*\)<\/version>.*/\1/'
```

Compare the versions:
- If already on the latest: report *"Akka SDK [version] — already latest"*
- If behind: ask *"Akka SDK [current] is installed. Version [latest] is available.
  Would you like to upgrade?"*
  - If yes: update the `<version>` in the `<parent>` section of `pom.xml`
  - If no: continue with current version

#### 7B.2 Check for Missing Artifacts

Scan for missing files from the expected project structure:

```bash
# Check each expected artifact
test -f .mcp.json || echo "MISSING: .mcp.json"
test -d .akka/constitution || echo "MISSING: .akka/constitution/"
test -d .akka/templates || echo "MISSING: .akka/templates/"
test -d .claude/commands || echo "MISSING: .claude/commands/"
test -d akka-context || echo "MISSING: akka-context/"
test -f CLAUDE.md || echo "MISSING: CLAUDE.md"
test -f AGENTS.md || echo "MISSING: AGENTS.md"
```

For any missing artifacts, regenerate them:

```bash
# Regenerate SDD resources (commands, templates, constitution, .mcp.json)
akka specify init . --agent claude-code
```

This is idempotent — it will only create missing files, not overwrite existing ones.

#### 7B.3 Update Context Documentation

Refresh the Akka SDK context to the latest version:

```bash
akka code context-update . --assistant claude-code --force
```

#### 7B.4 Re-check Dependencies

Run through Phases 2–6 checks to verify all dependencies are still installed and current.
This is already handled by the sequential phase execution — each phase checks before acting.

#### 7B.5 Enterprise Repair

If an enterprise manifest is detected, apply the same enterprise customizations as in
7A.4 (custom context, constitutions, templates, rules, skill overrides).

---

## Phase 8: Akka Context Documentation

**For new projects:** Already handled by `akka specify init .` in Phase 7A.2.

**For existing projects (repair/upgrade):** Already handled by `akka code context-update`
in Phase 7B.3.

**Verification:** Confirm the context directory exists and has content:

```bash
ls akka-context/ | wc -l
```

Should show ~161 files. If empty or missing, run:

```bash
akka code context-update . --assistant claude-code --force
```

---

## Phase 9: AI Key Configuration (Optional)

### 9.1 Check Existing Keys

Check environment variables for known LLM provider keys:

```bash
[ -n "$ANTHROPIC_API_KEY" ] && echo "Anthropic: configured" || echo "Anthropic: not set"
[ -n "$OPENAI_API_KEY" ] && echo "OpenAI: configured" || echo "OpenAI: not set"
[ -n "$GOOGLE_AI_API_KEY" ] && echo "Google AI: configured" || echo "Google AI: not set"
```

Also check `src/main/resources/application.conf` if it exists:

```bash
grep -E "(api-key|apiKey|api_key)" src/main/resources/application.conf 2>/dev/null
```

### 9.2 Ask the User

Inform the user:
*"AI API keys are only needed if you're building Akka services that call LLM providers
(e.g., agent development). They are NOT needed for standard Akka service development."*

Ask: *"Would you like to configure AI API keys now, or skip and set them up later?
You can always rerun `/akka.setup` to configure them."*

- **If the user defers:** Record that AI keys were skipped. Continue to Phase 10.

### 9.3 Configure Keys

If the user wants to configure:

1. Ask which provider(s) they want to configure (Anthropic, OpenAI, Google AI, or other)
2. For each provider, ask for the key value
3. Ask where to store each key:

   **Option A — Environment variable (recommended):**
   More secure — not visible in the repo.
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```
   Inform the user they should also add this to their shell profile (`~/.bashrc`,
   `~/.zshrc`, etc.) for persistence.

   **Option B — application.conf:**
   Convenient for development but the key is visible in the repo if committed.
   Add to `src/main/resources/application.conf`:
   ```hocon
   anthropic {
     api-key = "sk-ant-..."
   }
   ```
   **Warn the user:** *"Keys in application.conf will be visible to anyone who can
   see the repository. Consider using environment variables for production."*

---

## Phase 10: Validation

Run all checks to confirm the environment is fully operational.

### 10.1 Dependency Checks

```bash
java -version 2>&1 | head -1
mvn --version 2>&1 | head -1
akka version 2>&1
grep -q "akka-repository" ~/.m2/settings.xml 2>/dev/null && echo "Token: configured" || echo "Token: not configured"
docker info 2>/dev/null | head -1 || echo "Docker: not available"
```

### 10.2 Build Check

For projects with a `pom.xml`, verify the toolchain works:

```bash
mvn compile -q 2>&1
```

If compilation fails, report the error but do not block completion — the user can
fix build issues with `/akka.build`.

### 10.3 Summary Report

Output a summary in this format:

```
/akka.setup — Complete

  Java 21 (Temurin)      ✓ installed
  Maven 3.9.6            ✓ installed
  Akka CLI 3.x.x         ✓ installed
  Akka download token    ✓ configured
  Docker 24.0.7          ✓ installed        (or: ⏭ deferred)
  SDK version            ✓ 3.x.x (latest)
  Project scaffolded     ✓ com.example:my-cart
  Akka context docs      ✓ 161 files
  AI keys                ⏭ deferred         (or: ✓ configured)

Ready to go! Run /akka.specify to start building your first feature.
```

If enterprise customizations were applied, add an enterprise section:

```
  Enterprise overrides active: [Enterprise Name]
    Custom context          ✓ [N] files in akka-context-[name]/
    Custom constitution     ✓ merged
    Custom templates        ✓ [N] additional
    Skill overrides         ✓ [list of overridden skills]
    Post-setup hooks        ✓ [N] executed
```

### 10.4 Enterprise Post-Setup Hooks

If the enterprise manifest has `tooling.post-setup-hooks`, execute each hook now:

For each hook:
1. Show the command and its description to the user
2. Ask for confirmation before executing
3. Run the command
4. Report success or failure

Variable substitution: Replace `${artifact_id}`, `${group_id}`, `${project_dir}`,
`${team}` (from `$AKKA_TEAM` env var) in the command strings.

---

## Enterprise Customization Reference

This section summarizes how enterprise manifest sections are applied across phases.
Each section is only processed if the manifest was detected in Phase 1.

| Manifest Section | Phase | Action |
|-----------------|-------|--------|
| `tooling.java.install-command` | 2 | Replace default Java install command |
| `tooling.java.verify-command` | 2 | Replace default Java version check |
| `tooling.maven.install-command` | 3 | Replace default Maven install command |
| `tooling.maven.settings-overlay` | 5 | Download and merge Maven settings |
| `tooling.maven.mirrors` | 5 | Add mirror config to Maven settings |
| `tooling.akka-cli.install-command` | 4 | Replace default CLI install command |
| `tooling.docker.install-command` | 6 | Replace default Docker install command |
| `tooling.docker.verify-command` | 6 | Replace default Docker check |
| `tooling.docker.runtime` | 6 | Check for alternative runtime (e.g., podman) |
| `context.additional-sources` | 7 | Download additional context after scaffolding |
| `governance.constitutions` | 7 | Merge or replace constitution |
| `governance.templates` | 7 | Replace or add templates |
| `governance.rules` | 7 | Append rules to constitution |
| `sdlc.skill-overrides` | 7 | Replace default slash commands |
| `sdlc.gates` | 7 | Document gates in project (for downstream skills) |
| `sdlc.environments` | 7 | Document environments in project |
| `tooling.post-setup-hooks` | 10 | Execute post-setup commands |

---

## Error Handling

When any phase fails:

1. **Report the error clearly** — tell the user what failed and the specific error message.
2. **Do not retry blindly** — if the same error persists after one fix attempt, stop and ask
   the user for guidance.
3. **Suggest alternatives** — if one package manager fails, suggest another:
   - Homebrew fails → suggest SDKMAN for Java/Maven
   - apt fails → suggest SDKMAN
   - If all package managers fail, provide manual download links
4. **Non-blocking optional phases** — Docker (Phase 6) and AI keys (Phase 9) failures
   should not block completion. Record as deferred and continue.
5. **Build failures in validation** — a failed `mvn compile` in Phase 10 should be reported
   but not block the setup summary. The user can fix build issues with `/akka.build`.

## Key Rules

- This is the ENTRY POINT — it runs before the Akka CLI exists, so Phases 1–4 use only bash
- IDEMPOTENT — every phase checks before acting; already-installed components are skipped
- TRANSPARENT — show commands before executing, especially for privileged operations
- USER IN CONTROL — optional phases (Docker, AI keys) are presented as choices, never forced
- NO SILENT PRIVILEGE ESCALATION — always ask before sudo
- DELEGATE TO CLI — after Phase 4, use `akka` CLI commands rather than reimplementing their logic
- ENTERPRISE EXTENSIBLE — every phase checks the manifest and applies overrides when present
