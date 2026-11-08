# Concepts: [PROJECT]

**Project**: [project name] | **Track**: [ideation | modernization] | **Updated**: [DATE]
**Scope**: [project | the name of the area] | **Status**: [active | settled | parked]
**Written by**: `/akka:discover concepts`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  A finding is one list line:
    - [F-<n>] <claim> | evidence: <source>[; <source>] | status: observed|inferred|confirmed

  - <n> is unique across every file in discovery/; continue from the highest F-<n> there.
  - The claim and the evidence never contain "|".
  - Sources: a file path, S-<n> from discovery/research.md, a URL,
    `stated: <role or name>, <YYYY-MM-DD>`, `reasoning: <from what>` (inferred only),
    or `understanding.md U-<n>` once confirmed.

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

  Scope and Status say where the Story draws these concepts: a project-scoped
  topic in the Story's overview, an area in its own chapter once the topic is
  settled. When the topic has a topic.md, its header is read instead; a missing
  Scope reads as project and a missing Status as settled.
-->


## Glossary *(required)*

One row per term the people involved use. The definition is plain language a reader new to
the domain can follow.

| Term | Definition | Words to avoid | Finding |
|------|------------|----------------|---------|
| [term] | [one sentence] | [synonyms that mean something else here, or none] | [F-n] |

## Concepts *(required)*

One block per concept that has identity, state or rules.

### C-1: [Concept name]

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

- [F-20] [Claim about this concept] | evidence: [source] | status: [observed]

## Conflicting Usage *(required, or none)*

Terms that different people or documents use differently.

- [F-21] [Term] means [A] to [role] and [B] to [role] | evidence: [source]; [source] | status: observed

## Unknowns *(required, or none)*

- [Question] | ask: [role]
