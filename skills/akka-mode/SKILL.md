---
name: akka-mode
description: "Show or switch the project's conformance mode between Enforced and À la carte, within the set the organization allows."
---

## User Input

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

`/akka:mode` shows the project's conformance mode, or sets it. The mode is
recorded in `.akka/exit-conditions.yaml` and controls exactly one thing:
whether unmet exit conditions block shipping.

- **À la carte** — the default. `/akka:ship` proceeds even when conditions are
  unmet, recording an explicit override. The conditions are still resolved and
  still shown; they simply do not block.
- **Enforced** — `/akka:ship` refuses to release until every applicable
  condition is `green` and not stale, or covered by an effective waiver. You
  use sign-off, strike, and waive to resolve each `open` or `red` condition
  first.

Every Specify command is available in both modes. The mode changes the ship
gate, not the command set. How a condition is judged never depends on the mode
either — the two locked process-integrity gates, `PROC-AUDITOR-COVERAGE` and
`PROC-ADEQUACY-REVIEWED`, are computed identically in both. The difference is
only that Enforced blocks the ship while either is red, and À la carte reports
them as advisory.

The organization can constrain this. A policy may set a different default and
lock it; when the mode is locked, only the org-allowed mode(s) may be set. A
locked Enforced mode cannot be dropped to À la carte to bypass the ship gate.

## Outline

1. **Parse the argument from `the user's request`.** Three cases:

   - **Empty** — this is a query. Skip to step 2 with no argument.
   - **`enforced` or `a-la-carte`** — pass through unchanged.
   - **A recognizable spelling of à la carte** — the documentation renders the
     mode as "À la carte", so accept `alacarte`, `a la carte`, `à-la-carte`,
     and `à la carte` and normalize them to `a-la-carte` before calling the
     CLI. The CLI accepts only the two canonical spellings.

   Anything else: stop and tell the user *"`/akka:mode` takes `enforced` or
   `a-la-carte`, or no argument to show the current mode."* Do not call the CLI.

2. **Invoke the CLI.** Run `akka specify mode` (with the normalized argument,
   if any) in the project directory, via the shell. With no argument it prints
   the effective mode and whether an org policy has locked it. With an argument
   it writes the mode to the project state and confirms.

3. **Handle an old CLI.** `akka specify mode` requires Akka CLI **3.0.70 or
   later**. Earlier versions expose only `akka specify init`, so the shell
   reports an unknown command. If that happens, do not report it as a project
   or policy problem — say the installed CLI is too old, show the installed
   version from `akka version`, and give the upgrade command for their
   platform (`winget upgrade Akka.Cli`, `brew upgrade akka`, or the curl
   installer).

4. **Report plainly.** State the mode in the user's terms — "Enforced" or
   "À la carte" — and say what it means for shipping. When the mode is locked
   by org policy, say that it is locked and by whom, and do not present the
   other mode as an option. When a set succeeded, say which mode is now in
   effect and that nothing else about the project changed.

## Key rules

- Never edit `.akka/exit-conditions.yaml` directly to change the mode. The CLI
  enforces the org policy; a hand-edit bypasses it.
- Never retry a refusal in another form. If the org policy rejected the mode,
  that is the answer — report it and stop.
- Do not describe the mode as turning conditions on or off. Both modes resolve
  the same conditions; only ship-gating differs.
- With no argument this command is read-only. Do not set a mode the user did
  not ask for, and do not "helpfully" switch modes as part of another command.

## Done When

- [ ] The argument was parsed from `the user's request` and either recognized as a
      query, normalized to `enforced` / `a-la-carte`, or rejected without
      calling the CLI.
- [ ] `akka specify mode` was invoked, and an unknown-command failure was
      reported as a CLI version problem with the upgrade instruction — never as
      a project or policy error.
- [ ] The effective mode was reported plainly, along with what it means for
      shipping, and any org lock was stated as a lock rather than a choice.
