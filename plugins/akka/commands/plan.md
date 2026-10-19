---
description: Execute the implementation planning workflow using the plan template to generate design artifacts.
handoffs:
  - label: Create Tasks
    agent: akka.tasks
    prompt: Break the plan into tasks
    send: true
  - label: Create Checklist
    agent: akka.checklist
    prompt: Create a checklist for the following domain...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Call the `akka_sdd_list_specs` MCP tool to find the target feature. Then call `akka_sdd_get_template` with template_name="plan" to get the plan template. Identify the feature's spec path (FEATURE_SPEC) and plan destination (FEATURE_DIR/plan.md).

2. **Load context**: Read FEATURE_SPEC, `akka_sdd_constitution`, and `FEATURE_DIR/checklists/requirements.md` if it exists. Use the shared "Open policy decision format" defined in the Specify instructions: under `## Open policy decisions`, unchecked `OPD-<number>` entries are unresolved; checked entries must link to the saved answer in `../spec.md#<section-anchor>`. Preserve IDs and treat malformed entries or invalid resolution references as unresolved. Check both spec clarification markers and unresolved entries under "Open policy decisions" before technical research. If policy decisions remain open, report them and recommend `/akka:clarify`; do not choose policy values through research or declare the plan ready. If the user explicitly requests exploratory planning despite them, preserve each item as unresolved in `plan.md` and `research.md`, state the affected work and risk, and keep readiness blocked until those decisions are resolved. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - If the spec involves agents or model-generated behavior: check the project's installed Akka SDK version and its local documentation before choosing guardrail, classifier, sanitizer, evaluator, or identity mechanisms. Do not assume Akka SDK 3.7 features are available and do not upgrade the Akka SDK implicitly; if a required feature needs a newer Akka SDK, record the upgrade as an explicit decision in research.md.
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Map domain concepts to Akka components (Component Architecture table), then generate data-model.md, contracts/, quickstart.md
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Command ends after Phase 2 planning. Report branch, IMPL_PLAN path, and generated artifacts.

## Phases

### Phase 0: Outline & Research

1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:

   ```text
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

### Phase 1: Design & Contracts

**Prerequisites:** `research.md` complete

1. **Map domain concepts to Akka components** → the Component Architecture table in plan.md:
   - Read the "Choosing a component type" section in `akka-context/sdk/components/index.html.md` (first time in session) before mapping
   - For each domain concept, process, and query in the spec, choose the component per the decision guide: entity type (Key Value vs Event Sourced), Workflow vs Consumer, whether a View is needed, endpoint type, or a plain domain class instead of a component
   - Record every choice in the table with the reason. Where the decision guide names a close alternative (entity type, view vs direct entity read, workflow vs consumer, timed action vs workflow timer), also record the rejected alternative and why it was not chosen
   - ERROR if a close-call row lacks the rejected alternative

2. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

3. **Define interface contracts** (if project has external interfaces) → `/contracts/`:
   - Identify what interfaces the project exposes to users or other systems
   - Document the contract format appropriate for the project type
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications
   - Skip if project is purely internal (build scripts, one-off tools, etc.)

4. **Agent context update**:
   - Agent context files are managed automatically by the Akka CLI when running `akka_sdd_init`. No manual agent context update is needed.

**Output**: Component Architecture table in plan.md, data-model.md, /contracts/*, quickstart.md

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications

## Done When

- [ ] FEATURE_DIR, FEATURE_SPEC, and the plan template were resolved via `akka_sdd_list_specs` and `akka_sdd_get_template`.
- [ ] Technical Context is filled with concrete values; any remaining unknowns are explicitly marked `NEEDS CLARIFICATION`.
- [ ] The spec and requirements checklist were checked for open policy decisions; none were guessed, dropped, or treated as resolved by research. Any explicitly requested exploratory plan retains them and is not reported ready.
- [ ] Constitution Check was filled from `akka_sdd_constitution`, evaluated before Phase 0, and re-evaluated after Phase 1 design — with any violations either resolved or explicitly justified in the Complexity Tracking section.
- [ ] Phase 0 produced `research.md` with every `NEEDS CLARIFICATION` resolved (Decision / Rationale / Alternatives).
- [ ] The Component Architecture table in `plan.md` maps every domain concept, process, and query to a component (or a plain domain class), with close-call rows naming the rejected alternative and why it was not chosen — informed by the "Choosing a component type" section of `akka-context/sdk/components/index.html.md`.
- [ ] Phase 1 produced `data-model.md`, `quickstart.md`, and — if the project exposes external interfaces — `contracts/`.
- [ ] `FEATURE_DIR/plan.md` was written using the template structure and no gate error was left unresolved.
- [ ] Completion was reported with the branch, plan path, generated artifacts, and the next-command recommendation (`/akka:tasks`).
