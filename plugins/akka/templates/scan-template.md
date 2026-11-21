# Market Scan: [TOPIC TITLE]

**Topic**: [topic name] ([CODE]) | **Track**: [ideation | modernization] | **Updated**: [DATE]
**Written by**: `/akka:discover <topic> scan`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  This file is discovery/<topic>/scan.md: what others built with similar ideas. An example
  is one list line:
    - [X-<CODE>-<n>] <name> | kind: product|open-source|case-study|write-up | location: <where> | built: <one sentence> | received-well: <one sentence> | complaints: <one sentence> | means: <one sentence> | evidence: <S-ids>

  A finding is one list line:
    - [F-<CODE>-<n>] <claim> | evidence: <source>[; <source>] | status: observed|inferred|confirmed

  - <CODE> is the topic's code from its topic.md. <n> continues from the highest
    X-<CODE>-<n> or F-<CODE>-<n> in the topic's files and is never reused.
  - evidence on an example names only S-<CODE>-<n> materials with feeds: scan: the person's
    own (an attached file or a link) or a web source found for the scan. A link has a
    snapshot in materials/snapshots/. A field the sources do not answer reads unknown.
  - means is reasoned from the other fields, so it says so in its sentence.
  - Each borrowed idea and each pitfall is a finding with status inferred and
    `evidence: reasoning: <X ids>`. It is then an understanding item with `from: borrow`
    or `from: pitfall`.
  - No value contains "|". Nothing here is a secret.

  A section marked "required, or none" is never deleted. When it has nothing to record,
  its only line is `none: <what was checked>`.
-->

## Examples *(required, or none)*

- [X-PAY-1] [name] | kind: [product] | location: [URL] | built: [what they built] | received-well: [what users valued] | complaints: [what drew complaints] | means: [what it implies for this idea] | evidence: [S-PAY-4 section 2]

## Ideas Worth Borrowing *(required, or none)*

- [F-PAY-30] [An idea from the examples that this idea could use] | evidence: reasoning: [X-PAY-1, X-PAY-3] | status: inferred

## Pitfalls to Avoid *(required, or none)*

- [F-PAY-31] [A mistake the examples show, and how this idea could hit it] | evidence: reasoning: [X-PAY-2] | status: inferred

## Unknowns *(required, or none)*

What the examples do not show, with the role most likely to know.

- [Question] | ask: [role]
