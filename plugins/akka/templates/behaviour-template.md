# Behaviour: [SYSTEM]

**Project**: [project name] | **Topic**: [topic name] ([CODE]) | **Track**: modernization | **Updated**: [DATE]
**Written by**: `/akka:discover <topic> system`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  A finding is one list line:
    - [F-<CODE>-<n>] <claim> | evidence: <source>[; <source>] | status: observed|inferred|confirmed | rung: <rung>

  - This file is discovery/<topic>/behaviour.md, in the topic's folder. <CODE> is the topic's
    code from its topic.md (PAY in the examples below). <n> is unique within the
    topic: continue from the highest F-<CODE>-<n> in discovery/<topic>/, never reuse a
    number. Project-level files at the discovery/ root write F-<n> without a code.
  - The claim and the evidence never contain "|".
  - Every behaviour finding carries a rung:
      inspected            read in the source; a hypothesis, so status is inferred
      documented           documentation addresses this case; status observed
      exercised: <probe>   the named probe ran and showed it; status observed
      unresolvable         docs are silent and running it shows no defined behaviour;
                           status observed, and it is also listed under Decisions to Force
  - A claim with "every", "all", "none" or "only" cites a source that enumerated the whole
    set (a probe result or a bill of materials), never a few examples.
  - A threshold, length or size claim cites a probe of the value below, the value itself
    and the value above.
  - Sources: a file path with :line, a probe result `.akka/discovery/<probe>.json`, a URL,
    S-<n> from research.md, `stated: <role or name>, <YYYY-MM-DD>`, or
    `understanding.md U-<CODE>-<n>` once confirmed.

  A section marked "required, or none" is never deleted; when empty its only line is
  `none: <what was checked>`.
-->

## Behaviour Findings *(required)*

Grouped by capability. One finding per rule.

### [Capability name]

- [F-PAY-40] [When this happens, the system does that] | evidence: .akka/discovery/sequence.json | status: observed | rung: exercised: sequence
- [F-PAY-41] [Rule read in the source and not yet run] | evidence: [path:line] | status: inferred | rung: inspected

## Boundaries Probed *(required, or none)*

| Rule | Below | At | Above | Finding |
|------|-------|----|-------|---------|
| [rule] | [result] | [result] | [result] | [F-n] |

## Read but Not Run *(required, or none)*

Findings still at rung inspected, with the probe that would settle each. These lines name
a finding without the square brackets, because only the finding's own line defines it.

- F-PAY-41: settle with [probe name, or "no probe can reach it", and why]

## Decisions to Force *(required, or none)*

Behaviour that is arbitrary, order-dependent or undefined. The specification must choose,
so each becomes an item in `/akka:discover <topic> confirm` and a row in the plan's decisions log.
The original's behaviour is stated, never characterised as a bug or an accident.

- [F-PAY-42] [What the system does, and that it is undefined] | evidence: [source] | status: observed | rung: unresolvable

## Unknowns *(required, or none)*

- [Question] | next rung: [docs | probe <name> | ask <role>]
