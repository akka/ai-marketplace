---
description: Run the auditors for every exit condition in scope for the requested ship target (review or release), and on pass run the ship steps the organization declared for that target.
handoffs:
  - label: Fix Blockers
    agent: akka.specify
    prompt: Resolve the exit conditions blocking the ship
    send: true
  - label: Show Manifest
    agent: akka.specify
    prompt: Show the full definition-of-done manifest
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding.

## Purpose

`/akka:ship` runs the auditors for every applicable exit condition in scope for
the requested ship target, and on pass runs the ship steps the organization
declared for that target. The target argument is REQUIRED. Two targets are
accepted:

- **`review`** — runs the auditors for every applicable exit condition tagged
  `author` or `review`. On pass, runs the organization's review ship steps
  (typically push the branch and open a pull request).
- **`release`** — runs the auditors for every applicable exit condition at any
  tier (`author`, `review`, and `release`). On pass, runs the organization's
  release ship steps (typically deploy to production).

Author-time is a precondition, not a ship target. There is no `/akka:ship
author`. Every ship (review or release) refuses fast when any applicable
author-tier condition is not green, before running any higher-tier auditors.

## Outline

1. **Parse the target from `$ARGUMENTS`.** Read the first argument. It MUST be
   `review` or `release`. If missing, invalid, or anything else, stop and tell
   the user: *"`/akka:ship` requires an explicit target: `review` or `release`.
   For example: `/akka:ship review`."* Do not call the CLI.

2. **Invoke the CLI.** Run `akka specify ship <target>` in the project directory
   (via the shell). Capture the output. The CLI:
   - Runs the auditors for every applicable exit condition in scope for the
     target.
   - Reports the verdict (`READY_TO_SHIP` or `NOT_READY`).
   - Refuses to run any ship steps in Enforced mode unless the verdict is
     `READY_TO_SHIP`.
   - In À la carte mode, records an explicit override and proceeds even when
     the verdict is `NOT_READY`.
   - Writes a conformance receipt recording which target was shipped, what was
     verified, and any conditions that remained `open` with their reasons.

3. **Report plainly.** Present the CLI output. Do not restate internal condition
   ids, check keys, or the words "auditor" / "coverage gate" / "adequacy review".
   If the ship succeeded, say so and name the target that was shipped. If the
   ship refused, say what would unblock it — the reason field on each blocking
   condition is the user-facing action.

## Key rules

- The target is required. Never invoke the CLI without one.
- Never invent a target. If the user typed only `/akka:ship`, ask which target
  they intended rather than guessing.
- Ship steps are org-specific. This command runs the auditors and, on pass,
  hands off to whatever steps the organization declared in its policy.
- Same behavior in both modes for auditor evaluation; only ship-gating differs
  (advisory in À la carte, blocking in Enforced).

## Done When

- [ ] The target was parsed from `$ARGUMENTS` and validated as `review` or
      `release`; missing or invalid targets were reported to the user without
      calling the CLI.
- [ ] `akka specify ship <target>` was invoked with the validated target.
- [ ] The plain outcome was shown to the user, and any blocking conditions
      were surfaced with their user-facing reasons (no internal ids, no
      machinery words).
