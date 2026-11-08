# System Map: [SYSTEM]

**Project**: [project name] | **Track**: modernization | **Updated**: [DATE]
**Written by**: `/akka:discover system`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  A finding is one list line:
    - [F-<n>] <claim> | evidence: <source>[; <source>] | status: observed|inferred|confirmed | rung: <rung>

  - <n> is unique across every file in discovery/; continue from the highest F-<n> there.
  - The claim and the evidence never contain "|".
  - rung is how the claim was established, weakest first:
      inspected            read in the source (rung 1; a hypothesis, so status is inferred)
      documented           stated by documentation that addresses this case (rung 2)
      exercised: <probe>   observed by running the named probe (rung 3)
      unresolvable         the system has no defined behaviour here (rung 4)
    These are the words a specification's requirement annotation uses, so a requirement
    built on a finding copies its rung: `(observed, exercised: surface)`.
  - Sources: a file path with :line, a probe result `.akka/discovery/<probe>.json`,
    a bill of materials file under discovery/bom/, a URL, S-<n> from research.md,
    `stated: <role or name>, <YYYY-MM-DD>`, or `understanding.md U-<n>` once confirmed.

  A section marked "required, or none" is never deleted; when empty its only line is
  `none: <what was checked>`. A count of 0 is a finding, not an omission.
-->

## System Studied *(required)*

- **Source**: [path to a readable clone, and the commit or version]
- **Running instance**: [URL, or none]
- **Study level**: [read | run | diff]
- **Probe run**: [date of `.akka/discovery/run.json`, or not run]
- **Bill of materials**: [discovery/bom/, or not generated]

## Inventory *(required; every row has a count, 0 where none exists)*

| Kind | Count | Finding |
|------|-------|---------|
| HTTP or gRPC operations | [n] | [F-n] |
| Agent tools (for example MCP) | [n] | [F-n] |
| Command line commands | [n] | [F-n] |
| Graphical pages or screens | [n] | [F-n] |
| Wire types (payload shapes) | [n] | [F-n] |
| In-process API (library calls) | [n] | [F-n] |
| Configuration keys | [n] | [F-n] |
| Scheduled jobs | [n] | [F-n] |
| Tables or stores | [n] | [F-n] |
| External dependencies | [n] | [F-n] |

Counts come from a probe or a generated bill of materials, never from reading by hand.

## Structure Findings *(required)*

- [F-30] [Element and what it is] | evidence: [source] | status: observed | rung: exercised: surface

## Reachability *(required, or none)*

Which parts run when the system is driven the way it drives itself. Code that exists but
never runs is listed here, because it does not need rebuilding.

- [F-31] [Element] is reachable [directly | only as a side effect | not at all] | evidence: .akka/discovery/reachability.json | status: observed | rung: exercised: reachability

## Test Coverage *(required, or none)*

Which of the system's own tests touch each element.

- [F-32] [Element] is covered by [tests] | evidence: .akka/discovery/coverage.json | status: observed | rung: exercised: coverage

## Probes *(required)*

| Probe | Result | Reason |
|-------|--------|--------|
| [name] | [ran \| unavailable \| failed] | [missing capability or failure reason, or blank] |

## Unknowns *(required, or none)*

- [Question] | next rung: [docs | probe <name> | ask <role>]
