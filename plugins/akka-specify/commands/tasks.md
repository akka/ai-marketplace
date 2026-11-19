---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts.
handoffs:
  - label: Analyze For Consistency
    agent: akka.analyze
    prompt: Run a project analysis for consistency
    send: true
  - label: Implement Project
    agent: akka.implement
    prompt: Start the implementation in phases
    send: true
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
run and enforced the rules for it, so in a console run the run is open from the
first step: its id is the `run` `akka_run_context` answered. Any stop before the
normal close, such as a mode-check refusal, a missing argument, or a check that
needs a tool this run lacks, closes it with `akka_run_close`, that `run`,
`outcome: failed` and the reason. So in a console run: the feature is
`akka_run_context`'s `spec` (for `/akka:discover`, the topic is its `topic`),
and the command never searches for one; skip every step that finds, adopts,
starts or links an idea, and never ask a person a question: wherever this
command would ask one, it closes the run with `outcome: waiting` and `question`
set to the question (`--outcome waiting --question "<question>"` on the CLI);
the owner answers in the console, and the re-run reads the answer from
`akka_run_context`'s `questions` (`{station, run, question, answer}`) and does
not ask it again; run the mode check with `--idea` set to the `idea`
`akka_run_context` answered, and skip it when it cannot run here or no idea is
known; open the run by calling `akka_run_start` with `command` and `args` only,
no `idea` and no `station`, and the CLI joins the console's run; close it as
usual; and skip the carry-on step, because the console moves the idea on. A run
with no shell for the akka CLI that `akka_run_context` answers `console: false`
for is not a console run and keeps no record: open no run, ask nothing about
ideas or lanes, and carry the command out as before the idea record, skipping
every step marked **Idea record**.

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

The record names each station command by its `akka` plugin name, so this
plugin's commands open their runs under `/akka:` names.

**Idea record: open the run.** On a laptop run, call the `akka_run_start` MCP
tool with `station: tasks`, `command: /akka:tasks`, `idea` set to the idea found
above and `args` set to the user input. Where the tool is not available, run
`akka specify run start --station tasks --command /akka:tasks --idea <id> --args
"<the user input>" --json`, with the input quoted as one argument. A run is
never started without its idea. It answers JSON: `recorded`, and for a recorded
run its `idea` and `run.id`. Keep both: the last steps use them.

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

## Outline

1. **Setup**: Call the `akka_sdd_list_specs` MCP tool to find features and their available documents. From the response, identify the target feature's FEATURE_DIR and which artifacts exist (AVAILABLE_DOCS: spec.md, plan.md, tasks.md, etc.). If no features exist, instruct the user to run `/akka-specify:specify` first.

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (interface contracts), research.md (decisions), quickstart.md (test scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - Load spec.md and extract user stories with their priorities (P1, P2, P3, etc.)
   - If data-model.md exists: Extract entities and map to user stories
   - If contracts/ exists: Map interface contracts to user stories
   - If research.md exists: Extract decisions for setup tasks
   - Generate tasks organized by user story (see Task Generation Rules below)
   - Generate dependency graph showing user story completion order
   - Create parallel execution examples per user story
   - Validate task completeness (each user story has all needed tasks, independently testable)

4. **Generate tasks.md**: Use `akka_sdd_get_template` as structure, fill with:
   - Correct feature name from plan.md
   - Phase 1: Setup tasks (project initialization)
   - Phase 2: Foundational tasks (blocking prerequisites for all user stories)
   - Phase 3+: One phase per user story (in priority order from spec.md)
   - Each phase includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Phase: Polish & cross-cutting concerns
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - Dependencies section showing story completion order
   - Parallel execution examples per story
   - Implementation strategy section (MVP first, incremental delivery)

5. **Report**: Output path to generated tasks.md and summary:
   - Total task count
   - Task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)

6. **Close the run**. If a run was opened, call the `akka_run_close` MCP tool with `run` set to its id and `outputs` set to `FEATURE_DIR/tasks.md` as a project-relative path. Where the tool is not available, run `akka specify run close --run <id>` with `--file <path>` for tasks.md. On an error, print its message; the tasks already written stand.

7. **Idea record: end waiting for approval.** When a run was opened, the tasks now wait for the owner's approval before Implement runs. Say so and, when a run was opened, say how to give it: on the idea in the console's Ideas page, or `akka specify idea approve <idea> tasks`, where `<idea>` is the idea `akka_run_start` named. Do not carry out `/akka-specify:implement` or any later station; name `/akka-specify:implement` as the command for after the approval.

Context for task generation: $ARGUMENTS

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Story?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **[Story] label**: REQUIRED for user story phase tasks only
   - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md)
   - Setup phase: NO story label
   - Foundational phase: NO story label
   - User Story phases: MUST have story label
   - Polish phase: NO story label
5. **Description**: Clear action with exact file path

**Examples**:

- CORRECT: `- [ ] T001 Create project structure per implementation plan`
- CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- WRONG: `- [ ] Create User model` (missing ID and Story label)
- WRONG: `T001 [US1] Create model` (missing checkbox)
- WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** - PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own phase
   - Map all related components to their story:
     - Models needed for that story
     - Services needed for that story
     - Interfaces/UI needed for that story
     - If tests requested: Tests specific to that story
   - Mark story dependencies (most stories should be independent)

2. **From Contracts**:
   - Map each interface contract → to the user story it serves
   - If tests requested: Each interface contract → contract test task [P] before implementation in that story's phase

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it
   - If entity serves multiple stories: Put in earliest story or Setup phase
   - Relationships → service layer tasks in appropriate story phase

4. **From Setup/Infrastructure**:
   - Shared infrastructure → Setup phase (Phase 1)
   - Foundational/blocking tasks → Foundational phase (Phase 2)
   - Story-specific setup → within that story's phase

### Phase Structure

- **Phase 1**: Setup (project initialization)
- **Phase 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Phase 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
  - Each phase should be a complete, independently testable increment
- **Final Phase**: Polish & Cross-Cutting Concerns
