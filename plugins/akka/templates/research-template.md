# Research: [PROJECT]

**Project**: [project name] | **Topic**: [topic name] ([CODE]) | **Track**: [ideation | modernization] | **Updated**: [DATE]
**Written by**: `/akka:discover <topic> research`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  A finding is one list line:
    - [F-<CODE>-<n>] <claim> | evidence: <source>[; <source>] | status: observed|inferred|confirmed

  - This file is discovery/<topic>/research.md, in the topic's folder. <CODE> is the topic's
    code from its topic.md (PAY in the examples below). <n> is unique within the
    topic: continue from the highest F-<CODE>-<n> in discovery/<topic>/, never reuse a
    number. Project-level files at the discovery/ root write F-<n> without a code.
  - The claim and the evidence never contain the character "|".
  - status: observed = seen in a source a reader can open; inferred = reasoned, not seen;
    confirmed = a person agreed to it in `/akka:discover <topic> confirm`. Only confirmed
    findings may be cited by a specification.
  - A source is one of: a file path (with :line when it helps), S-<n> from the Sources
    section below (with a page or section), S-<CODE>-<n> from the topic's materials.md
    (with a page or section), a URL, `stated: <role or name>, <YYYY-MM-DD>`
    for something a person said, `reasoning: <what it was reasoned from>` (inferred
    findings only), or `understanding.md U-<CODE>-<n>` once confirmed.

  A section marked "required, or none" is never deleted. When it has nothing to record,
  its only line is `none: <what was checked>`. An empty section means "checked", never
  "not considered".
-->

## Summary

[Three to five sentences a new reader can read in thirty seconds: what is being built or
replaced, for whom, and why now.]

## Sources *(required)*

One line per source used, so findings can cite it by its number.

- S-1: [title] | owner: [author or team] | date: [YYYY-MM-DD] | where: [path or URL] | current: [yes | unsure | no, and why]

## Users and Needs *(required, or none)*

- [F-PAY-1] [Who uses it, and what they need from it] | evidence: [source] | status: [observed]

## Outcomes and Measures *(required, or none)*

- [F-PAY-2] [The outcome that would count as success, with a number where one is known] | evidence: [source] | status: [inferred]

## Constraints and Regulation *(required, or none)*

Rules, approvals, standards and dates that limit what can be built.

- [F-PAY-3] [Constraint] | evidence: [source] | status: [observed]

## Prior Work *(required, or none)*

Earlier attempts, internal documents and existing decisions that bear on this work.

- [F-PAY-4] [What was tried or decided before] | evidence: [source] | status: [observed]

## Unknowns *(required, or none)*

What nobody has answered yet, with the role most likely to know.

- [Question] | ask: [role]

## Requests for Other People *(required, or none)*

What to ask of whom, each with one sentence on why it matters.

- [Role]: [what to provide] | why: [one sentence]
