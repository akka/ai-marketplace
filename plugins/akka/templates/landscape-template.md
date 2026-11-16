# Landscape: [PROJECT]

**Project**: [project name] | **Topic**: [topic name] ([CODE]) | **Track**: [ideation | modernization] | **Updated**: [DATE]
**Written by**: `/akka:discover <topic> landscape`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  A finding is one list line:
    - [F-<CODE>-<n>] <claim> | evidence: <source>[; <source>] | status: observed|inferred|confirmed

  - This file is discovery/<topic>/landscape.md, in the topic's folder. <CODE> is the topic's
    code from its topic.md (PAY in the examples below). <n> is unique within the
    topic: continue from the highest F-<CODE>-<n> in discovery/<topic>/, never reuse a
    number. Project-level files at the discovery/ root write F-<n> without a code.
  - The claim and the evidence never contain "|".
  - Sources: a file path, S-<n> from the topic's research.md, a URL,
    `stated: <role or name>, <YYYY-MM-DD>`, `reasoning: <from what>` (inferred only),
    or `understanding.md U-<CODE>-<n>` once confirmed.

  A section marked "required, or none" is never deleted; when empty its only line is
  `none: <what was checked>`.
-->

## Question Being Compared

[One sentence: the job a person is trying to get done, which every option below is a way
of doing.]

## Options *(required)*

Every way the job is done today or could be done, including doing nothing.

| Option | Kind | Who uses it | Finding |
|--------|------|-------------|---------|
| O-1 [name] | [competitor \| alternative \| substitute \| status quo] | [who] | [F-PAY-n] |

Kinds: a **competitor** sells the same thing; an **alternative** is a different product for
the same job; a **substitute** is a different way of doing the job (a spreadsheet, a manual
step, an in-house tool); the **status quo** is what happens if nothing is built.

## Dimensions *(required)*

The dimensions the reader chose, each with why it matters to them. A dimension is
numbered L-<n>; D-<n> is kept for the plan's decisions.

- L-1 [dimension]: [why it matters]

## Comparison *(required)*

Every cell names the finding that supports it, or reads `unknown`.

| Option | L-1 [dimension] | L-2 [dimension] |
|--------|-----------------|-----------------|
| O-1 [name] | [value] [F-PAY-n] | unknown |

## Findings *(required)*

- [F-PAY-10] [Claim about an option on a dimension] | evidence: [source] | status: [observed]

## What This Means for the Specification *(required, or none)*

Inferences only; each one is a finding with status inferred.

- [F-PAY-11] [Implication] | evidence: reasoning: [F-PAY-n, F-PAY-n] | status: inferred

## Unknowns *(required, or none)*

- [Question] | ask: [role or source]
