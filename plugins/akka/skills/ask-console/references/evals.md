# Evaluation reads

Evaluation datasets, evaluators and experiments are read with `akka-optimize eval …`, with
`-o json` and the `--jq` filter in the block's source.

| Command | Answers |
|---|---|
| `eval datasets list` | One entry per dataset, describing its newest completed import. |
| `eval datasets get ID`, `eval datasets items ID --version V` | One dataset, and the items of one of its versions. |
| `eval evaluators list` | The evaluators. |
| `eval experiments history NAME` | Every run of a recurring experiment, most recent first. |
| `eval experiments get ID` | How far an experiment has got, and what it has found. |
| `eval experiments record ID [--summary]` | The finished record; `--summary` gives the measurements: rates, unsettled evaluations, and the per-group breakdown. |
| `eval experiments compare ID --baseline BASE` | An experiment against a baseline, item by item. |
| `eval experiments item EXPERIMENT ITEM` | One item's run and what each evaluator said about it. |

There is no command that lists every experiment. Start from an experiment name
(`history NAME`) or an id the user gave or clicked. Every number is the service's; nothing is
recomputed from the parts. `.metrics.overall.rate` in a record is the overall pass rate.

## Layouts

- **Inventory** ("Which evaluations do we have?"): a table of datasets, a table of
  evaluators, and, for a named experiment, a table of its runs from `history` with each run id
  as a link.
- **Health** ("Did the latest run pass?"): stats from `record`: pass rate, items measured
  and the gate outcome when the experiment defines a gate; a bar chart of the pass rate by
  group; a line chart of the pass rate across `history`.
- **Drilldown** ("Why did item 7 fail?"): a kv of the item from `item`, a table of its
  evaluations (evaluator, outcome, score, threshold, explanation last), and a code block of
  the response text.
- **Compare** ("Did the new version make the answers worse?"): stats of the counts from
  `compare` and a table of the items that moved, with before, after and the change.

## Status words

Gate outcomes are **HELD** (ok), **REGRESSED** (error) and **INSUFFICIENT_EVIDENCE**
(warn). For other outcomes and changes, use the words the output states, each with one
tone.
