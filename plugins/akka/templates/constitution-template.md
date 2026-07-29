# [PROJECT_NAME] Constitution
<!-- Example: Spec Constitution, TaskFlow Constitution, etc. -->

## Core Principles

### [PRINCIPLE_1_NAME]
<!-- Example: I. Library-First -->
[PRINCIPLE_1_DESCRIPTION]
<!-- Example: Every feature starts as a standalone library; Libraries must be self-contained, independently testable, documented; Clear purpose required - no organizational-only libraries -->

### [PRINCIPLE_2_NAME]
<!-- Example: II. CLI Interface -->
[PRINCIPLE_2_DESCRIPTION]
<!-- Example: Every library exposes functionality via CLI; Text in/out protocol: stdin/args → stdout, errors → stderr; Support JSON + human-readable formats -->

### [PRINCIPLE_3_NAME]
<!-- Example: III. Test-First (NON-NEGOTIABLE) -->
[PRINCIPLE_3_DESCRIPTION]
<!-- Example: TDD mandatory: Tests written → User approved → Tests fail → Then implement; Red-Green-Refactor cycle strictly enforced -->

### [PRINCIPLE_4_NAME]
<!-- Example: IV. Integration Testing -->
[PRINCIPLE_4_DESCRIPTION]
<!-- Example: Focus areas requiring integration tests: New library contract tests, Contract changes, Inter-service communication, Shared schemas -->

### [PRINCIPLE_5_NAME]
<!-- Example: V. Observability, VI. Versioning & Breaking Changes, VII. Simplicity -->
[PRINCIPLE_5_DESCRIPTION]
<!-- Example: Text I/O ensures debuggability; Structured logging required; Or: MAJOR.MINOR.BUILD format; Or: Start simple, YAGNI principles -->

### Requirements as Falsifiable Exit Conditions (Akka)
Every requirement that can be checked is captured as an exit condition with a binary, observable pass predicate and a check that delegates to the ecosystem's own tooling (a compiler, test runner, or linter) — authored per ecosystem, not per dependency. A requirement that cannot be stated as a falsifiable predicate is clarified with the human, never encoded as a check that cannot observe it. Every check is reviewed adversarially — "could this pass while the invariant is false?" — before it gates the build, and new or changed exit conditions are surfaced to the human for approval at the exit-condition level.

### Generated Harnesses and Generated Content Are Governed (Akka)
Enterprise-configuration assets and documentation are surfaces under the same coverage rule as code, not exceptions to it. Generated harnesses (CI, scanning, supply-chain, content style packages) are governed by the activated / configured / attested family: an asset is present, current against the recorded policy version, and enforcing — a step that does not gate the merge is treated as failing — or it is attested where it runs in an external system. Generated content is governed by language, structure, and tone: the deterministic prose rules and structure are verified by a linter in the project's own tree, and the holistic tone dimension is attested by a judge, never scored by the engine. Generation runs in the assistant; the engine verifies deterministically and records attestations. Nothing false-passes: a missing surface, a hollow asset, or an unattested delegated check reds or stalls, and never advances the build silently.

## [SECTION_2_NAME]
<!-- Example: Additional Constraints, Security Requirements, Performance Standards, etc. -->

[SECTION_2_CONTENT]
<!-- Example: Technology stack requirements, compliance standards, deployment policies, etc. -->

## [SECTION_3_NAME]
<!-- Example: Development Workflow, Review Process, Quality Gates, etc. -->

[SECTION_3_CONTENT]
<!-- Example: Code review requirements, testing gates, deployment approval process, etc. -->

## Governance
<!-- Example: Constitution supersedes all other practices; Amendments require documentation, approval, migration plan -->

[GOVERNANCE_RULES]
<!-- Example: All PRs/reviews must verify compliance; Complexity must be justified; Use [GUIDANCE_FILE] for runtime development guidance -->

**Version**: [CONSTITUTION_VERSION] | **Ratified**: [RATIFICATION_DATE] | **Last Amended**: [LAST_AMENDED_DATE]
<!-- Example: Version: 2.1.1 | Ratified: 2025-06-13 | Last Amended: 2025-07-16 -->
