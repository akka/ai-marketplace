# Review Artifacts: [PROJECT]

**Project**: [project name] | **Topic**: [topic name] ([CODE]) | **Updated**: [DATE]
**Written by**: `/akka:discover <topic> mock`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  This file is discovery/<topic>/mocks/index.md. Each artifact is one list line:
    - [M-<CODE>-<n>] <title> | file: <path> | kind: storyboard|mock|animatic|prototype | version: <n> | shows: <what it illustrates> | approval: <approval>

  - <CODE> is the topic's code from its topic.md (PAY in the examples below). <n> is
    unique within the topic; continue from the highest M-<CODE>-<n>.
  - file is relative to discovery/<topic>/mocks/.
  - shows names the findings, user stories or requirements it illustrates
    (F-<CODE>-<n>, US<n>, FR-<nnn>).
  - approval is exactly one of:
      pending
      approved by <name or role> on <YYYY-MM-DD>
      changes-requested by <name or role> on <YYYY-MM-DD>
    Only a value that begins with "approved" counts as an approval. It is written only
    from the reviewer's own answer.
  - None of the values contain "|".

  Every review, including earlier versions, is kept in Review History.
-->

## Artifacts *(required, or none)*

- [M-PAY-1] [Title] | file: [checkout-flow.html] | kind: [mock] | version: 1 | shows: [US1, F-PAY-4] | approval: pending

## Review History *(required, or none)*

One line per review, newest last.

- M-PAY-[n] v[n]: [approved | changes-requested] by [name or role] on [YYYY-MM-DD]: [reason in the reviewer's words]
