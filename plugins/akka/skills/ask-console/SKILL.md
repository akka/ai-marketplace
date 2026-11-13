---
name: ask-console
description: Answer a question from the Akka local console's Ask page by rendering a screen into the console with the akka_canvas_* tools, instead of replying in text. Covers what Akka Optimize serves to the console's login (spend, prices, models, routing policies, use cases, incidents, training, and evaluation datasets and experiments), the governance of the system the console is scoped to (its controls, risk survey, signed bundles, compliance and verdicts), its redkit red-team campaigns, and its files. Use when the console starts an ask, when the user follows up on a canvas session, or when the user asks to see something in the console and the akka_canvas_* tools are available.
---

# Ask the console

A question typed on the Akka local console's Ask page reaches this skill. The answer is a
screen in the console, not text: gather facts with read-only reads, pick blocks, and render
one complete screen. The console owns how every block looks.

## Tools

An ask has these tools and no others:

- `Read`, `Grep` and `Glob`, below the folder the ask starts in (the system's folder, or an
  empty folder when no system is chosen) and below this skill's folder.
- `akka_canvas_catalog`: the block vocabulary, value shapes, templates, the source contract
  and the screen rules.
- `akka_canvas_query`: runs one allowlisted read, a read-only command (`cmd`) or one of the
  console's governance and red-team read routes (`get`), and returns its JSON.
- `akka_canvas_render`: renders a complete screen into a session and returns its URL.
- `akka_canvas_session`: a session's questions, screen titles and block outlines, and the
  notes the user pinned to blocks.
- `akka_canvas_sessions`: saved sessions, newest first.
- `akka_canvas_pin`: pins a session's screen as a dashboard.
- `akka_canvas_dashboards`: pinned dashboards and their refresh state.

There is no shell. Every data read goes through `akka_canvas_query` or a block's `source`.

## Environment and scope

The console reads one environment: the login of the Akka CLI daemon. Every read runs as that
login, so there is nothing to choose. A `profile` on a query or a source is accepted and not
used; leave it out.

The ask's prompt names its scope: a system and its folder, or no system. Answer about that
scope unless the question names another system, and say the scope in the summary sentence.

## Screen rules

- A screen is a **title**, **one summary sentence**, and **data blocks**. Nothing else.
- A title is one plain name for what is displayed (`Spend by use case, last 7 days`). It is
  never two phrases joined by a separator (`·`, `|`, `—`) and never a finding. The same holds
  for block titles and session names.
- The summary is one sentence: what was asked and the answer.
- No commentary, caveats, methodology, recommendations, or notes about what was not done,
  not found, or not available, anywhere, including block titles and `detail` fields.
- No data is an answer: show the zeros and the empty tables.
- Questions are complete, grammatical sentences. Keep the user's question verbatim in
  `question`, and write every link's `ask` as a full question
  (`What is the status of model support-slm-v2?`).
- Set `sample: true` whenever any data on the screen is illustrative rather than read.

## Tables and statuses

- Cells are plain values. The console renders every cell in one colour and one font, so
  meaning is never encoded in text; state goes in `status` values.
- A status appears only where the state matters: at most one status column per table, and
  the normal state is left empty.
- Ids are `link` columns so the user can click through; names and descriptions are `text`.
- Seven columns at most; details belong on the drill-down.
- A dimension with one value per row gets its own column so it lines up down the table.
  `tags` are only for dimensions with several values per row, and are never coloured.
- One free-text column per table, placed last. The console folds long cells behind an
  expand chevron, so do not shorten text.
- One status word always has one tone.
- Bar charts carry values only, in one colour. States go in a status-list or a table.

## Loop

1. **Session.** Continue the session the prompt names when it exists; a clicked link or a
   follow-up question arrives with its session id.
2. **Notes.** For a follow-up, call `akka_canvas_session` first. Notes flagged `new` were
   pinned by the user to blocks since the last screen; treat them as part of the question.
3. **Classify** the question as `inventory` (what is there), `health` (how it is doing),
   `drilldown` (one thing) or `compare` (A against B), and use that template.
4. **Find the reads.**
   - Spend, prices, models, routing policies, use cases, incidents and training:
     [references/optimize.md](references/optimize.md).
   - Evaluation datasets, evaluators and experiments:
     [references/evals.md](references/evals.md).
   - The system's controls, risk survey, signed bundles, compliance and verdicts:
     [references/governance.md](references/governance.md).
   - The system's redkit corpora and red-team campaigns:
     [references/redteam.md](references/redteam.md).
   - The system's own files (its code, configuration and documents): `Read`, `Grep` and
     `Glob`. Blocks built from files carry inline data, not a `source`.
5. **Gather with `akka_canvas_query`.** Run each command first without `--jq` to see the
   fields it answers, then test the exact command and `--jq` filter that will be the block's
   source. A filter is written against output that has been read, never from memory. A `get`
   read takes no filter: run it once and read the fields it answers.
6. **Compose.** Call `akka_canvas_catalog` once per conversation. Give every block whose data
   comes from one command or one `get` read a `source` whose output is the block's fields. Inline data only for
   joins across commands or data from files. Two to eight blocks. Send the complete screen,
   never a diff, and reuse block ids across follow-ups when a block means the same thing.
7. **Render** with `akka_canvas_render`. When it returns errors, fix them and render again.
8. **Pin** with `akka_canvas_pin` when the user asks to keep or track a screen, or for a
   dashboard. Only blocks with a `source` refresh.
9. **Reply** as the ask's prompt says. Without such an instruction, reply in one line with
   the URL the render returned, and do not restate the screen.

## Re-running a session

`akka_canvas_session` returns the questions in order. Gather fresh data for the last
question, with the earlier ones as context, and render a new screen into the same session.

## The read allowlist

`akka_canvas_query` and block sources run `akka optimize …` or `akka-optimize …`, without a
shell, as the daemon's login. Only read commands are allowed. A command is refused when it
names a flag that changes where it connects or what it reads from disk: `--context`, `--url`
and any flag ending in `-url`, `--host`, `--region`, `--config`, `--file`, `--dir`,
`--lineage`, `--force` and their short forms. Every command takes `-o json` and `--jq`.

A `get` read is a GET of one of the console's read routes that
[references/governance.md](references/governance.md) and
[references/redteam.md](references/redteam.md) list, with only the query parameters they
name. Every other path, and every write, is refused. A `get` read takes no `--jq`.

Placeholders resolve at each run to ISO-8601 UTC instants: `{{now}}`, `{{hour}}` (start of
the current UTC hour) and `{{today}}` (start of the UTC day), each with an optional offset
such as `{{hour-7d}}` or `{{now-30m}}`.

A query fails with "not enabled" when Optimize is not enabled for the daemon's login. Every
Optimize read then has no data: render the screen with empty blocks carrying inline data and
no `source`.

A governance or red-team read that cannot answer gets the same treatment: its blocks are
empty, with inline data and no `source`, and the reply names the reason in one sentence.
This holds when the ask has no system in scope (every `get` names a system, so none is run),
when a module is switched off (`404 module-disabled`), when two bundles cannot be compared
(422), and for the runs a red-team list reports as `unreadable` or behind a `gitError`.
