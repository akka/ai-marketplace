# Concepts: [PROJECT]

**Project**: [project name] | **Track**: [ideation | modernization] | **Updated**: [DATE]
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

- [F-20] [Claim about this concept] | evidence: [source] | status: [observed]

## Conflicting Usage *(required, or none)*

Terms that different people or documents use differently.

- [F-21] [Term] means [A] to [role] and [B] to [role] | evidence: [source]; [source] | status: observed

## Unknowns *(required, or none)*

- [Question] | ask: [role]
