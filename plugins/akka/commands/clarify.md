---
description: Identify underspecified areas in the current feature spec by asking up to 5 highly targeted clarification questions and encoding answers back into the spec.
handoffs:
  - label: Build Technical Plan
    agent: akka.plan
    prompt: Create a plan for the spec. I am building with...
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

Goal: Detect and reduce ambiguity or missing decision points in the active feature specification and record the clarifications directly in the spec file.

Note: This clarification workflow is expected to run (and be completed) BEFORE invoking `/akka:plan`. If the user explicitly states they are skipping clarification (e.g., exploratory spike), you may proceed, but must warn that downstream rework risk increases.

Execution steps:

1. Call the `akka_sdd_list_specs` MCP tool to find features. From the response, identify the target feature's directory (FEATURE_DIR) and spec file path (FEATURE_SPEC). If no features exist, instruct the user to run `/akka:specify` first.
   - `FEATURE_DIR`
   - `FEATURE_SPEC`
   - (Optionally capture `IMPL_PLAN`, `TASKS` for future chained flows.)
   - If JSON parsing fails, abort and instruct user to re-run `/akka:specify` or verify feature branch environment.

2. Load the current spec file. Perform a structured ambiguity & coverage scan using this taxonomy. For each category, mark status: Clear / Partial / Missing. Produce an internal coverage map used for prioritization (do not output raw map unless no questions will be asked).

   Functional Scope & Behavior:
   - Core user goals & success criteria
   - Explicit out-of-scope declarations
   - User roles / personas differentiation

   Domain & Data Model:
   - Entities, attributes, relationships
   - Identity & uniqueness rules
   - Lifecycle/state transitions
   - Data volume / scale assumptions

   Interaction & UX Flow:
   - Critical user journeys / sequences
   - Error/empty/loading states
   - Accessibility or localization notes

   Non-Functional Quality Attributes:
   - Performance (latency, throughput targets)
   - Scalability (horizontal/vertical, limits)
   - Reliability & availability (uptime, recovery expectations)
   - Observability (logging, metrics, tracing signals)
   - Security & privacy (authN/Z, data protection, threat assumptions)
   - Compliance / regulatory constraints (if any)

   Integration & External Dependencies:
   - External services/APIs and failure modes
   - Data import/export formats
   - Protocol/versioning assumptions

   Edge Cases & Failure Handling:
   - Negative scenarios
   - Rate limiting / throttling
   - Conflict resolution (e.g., concurrent edits)

   Constraints & Tradeoffs:
   - Technical constraints (language, storage, hosting)
   - Explicit tradeoffs or rejected alternatives

   Terminology & Consistency:
   - Canonical glossary terms
   - Avoided synonyms / deprecated terms

   Completion Signals:
   - Acceptance criteria testability
   - Measurable Definition of Done style indicators

   Misc / Placeholders:
   - TODO markers / unresolved decisions
   - Ambiguous adjectives ("robust", "intuitive") lacking quantification

   For each category with Partial or Missing status, add a candidate question opportunity unless:
   - Clarification would not materially change implementation or validation strategy
   - Information is better deferred to planning phase (note internally)

3. Generate (internally) a prioritized queue of candidate clarification questions (maximum 5). Do NOT output them all at once. Apply these constraints:
    - Maximum of 10 total questions across the whole session.
    - Each question must be answerable with EITHER:
       - A short multiple‑choice selection (2–5 distinct, mutually exclusive options), OR
       - A one-word / short‑phrase answer (explicitly constrain: "Answer in <=5 words").
    - Only include questions whose answers materially impact architecture, data modeling, task decomposition, test design, UX behavior, operational readiness, or compliance validation.
    - Ensure category coverage balance: attempt to cover the highest impact unresolved categories first; avoid asking two low-impact questions when a single high-impact area (e.g., security posture) is unresolved.
    - Exclude questions already answered, trivial stylistic preferences, or plan-level execution details (unless blocking correctness).
    - Favor clarifications that reduce downstream rework risk or prevent misaligned acceptance tests.
    - If more than 5 categories remain unresolved, select the top 5 by (Impact * Uncertainty) heuristic.

4. Sequential questioning loop (interactive):
    - Present EXACTLY ONE question at a time.
    - For multiple‑choice questions:
       - **Analyze all options** and determine the **most suitable option** based on:
          - Best practices for the project type
          - Common patterns in similar implementations
          - Risk reduction (security, performance, maintainability)
          - Alignment with any explicit project goals or constraints visible in the spec
       - Present your **recommended option prominently** at the top with clear reasoning (1-2 sentences explaining why this is the best choice).
       - Format as: `**Recommended:** Option [X] - <reasoning>`
       - Then render all options as a Markdown table:

       | Option | Description |
       |--------|-------------|
       | A | <Option A description> |
       | B | <Option B description> |
       | C | <Option C description> (add D/E as needed up to 5) |
       | Short | Provide a different short answer (<=5 words) (Include only if free-form alternative is appropriate) |

       - After the table, add: `You can reply with the option letter (e.g., "A"), accept the recommendation by saying "yes" or "recommended", or provide your own short answer.`
    - For short‑answer style (no meaningful discrete options):
       - Provide your **suggested answer** based on best practices and context.
       - Format as: `**Suggested:** <your proposed answer> - <brief reasoning>`
       - Then output: `Format: Short answer (<=5 words). You can accept the suggestion by saying "yes" or "suggested", or provide your own answer.`
    - After the user answers:
       - If the user replies with "yes", "recommended", or "suggested", use your previously stated recommendation/suggestion as the answer.
       - Otherwise, validate the answer maps to one option or fits the <=5 word constraint.
       - If ambiguous, ask for a quick disambiguation (count still belongs to same question; do not advance).
       - Once satisfactory, record it in working memory (do not yet write to disk) and move to the next queued question.
    - Stop asking further questions when:
       - All critical ambiguities resolved early (remaining queued items become unnecessary), OR
       - User signals completion ("done", "good", "no more"), OR
       - You reach 5 asked questions.
    - Never reveal future queued questions in advance.
    - If no valid questions exist at start, immediately report no critical ambiguities.

5. Integration after EACH accepted answer (incremental update approach):
    - Maintain in-memory representation of the spec (loaded once at start) plus the raw file contents.
    - For the first integrated answer in this session:
       - Ensure a `## Clarifications` section exists (create it just after the highest-level contextual/overview section per the spec template if missing).
       - Under it, create (if not present) a `### Session YYYY-MM-DD` subheading for today.
    - Append a bullet line immediately after acceptance: `- Q: <question> → A: <final answer>`.
    - Then immediately apply the clarification to the most appropriate section(s):
       - Functional ambiguity → Update or add a bullet in Functional Requirements.
       - User interaction / actor distinction → Update User Stories or Actors subsection (if present) with clarified role, constraint, or scenario.
       - Data shape / entities → Update Data Model (add fields, types, relationships) preserving ordering; note added constraints succinctly.
       - Non-functional constraint → Add/modify measurable criteria in Non-Functional / Quality Attributes section (convert vague adjective to metric or explicit target).
       - Edge case / negative flow → Add a new bullet under Edge Cases / Error Handling (or create such subsection if template provides placeholder for it).
       - Terminology conflict → Normalize term across spec; retain original only if necessary by adding `(formerly referred to as "X")` once.
    - If the clarification invalidates an earlier ambiguous statement, replace that statement instead of duplicating; leave no obsolete contradictory text.
    - Save the spec file AFTER each integration to minimize risk of context loss (atomic overwrite).
    - Preserve formatting: do not reorder unrelated sections; keep heading hierarchy intact.
    - Keep each inserted clarification minimal and testable (avoid narrative drift).

6. Validation (performed after EACH write plus final pass):
   - Clarifications session contains exactly one bullet per accepted answer (no duplicates).
   - Total asked (accepted) questions ≤ 5.
   - Updated sections contain no lingering vague placeholders the new answer was meant to resolve.
   - No contradictory earlier statement remains (scan for now-invalid alternative choices removed).
   - Markdown structure valid; only allowed new headings: `## Clarifications`, `### Session YYYY-MM-DD`.
   - Terminology consistency: same canonical term used across all updated sections.

7. Write the updated spec back to `FEATURE_SPEC`.

8. **Refresh spec visualize**: If any clarification was written into the spec, bring `FEATURE_DIR/spec-visualize.md` back in line with it. Skip this step if no answers were accepted.
   - **File exists**: update it in place. Keep its structure, colors, and conventions, except that the label rule below wins: quote any unquoted label in a diagram you redraw. Redraw only the diagrams the answers affect: new or renamed stories, actors, entities, or statuses; changed dependencies or transitions; renamed terms (rename them everywhere). Move every item a clarification resolved out of `## Gaps` and into its diagram, and delete `## Gaps` once it is empty.
   - **Include rules still apply**: add the Entity Relationship Map if the spec now has Key Entities, and the Status Lifecycle if it now describes one. Remove either section if the spec no longer supports it. Renumber the remaining diagrams consecutively.
   - **File missing** (spec written by an older plugin version): create it with the diagrams `/akka:specify` produces, but only if the spec has the user stories and actors that diagrams 1 and 2 need; otherwise do not create it and report what is missing. Start the file with `# Spec Visualize: [FEATURE]` and a `**Feature**: [FEATURE] | **Spec**: [link to spec.md]` line, then write numbered `## N. <Diagram>` sections, each holding one `mermaid` code block:
     - **User Journey Map** (`flowchart TD`): one rounded node per story, P1 at top, dependency arrows labelled with why. Fill P1 `#2196F3`, P2 `#FF9800`, P3+ `#4CAF50`.
     - **Actor–Goal Overview** (`flowchart LR`): rounded actor nodes in an "Actors" subgraph (human actors `#4CAF50`) linked to rectangle goal nodes in a "System" subgraph (`#2196F3`).
     - **Entity Relationship Map** (`flowchart TD`, include rules above): one rounded node per entity, unfilled, edges labelled with the relationship and any cardinality the spec states. No fields or types.
     - **Status Lifecycle** (`flowchart TD`, include rules above): statuses exactly as named, transitions labelled with their trigger. Entry `#2196F3`, intermediate `#FF9800`, review/decision `#9C27B0`, terminal success `#4CAF50`, terminal failure `#F44336`, error `#B71C1C`.
     - Use white text (`color:#fff`) on filled nodes, and only the colors whose categories occur in the feature. Show external systems in an "External / Out of Scope" subgraph styled `stroke-dasharray:5 5,stroke:#999,fill:#f5f5f5,color:#333`, connected with `-.->`. List items whose markers are still open under a final `## Gaps` section.
   - Diagrams stay non-technical and use the spec's own terms. Wrap every node label in double quotes (`S1(["P1: Checkout (guest)"])`) so parentheses, brackets or `#` in spec terms do not break the Mermaid parser. Never draw an item (story, actor, goal, entity, relationship, status or transition) whose [NEEDS CLARIFICATION] marker is still open; it stays under `## Gaps`.

9. Report completion (after questioning loop ends or early termination):
   - Number of questions asked & answered.
   - Path to updated spec.
   - Sections touched (list names).
   - Path to `spec-visualize.md` and the diagrams redrawn, added, or removed (or "unchanged").
   - Coverage summary table listing each taxonomy category with Status: Resolved (was Partial/Missing and addressed), Deferred (exceeds question quota or better suited for planning), Clear (already sufficient), Outstanding (still Partial/Missing but low impact).
   - If any Outstanding or Deferred remain, recommend whether to proceed to `/akka:plan` or run `/akka:clarify` again later post-plan.
   - Suggested next command. If policy-decision markers remain, recommend `/akka:clarify` again, not `/akka:plan`.

Behavior rules:

- Policy-decision markers (thresholds, access permissions, retention, sensitive-data rules, approvals) are not subject to the specify marker limit: put them first in the question queue and never infer an answer. Any not reached within the 5-question limit stay as markers for the next run.
- If no meaningful ambiguities found (or all potential questions would be low-impact), respond: "No critical ambiguities detected worth formal clarification." and suggest proceeding.
- If spec file missing, instruct user to run `/akka:specify` first (do not create a new spec here).
- Never exceed 5 total asked questions (clarification retries for a single question do not count as new questions).
- Avoid speculative tech stack questions unless the absence blocks functional clarity.
- Respect user early termination signals ("stop", "done", "proceed").
- If no questions asked due to full coverage, output a compact coverage summary (all categories Clear) then suggest advancing.
- If quota reached with unresolved high-impact categories remaining, explicitly flag them under Deferred with rationale.

Context for prioritization: $ARGUMENTS

## Done When

- [ ] The active FEATURE_DIR and FEATURE_SPEC were resolved via `akka_sdd_list_specs` (or the user was told to run `/akka:specify` first).
- [ ] A structured ambiguity & coverage scan was performed across every taxonomy category with a Clear / Partial / Missing status.
- [ ] No more than 5 questions were asked in total; each was answerable with a short multiple-choice selection or a `<=5`-word short answer.
- [ ] Each accepted answer produced exactly one bullet under `## Clarifications` → `### Session YYYY-MM-DD` and was integrated into the correct target section (Functional Requirements, User Stories, Data Model, Non-Functional / Quality Attributes, Edge Cases, or terminology).
- [ ] Any earlier statement invalidated by a clarification was replaced, not duplicated.
- [ ] The spec file was saved to FEATURE_SPEC after each integration and passes validation (no lingering vague placeholders the new answer was meant to resolve; markdown structure valid; only allowed new headings added).
- [ ] If any clarification was integrated, `FEATURE_DIR/spec-visualize.md` was updated (or created if missing) to match the spec — or, if it was missing and the spec lacked the stories and actors for diagrams 1 and 2, it was not created and what was missing was reported. In a written file, resolved items were moved out of Gaps into their diagrams, the optional diagrams follow the include rules, and no item with an open marker is drawn.
- [ ] The final report listed questions asked/answered, sections touched, the spec-visualize.md changes, a coverage summary (Resolved / Deferred / Clear / Outstanding), and the suggested next command.
