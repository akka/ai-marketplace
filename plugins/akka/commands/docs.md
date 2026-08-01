---
description: Generate or refresh rendered project documentation, then verify it against the content-governance exit-condition family (language, completeness, tone).
handoffs:
  - label: Re-run Conformance
    agent: akka.specify
    prompt: Re-check the build against all exit conditions and report the plain summary.
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Purpose

`/akka:docs` is a generator. It writes and refreshes the project's rendered
documentation under `docs/`, then hands that output to the content-governance
exit-condition family that verifies it. Documentation is a surface class in the
single coverage gate: every documentable thing needs a page, the same way every
code module needs a covering check. Generation lives here in the assistant; the
engine verifies the deterministic conditions and records the attestation for the
one condition it cannot decide.

## When it runs

`/akka:docs` is primarily an À la carte command. The developer invokes it
directly when they want to (re)generate the project's rendered documentation
and see how the content-governance exit conditions decided. In Enforced mode
the assistant runs the same activity autonomously as part of its build loop,
whenever CONTENT-LANGUAGE, Completeness, or CONTENT-TONE is `open` and the
assistant can act on it. In both modes the behavior is identical; only
ship-gating differs.

## Outline

1. **Enumerate the documentable things.** Collect what the project can document
   from observable sources — the a-la-carte commands, the active exit conditions,
   the public API endpoints detected in the tree. This enumerable set is the
   completeness target.

2. **Load the fixed template.** Read
   `plugins/akka/templates/docs-template.html` from the akka plugin. This file
   is the fixed design contract for `/akka:docs`: it contains the full CSS,
   the full HTML skeleton, the header, the stats grid, the collapsible
   diagram and component sections, the SVG scaffolding for the interaction
   diagram, and the layered scaffolding for the component graph. Every
   generated `docs/index.html` uses this template verbatim — the assistant
   MUST NOT modify the CSS, the layout, the fonts, the colors, or any other
   design detail. Customers do not override the design; the template is the
   design.

3. **Fill the placeholders and paste the fragments.** The template contains
   two kinds of insertion points:

   - **Single-value placeholders**: `{{TITLE}}`, `{{LEAD}}`,
     `{{STAT_COMPONENTS}}`, `{{STAT_EVENTS}}`, `{{STAT_ENDPOINTS}}`,
     `{{STAT_VIEWS}}`, `{{STAT_DOMAIN_OBJECTS}}`, `{{ENTITY_HINT}}`,
     `{{INTERACTION_HINT}}`, `{{COMPONENT_GRAPH_HINT}}`,
     `{{FOOTER_TARGET}}`. Fill each with the project-specific value.

   - **Region placeholders**: `{{ENTITY_BOXES}}`, `{{INTERACTION_SVG_BODY}}`,
     `{{COMPONENT_GRAPH_LAYERS}}`, `{{COMPONENT_REFERENCE}}`. The template
     shows each region's fragment shapes as HTML comments directly above the
     placeholder. Copy the fragment verbatim for every entity / domain object
     / component / lane / message and fill only the identifier and field
     values. Do not restyle. Do not restructure.

   Component-kind coloring is fixed by the CSS classes (`ese`, `kve`, `view`,
   `wf`, `agent`, `ep`, `ext`). Choose the class that matches the component's
   Akka type; the accent color follows automatically.

4. **Write `docs/index.html`.** After filling every placeholder, write the
   result to `docs/index.html` in the project directory. The file is
   self-contained — no external JavaScript, no external CSS, no build step
   needed to view — so it can be opened directly in a browser or served from
   any static host.

5. **Pages for enumerated documentable things beyond the four rendered
   artifacts.** For every à-la-carte command, active exit condition, and
   detected public endpoint that is not already covered by the four
   rendered artifacts, append a matching `<details class="sec">` section to
   the `{{COMPONENT_REFERENCE}}` region using the same fragment shape shown
   in the template. Follow the project's terminology; the deterministic
   checks below verify it.

6. **Verify against the content-governance family.** Run the three conditions and
   report each. Each has a default ship tier:

   - **CONTENT-LANGUAGE (deterministic, ship tier: author).** The Vale prose linter
     over `docs/` using the project's `.vale.ini` (generated into `/harnesses/content/`
     by `/akka:harnesses`). It decides the falsifiable rules: banned phrasings
     absent, mandated substitutions honored, terminology correct, and the
     structural conventions — required sections present, heading conventions
     followed. This is an introspective check: shell out to Vale, map a non-zero
     exit to `red`. On a machine without Vale the condition is `open` with reason
     `blocked-outside-project` and Vale named as the missing tool, never a false
     `red`. The author-tier default means this check runs on every ship — Vale is
     fast enough to be a per-commit gate.

   - **Completeness (the coverage gate, ship tier: author).** Every documentable
     thing enumerated in step 1 has a page on disk. A documentable thing with no
     page reds the gate. Completeness is not a separate command — it is the
     documentation surface class inside the single coverage gate. A thing
     intentionally left undocumented is a recorded waiver with a reason, not a
     silent omission. The author-tier default means every ship verifies that no
     documentable thing has been left without a page.

   - **CONTENT-TONE (delegated, ship tier: review).** The holistic dimension a
     linter cannot reduce to a token list — state a fact, not a flourish;
     declarative, not persuasive; reads like a person. Do not score prose 1-to-5;
     that rubber-stamps. Apply the project's decomposed rubric as single-criterion
     pass/fail predicates, framed adversarially ("find every place this reads like
     marketing"). When the pages pass, call `akka_harness_attest` with the tone
     condition key and a receipt reference. The attestation is keyed to a
     content-plus-rubric signature, so a rule change or an edit invalidates it and
     the condition returns to `open` with reason `needs-user-action` until re-run.
     The engine records that the judge ran and covered the current content; it
     never scores the prose itself. The review-tier default means CONTENT-TONE is
     verified before the change is opened for team review, not on every commit —
     re-attesting every time a source file changes would be excessive.

7. **Report.** Call `akka_ec_conform`, then present `akka_ec_summary` to the user
   **verbatim** — the plain outcome. Do NOT restate internal condition ids or the
   words "auditor" / "coverage gate". Offer *"say 'show details' for the full
   checklist"* for the manifest.

## Key rules

- The engine never calls a model. The deterministic language check delegates to
  Vale; completeness is a page-exists test; only the tone judgment runs here in
  the assistant, and it reaches the engine as an attestation, not a score.
- Nothing false-passes. A missing page reds the coverage gate; a banned phrasing
  reds the language check; tone with no attestation stays `open` with reason
  `needs-user-action`.
- Same behavior in both modes. The generator and the three conditions exist in
  À la carte and Enforced mode alike. Only ship-gating differs: advisory in
  À la carte, blocking in Enforced.

## Done When

- [ ] The documentable things (commands, active exit conditions, detected endpoints) were enumerated as the completeness target.
- [ ] A page was generated or refreshed under `docs/` for each documentable thing, following the project's structural and terminology conventions.
- [ ] CONTENT-LANGUAGE ran Vale over `docs/` with the project's `.vale.ini` and reported `green`/`red` (or `open` with reason `blocked-outside-project` where Vale is unavailable — never a false `red`).
- [ ] Completeness was checked as the documentation surface class of the coverage gate; any undocumented thing reds the gate or was recorded as a waiver with a reason.
- [ ] CONTENT-TONE applied the decomposed adversarial rubric as pass/fail predicates and, on pass, was attested via `akka_harness_attest` with the condition key and a receipt reference — never left as a numeric score.
- [ ] `akka_ec_conform` was called and the plain `akka_ec_summary` (never internal ids or the word "auditor") was shown to the user.
