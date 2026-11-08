# Materials: [TOPIC TITLE]

**Topic**: [topic name] ([CODE]) | **Written by**: the console and `/akka:discover <topic>`

<!--
  RECORD FORMATS (read by the console and the exit conditions; keep them exact)

  This file is discovery/<topic>/materials.md: what a person brought for discovery to
  study. A material is one list line:
    - [S-<CODE>-<n>] <name> | kind: <kind> | location: <where> | feeds: <step>[, <step>] | status: not-read|read|unreachable | by: <name or role> | date: <YYYY-MM-DD> | note: <why it matters>

  - <CODE> is the topic's code from its topic.md. <n> continues from the highest
    S-<CODE>-<n> named anywhere in the topic's files and is never reused while
    anything names it. S-<n> without a code is a research.md source, not a material.
  - kind and location:
      file         an attached file; location is materials/<file>, in the topic's
                   materials/ folder beside this file
      link         an http or https URL
      codebase     an absolute folder path to a readable copy of the source
      database     the NAME of the environment variable that holds the database's
                   address (CLAIMS_DB_URL), never the address, a URL or a
                   connection string; the schema probe reads it by that name
      competitor   a product that does the same job; location is a URL or blank
      inspiration  a system the person admires for some part of the job; a URL or blank
      person       someone to talk to; location is their team or role, never a
                   personal address
  - feeds names the discovery steps the material informs: research, concepts,
    landscape, system. Without it: file and link feed research, concepts; codebase
    and database feed system; competitor and inspiration feed landscape; person
    feeds research.
  - status: not-read until /akka:discover has read it; read once it has; unreachable
    when it could not be opened (a missing file, a folder that does not exist, a link
    that does not answer, a variable that is not set). The console shows a file or a
    code base that is not there as unreachable whatever this field says.
  - A finding cites a material in its evidence by its identifier, with a page or
    section when it helps: `evidence: S-PAY-2 sheet Q3`.
  - No value contains "|". Nothing in this file is a secret: a password, a key, a token
    or a connection string is never written here.
-->

## Materials

- [S-PAY-1] [name] | kind: [file] | location: [materials/refunds-2026.xlsx] | feeds: [research, concepts] | status: [not-read] | by: [name or role] | date: [YYYY-MM-DD] | note: [why it matters]
