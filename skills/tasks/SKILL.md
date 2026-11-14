---
name: tasks
description: "Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts."
---

## User Input

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. **Setup**: Call the `akka_sdd_list_specs` MCP tool to find features and their available documents. From the response, identify the target feature's FEATURE_DIR and which artifacts exist (AVAILABLE_DOCS: spec.md, plan.md, tasks.md, etc.). If no features exist, instruct the user to run `/akka:specify` first. Then, if you are running in Claude Code (the plugin's hooks run only there; skip the run record in any other harness), start the run record: write `.akka/runs/build/.active.json` (create the folders) as JSON with `spec` (the name of FEATURE_DIR's folder), `command` (`tasks`), `startedAt` (the current UTC time as `YYYY-MM-DDTHH:MM:SSZ`, from a clock command such as `date -u +%Y-%m-%dT%H:%M:%SZ`, or `(Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ssZ')` in PowerShell), `tasksFile` (FEATURE_DIR/tasks.md, relative to the project root) and `tasksDone` (the ids of the tasks already ticked in tasks.md, or `[]` when tasks.md does not exist). The plugin's Stop and SessionEnd hooks read this file to record the session's model usage under `.akka/runs/build/<spec>/`. Add `.akka/runs/build/.active.json` and `.akka/runs/build/.state.json` to the project's `.gitignore` if they are not listed, so no commit stages them. If the file cannot be written, continue without it.

2. **Load design documents**: Read from FEATURE_DIR:
   - **Required**: plan.md (tech stack, libraries, structure), spec.md (user stories with priorities)
   - **Optional**: data-model.md (entities), contracts/ (interface contracts), research.md (decisions), quickstart.md (test scenarios)
   - Note: Not all projects have all documents. Generate tasks based on what's available.

3. **Execute task generation workflow**:
   - Load plan.md and extract tech stack, libraries, project structure
   - If plan.md has Delivery Phases and a Model Plan: extract each phase (its `### Phase <n>` heading, goal and acceptance test) and the model for each phase and purpose, to tag tasks with `[Ph<n>]` and `[model: <name>]`
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
   - Group 1: Setup tasks (project initialization)
   - Group 2: Foundational tasks (blocking prerequisites for all user stories)
   - Group 3+: One group per user story (in priority order from spec.md)
   - Each group includes: story goal, independent test criteria, tests (if requested), implementation tasks
   - Final Group: Polish & cross-cutting concerns
   - All tasks must follow the strict checklist format (see Task Generation Rules below)
   - Clear file paths for each task
   - A User Story Dependencies section with one line per user story, `- **USn**: <stories it needs> (why)`, or `- **USn**: none (why)` for a story that needs no other; every story has a line, and the console reads these lines
   - Parallel execution examples per story
   - Implementation strategy section (MVP first, incremental delivery)

5. **Refresh the docs.** Before reporting, in this session, run `/akka:docs` (the implementation docs and the Story) so they match what this command wrote. Keep its outcome for the report. If you started a run record, then set `"closing": true` in `.akka/runs/build/.active.json` now; the plugin's next Stop hook writes the record and removes the marker.

6. **Report** (the last step, after the docs refresh): Output path to generated tasks.md and summary:
   - Total task count
   - Task count per user story
   - Parallel opportunities identified
   - Independent test criteria for each story
   - Suggested MVP scope (typically just User Story 1)
   - Format validation: Confirm ALL tasks follow the checklist format (checkbox, ID, labels, file paths)

Context for task generation: the user's request

The tasks.md should be immediately executable - each task must be specific enough that an LLM can complete it without additional context.

## Task Generation Rules

**CRITICAL**: Tasks MUST be organized by user story to enable independent implementation and testing.

**Tests are OPTIONAL**: Only generate test tasks if explicitly requested in the feature specification or if user requests TDD approach.

### Checklist Format (REQUIRED)

Every task MUST strictly follow this format:

```text
- [ ] [TaskID] [P?] [Ph<phase>?] [Story?] [model: <name>?] [effort: <level>?] Description with file path
```

**Format Components**:

1. **Checkbox**: ALWAYS start with `- [ ]` (markdown checkbox)
2. **Task ID**: Sequential number (T001, T002, T003...) in execution order
3. **[P] marker**: Include ONLY if task is parallelizable (different files, no dependencies on incomplete tasks)
4. **[Story] label**: REQUIRED for user story group tasks only
   - Format: [US1], [US2], [US3], etc. (maps to user stories from spec.md)
   - Setup group: NO story label
   - Foundational group: NO story label
   - User Story groups: MUST have story label
   - Polish group: NO story label
5. **[Ph<phase>] tag**: REQUIRED when plan.md has a Delivery Phases section, otherwise omitted
   - Format: [Ph1], [Ph2], ... naming the plan's `### Phase <n>` heading the task delivers
   - Every phase in plan.md has at least one task, and no task names a phase plan.md does not have
   - This is the plan's delivery phase. It is independent of this file's own numbered groups (Setup, Foundational, one per user story), so a task in "Group 3: User Story 1" may carry [Ph2]
6. **[model: <name>] tag**: OPTIONAL
   - Include it when plan.md's Model Plan has a row for the task's phase and purpose (design, implementation, review, tests, research, visual checks, documentation); use that row's model
   - Omit it when there is no Model Plan; `/akka:implement` then chooses from `.akka/models.md`
7. **[effort: low|medium|high] tag**: OPTIONAL
   - Write it directly after the `[model: <name>]` tag, using the effort in the same Model Plan row
   - Omit it whenever the `[model: <name>]` tag is omitted
8. **Description**: Clear action with exact file path

**Examples**:

- CORRECT: `- [ ] T001 Create project structure per implementation plan`
- CORRECT: `- [ ] T005 [P] Implement authentication middleware in src/middleware/auth.py`
- CORRECT: `- [ ] T012 [P] [US1] Create User model in src/models/user.py`
- CORRECT: `- [ ] T014 [US1] Implement UserService in src/services/user_service.py`
- CORRECT: `- [ ] T015 [P] [Ph2] [US1] [model: sonnet] [effort: medium] Create Order record in src/main/java/com/example/domain/Order.java`
- WRONG: `- [ ] T016 [US1] [Ph2] Create model in src/models/order.py` (phase tag after the story label)
- WRONG: `- [ ] Create User model` (missing ID and Story label)
- WRONG: `T001 [US1] Create model` (missing checkbox)
- WRONG: `- [ ] [US1] Create User model` (missing Task ID)
- WRONG: `- [ ] T001 [US1] Create model` (missing file path)

### Task Organization

1. **From User Stories (spec.md)** - PRIMARY ORGANIZATION:
   - Each user story (P1, P2, P3...) gets its own group
   - Map all related components to their story:
     - Models needed for that story
     - Services needed for that story
     - Interfaces/UI needed for that story
     - If tests requested: Tests specific to that story
   - Mark story dependencies (most stories should be independent) as the User Story Dependencies lines

2. **From Contracts**:
   - Map each interface contract → to the user story it serves
   - If tests requested: Each interface contract → contract test task [P] before implementation in that story's group

3. **From Data Model**:
   - Map each entity to the user story(ies) that need it
   - If entity serves multiple stories: Put in earliest story or Setup group
   - Relationships → service layer tasks in appropriate story group

4. **From Setup/Infrastructure**:
   - Shared infrastructure → Setup group (Group 1)
   - Foundational/blocking tasks → Foundational group (Group 2)
   - Story-specific setup → within that story's group

### Group Structure

- **Group 1**: Setup (project initialization)
- **Group 2**: Foundational (blocking prerequisites - MUST complete before user stories)
- **Group 3+**: User Stories in priority order (P1, P2, P3...)
  - Within each story: Tests (if requested) → Models → Services → Endpoints → Integration
  - Each group should be a complete, independently testable increment
- **Final Group**: Polish & Cross-Cutting Concerns

## Done When

- [ ] `FEATURE_DIR/tasks.md` was written using the template returned by `akka_sdd_get_template` (or the built-in fallback if the template call returned empty).
- [ ] Group structure is Group 1 Setup, Group 2 Foundational, Group 3+ one group per user story in priority order, and a Final Polish group.
- [ ] Every task line strictly matches `- [ ] TXXX [P?] [Ph<phase>?] [Story?] [model: <name>?] [effort: <level>?] <description with file path>` — task ID, optional `[P]` parallel marker, `[Ph<n>]` delivery-phase tag on every task when plan.md has Delivery Phases, `[US#]` label on user-story-group tasks only, `[model: <name>]` and `[effort: <level>]` only where the Model Plan names them, and an exact file path.
- [ ] When plan.md has Delivery Phases, every phase has at least one task and every `[Ph<n>]` names a phase that exists.
- [ ] Task IDs are sequential (`T001, T002, …`) and unique across the file.
- [ ] Every user story from spec.md has all needed tasks and is independently testable per the story goal and independent test criteria in its group header.
- [ ] A User Story Dependencies section has one `- **USn**: <stories it needs> (why)` line for every user story, and a Dependencies section lists user-story completion order, and a Parallel Execution Examples subsection is provided per story.
- [ ] `/akka:docs` ran before the report, the run record marker was written first when running in Claude Code, and it was then set to `"closing": true`.
- [ ] The report includes total task count, per-story count, parallel opportunities, and the suggested MVP scope (typically User Story 1 only).
