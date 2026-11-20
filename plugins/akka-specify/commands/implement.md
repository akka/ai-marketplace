---
description: Execute the implementation plan by processing and executing all tasks defined in tasks.md
handoffs:
  - label: Build & Run Locally
    agent: akka.build
    prompt: Build, test, and run the service locally
    send: true
  - label: Review Code
    agent: akka.review
    prompt: Review the implementation against the spec
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
it is available: it answers `{ console, idea, station, run, spec, topic,
questions }`, and `console: true` means the console started this command. Only
without that tool, the console started it when `AKKA_RUN_ID` is set in its
environment, or when the command has no shell to run the akka CLI in. The
console has already opened the run and enforced the rules for it, so in a
console run the run is open from the first step: its id is the `run`
`akka_run_context` answered. Any stop before the normal close, such as a
mode-check refusal, a missing argument, or a check that needs a tool this run
lacks, closes it with `akka_run_close`, that `run`, `outcome: failed` and the
reason. So in a console run: the feature is `akka_run_context`'s `spec` (for
`/akka:discover`, the topic is its `topic`), and the command never searches for
one; skip every step that finds, adopts, starts or links an idea, and never ask
a person a question: wherever this command would ask one, it closes the run with
`outcome: waiting` and `question` set to the question (`--outcome waiting
--question "<question>"` on the CLI); the owner answers in the console, and the
re-run reads the answer from `akka_run_context`'s `questions` (`{station, run,
question, answer}`) and does not ask it again; run the mode check with `--idea`
set to the `idea` `akka_run_context` answered, and skip it when it cannot run
here or no idea is known; open the run by calling `akka_run_start` with
`command` and `args` only, no `idea` and no `station`, and the CLI joins the
console's run; close it as usual; and skip the carry-on step, because the
console moves the idea on. A run with no shell for the akka CLI that
`akka_run_context` answers `console: false` for is not a console run and keeps
no record: open no run, ask nothing about ideas or lanes, and carry the command
out as before the idea record, skipping every step marked **Idea record**.

**Idea record: implement in a console run.** When a checklist is incomplete, do
not ask whether to proceed: close the run with `outcome: waiting` and that
question. Never merge to `main` in a console run: skip the merge question and
leave the feature branch, because the merge is a person's choice. The feature
branch is `akka_run_context`'s `spec`, the idea's spec name, not the spec's
**Feature Branch** field. When the feature branch already exists and cannot be
entered (HEAD is elsewhere and checking out is not granted), close the run
`failed` with the reason. Build and test with `mvn` in the shell (for example
`mvn -q compile`, `mvn test` and `mvn verify`), which a console run of this
command may run: it refuses the `akka_maven_*` tools, so a task that names one
runs as the matching `mvn` command.

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
tool with `station: implement`, `command: /akka:implement`, `idea` set to the
idea found above and `args` set to the user input. Where the tool is not
available, run `akka specify run start --station implement --command
/akka:implement --idea <id> --args "<the user input>" --json`, with the input
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

## Outline

1. Call the `akka_sdd_list_specs` MCP tool to find features. Verify that tasks.md exists for the target feature (has_tasks must be true). If tasks.md is missing, instruct the user to run `/akka-specify:tasks` first. Read the tasks.md content from FEATURE_DIR. Also note which other artifacts are available (AVAILABLE_DOCS).

2. **Create or check out the feature branch**:
   - Read the spec.md from FEATURE_DIR and find the **Feature Branch** field (e.g. `001-counter-service`)
   - Call `akka_git_status` to check the current branch
   - If not already on the feature branch, call `akka_git_create_branch` with the branch name from the spec
   - All implementation work must happen on the feature branch, not on `main`

3. **Check checklists status** (if FEATURE_DIR/checklists/ exists):
   - Scan all checklist files in the checklists/ directory
   - For each checklist, count:
     - Total items: All lines matching `- [ ]` or `- [X]` or `- [x]`
     - Completed items: Lines matching `- [X]` or `- [x]`
     - Incomplete items: Lines matching `- [ ]`
   - Create a status table:

     ```text
     | Checklist | Total | Completed | Incomplete | Status |
     |-----------|-------|-----------|------------|--------|
     | ux.md     | 12    | 12        | 0          | ✓ PASS |
     | test.md   | 8     | 5         | 3          | ✗ FAIL |
     | security.md | 6   | 6         | 0          | ✓ PASS |
     ```

   - Calculate overall status:
     - **PASS**: All checklists have 0 incomplete items
     - **FAIL**: One or more checklists have incomplete items

   - **If any checklist is incomplete**:
     - Display the table with incomplete item counts
     - **STOP** and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)"
     - Wait for user response before continuing
     - If user says "no" or "wait" or "stop", halt execution
     - If user says "yes" or "proceed" or "continue", proceed to step 3

   - **If all checklists are complete**:
     - Display the table showing all checklists passed
     - Automatically proceed to step 3

4. Load and analyze the implementation context:
   - **REQUIRED**: Read tasks.md for the complete task list and execution plan
   - **REQUIRED**: Read plan.md for tech stack, architecture, and file structure
   - **IF EXISTS**: Read data-model.md for entities and relationships
   - **IF EXISTS**: Read contracts/ for API specifications and test requirements
   - **IF EXISTS**: Read research.md for technical decisions and constraints
   - **IF EXISTS**: Read quickstart.md for integration scenarios

5. **Project Setup Verification**:
   - **REQUIRED**: Create/verify ignore files based on actual project setup:

   **Detection & Creation Logic**:
   - Call `akka_git_status` to determine if the repository is a git repo (create/verify .gitignore if so)
   - Check if Dockerfile* exists or Docker in plan.md → create/verify .dockerignore
   - Check if .eslintrc* exists → create/verify .eslintignore
   - Check if eslint.config.* exists → ensure the config's `ignores` entries cover required patterns
   - Check if .prettierrc* exists → create/verify .prettierignore
   - Check if .npmrc or package.json exists → create/verify .npmignore (if publishing)
   - Check if terraform files (*.tf) exist → create/verify .terraformignore
   - Check if .helmignore needed (helm charts present) → create/verify .helmignore

   **If ignore file already exists**: Verify it contains essential patterns, append missing critical patterns only
   **If ignore file missing**: Create with full pattern set for detected technology

   **Common Patterns by Technology** (from plan.md tech stack):
   - **Node.js/JavaScript/TypeScript**: `node_modules/`, `dist/`, `build/`, `*.log`, `.env*`
   - **Python**: `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `dist/`, `*.egg-info/`
   - **Java**: `target/`, `*.class`, `*.jar`, `.gradle/`, `build/`
   - **C#/.NET**: `bin/`, `obj/`, `*.user`, `*.suo`, `packages/`
   - **Go**: `*.exe`, `*.test`, `vendor/`, `*.out`
   - **Ruby**: `.bundle/`, `log/`, `tmp/`, `*.gem`, `vendor/bundle/`
   - **PHP**: `vendor/`, `*.log`, `*.cache`, `*.env`
   - **Rust**: `target/`, `debug/`, `release/`, `*.rs.bk`, `*.rlib`, `*.prof*`, `.idea/`, `*.log`, `.env*`
   - **Kotlin**: `build/`, `out/`, `.gradle/`, `.idea/`, `*.class`, `*.jar`, `*.iml`, `*.log`, `.env*`
   - **C++**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.so`, `*.a`, `*.exe`, `*.dll`, `.idea/`, `*.log`, `.env*`
   - **C**: `build/`, `bin/`, `obj/`, `out/`, `*.o`, `*.a`, `*.so`, `*.exe`, `Makefile`, `config.log`, `.idea/`, `*.log`, `.env*`
   - **Swift**: `.build/`, `DerivedData/`, `*.swiftpm/`, `Packages/`
   - **R**: `.Rproj.user/`, `.Rhistory`, `.RData`, `.Ruserdata`, `*.Rproj`, `packrat/`, `renv/`
   - **Universal**: `.DS_Store`, `Thumbs.db`, `*.tmp`, `*.swp`, `.vscode/`, `.idea/`

   **Tool-Specific Patterns**:
   - **Docker**: `node_modules/`, `.git/`, `Dockerfile*`, `.dockerignore`, `*.log*`, `.env*`, `coverage/`
   - **ESLint**: `node_modules/`, `dist/`, `build/`, `coverage/`, `*.min.js`
   - **Prettier**: `node_modules/`, `dist/`, `build/`, `coverage/`, `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`
   - **Terraform**: `.terraform/`, `*.tfstate*`, `*.tfvars`, `.terraform.lock.hcl`
   - **Kubernetes/k8s**: `*.secret.yaml`, `secrets/`, `.kube/`, `kubeconfig*`, `*.key`, `*.crt`

6. Parse tasks.md structure and extract:
   - **Task phases**: Setup, Tests, Core, Integration, Polish
   - **Task dependencies**: Sequential vs parallel execution rules
   - **Task details**: ID, description, file paths, parallel markers [P]
   - **Execution flow**: Order and dependency requirements

7. Execute implementation following the task plan:
   - **Phase-by-phase execution**: Complete each phase before moving to the next
   - **Respect dependencies**: Run sequential tasks in order, parallel tasks [P] can run together
   - **Follow TDD approach**: Execute test tasks before their corresponding implementation tasks
   - **File-based coordination**: Tasks affecting the same files must run sequentially
   - **Validation checkpoints**: Verify each phase completion before proceeding

8. Implementation execution rules:
   - **Setup first**: Initialize project structure, dependencies, configuration
   - **Tests before code**: If you need to write tests for contracts, entities, and integration scenarios
   - **Core development**: Implement models, services, CLI commands, endpoints
   - **Integration work**: Database connections, middleware, logging, external services
   - **Polish and validation**: Unit tests, performance optimization, documentation

9. Progress tracking and error handling:
   - Report progress after each completed task
   - Halt execution if any non-parallel task fails
   - For parallel tasks [P], continue with successful tasks, report failed ones
   - Provide clear error messages with context for debugging
   - Suggest next steps if implementation cannot proceed
   - **IMPORTANT** For completed tasks, make sure to mark the task off as [X] in the tasks file.

10. **Commit the implementation**:
   - Call `akka_git_add` to stage all changes
   - Call `akka_git_commit` with a descriptive message summarizing the implemented feature

11. **Ask about merging to main**:
   - Ask the user: "Would you like to merge the feature branch back to main?"
   - If yes: call `akka_git_checkout` to switch to `main`, then `akka_git_merge` with the feature branch name
   - If no: stay on the feature branch — the user may want to create a PR or continue iterating

12. Completion validation:
   - Verify all required tasks are completed
   - Check that implemented features match the original specification
   - Validate that tests pass and coverage meets requirements
   - Confirm the implementation follows the technical plan
   - Report final status with summary of completed work

13. **Close the run**. If a run was opened, call the `akka_run_close` MCP tool with `run` set to its id, `outputs` set to the code and test files this run created or changed and `FEATURE_DIR/tasks.md`, as project-relative paths, and `tasks` set to the ids of the tasks this run marked `[X]`. Where the tool is not available, run `akka specify run close --run <id>` with one `--file <path>` for each output and one `--task <id>` for each task. On an error, print its message; the committed work stands.

14. **Carry on or stop.** In a console run, skip this step: the console moves the idea on. If a run was opened, run `akka specify idea next --idea <idea> --from implement --json`, where `<idea>` is the `idea` the run start returned. It answers `{ go, next, reason }`. When `go` is true, carry on into the `/akka-specify:` command of the same name in this conversation, following its own instructions, when this plugin has one. Otherwise stop, print `reason`, and name `next.command` when there is one. This plugin has no `conform`, `converge` or `ship`: for those, stop and name the `/akka:` command. Without a run, stop and name the next command.

Note: This command assumes a complete task breakdown exists in tasks.md. If tasks are incomplete or missing, suggest running `/akka-specify:tasks` first to regenerate the task list.
