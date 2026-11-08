# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`
**Discovery**: [the discovery/ files read, or none]

**Note**: This template is filled in by the `/akka:plan` command. See `.akka/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

[Gates determined based on constitution file]

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/akka:plan command output)
├── research.md          # Phase 0 output (/akka:plan command)
├── data-model.md        # Phase 1 output (/akka:plan command)
├── quickstart.md        # Phase 1 output (/akka:plan command)
├── contracts/           # Phase 1 output (/akka:plan command)
└── tasks.md             # Phase 2 output (/akka:tasks command - NOT created by /akka:plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: Single Akka service (DEFAULT)
src/
├── main/
│   ├── java/{org}/{app}/
│   │   ├── api/           # HTTP/gRPC/MCP endpoints, request/response records
│   │   ├── application/   # Akka components: entities, views, workflows, consumers, agents
│   │   └── domain/        # Domain records and business logic (no Akka imports)
│   ├── proto/             # Protobuf definitions (gRPC endpoints only)
│   └── resources/
│       └── static-resources/  # Web UI assets (only if the service serves a UI)
└── test/
    └── java/{org}/{app}/  # Unit and integration tests

# [REMOVE IF UNUSED] Option 2: Akka service + separately hosted frontend
backend/
└── [same as Option 1]

frontend/
├── src/
└── tests/

# [REMOVE IF UNUSED] Option 3: Multiple Akka services (one per bounded context)
services/
├── {service-a}/
│   └── [same as Option 1]
└── {service-b}/
    └── [same as Option 1]
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Component Architecture

*Filled during Phase 1 (design). Before completing this table, read the
"Choosing a component type" section in `akka-context/sdk/components/index.html.md`.*

| Domain concept / process | Component | Why this component | Rejected alternative and why not (close-call decisions) |
|--------------------------|-----------|--------------------|----------------------------------|
| [e.g., Wallet] | Event Sourced Entity | Transaction ledger is a business requirement | Key Value Entity: no history, cannot audit |
| [e.g., Transfer process] | Workflow | Multi-step, needs compensation and a queryable status | Consumer chain: no compensation path, no status |
| [e.g., Wallets by owner query] | View | Lookup by non-id attribute across entities | Direct entity read: only works by id |

Rows for close-call decisions (entity type, view vs direct entity read,
workflow vs consumer, timed action vs workflow timer) MUST name the rejected
alternative and why it was not chosen (constitution: "Right component for the
job"). For obvious choices the last column may stay empty. Pure logic with no
state, subscription, schedule, or API surface is a plain domain class and does
not appear in this table.

## Delivery Phases

*Filled during Phase 2 (delivery plan). Only delivery phases use headings that begin with
"Phase": the Model Plan and the exit conditions read every such heading as a phase. Tasks
name their phase with a `[P<n>]` tag.*

**Critical path**: [Phase 1 → Phase 2 → Phase 4; Phase 3 runs beside Phase 2]

### Phase 1: [Name]

- **Goal**: [what is true when this phase is done, in one sentence]
- **Steps**: [the main steps, in order]
- **Parallel with**: [other phases that can run at the same time, or none]
- **Acceptance test**: [a check that can fail, and how it is run]
- **Gate**: [review gate that must be approved before this phase starts, or none]
- **Risk**: [what is most likely to go wrong, and how early it would show]
- **Rollback**: [how to undo this phase without losing earlier phases]
- **Size**: [S (hours) | M (one to three days) | L (a week or more; consider splitting)]

### Phase 2: [Name]

- **Goal**: [...]
- **Steps**: [...]
- **Parallel with**: [...]
- **Acceptance test**: [...]
- **Gate**: [...]
- **Risk**: [...]
- **Rollback**: [...]
- **Size**: [...]

## Review Gates *(required, or none)*

Artifacts a person approves before a phase starts. Each artifact is registered in
`discovery/<topic>/mocks/index.md` with `/akka:discover <topic> mock`.

| Gate | Before phase | What is reviewed | Artifact | Approver |
|------|--------------|------------------|----------|----------|
| G-1 | Phase 2 | [screens of the checkout flow] | [M-1] | [role] |

## Baseline *(required for a modernization, otherwise required or none)*

What is true today, measured, so the result can be compared with it. Only measured values
go in this section, one bullet per metric, in the form `- <metric>: <value> | method: ... |
source: ...`. The metric name contains no colon. A value not yet measured goes under
Metrics and Targets.

- [p95 quote latency]: [840 ms] | method: [timing probe, 200 requests] | source: [F-n or .akka/discovery/timing.json]

## Metrics and Targets *(required, or none)*

- [metric] | target: [value] | method: [how it will be measured] | serves: [SC-001 or F-n] | measured before: [Phase n, or already in Baseline]

## Model Plan

*One row per phase and purpose. Every phase heading above needs at least one row with a
model and an effort. Start from `.akka/models.md` when it exists and say why a row differs.
No subheadings in this section.*

| Phase | Purpose | Model | Effort | Cost | Speed | Accuracy | Why |
|-------|---------|-------|--------|------|-------|----------|-----|
| Phase 1 | [design] | [opus] | [high] | [highest] | [slowest] | [highest] | [The data model is fixed here and everything builds on it.] |
| Phase 2 | [implementation] | [sonnet] | [medium] | [medium] | [medium] | [high] | [Follows the design closely.] |
| Phase 2 | [visual checks] | [haiku] | [low] | [lowest] | [fastest] | [adequate] | [Many simple screenshot checks.] |

**Downgrade rule**: [When usage reaches 85% of the plan's allowance, every sub-agent moves
one tier down, as `.akka/models.md` defines. Exceptions: none.]

**Estimate**: [rough total effort and cost by phase, in relative terms unless prices were given]

## Decisions Log *(required, or none)*

Every choice that changes the plan, including the open decisions carried from
`discovery/understanding.md`. When a decision is made, the Decision cell states the answer.

| ID | Decision | Recommendation | Owner | Status |
|----|----------|----------------|-------|--------|
| D-1 | [Which storage holds the audit log?] | [Event Sourced Entity: the log is the event journal] | [role] | [open \| decided YYYY-MM-DD \| dropped] |

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
