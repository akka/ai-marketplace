---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md after task generation.
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Before anything else

Open this run in the idea's record. Call the `akka_run_start` MCP tool with
`station: review`, `command: /akka:analyze` and `args` set to the user input.
Where the tool is not available, run `akka specify run start --station review
--command /akka:analyze` instead. Keep the run id it returns: the last step
closes the run. When it refuses because no idea matches the branch and none was
named, continue without a run, and say in one line that this run is not
recorded. On any other error or a non-zero exit, print its message verbatim and
stop. Do not continue, and do not work around it; the message names the remedy.
The one exception is a CLI that does not know the command (no `akka_run_start`
tool, and `run` rejected as an unknown command): it predates the idea record, so
say so and continue without a run.

The receipt under `.akka/record/` is the CLI's to write; it is not a file this
command modifies.

## Goal

Identify inconsistencies, duplications, ambiguities, and underspecified items across the three core artifacts (`spec.md`, `plan.md`, `tasks.md`) before implementation. This command MUST run only after `/akka:tasks` has successfully produced a complete `tasks.md`.

## Operating Constraints

**STRICTLY READ-ONLY**: Do **not** modify any files. Output a structured analysis report. Offer an optional remediation plan (user must explicitly approve before any follow-up editing commands would be invoked manually).

**Constitution Authority**: The constitution (`akka_sdd_constitution`) is **non-negotiable** within this analysis scope. Constitution conflicts are automatically CRITICAL and require adjustment of the spec, plan, or tasks—not dilution, reinterpretation, or silent ignoring of the principle.

## Execution Steps

### 1. Initialize Analysis Context

Call the `akka_sdd_list_specs` MCP tool to find features. Verify that tasks.md exists for the target feature (has_tasks must be true). If tasks.md is missing, instruct the user to run `/akka:tasks` first. Read the tasks.md content from FEATURE_DIR. Also note which other artifacts are available (AVAILABLE_DOCS).

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
- Task groups
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

- If CRITICAL issues exist: Recommend resolving before `/akka:implement`
- If only LOW/MEDIUM: User may proceed, but provide improvement suggestions
- Provide explicit command suggestions: e.g., "Run /akka:specify with refinement", "Run /akka:plan to adjust architecture", "Manually edit tasks.md to add coverage for 'performance-metrics'"

### 8. Offer Remediation

Ask the user: "Would you like me to suggest concrete remediation edits for the top N issues?" (Do NOT apply them automatically.)

### 9. Close the run

If a run was opened, call the `akka_run_close` MCP tool with `run` set to its id and no outputs: this command writes no file. Where the tool is not available, run `akka specify run close --run <id>`. On an error, print its message; the report stands.

### 10. Carry on or stop

Read the idea with `akka specify idea show <idea> --json`: `next` names the next station's command, and `waits` lists what waits on a person. Outside Enforced mode (`akka specify mode`), when `idea.advance` is `continue` and `waits` is empty, carry on into that command in this conversation, following its own instructions, instead of stopping. Never carry on into `/akka:ship` or `/akka:deploy`. Otherwise stop and name the next command: when `advance` is `step` or absent, in Enforced mode, when anything waits on a person, or when no run was opened.

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

## Done When

- [ ] `akka_sdd_list_specs` resolved FEATURE_DIR with `has_tasks == true`; `spec.md`, `plan.md`, and `tasks.md` were all read.
- [ ] The constitution was loaded via `akka_sdd_constitution` for principle validation.
- [ ] No files were modified — this run was strictly read-only.
- [ ] Every finding has a stable ID, category, severity (`CRITICAL` / `HIGH` / `MEDIUM` / `LOW`), source location(s), summary, and recommendation.
- [ ] Constitution MUST violations, if any, were flagged as CRITICAL.
- [ ] The findings table is capped at 50 rows, with any overflow summarized separately.
- [ ] A Coverage Summary table, Constitution Alignment Issues section (if any), Unmapped Tasks section (if any), and the Metrics block (total requirements, total tasks, coverage %, ambiguity count, duplication count, critical issues count) were all included.
- [ ] A Next Actions block named specific follow-up commands (`/akka:specify` refinement, `/akka:plan` adjustment, or manual edits to `tasks.md`) and recommended blocking `/akka:implement` iff CRITICAL issues exist.
- [ ] The user was offered — but not automatically given — concrete remediation edits for the top N issues.
- [ ] The run was opened at the `review` station with `akka_run_start` before any other step and closed with `akka_run_close` at the end, or the CLI was reported as predating the idea record.
- [ ] Outside Enforced mode, the command carried on into the next station's command only when the idea's `advance` was `continue` and nothing waited on a person, and never into `/akka:ship` or `/akka:deploy`; otherwise it stopped and named the next command.
