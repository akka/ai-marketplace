# Model Policy: [PROJECT]

**Updated**: [DATE] | **Owner**: [name or role]

<!--
  This file is .akka/models.md. /akka:implement reads it to choose the model and effort
  for each sub-agent; /akka:plan starts its Model Plan from it.

  Model names are the names the agent harness accepts (for example opus, sonnet, haiku in
  Claude Code). Effort is low, medium or high.
-->

## Tiers *(required)*

Most capable first. The downgrade rule moves a purpose one step down this list.

1. [opus]: most accurate, slowest, highest cost
2. [sonnet]: balanced
3. [haiku]: fastest, lowest cost

## Purposes *(required)*

| Purpose | Model | Effort | Cost | Speed | Accuracy | Why |
|---------|-------|--------|------|-------|----------|-----|
| design | [opus] | high | highest | slowest | highest | [Mistakes in a design spread to everything built on it.] |
| implementation | [sonnet] | medium | medium | medium | high | [Most code follows a plan that already fixed the hard choices.] |
| review | [opus] | high | highest | slowest | highest | [A review is only worth its accuracy.] |
| tests | [sonnet] | medium | medium | medium | high | [Tests follow the specification closely.] |
| research | [sonnet] | medium | medium | medium | high | [Reading and summarising sources.] |
| visual checks | [haiku] | low | lowest | fastest | adequate | [Screenshots and layout checks are many and simple.] |
| documentation | [sonnet] | low | medium | medium | high | [Prose follows code that already exists.] |

## Downgrade Rule *(required)*

When usage reaches 85% of the plan's allowance, every sub-agent moves one tier down: the
first tier uses the second, the second uses the third, and the last tier stays. The main
session's model is not changed by the AI; the AI tells the person and suggests they switch.
The rule lifts when the allowance resets.

## Exceptions *(required, or none)*

Tasks or phases that keep their model under the downgrade rule, each with the reason.

- [purpose or phase]: [model] | why: [reason]
