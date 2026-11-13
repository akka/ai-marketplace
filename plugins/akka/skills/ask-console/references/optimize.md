# Akka Optimize reads

Every command below is an allowlisted read. Write it as `akka-optimize <command>` (or
`akka optimize <command>`) with `-o json`, and put the `--jq` filter in the block's
`source.cmd` so the stdout is the block's fields.

## What each command answers

| Question | Commands |
|---|---|
| What did a period cost, and on what? | `spend get --from F --to T [--by none\|model\|useCase\|model,useCase\|caller]` |
| How did a period change against another? | `spend compare --from F --to T --against-from F2 --against-to T2 [--by …]` |
| How did spend move over time? | `spend series --from F --to T [--by …]` |
| What did conversations cost? | `spend conversations list --from F --to T` |
| What does each model cost per million tokens? | `pricing-catalog get [--at INSTANT]`, `pricing-catalog versions list` |
| Which models are in the portfolio? | `models list [--state S] [--risk-tier T] [--alerting] [--needs-review]` |
| What is the status of one model? | `models get NAME [--usage] [--history] [--reports]`, `models conditions\|actions\|attestations list NAME` |
| How is a use case routed? | `routing-policies get USECASE` |
| Which use cases carry the traffic? | `use-cases working-set [--settled]`, `use-cases status`, `use-cases exemplars list USECASE` |
| Which use-case manifests exist? | `use-cases manifests list`, `use-cases manifests get TAG`, `use-cases manifests diff TAG` |
| Which routing rules are in force? | `rulesets list\|get\|history`, `routing-classifiers list\|get\|history` |
| What went wrong? | `incidents list [--kind anomaly\|blocked\|scrub] [--state open\|resolved] [--window 1d\|7d\|30d\|90d\|365d]` |
| How is training going? | `training runs list [--phase P]`, `training runs get\|metrics\|hparams ID`, `training evaluations list\|get\|report`, `training projects list\|get\|history\|scores`, `training base-models list\|get\|candidates`, `training capacity`, `training info` |
| What does the registry hold? | `registry models\|datasets\|bundles list\|get\|versions`, `registry namespaces list\|get`, `registry info` |
| Is Optimize reachable for this login? | `status` |

## Spend

A spend window is whole UTC hours: `--from {{hour-7d}} --to {{hour}}`, `--from` inclusive
and `--to` exclusive. The service refuses a window it cannot answer.

`spend get` answers `{ window, rows: [...], total }`. Each row, and `total`, carries `model`,
`useCase`, `tags`, `exchanges`, `tokens` (`total`, `input`, `cacheRead`, `cacheWrite`,
`output`, `reasoning`), `unpriced.exchanges` and `spend`. `spend` is a figure:
`{ value, unit, per, absent }`, where `value` is a decimal string and `absent` says why a
figure has no value. A figure with no value is shown as an empty cell and never as zero, and
it is left out of a chart.

`spend compare` answers `{ period, against, rows: [...] }`; each row carries `model`,
`useCase`, and the two sides as `period` and `against`, each shaped like a `spend get` row.
The change is the period less the period it is compared against.

A use case that is the empty string is traffic with no use-case label; show it as
`Unlabelled`.

```
bar-chart   akka-optimize spend get --from {{hour-7d}} --to {{hour}} --by useCase -o json --jq
            '{unit: .total.spend.unit,
              bars: [.rows[] | select((.spend.absent // "") == "")
                     | {label: (if .useCase == "" then "Unlabelled" else .useCase end),
                        value: (.spend.value | tonumber)}] | sort_by(-.value)}'
```

## Prices

`pricing-catalog get` answers `{ version, effectiveAt, source, models: [...] }`. Each model
carries `servedName`, `model` (`provider`, `name`, `version`), `currency`, and its rates per
million tokens: `input`, `output`, `cacheRead`, `cacheWrite`, `reasoning`. A rate the
catalog does not state is null.

## Status words

Use the words the output states, each with one tone: lifecycle states as written, an
incident's severity as written, a model with a breached condition as alerting (error), and a
model with a decision pending as needs review (warn).

## Compare across capabilities

A question such as "Is the cheaper model good enough to switch to?" joins prices and spend
from this page with evaluation results from [evals.md](evals.md). Blocks that join commands
carry inline data; blocks from one command keep their source.
