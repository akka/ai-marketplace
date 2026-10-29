---
name: visualize
description: "Generate Mermaid diagrams for a feature from its spec.md (requirement-level views) and plan.md (technical component diagrams)."
---

## User Input

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

`/akka:visualize` draws Mermaid diagrams for one feature from the artifacts the
workflow has already written. `spec.md` yields non-technical requirement
diagrams in `spec-diagrams.md`; `plan.md` yields technical component diagrams
in `plan-diagrams.md`. The two files are independent: each is written whenever
its source exists.

Every diagram file records, directly under its H1, the SHA-256 of the source
files it was drawn from. A re-run regenerates only the files whose sources have
changed, so a hand edit to `spec.md` or `plan.md` is detected. `/akka:specify`,
`/akka:clarify` and `/akka:plan` follow the Requirements or Technical mode below
to refresh a diagram file that already exists after they write; they never
create one.

The output is Markdown Mermaid that any Mermaid-aware Markdown viewer renders.
It is not the `docs/index.html` SVG skin that `/akka:docs` produces.

## Outline

1. **Setup.** Call `akka_sdd_list_specs`. Remove a `--force` flag from
   `the user's request` if present; if the remaining text names a feature (number,
   short name or directory), select that feature, otherwise identify the target
   feature from the response. If more than one feature matches, list them and
   ask. Set FEATURE_DIR to the feature's absolute directory and check which of
   `FEATURE_DIR/spec.md` and `FEATURE_DIR/plan.md` exist.

2. **Select modes.** The modes are independent; run every one that applies:
   - `spec.md` exists → **Requirements mode** writes `FEATURE_DIR/spec-diagrams.md`.
   - `plan.md` exists → **Technical mode** writes `FEATURE_DIR/plan-diagrams.md`.
   - Both exist → run both modes and write two files.
   - Neither exists → report what is missing, recommend `/akka:specify`, and stop.

3. **Load the templates.** For each selected mode, load
   `spec-diagrams-template.md` (Requirements) or `plan-diagrams-template.md`
   (Technical) from the first of these locations that has it:
   1. The akka plugin: `plugins/akka/templates/<name>`.
   2. The project: `.akka/templates/`. The Akka CLI installs templates there
      without the `-template` suffix (`spec-diagrams.md`, `plan-diagrams.md`);
      accept either name.
   3. The released marketplace, which is what the Akka CLI installs from:
      `https://raw.githubusercontent.com/akka/ai-marketplace/stable/plugins/akka/templates/<name>`.
      Read it; do not save it into the project.

   Do not call `akka_sdd_get_template` for these; the CLI does not know them.
   If no location has the template, report the locations tried and stop that
   mode; never reconstruct a template from memory. The template is the
   structure of the output file: its color table, external-system rules, topic-node rules, sequence
   numbers, section order, and the guidance comment in each section all apply.

4. **Check freshness.** Compute the SHA-256 of the exact bytes of each source
   with `sha256sum <file>` (or `shasum -a 256 <file>` on macOS):
   - Requirements mode: `spec.md`.
   - Technical mode: `plan.md` and `spec.md`. If `spec.md` is missing, draw from
     `plan.md` alone and stamp `spec.md sha256=missing`.

   If the output file exists, read the `<!-- visualize-source: ... -->` line
   directly under its H1 and compare:
   - Every hash matches and `the user's request` does not contain `--force` → report
     "diagrams are up to date" for that mode and skip it.
   - A hash differs → regenerate that mode, and name the source that changed.
   - The file has no stamp, or the stamp cannot be read → treat it as stale and
     regenerate.

   If the output file does not exist, generate it.

5. **Requirements mode** (from `spec.md`).

   a. **Load context.** Read `FEATURE_DIR/spec.md` to extract:
      - All user stories with their priorities, titles, and dependency relationships
      - Actors and their goals (who interacts with the system and what they do)
      - Key entities and their relationships (if defined)
      - Status lifecycle or state progression (if defined)
      - Edge cases and assumptions

   b. **Generate the requirement diagrams** following the template conventions:
      - **Diagram 1 — User Journey Map**: flowchart of all user stories arranged
        by priority, showing dependency relationships between stories. Color by
        priority tier.
      - **Diagram 2 — Actor–Goal Overview**: flowchart showing actors, the
        system, and external systems. Connect actors to their goals derived from
        user stories. This is a use-case-level view.
      - **Diagram 3 — Entity Relationship Map**: ONLY if the spec defines Key
        Entities; omit the whole section otherwise. Show entities and their
        conceptual relationships (no database details).
      - **Diagram 4 — Status Lifecycle**: ONLY if the spec describes a status
        lifecycle or state progression; omit the whole section otherwise. Show
        statuses and transitions with triggers.

6. **Technical mode** (from `plan.md` plus `spec.md`).

   a. **Load context.** Read `FEATURE_DIR/plan.md` and `FEATURE_DIR/spec.md` to extract:
      - All components (Endpoints, Workflows, Agents, Views, Entities, Consumers)
      - Their dependencies and call relationships
      - Workflow states and transitions (if a Workflow is present)
      - External systems and actors
      - Topic names (if `@Produce.ToTopic` / `@Consume.FromTopic` is used)

   b. **Generate the technical diagrams** following the template conventions
      (color, external nodes, topic nodes, sequence numbers):
      - **Diagram 1 — Component Dependencies**: flowchart of all components,
        grouped by layer: Endpoint, Workflow, Agent, View, Entity, Consumer.
        Draw a subgraph only for the layers the plan uses.
      - **Diagram 2 — Sequence Diagram**: end-to-end flows. At minimum the happy
        path and one error path; add a HITL path when the plan has a human
        review or approval step.
      - **Diagram 3 — Workflow State Machines**: ONLY if the feature uses Akka
        Workflows; omit the whole section otherwise. Produce **one numbered
        subsection per Workflow class** (3.1, 3.2, …), each with its own Mermaid
        flowchart, titled with the class name (e.g. `### 3.1 OrderWorkflow`).

7. **Self-check every Mermaid block** before writing, and fix anything that fails:
   - Every node, edge, participant and transition is stated in `spec.md` or
     `plan.md`. Remove anything inferred from a class name.
   - Every `linkStyle` index exists in that diagram's edge list. Indices are
     0-based in declaration order, and a chained `A --> B --> C` declares two
     edges.
   - Every label containing special characters (`( ) [ ] { } < > : ; , / | # &`
     or a quote) is wrapped in double quotes; a literal double quote inside a
     label is written `#quot;`.
   - Every `style` target is a node or subgraph id declared in that diagram.
   - Sequence diagrams use no `-.>>`, and every `rect`, `alt`, `opt` and `loop`
     block is closed with `end`.

   If the Mermaid CLI (`mmdc`) is on the PATH, render each block as a final
   check; a parse error means the block is not done.

8. **Write the files.** Write `FEATURE_DIR/spec-diagrams.md` and/or
   `FEATURE_DIR/plan-diagrams.md` from the template structure: fill
   `[FEATURE]` and the source link, fill the stamp line with the hashes from
   step 4, replace each example diagram with the real one, and delete every
   section that was omitted, heading included.

9. **Report.** For each mode, state one of: the path written and which
   diagrams were generated or omitted, with the reason for each omission;
   "diagrams are up to date"; or what is missing from the source that stopped
   the mode. After a spec-only run, suggest `/akka:plan`.

## Key rules

### General

- Use absolute paths
- NEVER invent categories to justify using a color — use only colors present in the actual feature
- Draw only the components, calls, actors and transitions that `plan.md` or
  `spec.md` actually state. Never infer a call from a class name: a component
  that exists may have no caller, and a diagram showing a call that does not
  happen is worse than no diagram, because it is believed.
- Run the step 7 self-check on every block before writing.
- This command writes only `spec-diagrams.md` and `plan-diagrams.md`. It runs
  no auditors, calls no `akka_ec_*` tools, and never changes `spec.md`,
  `plan.md` or any other artifact.
- These are Markdown Mermaid diagrams, not the `docs/index.html` SVG skin. Use
  the palette in the diagram templates; `akka-style-guide.md` and
  `diagram_check.py` do not apply to them.
- When a mode stops, leave any existing diagram file for it untouched. Its old
  stamp marks it as stale. When another command runs a mode as a refresh, a
  stopped mode is reported and the other command's own result stands.

### Requirements Mode

- Diagrams MUST be non-technical — no implementation details, no class names, no API paths
- Use language from the spec (user story titles, entity names, status names) — do not rename or translate
- Diagram 3 (entity relationships) MUST be omitted entirely if no Key Entities section exists in the spec
- Diagram 4 (status lifecycle) MUST be omitted entirely if the spec does not describe a status lifecycle
- If `spec.md` does not yet have enough detail to generate accurate diagrams, report what is missing and stop

### Technical Mode

- NEVER use `-.>>` in sequence diagrams (invalid Mermaid syntax) — use `-->>` for dotted arrows
- NEVER collapse a topic into an arrow label — always represent it as an explicit cylinder node
- Diagram 3 (state machines) MUST be omitted entirely if no Akka Workflow is used
- There MUST be exactly one state machine subsection per Workflow class — never merge multiple workflows into one diagram
- If `plan.md` does not yet have enough component detail to generate accurate diagrams, report what is missing and stop

## Done When

- [ ] FEATURE_DIR was resolved via `akka_sdd_list_specs`, using `the user's request` to pick the feature when it named one.
- [ ] Every mode whose source exists was run; with neither `spec.md` nor `plan.md`, the missing files were reported and `/akka:specify` recommended.
- [ ] The templates were loaded from the akka plugin, then `.akka/templates/`, then the `stable` marketplace, in that order; `akka_sdd_get_template` was not called for them.
- [ ] Each existing diagram file's stamp was compared with the current source hashes; a matching mode was skipped as up to date unless `--force` was given, and a changed source was named.
- [ ] Requirements mode produced the User Journey Map and Actor–Goal Overview, plus the Entity Relationship Map and Status Lifecycle only where the spec defines them, all in the spec's own non-technical wording.
- [ ] Technical mode produced Component Dependencies grouped by layer, a Sequence Diagram with a happy path, at least one error path and a HITL path where applicable, and one state machine per Workflow class where Workflows are used.
- [ ] Topics are cylinder nodes, no sequence diagram uses `-.>>`, and no node or call was inferred from a class name.
- [ ] Every block passed the self-check: `linkStyle` indices exist, special-character labels are quoted, `style` targets are declared.
- [ ] Each written file carries a `visualize-source` stamp with the SHA-256 of every source it was drawn from.
- [ ] Only `spec-diagrams.md` and `plan-diagrams.md` were written; no spec, plan or exit condition was changed.
- [ ] The report listed the paths written and each diagram generated or omitted, with the reason for every omission.
