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

## Before anything else

Open this run in the idea's record. Call the `akka_run_start` MCP tool with
`station: plan`, `command: /akka:plan` and `args` set to the user input. Where
the tool is not available, run `akka specify run start --station plan --command
/akka:plan` instead. Keep the run id it returns: the last step closes the run.
When it refuses because no idea matches the branch and none was named, continue
without a run, and say in one line that this run is not recorded. On any other
error or a non-zero exit, print its message verbatim and stop. Do not continue,
and do not work around it; the message names the remedy. The one exception is a
CLI that does not know the command (no `akka_run_start` tool, and `run` rejected
as an unknown command): it predates the idea record, so say so and continue
without a run.

The record names each station command by its `akka` plugin name, so this
plugin's commands open their runs under `/akka:` names.

## Outline

1. **Setup**: Call the `akka_sdd_list_specs` MCP tool to find the target feature. Then call `akka_sdd_get_template` with template_name="plan" to get the plan template. Identify the feature's spec path (FEATURE_SPEC) and plan destination (FEATURE_DIR/plan.md).

2. **Load context**: Read FEATURE_SPEC and `akka_sdd_constitution`. Load IMPL_PLAN template (already copied).

3. **Execute plan workflow**: Follow the structure in IMPL_PLAN template to:
   - Fill Technical Context (mark unknowns as "NEEDS CLARIFICATION")
   - Fill Constitution Check section from constitution
   - Evaluate gates (ERROR if violations unjustified)
   - Phase 0: Generate research.md (resolve all NEEDS CLARIFICATION)
   - Phase 1: Generate data-model.md, contracts/, quickstart.md
   - Re-evaluate Constitution Check post-design

4. **Stop and report**: Planning ends after Phase 2. Report branch, IMPL_PLAN path, and generated artifacts.

5. **Close the run**. If a run was opened, call the `akka_run_close` MCP tool with `run` set to its id and `outputs` set to the files and folders this run wrote, as project-relative paths: `plan.md`, `research.md`, `data-model.md`, `quickstart.md` and `contracts/` under FEATURE_DIR, whichever exist. A folder ends in `/`. Where the tool is not available, run `akka specify run close --run <id>` with one `--output <path>` for each output. On an error, print its message; the plan already written stands.

6. **Carry on or stop.** Read the idea with `akka specify idea show <idea> --json`: `next` names the next station's command, and `waits` lists what waits on a person. Outside Enforced mode (`akka specify mode`), when `idea.advance` is `continue` and `waits` is empty, carry on into the `/akka-specify:` command of that name in this conversation, following its own instructions, instead of stopping. Never carry on into `/akka:ship` or `/akka:deploy`. Otherwise stop and name the next command: when `advance` is `step` or absent, in Enforced mode, when anything waits on a person, or when no run was opened.

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

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Define interface contracts** (if project has external interfaces) → `/contracts/`:
   - Identify what interfaces the project exposes to users or other systems
   - Document the contract format appropriate for the project type
   - Examples: public APIs for libraries, command schemas for CLI tools, endpoints for web services, grammars for parsers, UI contracts for applications
   - Skip if project is purely internal (build scripts, one-off tools, etc.)

3. **Agent context update**:
   - Agent context files are managed automatically by the Akka CLI when running `akka_sdd_init`. No manual agent context update is needed.

**Output**: data-model.md, /contracts/*, quickstart.md

## Key rules

- Use absolute paths
- ERROR on gate failures or unresolved clarifications
