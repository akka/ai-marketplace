# Governance reads

A system's governance is read from the console's own routes with
`akka_canvas_query { get: "<path>" }`. Each read is a GET of one of the paths below, run in
the console, and answers the route's JSON as it is. `:system` is the system's id (lowercase
letters, digits and hyphens); every other `:name` is one id, version or file name, never a
path. Any other path, any write and any query parameter not listed is refused.

These reads take no `--jq`. Read the answer, then put the block's data inline. A block's
`source` may be `{ get: "<path>" }` only when the answer is already the block's fields.

## Controls, survey and bundles

| Path | Answers |
|---|---|
| `/policies/:system/overview` | The system's governance at a glance: revisions, the pinned corpus, control counts by provenance, and the signed bundles. |
| `/policies/:system/stage` | The system's governance stage. |
| `/policies/:system/board` | The controls board: the stage, what holds it, the readiness rows, the bundle in force and the rail of bundles. |
| `/policies/:system/baseline` | The organization's governance baseline the system has pinned. |
| `/policies/:system/frameworks` | The frameworks of the pinned regulation corpus. |
| `/policies/:system/survey` | The risk survey's answers. |
| `/policies/:system/survey-definition`, `/policies/:system/survey-presets` | The risk survey's questions and presets. |
| `/policies/:system/survey/bom` | The bill of materials the survey was answered from. |
| `/policies/:system/drift` | How the controls differ from what the survey now derives. |
| `/policies/:system/derived` | The controls the survey derives. |
| `/policies/:system/coverage` | How the controls cover the corpus's requirements. |
| `/policies/:system/controls` | The draft controls, each with its provenance and sign-off. |
| `/policies/:system/bundles` | The signed bundles, oldest first. |
| `/policies/:system/bundles/v/:version` | One signed bundle. |
| `/policies/:system/bundles/compare?from=V&to=W` | Two bundles compared; `to=draft` compares against the draft. |
| `/policies/:system/corpus` | The pinned regulation corpus. |
| `/policies/:system/corpus/controls/:controlId` | One corpus control and what it requires. |

## Compliance

| Path | Answers |
|---|---|
| `/compliance/:system[?at=T]` | Whether the controls of the bundle in force are satisfied, at `at` or now. |
| `/compliance/:system/timeline[?from=F&to=T&step=day\|week]` | The counts at the end of each day or week, and the signings between. |
| `/compliance/:system/controls/:rowId/history[?from=F&to=T]` | One control's status over the period, and its verdicts. |

## Verdicts

| Path | Answers |
|---|---|
| `/verdicts/:system/list` | One page of the verdict ledger, newest first: `{ verdicts, total, matched, next?, facets, problems, bundles }`. Filters `bundle`, `control`, `mechanism`, `environment` and `conclusion` each may repeat; `from`, `to`, `limit` (1 to 500) and `cursor` (the previous page's `next`). |
| `/verdicts/:system/verdict/:id` | One verdict with its detail. |
| `/verdicts/:system/controls` | Every control of the bundle in force with its verdicts. |
| `/verdicts/:system/analysis[?bundle=V&from=F&to=T]` | Each control's conclusions and changes per environment over a period, against the prior period. |
| `/verdicts/:system/analysis/controls/:rowId` | One control's verdicts, each with its bundle, and its changes. |
| `/verdicts/:system/sources` | The runs that can be loaded as verdicts, and the mapping file. |

Times are RFC 3339 instants or dates; a date is a UTC day. Every answer is the console's:
nothing is recomputed from the parts.

## Layouts

- **Inventory** ("Which controls do we have?"): stats from `board`, and a table of the
  controls from `controls` with each row id as a link.
- **Health** ("Are we compliant?"): stats from `/compliance/:system`, and a line chart of
  the counts from `timeline`.
- **Drilldown** ("What does control X require?"): a kv of the corpus control, and a table of
  its verdicts from `analysis/controls/:rowId`.
- **Compare** ("What changed in the new bundle?"): a table of the rows `bundles/compare`
  answers as added, removed or changed.

## Status words

Use the words the answers state (Approved, Waived, Rejected, Not reviewed; the conclusions
of verdicts), each with one tone.
