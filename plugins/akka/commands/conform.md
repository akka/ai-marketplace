---
description: Run the in-scope auditors, print the definition-of-done manifest, and return the engine verdict — READY_TO_SHIP or NOT_READY.
handoffs:
  - label: Fix Blockers
    agent: akka.specify
    prompt: Resolve the exit conditions blocking the ship
    send: true
  - label: Ship for Review
    agent: akka.ship
    prompt: Run the auditors for the review target and, on pass, run the review ship steps
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

In a project with a `discovery/` folder this command relies on the discovery gates in `akka specify conform`, which need an akka CLI with discovery support. Check first: run `akka specify probes --help`. If its list of commands does not include `findings`, the CLI predates discovery. Tell the person so, name what is missing (the discovery gates and `akka specify probes findings`), and stop, because a spec may rely only on confirmed findings and this CLI cannot check them. Treat an `unknown command` or `unknown flag` error from any `akka specify` call the same way, naming the subcommand or flag. A project without `discovery/` needs neither and skips this check.

## Before anything else

Run `akka specify mode --allows conform`. Add `--as-engine` when you are carrying
this command out as a step of the sequence `/akka:specify` drives in Enforced
mode, rather than because a person invoked it. It exits non-zero when the
project's mode does not permit the command. On a non-zero exit, print its message verbatim and stop. Do
not continue, and do not work around it. The one exception is a CLI that rejects
`--allows` as an unknown flag: it predates the mode check (older than 3.0.74), so
say so and continue without the check.

Enforced mode gives the sequence to the engine, so a step it sequences is refused
to a person and permitted to the engine. A refusal with a reason of its own, such
as re-running setup, stands either way. The message names the remedy.

Then open this run in the idea's record. Call the `akka_run_start` MCP tool with
`station: conform`, `command: /akka:conform` and `args` set to the user input.
Where the tool is not available, run `akka specify run start --station conform
--command /akka:conform` instead. Keep the run id it returns: the last step
closes the run. On an error or a non-zero exit, print its message verbatim and
stop, as for the mode check; the message names the remedy. The one exception is
a CLI that does not know the command (no `akka_run_start` tool, and `run`
rejected as an unknown command): it predates the idea record, so say so and
continue without a run.

## Purpose

`/akka:conform` runs the in-scope auditors and reports whether the feature is
ready to ship. For every machine-checkable exit condition it runs the
condition's auditor — building, testing, linting, or probing as the check
requires — and resolves it to a state. It then prints the same manifest
`/akka:status` shows, and returns a verdict.

The verdict is assessed against the **release** tier, so it covers every
applicable condition at every ship tier — not just the tier you happen to be
shipping to next.

Two commands sit close to this one and are not it:

- **`/akka:status`** prints the same manifest but never runs an auditor.
  Status leaves machine-checkable conditions `open`; conform resolves them.
  Once conform has evaluated, the two agree.
- **`/akka:converge`** diffs the codebase against the spec, plan, and tasks and
  queues unbuilt work. Conform evaluates the exit conditions and reports
  readiness. Neither substitutes for the other.

`/akka:ship` reads this same verdict — in Enforced mode it releases only when
the verdict is `READY_TO_SHIP`.

## The verdict

- **`READY_TO_SHIP`** — every applicable condition is `green` and not stale, or
  covered by an effective waiver.
- **`NOT_READY`** — any other combination.

In a project with a `discovery/` folder, a CLI that predates scoping the
discovery gates in leaves them out in À la carte mode unless exit conditions are
honoured. Check that the manifest lists the `PROC-` discovery gate rows (such as
`PROC-FINDINGS-CONFIRMED`). If it does not, say plainly that the discovery gates
were not evaluated, and do not present `READY_TO_SHIP` as covering them.

A `NOT_READY` verdict says what is blocking and what to do about it:

- conditions `open` with reason `needs-user-action` are waiting on the user;
- conditions `open` with reason `blocked-outside-project` need a tool or policy
  change beyond this project — never treat one as a failure the user caused;
- stale greens need their auditor re-run.

## Outline

1. **Evaluate.** Call `akka_ec_conform` for the project directory. This runs
   the available auditors and returns the manifest plus the verdict. It is the
   full CLI pipeline — org floor, project strikes, waivers, sign-offs, and mode
   — so it agrees exactly with `akka specify conform`.

   This is not a cheap call. It executes real builds and probes. Do not run it
   speculatively or in a loop; if the user only wants to see where things
   stand, `/akka:status` is the read-only view.

2. **Report the plain outcome.** Call `akka_ec_summary` and present it to the
   user **verbatim**. It is the user-facing summary, and it contains no
   internal ids or machinery words by construction.

3. **Surface the blockers.** For a `NOT_READY` verdict, list what is blocking,
   each with its user-facing reason and the action it implies. Distinguish the
   two `open` reasons — waiting on the user is a different ask from blocked
   outside the project, and collapsing them sends people to fix the wrong
   thing. Name stale greens as needing a re-run, not as failures.

   Prohibition (NEVER) conditions resolve in their own section of the manifest.
   An unaudited prohibition reds — say so plainly rather than reporting it as
   an ordinary open item.

   Do not restate internal condition ids, check keys, or the words "auditor" /
   "coverage gate" / "adequacy review". Offer *"say 'show details' for the full
   checklist"* for the manifest.

4. **Close the run with the manifest** (the last step). If a run was opened,
   write the manifest `akka_ec_conform` returned, as printed, to a temporary
   file outside the project. Call the `akka_run_close` MCP tool with `run` set
   to its id and `manifest` set to that file's path, then delete the file. The
   record keeps the manifest beside the receipt with the engine's verdict.
   Where the tool is not available, run `akka specify run close --run <id>
   --manifest <file>`. Do this whatever the verdict. On an error, print its
   message; the verdict already reported stands.

## Key rules

- Report the verdict the engine returned. Never soften a `NOT_READY`, and never
  infer `READY_TO_SHIP` from a manifest that looks clean — the verdict accounts
  for staleness and waiver effectiveness, which reading states does not.
- The mode does not change the verdict. Conform judges identically wherever the
  exit-condition set is active; only `/akka:ship` acts on the verdict
  differently. Never restate a `NOT_READY` as though it were a pass because the
  project is À la carte — but do say what it means there, because a verdict
  that reads as a blocker when nothing is blocked is its own kind of wrong.
  Report the verdict, then name the consequence: in À la carte, that ship
  proceeds anyway with a recorded override.
- Where the exit-condition set is dormant there is nothing to conform to.
  Say so plainly — the project has no checks set up yet — and do not present a
  `READY_TO_SHIP` over the Akka baseline as though the project had passed a
  definition of done it never defined.
- Never resolve a condition to get a better verdict. Sign-off, strike, and
  waive are the user's decisions to record, not steps to reach `READY_TO_SHIP`.
- `blocked-outside-project` is not the user's failure. Report it as a missing
  tool or policy change and name what is missing.

## Done When

- [ ] `akka_ec_conform` was called once for the project directory and its
      verdict was reported as returned.
- [ ] The plain `akka_ec_summary` was shown to the user verbatim (never
      internal ids or machinery words).
- [ ] For `NOT_READY`, every blocking condition was surfaced with its
      user-facing reason, with `needs-user-action`, `blocked-outside-project`,
      and stale greens distinguished from each other.
- [ ] Any red prohibition was named as a prohibition rather than folded in with
      the ordinary open items.
- [ ] No condition was signed off, struck, or waived in the course of running
      this command.
- [ ] The run was opened with `akka_run_start` after the mode check and closed
      with `akka_run_close` passing the manifest, or the CLI was reported as
      predating the idea record.
