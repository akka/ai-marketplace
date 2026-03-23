# Enterprise Manifest Schema

Maintenance reference for `/akka-specify:setup` enterprise customization. Documents the `.akka/enterprise.yaml` manifest format.

## Manifest Locations (Precedence Order)

1. **Project-level**: `.akka/enterprise.yaml` (checked into the project repo)
2. **User-level**: `~/.akka/enterprise.yaml` (org-wide defaults on developer's machine)
3. **URL-fetched**: From `$AKKA_ENTERPRISE_CONFIG_URL` environment variable

Project-level overrides user-level, which overrides URL-fetched.

## Full Schema

```yaml
# Enterprise customization manifest for /akka-specify:setup
# Version 1.0

version: "1"

# ─── A. Custom Context Extensions ───────────────────────────────────
# Additional documentation sources merged alongside akka-context/
context:
  additional-sources:
    - name: "acme-patterns"
      # Source can be a git repo URL, zip URL, or local path
      source: "https://git.internal.acme.com/akka-patterns/akka-context.git"
      # Target directory relative to project root
      path: "akka-context-acme/"
    - name: "acme-security"
      source: "https://artifactory.acme.com/akka/security-guidelines.tar.gz"
      path: "akka-context-acme/security/"

# ─── B. Governance Requirements ─────────────────────────────────────
# Architectural standards, compliance rules, and coding conventions
governance:
  # Custom constitutions merged with or replacing the default
  constitutions:
    - source: "https://git.internal.acme.com/governance/akka-constitution.md"
      # "merge" adds to default, "replace" overrides entirely
      mode: "merge"

  # Custom templates that replace or extend defaults
  templates:
    - name: "spec"
      source: "https://git.internal.acme.com/governance/templates/spec.md"
      mode: "replace"
    - name: "security-checklist"
      source: "https://git.internal.acme.com/governance/templates/security-checklist.md"
      # "add" creates a new template type (doesn't replace existing)
      mode: "add"

  # Free-text rules surfaced to the AI assistant via constitution
  rules:
    - "All entities must use event sourcing"
    - "All endpoints require @Acl annotation with explicit principal"
    - "No secrets in application.conf — use environment variables only"

# ─── C. Internal Tooling and Onboarding ─────────────────────────────
# Override dependency installation methods and Maven configuration
tooling:
  # Override install commands (used instead of defaults in Phases 2-4)
  java:
    install-command: "corp-sdk install java@21"
    verify-command: "java --version"
  maven:
    install-command: "corp-sdk install maven@3.9"
    # Additional Maven settings to inject
    settings-overlay: "https://portal.acme.com/maven/settings-overlay.xml"
    # Maven repository mirrors
    mirrors:
      - id: "acme-central"
        url: "https://artifactory.acme.com/maven-central/"
        mirror-of: "central"
  docker:
    install-command: "corp-sdk install podman"
    verify-command: "podman info"
    # Signals to /akka-specify:build and /akka-specify:deploy to use this runtime
    runtime: "podman"
  akka-cli:
    install-command: "curl -s https://internal.acme.com/akka/install.sh | bash"

  # Commands run after setup completes
  post-setup-hooks:
    - name: "Register in Backstage"
      command: "backstage-cli register --type akka-service --name ${artifact_id}"
    - name: "Configure git remote"
      command: "git remote add origin https://git.acme.com/${team}/${artifact_id}.git"
    - name: "Create CI pipeline"
      command: "corp-ci create-pipeline --template akka-service --repo ${artifact_id}"

# ─── D. SDLC Component Overrides ────────────────────────────────────
# Override downstream skill behavior, add gates, define environments
sdlc:
  # Replace default slash commands with enterprise versions
  skill-overrides:
    - skill: "akka.deploy"
      source: "https://git.internal.acme.com/akka-skills/deploy-gitops.md"
    - skill: "akka.build"
      source: "https://git.internal.acme.com/akka-skills/build-internal.md"
    - skill: "akka.review"
      source: "https://git.internal.acme.com/akka-skills/review-compliance.md"

  # Checkpoints requiring external approval or validation
  gates:
    pre-deploy:
      - name: "Security scan"
        command: "corp-security scan --project ."
        required: true
      - name: "Change request"
        command: "corp-cm create-cr --service ${artifact_id} --env ${environment}"
        required-for: ["staging", "prod"]
    pre-implement:
      - name: "Architecture review"
        # "condition" is evaluated by the AI assistant
        condition: "component_type in [workflow, agent]"
        action: "prompt"
        message: "Has this design been reviewed by the architecture board?"

  # Deployment environment profiles
  environments:
    dev:
      deploy-target: "direct"
      approval-required: false
    staging:
      deploy-target: "gitops"
      gitops-repo: "https://git.acme.com/gitops/staging.git"
      approval-required: true
      approvers: ["team-lead", "sre-oncall"]
    prod:
      deploy-target: "gitops"
      gitops-repo: "https://git.acme.com/gitops/production.git"
      approval-required: true
      approvers: ["engineering-director", "sre-lead"]
      change-management: true
```

## Variable Substitution

The following variables are available in `command` strings and `source` URLs:

| Variable | Description | Example |
|----------|-------------|---------|
| `${artifact_id}` | Maven artifactId from pom.xml | `my-shopping-cart` |
| `${group_id}` | Maven groupId from pom.xml | `com.acme` |
| `${project_dir}` | Absolute path to project root | `/home/dev/my-shopping-cart` |
| `${team}` | Value of `AKKA_TEAM` env var | `payments` |
| `${environment}` | Target deployment environment | `staging` |

## Section Processing in /akka-specify:setup

| Manifest Section | Applied During |
|-----------------|----------------|
| `tooling.java` | Phase 2 (Java Installation) |
| `tooling.maven` | Phase 3 (Maven Installation) |
| `tooling.docker` | Phase 6 (Docker) |
| `tooling.akka-cli` | Phase 4 (Akka CLI Installation) |
| `context.additional-sources` | Phase 7/8 (after standard context) |
| `governance.constitutions` | Phase 7 (after SDD init) |
| `governance.templates` | Phase 7 (after SDD init) |
| `governance.rules` | Phase 7 (written to constitution) |
| `sdlc.skill-overrides` | Phase 7 (after commands installed) |
| `tooling.post-setup-hooks` | After Phase 9 |
| `sdlc.gates` | Informational — documented in project for downstream skills |
| `sdlc.environments` | Informational — documented in project for downstream skills |
