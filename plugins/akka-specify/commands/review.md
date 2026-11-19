---
description: Review implemented code against the spec, plan, and constitution.
handoffs:
  - label: Fix Issues
    agent: akka.implement
    prompt: Fix the issues found in review
    send: true
  - label: Track Issues
    agent: akka.issues
    prompt: Track the issues found in this review
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Before anything else

This command keeps a run in the idea's record when the akka CLI has one: the
`akka_run_start` MCP tool is available, or `akka specify run start --help` exits
0. A CLI without it predates the idea record. With such a CLI, say so once and
carry this command out as before: skip every step marked **Idea record**, and
open no run.

**Idea record: find the idea.** Find the feature this command works on first:
call `akka_sdd_list_specs` and identify the target feature as the first step
below does. Its idea is the one in `akka specify idea list --json` whose `spec`
is the feature's folder name (`NNN-name`); an idea is never found from the git
branch. When that idea has `derived: true`, it has no record yet: adopt it with
`akka specify ideas adopt --idea <id>` (with a CLI whose `adopt` has no
`--idea`, `akka specify ideas adopt`), then use it. Pass its id as `idea` to the
run start. When no feature or no idea is found, pass no idea.

The record names each station command by its `akka` plugin name, so this
plugin's commands open their runs under `/akka:` names.

**Idea record: open the run.** Call the `akka_run_start` MCP tool with `station:
review`, `command: /akka:review`, `idea` set to the idea found above (left out
when none was found) and `args` set to the user input. Where the tool is not
available, run `akka specify run start --station review --command /akka:review
--idea <id> --args "<the user input>" --json`, leaving out `--idea` when no idea
was found, quoting the input as one argument. It answers JSON: `recorded`, and
for a recorded run its `idea` and `run.id`. Keep both: the last steps use them.

- When it answers `recorded: false`, continue without a run, and say in one line
  that this run is not recorded, with its `reason`.
- A refusal by rule is an error whose JSON is `{refused, message, remedy}`,
  `refused` naming the rule: `paused`, `limit`, `shipped`, `dropped`,
  `approval`, `order` or `no-idea-enforced`. Print `message` and `remedy`
  verbatim and stop. For `no-idea-enforced` the remedy is `akka specify ideas
  adopt`, run once for the project.
- Any other error, one without `refused` (such as no login or several matching
  ideas), does not stop the command: continue without a run, and say in one line
  that this run is not recorded.

**Idea record: a run that fails is closed too.** Once the run is open, every way
the command ends closes it. When the work fails (a build or tests fail, or a
step stops the command early), call `akka_run_close` with `run`, `outcome:
failed` and `error` set to what failed, in one line, then stop. Where the tool
is not available, run `akka specify run close --run <id> --outcome failed
--error "<what failed>"`. When the person stops the command, close the run with
`outcome: stopped`. The close step below is for the work's normal end.

## Outline

1. **Setup**: Call `akka_sdd_list_specs` to find the target feature. Load the spec, plan, tasks, and checklist.

2. **Load context**: Read the constitution using `akka_sdd_constitution`. Understand what patterns and rules must be followed.

3. **Review implementation against spec**:
   - Are all functional requirements implemented?
   - Are all acceptance criteria met?
   - Are there deviations from the spec? If so, are they justified?

4. **Review implementation against constitution**:
   - Event sourcing: Are events designed as facts? Are handlers pure?
   - Effects API: Are command handlers returning Effects? No side effects?
   - ComponentClient: Used for all cross-component calls?
   - ACLs: Defined on all endpoints?
   - Serialization: `@TypeName` on all state/event classes?
   - Testing: Unit and integration tests present?

5. **Code quality review**:
   - No business logic in endpoints
   - No blocking I/O in handlers
   - No shared mutable state
   - Error handling uses `effects().error()`, not exceptions
   - No fat events (events contain only changed data)

6. **Checklist verification**: Walk through the checklist and mark items as passed or failed.

7. **Report**:
   - Overall assessment: approved / approved with issues / needs rework
   - Issues found (categorized by severity)
   - Checklist completion percentage
   - Recommendations

8. **Close the run**. If a run was opened, call the `akka_run_close` MCP tool with `run` set to its id and `outputs` set to the checklist files step 6 marked, as project-relative paths, or to none. Where the tool is not available, run `akka specify run close --run <id>` with one `--output <path>` for each output. On an error, print its message; the report stands.

9. **Carry on or stop.** If a run was opened, run `akka specify idea next --idea <idea> --from review --json`, where `<idea>` is the `idea` the run start returned. It answers `{ go, next, reason }`. When `go` is true, carry on into the `/akka-specify:` command of the same name in this conversation, following its own instructions, when this plugin has one. Otherwise stop, print `reason`, and name `next.command` when there is one. This plugin has no `conform`, `converge` or `ship`: for those, stop and name the `/akka:` command. Without a run, stop and name the next command.

## Key Rules

- Be specific: reference file paths and line numbers
- Every issue must cite the rule it violates
- Distinguish between must-fix (errors) and should-fix (warnings)
- Acknowledge good patterns and practices, not just problems
