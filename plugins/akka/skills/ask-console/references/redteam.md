# Red-team reads

A system's redkit red-team campaigns are read from the console's own routes with
`akka_canvas_query { get: "<path>" }`. Each read is a GET of one of the paths below, run in
the console, and answers the route's JSON as it is. `:system` is the system's id; `:campaign`
and `:file` name one campaign folder and one run file, never a path. Any other path, any
write and any query parameter not listed is refused.

These reads take no `--jq`. Read the answer, then put the block's data inline. A block's
`source` may be `{ get: "<path>" }` only when the answer is already the block's fields.

| Path | Answers |
|---|---|
| `/specify/:system/redteam/corpora` | The redkit corpora the system keeps: each corpus's name, hazards, item count and the rules its items attack. |
| `/specify/:system/runs/redteam` | Every red-team run, newest first, without its record and text: `{ runs, unreadable, gitError? }`. Each run names its `campaign` and `file`. |
| `/specify/:system/runs/redteam/:campaign/:file` | One run whole: its run, panels, record and text. |

A red-team run that has been loaded as verdicts is read with the verdict reads in
[governance.md](governance.md): `/verdicts/:system/list` lists it, and each of its verdicts
names the run in `source.ref` (`redteam/<campaign>/<file>`).

## Layouts

- **Inventory** ("Which red-team campaigns have we run?"): a table of the runs, newest
  first, with each campaign as a link, and a table of the corpora.
- **Health** ("Did the last campaign break through?"): stats from the run's panels, and a
  table of its rules. Panels have no fixed fields; read a run's panels before naming a
  figure, and show only the figures they hold.
- **Drilldown** ("Why did rule R break through?"): a kv of the rule's figures, and a table of
  the attempts that broke through.
- **Compare** ("Is the new model more robust?"): an outcome grid of rules by run.

## Status words

A rule **Held** (ok) or **Broke through** (error). For other outcomes, use the words the run
states, each with one tone.
