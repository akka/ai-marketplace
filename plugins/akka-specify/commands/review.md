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

Open this run in the idea's record. Call the `akka_run_start` MCP tool with
`station: review`, `command: /akka:review` and `args` set to the user input.
Where the tool is not available, run `akka specify run start --station review
--command /akka:review` instead. Keep the run id it returns: the last step
closes the run. When it refuses because no idea matches the branch and none was
named, continue without a run, and say in one line that this run is not
recorded. On any other error or a non-zero exit, print its message verbatim and
stop. Do not continue, and do not work around it; the message names the remedy.
The one exception is a CLI that does not know the command (no `akka_run_start`
tool, and `run` rejected as an unknown command): it predates the idea record, so
say so and continue without a run.

The record names each station command by its `akka` plugin name, so this
plugin's commands open their runs under `/akka:` names.

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

9. **Carry on or stop.** Read the idea with `akka specify idea show <idea> --json`: `next` names the next station's command, and `waits` lists what waits on a person. Outside Enforced mode (`akka specify mode`), when `idea.advance` is `continue` and `waits` is empty, carry on into the `/akka-specify:` command of that name in this conversation, following its own instructions, instead of stopping. Never carry on into `/akka:ship` or `/akka:deploy`. Otherwise stop and name the next command: when `advance` is `step` or absent, in Enforced mode, when anything waits on a person, or when no run was opened.

## Key Rules

- Be specific: reference file paths and line numbers
- Every issue must cite the rule it violates
- Distinguish between must-fix (errors) and should-fix (warnings)
- Acknowledge good patterns and practices, not just problems
