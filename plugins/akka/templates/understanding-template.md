# Shared Understanding: [PROJECT]

**Project**: [project name] | **Topic**: [topic name] ([CODE]) | **Track**: [ideation | modernization] | **Updated**: [DATE]
**Written by**: `/akka:discover <topic> confirm`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  This file is discovery/<topic>/understanding.md. An understanding item is one list
  line that starts at the beginning of the line, followed by indented lines that
  explain it:

    - [U-<CODE>-<n>] <restatement> | impact: high|normal | covers: F-<CODE>-<n>[, F-<CODE>-<n>] | response: agree|amend|rethink|disagree|open | version: <n> | reason: <reason> | by: <name or role> | date: <YYYY-MM-DD>
      - v1 (AI)
        - What I think you mean: <one or two plain sentences>
        - Why I am asking: <one sentence, including what depends on the answer>
        - My suggestion: <one sentence, only when there is a choice>
        - An example: <one sentence>
        - What changes if I am wrong: <one or two sentences>
      - comment (<name or role>, <YYYY-MM-DD>): <the person's words>
      - answer (<name or role>, <YYYY-MM-DD>): agree|amend|disagree
      - v2 (AI)
        - What I think you mean: ...

  - <CODE> is the topic's code from its topic.md (PAY in the examples below). <n> is
    unique within the topic; continue from the highest U-<CODE>-<n>. An item keeps its
    identifier through every version.
  - The restatement is one plain sentence a reader new to the project can judge. It
    never contains "|".
  - impact is high when a wrong answer would change scope, data, a rule, a gate or a
    test. Everything else is normal.
  - The indented lines are the item's thread, oldest first, and are never items of
    their own. Each version the AI writes is a `v<n> (AI)` line with up to five parts
    beneath it, in that order. The first three are the default view, always visible
    when the item is open: What I think you mean, Why I am asking, and My suggestion
    (left out when there is no choice to make). The last two are shown behind one
    click ("More"): An example and What changes if I am wrong. Each comment is a `comment (<who>, <date>)` line. Nothing in the
    thread is deleted.
  - version is the version the response answers. A new item is version 1.
  - response is what the person answered:
      agree     the restatement is right.
      amend     the person rewrote it; their wording replaces the restatement on the
                item line, and the AI's wording stays in the thread.
      rethink   the person commented; the item goes back to the AI. The AI adds the
                next `v<n> (AI)` to the thread, raises version to it and sets the
                response to open.
      disagree  the restatement is wrong; reason is required.
      open      nobody has answered the newest version yet.
    A high-impact item blocks the specification while its response is open, rethink
    or disagree, while its thread holds a version newer than the one answered, or
    while a comment follows the newest version with no answer line after it. An
    answer line records a response given after a comment, without a new version.
  - by and date name who answered and when. They are filled only from the person's
    answer.
  - A conflict item, written by `/akka:discover <topic> concepts` when two topics define the
    same concept name differently, adds `| conflict: <CODE>/C-<CODE>-<n>, <CODE>/C-<CODE>-<n>`.

  A section marked "required, or none" is never deleted; when empty its only line is
  `none: <what was checked>`.
-->

## Outcome *(required)*

- **Items**: [n] | **Agreed**: [n] | **Amended**: [n] | **Rethinking**: [n] | **Disagreed**: [n] | **Open**: [n]
- **Open high-impact items**: [n]
- **Last session**: [YYYY-MM-DD], with [names or roles]

## Items *(required)*

- [U-PAY-1] [The restatement] | impact: high | covers: F-PAY-3, F-PAY-7 | response: agree | version: 2 | reason: [why, in the person's words] | by: [name or role] | date: [YYYY-MM-DD]
  - v1 (AI)
    - What I think you mean: [the AI's understanding, in one or two sentences]
    - Why I am asking: [one sentence, including what depends on the answer]
    - My suggestion: [one sentence, only when there is a choice]
    - An example: [one sentence]
    - What changes if I am wrong: [one or two sentences]
  - comment ([name or role], [YYYY-MM-DD]): [the person's words]
  - v2 (AI)
    - What I think you mean: [the revised understanding]
    - Why I am asking: [one sentence, including what depends on the answer]
    - My suggestion: [one sentence, only when there is a choice]
    - An example: [one sentence]
    - What changes if I am wrong: [one or two sentences]
- [U-PAY-2] [The person's wording] | impact: normal | covers: F-PAY-12 | response: amend | version: 1 | reason: [why] | by: [name or role] | date: [YYYY-MM-DD]
  - v1 (AI)
    - What I think you mean: [the AI's original wording and explanation]
    - Why I am asking: [what depends on the answer]
    - An example: [one concrete case]
    - What changes if I am wrong: [the consequence]
- [U-PAY-3] [Restatement] | impact: high | covers: F-PAY-20 | response: open | version: 1
  - v1 (AI)
    - What I think you mean: [explanation]
    - Why I am asking: [what depends on the answer]
    - My suggestion: [one sentence, only when there is a choice]
    - An example: [one concrete case]
    - What changes if I am wrong: [the consequence]

## Follow-ups *(required, or none)*

What happens next for each item answered disagree, or amended against observed evidence.

- U-PAY-[n]: [next step: probe, ask someone, or record a decision] | owner: [role]

## Decisions Raised *(required, or none)*

Choices the specification must make that discovery cannot settle. The plan's decisions log
carries them forward.

- D-[n]: [decision to make] | recommendation: [option and why] | owner: [role] | status: open
