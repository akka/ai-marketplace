# Topic: [TOPIC TITLE]

**Goal**: [the goal or question, in one sentence] | **Track**: [ideation | modernization] | **Code**: [PAY]
**Scope**: [project | the name of an area] | **Status**: [active | settled | parked] | **Owner**: [name or role] | **Started**: [YYYY-MM-DD]
**Choices**: scan: [yes | no | skipped] | probes: [built-in probe ids, or none] | web: [yes | no] | web-on: [YYYY-MM-DD] | skipped-by: [who] | skipped-on: [YYYY-MM-DD]
**Written by**: `/akka:discover <topic>`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  This file is discovery/<topic>/topic.md, the header of one discovery topic. The
  topic's inputs (notes.md, materials.md and the attached files in materials/) and
  its other files (research.md, landscape.md, concepts.md, system-map.md,
  behaviour.md, understanding.md, mocks/index.md) sit beside it in the same folder.

  - The folder name is the topic name: lower case, words joined by "-". It is never
    one of the sub-command words research, landscape, concepts, system, scan, confirm or
    mock.
  - Goal: the question this topic answers or the outcome it works toward.
  - Track: ideation for a new idea, modernization for a rebuild of an existing system.
  - Code: two to four capital letters, unique among the project's topics, assigned
    when the topic is created and never changed. Every identifier the topic writes
    carries it: findings F-<CODE>-<n>, understanding items U-<CODE>-<n>, mocks
    M-<CODE>-<n>, concepts C-<CODE>-<n>. n is unique within the topic.
  - Scope: project when the topic is about the whole project; otherwise the name of
    the area it covers. The Story draws a project-scoped topic in its overview and an
    area topic in its own chapter.
  - Status: active while discovery is under way; settled when its understanding is
    agreed; parked when work has stopped without a conclusion.
  - Owner: the person or role who answers for the topic. Started: the date it was
    created.
  - Choices: scan is yes when the person chose a market scan, no when none was asked for,
    and skipped when the person declined it, with skipped-by and skipped-on set from that
    answer. probes lists the built-in probes the person allowed at the start, or none; the
    system step runs only those. web is yes or no once the person has been asked whether
    discovery may search the public web, with web-on the date; both are left out until then.
    A scan chosen at the start allows the scan step to search the web and sets no web value. What ran is recorded in system-map.md, not here.
  - Header values never contain "|" or "*".
-->

## Where It Stands

[One or two sentences: what has been learned so far and what the next step is.]

## Files

- [research.md] | [n] findings: [n] confirmed, [n] inferred, [n] observed

## Related Topics *(required, or none)*

Other topics this one depends on or shares concepts with.

- [topic name] ([CODE]): [how they relate]
