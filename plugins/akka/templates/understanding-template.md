# Shared Understanding: [PROJECT]

**Project**: [project name] | **Track**: [ideation | modernization] | **Updated**: [DATE]
**Written by**: `/akka:discover confirm`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  An understanding item is one list line:
    - [U-<n>] <restatement> | impact: high|normal | covers: F-<n>[, F-<n>] | response: agree|amend|disagree|open | reason: <reason> | by: <name or role> | date: <YYYY-MM-DD>

  - <n> is unique in this file; continue from the highest U-<n>.
  - The restatement is the AI's own plain-language sentence. It never contains "|".
  - impact is high when a wrong answer would change scope, data, a rule, a gate or a
    test. Everything else is normal.
  - response is what the person answered. An item nobody has answered is open.
    A high-impact item that is open or disagree blocks the specification.
  - An amend adds `| amended: <the person's wording>`.
  - by and date name who answered and when. They are filled only from the person's answer.

  A section marked "required, or none" is never deleted; when empty its only line is
  `none: <what was checked>`.
-->

## Outcome *(required)*

- **Items**: [n] | **Agreed**: [n] | **Amended**: [n] | **Disagreed**: [n] | **Open**: [n]
- **Open high-impact items**: [n]
- **Last session**: [YYYY-MM-DD], with [names or roles]

## Items *(required)*

- [U-1] [The AI's restatement of what it understands] | impact: high | covers: F-3, F-7 | response: agree | reason: [why, in the person's words] | by: [name or role] | date: [YYYY-MM-DD]
- [U-2] [Restatement] | impact: normal | covers: F-12 | response: amend | amended: [the person's wording] | reason: [why] | by: [name or role] | date: [YYYY-MM-DD]
- [U-3] [Restatement] | impact: high | covers: F-20 | response: open

## Follow-ups *(required, or none)*

What happens next for each item answered disagree, or amended against observed evidence.

- U-[n]: [next step: probe, ask someone, or record a decision] | owner: [role]

## Decisions Raised *(required, or none)*

Choices the specification must make that discovery cannot settle. The plan's decisions log
carries them forward.

- D-[n]: [decision to make] | recommendation: [option and why] | owner: [role] | status: open
