---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Before anything else

This command keeps a run in the idea's record when the akka CLI has one: the
`akka_run_start` MCP tool is available, or the output of `akka specify run start
--help` contains `--station`. A CLI without it predates the idea record. With
such a CLI, say so once and carry this command out as before: skip every step
marked **Idea record**, and open no run.

**Idea record: a console run.** Call the `akka_run_context` MCP tool first when
it is available: it answers `{ console, idea, station, run }`, and `console:
true` means the console started this command. Only without that tool, the
console started it when `AKKA_RUN_ID` is set in its environment, or when the
command has no shell to run the akka CLI in. The console has already opened the
run and enforced the rules for it. So in a console run: skip every step that
finds, adopts, starts or links an idea, and ask no question before the run is
closed; run the mode check with `--idea` set to the `idea` `akka_run_context`
answered, and skip it when it cannot run here or no idea is known; open the run
by calling `akka_run_start` with `command` and `args` only, no `idea` and no
`station`, and the CLI joins the console's run; close it as usual; and skip the
carry-on step, because the console moves the idea on. A run with no shell for
the akka CLI that `akka_run_context` answers `console: false` for is not a
console run and keeps no record: open no run, ask nothing about ideas or lanes,
and carry the command out as before the idea record, skipping every step marked
**Idea record**.

**Idea record: find the idea.** On a laptop run, find the feature this command
works on first: call `akka_sdd_list_specs` and identify the target feature as
the first step below does. Its idea is the one in `akka specify idea list
--json` whose `spec` is the feature's folder name (`NNN-name`); an idea is never
found from the git branch. When that idea has `derived: true`, it has no record
yet: adopt it with `akka specify ideas adopt --idea <id>`, then use it. When no
idea has it, read the mode with `akka specify mode`. In À la carte mode, open no
run: say in one line that this run is not recorded, and continue. In Enforced
mode, stop: the project's specs and topics get their ideas once with `akka
specify ideas adopt`, and this command runs after that. Pass the idea's id as
`idea` to the run start.

On a laptop run, the run opens at one of two stations. When this command was
reached by carrying on from another station command's `akka specify idea next`,
it opens at that answer's `next.station` (Review). When a person invoked it, it
opens at the idea's current station, its `at` in the same list: the CLI records
`/akka:analyze` there from Tasks on, without moving the idea on. The station it
opens at is the station it carries on from.

The record names each station command by its `akka` plugin name, so this
plugin's commands open their runs under `/akka:` names.

The receipt under `.akka/record/` is the CLI's to write; it is not a file this
command modifies.

**Idea record: open the run.** On a laptop run, call the `akka_run_start` MCP
tool with `station` set to the station above, `command: /akka:analyze`, `idea`
set to the idea found above and `args` set to the user input. Where the tool is
not available, run `akka specify run start --station <station> --command
/akka:analyze --idea <id> --args "<the user input>" --json`, with the input
quoted as one argument. A run is never started without its idea. It answers
JSON: `recorded`, and for a recorded run its `idea` and `run.id`. Keep both: the
last steps use them.

- When it answers `recorded: false`, continue without a run, and say in one line
  that this run is not recorded, with its `reason`.
- A refusal by rule is an error whose JSON is `{refused, message, remedy}`,
  `refused` naming the rule: `paused`, `limit`, `shipped`, `dropped`,
  `approval`, `order`, `no-idea-enforced`, `idea-unresolved` or `console-run`.
  Print `message` and `remedy` verbatim and stop.
- Any other error, one without `refused` (such as no login), does not stop the
  command: continue without a run, and say in one line that this run is not
  recorded.

**Idea record: a run that fails is closed too.** Once the run is open, every way
the command ends closes it. When the work fails (a build or tests fail, or a
step stops the command early), call `akka_run_close` with `run`, `outcome:
failed` and `error` set to what failed, in one line, then stop. Where the tool
is not available, run `akka specify run close --run <id> --outcome failed
--error "<what failed>"`. When the person stops the command, close the run with
`outcome: stopped`. This holds in a console run too. The close step below is for
the work's normal end.

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This command MUST run only after `/akka-specify:tasks` has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The constitution (`akka_sdd_constitution`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle.

## Execution Steps

### 1. Initialize Analysis Context

Call the `akka_sdd_list_specs` MCP tool to find features. Verify that tasks.md exists for the target feature (has_tasks must be true). If tasks.md is missing, instruct the user to run `/akka-specify:tasks` first. Read the tasks.md content from FEATURE_DIR. Also note which other artifacts are available (AVAILABLE_DOCS).

- SPEC = FEATURE_DIR/spec.md
- PLAN = FEATURE_DIR/plan.md
- TASKS = FEATURE_DIR/tasks.md

Abort with an error message if any required file is missing (instruct the user to run missing prerequisite command).

### 2. Load Artifacts (Progressive Disclosure)

Load only the minimal necessary context from each artifact:

**From spec.md:**

- Overview/Context
- Functional Requirements
- Non-Functional Requirements
- User Stories
- Edge Cases (if present)

**From plan.md:**

- Architecture/stack choices
- Data Model references
- Phases
- Technical constraints

**From tasks.md:**

- Task IDs
- Descriptions
- Phase grouping
- Parallel markers [P]
- Referenced file paths

**From constitution:**

- Load `akka_sdd_constitution` for principle validation

### 3. Build Semantic Models

Create internal representations (do not include raw artifacts in output):

- **Requirements inventory**: Each functional + non-functional requirement with a stable key (derive slug based on imperative phrase; e.g., "User can upload file" → `user-can-upload-file`)
- **User story/action inventory**: Discrete user actions with acceptance criteria
- **Task coverage mapping**: Map each task to one or more requirements or stories (inference by keyword / explicit reference patterns like IDs or key phrases)
- **Constitution rule set**: Extract principle names and MUST/SHOULD normative statements

### 4. Detection Passes (Token-Efficient Analysis)

Focus on high-signal findings. Limit to 50 findings total; aggregate remainder in overflow summary.

#### A. Duplication Detection

- Identify near-duplicate requirements
- Mark lower-quality phrasing for consolidation

#### B. Ambiguity Detection

- Flag vague adjectives (fast, scalable, secure, intuitive, robust) lacking measurable criteria
- Flag unresolved placeholders (TODO, TKTK, ???, `<placeholder>`, etc.)

#### C. Underspecification

- Requirements with verbs but missing object or measurable outcome
- User stories missing acceptance criteria alignment
- Tasks referencing files or components not defined in spec/plan

#### D. Constitution Alignment

- Any requirement or plan element conflicting with a MUST principle
- Missing mandated sections or quality gates from constitution

#### E. Coverage Gaps

- Requirements with zero associated tasks
- Tasks with no mapped requirement/story
- Non-functional requirements not reflected in tasks (e.g., performance, security)

#### F. Inconsistency

- Terminology drift (same concept named differently across files)
- Data entities referenced in plan but absent in spec (or vice versa)
- Task ordering contradictions (e.g., integration tasks before foundational setup tasks without dependency note)
- Conflicting requirements (e.g., one requires Next.js while other specifies Vue)

### 5. Severity Assignment

Use this heuristic to prioritize findings:

- **CRITICAL**: Violates constitution MUST, missing core spec artifact, or requirement with zero coverage that blocks baseline functionality
- **HIGH**: Duplicate or conflicting requirement, ambiguous security/performance attribute, untestable acceptance criterion
- **MEDIUM**: Terminology drift, missing non-functional task coverage, underspecified edge case
- **LOW**: Style/wording improvements, minor redundancy not affecting execution order

### 6. Produce Compact Analysis Report

Output a Markdown report (no file writes) with the following structure:

## Specification Analysis Report

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Duplication | HIGH | spec.md:L120-134 | Two similar requirements ... | Merge phrasing; keep clearer version |

(Add one row per finding; generate stable IDs prefixed by category initial.)

**Coverage Summary Table:**

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|

**Constitution Alignment Issues:** (if any)

**Unmapped Tasks:** (if any)

**Metrics:**

- Total Requirements
- Total Tasks
- Coverage % (requirements with >=1 task)
- Ambiguity Count
- Duplication Count
- Critical Issues Count

### 7. Provide Next Actions

At end of report, output a concise Next Actions block:

- If CRITICAL issues exist: Recommend resolving before `/akka-specify:implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /akka-specify:specify with refinement", "Run /akka-specify:plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'"

### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

### 9. Close the run

If a run was opened, call the `akka_run_close` MCP tool with `run` set to its id and no outputs: this command writes no file. Where the tool is not available, run `akka specify run close --run <id>`. On an error, print its message; the report stands.

### 10. Carry on or stop

In a console run, skip this step: the console moves the idea on. Carry on only when the report has no CRITICAL issue and this command asked the user nothing; with no issues, step 8 has nothing to offer. Otherwise stop and say why: the CRITICAL issues, or the question that waits for an answer. When neither holds: if a run was opened, run `akka specify idea next --idea <idea> --from <the station the run opened at> --json`, where `<idea>` is the `idea` the run start returned. It answers `{ go, next, reason }`. When `go` is true, carry on into the `/akka-specify:` command of the same name in this conversation, following its own instructions, when this plugin has one. Otherwise stop, print `reason`, and name `next.command` when there is one. This plugin has no `conform`, `converge` or `ship`: for those, stop and name the `/akka:` command. Without a run, stop and name the next command.

## Operating Principles

### Context Efficiency

- **Minimal high-signal tokens**: Focus on actionable findings, not exhaustive documentation
- **Progressive disclosure**: Load artifacts incrementally; don't dump all content into analysis
- **Token-efficient output**: Limit findings table to 50 rows; summarize overflow
- **Deterministic results**: Rerunning without changes should produce consistent IDs and counts

### Analysis Guidelines

- **NEVER modify files** (this is read-only analysis)
- **NEVER hallucinate missing sections** (if absent, report them accurately)
- **Prioritize constitution violations** (these are always CRITICAL)
- **Use examples over exhaustive rules** (cite specific instances, not generic patterns)
- **Report zero issues gracefully** (emit success report with coverage statistics)
