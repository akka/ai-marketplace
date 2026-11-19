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

**Idea record: review in a console run.** Use only the tools the console grants
this run. Skip the optional runtime verification, and say so in one line.

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
tool with `station: review`, `command: /akka:review`, `idea` set to the idea
found above and `args` set to the user input. Where the tool is not available,
run `akka specify run start --station review --command /akka:review --idea <id>
--args "<the user input>" --json`, with the input quoted as one argument. A run
is never started without its idea. It answers JSON: `recorded`, and for a
recorded run its `idea` and `run.id`. Keep both: the last steps use them.

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

9. **Carry on or stop.** In a console run, skip this step: the console moves the idea on. If a run was opened, run `akka specify idea next --idea <idea> --from review --json`, where `<idea>` is the `idea` the run start returned. It answers `{ go, next, reason }`. When `go` is true, carry on into the `/akka-specify:` command of the same name in this conversation, following its own instructions, when this plugin has one. Otherwise stop, print `reason`, and name `next.command` when there is one. This plugin has no `conform`, `converge` or `ship`: for those, stop and name the `/akka:` command. Without a run, stop and name the next command.

## Key Rules

- Be specific: reference file paths and line numbers
- Every issue must cite the rule it violates
- Distinguish between must-fix (errors) and should-fix (warnings)
- Acknowledge good patterns and practices, not just problems
