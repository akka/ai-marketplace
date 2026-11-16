# Concepts: [PROJECT]

**Project**: [project name] | **Topic**: [topic name] ([CODE]) | **Track**: [ideation | modernization] | **Updated**: [DATE]
**Written by**: `/akka:discover <topic> concepts`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  A finding is one list line:
    - [F-<CODE>-<n>] <claim> | evidence: <source>[; <source>] | status: observed|inferred|confirmed

  - This file is discovery/<topic>/concepts.md, in the topic's folder. <CODE> is the
    topic's code from its topic.md (PAY in the examples below). <n> is unique within
    the topic: continue from the highest F-<CODE>-<n> (or C-<CODE>-<n> for a concept)
    in discovery/<topic>/, never reuse a number.
  - The claim and the evidence never contain "|".
  - Sources: a file path, S-<n> from the topic's research.md, a URL,
    `stated: <role or name>, <YYYY-MM-DD>`, `reasoning: <from what>` (inferred only),
    or `understanding.md U-<CODE>-<n>` once confirmed.

  A section marked "required, or none" is never deleted; when empty its only line is
  `none: <what was checked>`.

  This file feeds the specification's Key Entities and the console glossary.

  A concept's picture is one fenced block, opened with ```visual and closed with ```,
  inside the concept's block. /akka:docs draws it in the project Story from fixed
  shapes, so it holds data only. The first two lines are always:
    kind: relationship | flow | state | comparison | timeline
    title: <short name, at most 60 characters>
  then the lines for the kind (an optional field follows " | "):
    relationship  focus: <name>                       exactly one
                  link: <name> | <label>              one to four
    flow          step: <name> | <note>               two to four, in order
    state         state: <name> | focus|end           two to four, in order
                  move: <from> -> <to> | <guard>      one to four; every move goes to the
                                                      next state, except at most one
    comparison    before: <text> | dropped            one to four
                  after: <text> | new                 one to four
    timeline      point: <label> | done|now|next      two to six, at most one now
  focus, new and now are drawn in the accent colour: at most two per block.
  Names fit their box: at most 14 characters; labels, guards and timeline
  labels at most 10; notes at most 20; comparison text at most 28. A concept
  whose findings are all confirmed must have a valid block (STORY-CONCEPTS-VISUAL).

  The topic's Scope and Status, in its topic.md, say where the Story draws these
  concepts: a project-scoped topic in the Story's overview, an area in its own
  chapter once the topic is settled.

  A concept is defined once, in its topic, and stays there. Promoting it to the
  project's shared list adds one reference line to the project-level
  discovery/concepts.md, never a copy of the block:
    - see: <CODE>/C-<CODE>-<n> | shared
  The Story then draws the concept in its overview and counts it once. The
  project-level discovery/concepts.md holds these references and the concepts of
  project-scoped material, whose identifiers carry no code (C-<n>, F-<n>).

  When two topics define the same concept name differently, neither definition is
  changed here. /akka:discover <topic> concepts writes a conflict item into the
  understanding.md of each topic involved, for a person to reconcile.
-->


## Glossary *(required)*

One row per term the people involved use. The definition is plain language a reader new to
the domain can follow.

| Term | Definition | Words to avoid | Finding |
|------|------------|----------------|---------|
| [term] | [one sentence] | [synonyms that mean something else here, or none] | [F-PAY-n] |

## Concepts *(required)*

One block per concept that has identity, state or rules.

### C-PAY-1: [Concept name]

- **What it is**: [one sentence]
- **Identified by**: [what makes one distinct from another]
- **States**: [the states it moves through, in order, or none]
- **Related to**: [other concepts and how]
- **Rules**: [the rules attached to it, each a finding]

```visual
kind: [relationship]
title: [What a claim holds]
focus: [Claim]
link: [Claimant] | [made by]
link: [Policy] | [covered by]
```

- [F-PAY-20] [Claim about this concept] | evidence: [source] | status: [observed]

## Conflicting Usage *(required, or none)*

Terms that different people or documents use differently.

- [F-PAY-21] [Term] means [A] to [role] and [B] to [role] | evidence: [source]; [source] | status: observed

## Shared with the Project *(required, or none)*

Concepts of this topic promoted to the project's shared list. Each has a reference line in
discovery/concepts.md; the definition stays above.

- C-PAY-[n]: promoted on [YYYY-MM-DD] by [name or role]

## Conflicts with Other Topics *(required, or none)*

Concept names another topic defines differently. Each has a conflict item in this topic's
understanding.md; the definitions are not changed until a person reconciles them.

- C-PAY-[n] [name] and [CODE]/C-[CODE]-[n]: [how they differ] | understanding: U-PAY-[n]

## Unknowns *(required, or none)*

- [Question] | ask: [role]
