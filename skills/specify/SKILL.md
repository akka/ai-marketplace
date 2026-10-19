---
name: specify
description: "Create or update the feature specification from a natural language feature description."
---

## User Input

You **MUST** consider the user input before proceeding (if not empty).

## Outline

The text the user typed after `/akka:specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `the user's request` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

0. **Prerequisite check**: Before doing anything else, verify the environment is ready:
   - Call `akka_sdd_list_specs` — if this MCP tool is not available, the Akka MCP server is not configured. Stop and tell the user: *"The Akka MCP server is not running. Run `/akka:setup` first to configure your project, or run `akka specify init .` from the terminal."*
   - Check if the current directory has a `pom.xml` or `.akka/` directory. If neither exists, warn: *"This doesn't look like an Akka project directory. Run `/akka:setup` to scaffold a new project, or `cd` into an existing one."*
   - If both checks pass, proceed.

1. **Generate a concise short name** (2-4 words) for the branch:
   - Analyze the feature description and extract the most meaningful keywords
   - Create a 2-4 word short name that captures the essence of the feature
   - Use action-noun format when possible (e.g., "add-user-auth", "fix-payment-bug")
   - Preserve technical terms and acronyms (OAuth2, API, JWT, etc.)
   - Keep it concise but descriptive enough to understand the feature at a glance
   - Examples:
     - "I want to add user authentication" → "user-auth"
     - "Implement OAuth2 integration for the API" → "oauth2-api-integration"
     - "Create a dashboard for analytics" → "analytics-dashboard"
     - "Fix payment processing timeout bug" → "fix-payment-timeout"

2. **Check for existing branches before creating new one**:

   a. First, fetch all remote branches to ensure we have the latest information.

   b. Find the highest feature number across all sources for the short-name:
      - Remote branches: `git ls-remote --heads origin | grep -E 'refs/heads/[0-9]+-<short-name>$'`
      - Local branches: `git branch | grep -E '^[* ]*[0-9]+-<short-name>$'`
      - Specs directories: Check for directories matching `specs/[0-9]+-<short-name>`

   c. Determine the next available number:
      - Extract all numbers from all three sources
      - Find the highest number N
      - Use N+1 for the new branch number

   d. Call the `akka_sdd_create_spec` MCP tool with feature_name set to a short, hyphenated name derived from the user's feature description (e.g. "user-authentication"). The tool creates a numbered feature directory under the specs directory, initializes spec.md from the template, and returns the path. Use this path as FEATURE_SPEC and its parent directory as FEATURE_DIR.
      - Pass `number` (N+1) and `short_name` parameters along with the feature description

   **IMPORTANT**:
   - Check all three sources (remote branches, local branches, specs directories) to find the highest number
   - Only match branches/directories with the exact short-name pattern
   - If no existing branches/directories found with this short-name, start with number 1
   - The tool output will contain BRANCH_NAME and SPEC_FILE paths

3. Load `akka_sdd_get_template` to understand required sections.

4. Follow this execution flow:

    1. Parse user description from Input
       If empty: ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
       For agent features, apply the conditional "Agent behavior, protection, and evaluation requirements" guidance below.
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers in the spec**; list any further unresolved policy decisions under "Open policy decisions" in the checklist notes, to be resolved with `/akka:clarify`.
       - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details
    4. Fill User Scenarios & Testing section
       If no clear user flow: ERROR "Cannot determine user scenarios"
    5. Generate Functional Requirements
       Each requirement must be testable
       Use reasonable defaults for unspecified details (document assumptions in Assumptions section)
    6. Define Success Criteria
       Create measurable, technology-agnostic outcomes
       Include both quantitative metrics (time, performance, volume) and qualitative measures (user satisfaction, task completion)
       Each criterion must be verifiable without implementation details
    7. Identify Key Entities (if data involved)
    8. Return: SUCCESS (spec ready for planning)

5. Write the specification to SPEC_FILE using the template structure, replacing placeholders with concrete details derived from the feature description (arguments) while preserving section order and headings.

6. **Specification Quality Validation**: After writing the initial spec, validate it against quality criteria:

   a. **Create Spec Quality Checklist**: Generate a checklist file at `FEATURE_DIR/checklists/requirements.md` using the checklist template structure with these validation items:

      ```markdown
      # Specification Quality Checklist: [FEATURE NAME]

      **Purpose**: Validate specification completeness and quality before proceeding to planning
      **Created**: [DATE]
      **Feature**: [Link to spec.md]

      ## Content Quality

      - [ ] No implementation details (languages, frameworks, APIs)
      - [ ] Focused on user value and business needs
      - [ ] Written for non-technical stakeholders
      - [ ] All mandatory sections completed

      ## Requirement Completeness

      - [ ] No [NEEDS CLARIFICATION] markers remain
      - [ ] Requirements are testable and unambiguous
      - [ ] Success criteria are measurable
      - [ ] Success criteria are technology-agnostic (no implementation details)
      - [ ] All acceptance scenarios are defined
      - [ ] Edge cases are identified
      - [ ] Scope is clearly bounded
      - [ ] Dependencies and assumptions identified

      ## Feature Readiness

      - [ ] All functional requirements have clear acceptance criteria
      - [ ] User scenarios cover primary flows
      - [ ] Feature meets measurable outcomes defined in Success Criteria
      - [ ] No implementation details leak into specification

      ## Open policy decisions

      - [ ] OPD-1: <decision to obtain> (affects: <requirement or area>).

      ## Notes

      - Open policy decisions are tracked separately from quality-check pass/fail results. Resolve them with `/akka:clarify` before declaring readiness for `/akka:plan`.
      - Other incomplete quality items require spec updates; clarification markers and open policy decisions do not prevent invoking `/akka:clarify`.
      ```

   **Open policy decision format**: Use the exact `## Open policy decisions` heading in `FEATURE_DIR/checklists/requirements.md`. Each unresolved entry is `- [ ] OPD-1: <decision> (affects: <requirement or area>).` Allocate stable, unique `OPD-<number>` IDs within the feature; preserve them across runs and do not reuse or renumber them. On resolution, retain the entry as `- [x] OPD-1: <decision> (affects: <requirement or area>). → resolved in spec: [<section>](../spec.md#<section-anchor>)`. Record the answer in that spec section before checking the entry. Omit the example placeholder entry when there are no decisions; never remove real unresolved entries when regenerating the checklist. Other skills use this same format. If an existing entry has no checkbox or an invalid resolution reference, preserve it as unresolved until reconciled; do not silently treat it as resolved.

   b. **Run Validation Check**: Review the spec against each quality checklist item outside `## Open policy decisions`:
      - For each item, determine if it passes or fails
      - Document specific issues found (quote relevant spec sections)

   c. **Handle Validation Results**:

      - **If all quality items pass**: Mark those quality items complete. Check open policy decisions separately: if any remain unchecked, preserve them and recommend `/akka:clarify`, not readiness for planning.

      - **If quality items fail (excluding [NEEDS CLARIFICATION] and the entire Open policy decisions section)**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep markers only for the 3 most critical (by scope/security/UX impact). Resolve routine details with documented assumptions. Do not guess unresolved policy decisions: list them under "Open policy decisions" in `checklists/requirements.md` and recommend `/akka:clarify`, not `/akka:plan`; do not declare the spec ready while any remain open.
        3. For each clarification needed (max 3), present options to user in this format:

           ```markdown
           ## Question [N]: [Topic]

           **Context**: [Quote relevant spec section]

           **What we need to know**: [Specific question from NEEDS CLARIFICATION marker]

           **Suggested Answers**:

           | Option | Answer | Implications |
           |--------|--------|--------------|
           | A      | [First suggested answer] | [What this means for the feature] |
           | B      | [Second suggested answer] | [What this means for the feature] |
           | C      | [Third suggested answer] | [What this means for the feature] |
           | Custom | Provide your own answer | [Explain how to provide custom input] |

           **Your choice**: _[Wait for user response]_
           ```

        4. **CRITICAL - Table Formatting**: Ensure markdown tables are properly formatted:
           - Use consistent spacing with pipes aligned
           - Each cell should have spaces around content: `| Content |` not `|Content|`
           - Header separator must have at least 3 dashes: `|--------|`
           - Test that the table renders correctly in markdown preview
        5. Number questions sequentially (Q1, Q2, Q3 - max 3 total)
        6. Present all questions together before waiting for responses
        7. Wait for user to respond with their choices for all questions (e.g., "Q1: A, Q2: Custom - [details], Q3: B")
        8. Update the spec by replacing each [NEEDS CLARIFICATION] marker with the user's selected or provided answer
        9. Re-run validation after all clarifications are resolved

   d. **Update Checklist**: After each validation iteration, update the checklist file with current pass/fail status

7. Report completion with branch name, spec file path, checklist results, and readiness for the next phase (`/akka:clarify` or `/akka:plan`).

**NOTE:** The script creates and checks out the new branch and initializes the spec file before writing.

## General Guidelines

## Quick Guidelines

- Focus on **WHAT** users need and **WHY**.
- Avoid HOW to implement (no tech stack, APIs, code structure).
- Written for business stakeholders, not developers.
- DO NOT create any checklists that are embedded in the spec. That will be a separate command.

### Section Requirements

- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation

When creating this spec from a user prompt:

1. **Make informed guesses**: Use context, industry standards, and common patterns to fill gaps
2. **Document assumptions**: Record reasonable defaults in the Assumptions section
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers; list further unresolved policy decisions under "Open policy decisions" in the checklist notes for `/akka:clarify`. Use markers only for critical decisions that:
   - Significantly impact feature scope or user experience
   - Have multiple reasonable interpretations with different implications
   - Lack any reasonable default
4. **Prioritize clarifications**: scope > security/privacy > user experience > technical details
5. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
6. **Common areas needing clarification** (only if no reasonable default exists):
   - Feature scope and boundaries (include/exclude specific use cases)
   - User types and permissions (if multiple conflicting interpretations possible)
   - Security/compliance requirements (when legally/financially significant)

**Examples of reasonable defaults** (don't ask about these):

- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: Use project-appropriate patterns (REST/GraphQL for web services, function calls for libraries, CLI args for tools, etc.)

### Agent behavior, protection, and evaluation requirements

Apply this guidance only when the feature involves agents or model-generated behavior. Use the description, existing service requirements, policies, and configuration to answer these questions first; ask only where a missing decision affects scope or acceptance. Do not add controls or a governance workflow merely because an agent exists.

- **Enforcement boundaries**: Identify what must be checked before sending input to a model, executing a tool, or delivering a reply. State whether a violation blocks the operation, transforms data, or is recorded for review. Define behavior when the check fails to run or cannot reach a decision.
- **Streaming**: Establish whether replies must stream immediately or pass a complete-response check before delivery. Surface conflicting requirements: a check after delivery cannot prevent disclosure of content already streamed.
- **Sensitive data**: Identify the data to protect, the agents in scope, and the relevant destinations: model input, tool results, logs, or external responses. Specify the required transformation or restriction for each; do not assume one sanitizer covers every boundary or historical records.
- **Retrospective evaluation**: Define the quality criteria, which interactions to assess, whether failed interactions are included, the required coverage or sampling, and the expected response to adverse findings. An assessment after completion cannot prevent the action it assesses.
- **Decision policy**: Where classification informs behavior, define the meaning of labels or scores, the decision criteria, and handling of uncertainty, invalid output, or classifier failure. Distinguish the classification signal from the action taken on it.
- **Access control**: Establish which users, services, and components may invoke each operation. Distinguish component identity, end-user permissions, and tool authorization, including resource and purpose restrictions where required.
- **Evidence**: Define which decisions and assessments must be traceable and which identifiers, policy/model versions, and outcomes are needed for investigation, subject to the data-handling requirements.

Keep requirements focused on observable behavior and free of Akka SDK interfaces or component names. Record constraints stated by the user (existing implementations, required Akka SDK version) under Assumptions; `/akka:plan` selects the mechanisms.

**Policy decisions are not reasonable defaults.** Do not invent consequential classification thresholds, access permissions, retention periods, sensitive-data rules, or approval requirements. Reuse established requirements when available; otherwise obtain the missing decision. The three-marker limit does not cap the number of unresolved policy decisions; track the rest as open policy decisions. Do not mark readiness while such decisions remain open.

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

For probabilistic model behavior, define acceptance over an agreed, representative dataset with repeated trials, measurable error limits, and a stated aggregation rule. Include adverse and uncertain cases where relevant. Use stakeholder-approved targets; one passing example or a model's self-reported confidence does not establish quality. Leave the choice of verification tooling to Plan.

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"
- "Across the approved support dataset and repeated trials, the rate of harmful replies remains below the agreed limit while benign requests meet the agreed acceptance rate."

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)

## Exit conditions and the feedback loop

Akka Specify turns requirements into machine-checked **exit conditions**, each backed by a **check** that delegates to the ecosystem's own tooling. In Enforced mode the engine will not let the build advance until every check passes and has been reviewed. In À la carte mode every check is advisory — the user always sees the full picture and the run never blocks on a failing condition.

**Check first whether this loop applies at all.** Run `akka specify mode`. In À la carte mode the exit-condition set is dormant until the developer asks for it, and the whole of this section is then **skipped**: capture nothing, create no auditors, call no `akka_ec_*` tool, and do not report a verdict. Treat `/akka:specify` as spec-and-plan work and nothing more. The dormant state is not a gap to close and not something to talk the user into — mention exit conditions only if they ask what else is available, and never more than once. If the developer does ask for checks, run `akka specify mode a-la-carte --exit-conditions=honor` and then follow this loop with every result advisory.

When the set is active, on each `/akka:specify <feedback>` turn:

### 1. Capture feedback as exit conditions

For each requirement the feedback expresses:

1. **Classify** — an answer to an open decision (set the value in an existing condition), a new checkable invariant (a new exit condition), a revealed-inadequate check (tighten it), or a one-off/subjective item (do the task, or ask — do not invent a check).
2. **Falsifiability gate** — only create an exit condition if you can state a *binary* pass predicate that is FALSE exactly when the requirement is violated, over an observable signal. If you cannot, ask a clarifying question instead of inventing a meaningless check.
3. **Define the condition** — id, tier, dod_type, a one-line invariant, and how it is checked.
4. **Choose the check by delegation** — prefer the tool that already decides this (`tsc --noEmit`, `mvn compile`/`test`, `go build`, a linter). Author it as a declarative command: `{run: [...], applies_to: {requirement, module}}`. Write bespoke logic only when no tool observes the invariant.
5. **Must not** — do not create a check that always passes, that could pass while the invariant is false, that is subjective without a probe, that is over-broad, or that duplicates an existing condition.
6. Record it with `akka_ec_capture` (the condition as JSON). The check will not run until the human approves it.

### 2. Surface the exit conditions for the human, at the exit-condition level

Present the new/changed exit conditions in plain language — *"I'd like to add these exit conditions,"* each with a one-line description and **how I'll check it** — and ask the human to approve / adjust / skip. Never phrase this as "approve running a command"; it is always about the checks. When the human approves, call `akka_ec_approve` with the condition id.

### 3. Review the checks adversarially

Before finishing a turn (and always before ship), for each check attempt to construct an input where **the check passes while its invariant is false**. If you can, the check is inadequate — fix it or ask. Then call `akka_ec_adequacy_submit` to record the review for the current checks.

### 4. Report plainly

After any feedback, call `akka_ec_conform`, then present `akka_ec_summary` to the user **verbatim** — it is the plain outcome (decisions needed / building / ready). Do NOT restate internal condition ids, check keys, or the words "auditor" / "coverage gate" / "adequacy review". Offer *"say 'show details' for the full checklist"* for the manifest.

### Routing and mode

Once a build is active, treat every reply as feedback and run this loop — the user does not need to prefix `/akka:specify` each time. The gates are state-based, so a reply that is not recorded simply does not advance the build and the pending item re-surfaces (a stall, never a false pass). This capture-and-review logic is identical wherever the exit-condition set is active; Enforced mode additionally blocks on the gates. Where the set is dormant the loop does not run at all, so there are no gates to stall on.

### Companion generators

Two surfaces beyond code have their own generator commands, each paired with an exit-condition family the engine verifies:

- `/akka:harnesses` generates the enterprise-configuration assets (CI, scanning, supply-chain, content style packages) into `/harnesses/` and records them in `.akka/harnesses.lock`. Its family is activated / configured / attested.
- `/akka:docs` generates the rendered documentation under `docs/`. Its family is language, structure, completeness, and tone.

Generation runs in the assistant; the engine detects the surfaces, verifies deterministically, and records the attestations the assistant submits. Both follow the same mode invariant — advisory where the exit-condition set is active in À la carte, blocking in Enforced — so a coverage gap in a harness or a page reds the same single gate as an uncovered code module. Both generators still run while the set is dormant; they simply produce no conditions and no gate.

## Done When

- [ ] The mode was read before any `akka_ec_*` call, and where the exit-condition set was dormant nothing was captured, approved, audited, or reported as a verdict.
- [ ] Where the set was active: any checkable requirement in the feedback was captured as an exit condition + check via `akka_ec_capture`, surfaced for approval at the exit-condition level, and approved via `akka_ec_approve`.
- [ ] Where the set was active: the active checks were reviewed adversarially and `akka_ec_adequacy_submit` was called; the plain `akka_ec_summary` (never internal ids) was shown to the user.
- [ ] A short-name and next feature number were derived by checking remote branches, local branches, and the `specs/` directory; the highest existing N was used and N+1 was passed to `akka_sdd_create_spec`.
- [ ] `akka_sdd_create_spec` created a numbered FEATURE_DIR and returned BRANCH_NAME and SPEC_FILE.
- [ ] The specification was written to SPEC_FILE using the template structure, with all mandatory sections filled and section order preserved.
- [ ] Success Criteria are measurable, technology-agnostic, user-focused, and verifiable.
- [ ] No more than 3 `[NEEDS CLARIFICATION]` markers remain; routine gaps are resolved by documented assumptions, and all other unresolved policy decisions are listed under "Open policy decisions" in the checklist.
- [ ] `FEATURE_DIR/checklists/requirements.md` was created and every quality item outside `## Open policy decisions`, excluding `[NEEDS CLARIFICATION]`, passes (or the user was warned after 3 failed iterations). Open policy entries are excluded from pass/fail validation and retries; their unresolved status is checked separately for readiness.
- [ ] For agent features, relevant protection, evaluation, and failure behavior is specified; open policy decisions prevent a readiness claim and the next-command recommendation is `/akka:clarify`.
- [ ] Completion was reported to the user with branch name, spec file path, checklist results, and the next-command recommendation (`/akka:clarify` or `/akka:plan`).
