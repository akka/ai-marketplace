---
description: Create or update the feature specification from a natural language feature description.
handoffs:
  - label: Build Technical Plan
    agent: akka.plan
    prompt: Create a plan for the spec. I am building with...
  - label: Clarify Spec Requirements
    agent: akka.clarify
    prompt: Clarify specification requirements
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Before anything else

This command keeps a run in the idea's record when the akka CLI has one: the
`akka_run_start` MCP tool is available, or the output of `akka specify run start
--help` contains `--station`. A CLI without it predates the idea record. With
such a CLI, say so once and carry this command out as before: skip every step
marked **Idea record**, and open no run.

**Idea record: a console run.** Call the `akka_run_context` MCP tool first when
it is available: it answers `{ console, idea, station, run, spec, topic,
questions }`, and `console: true` means the console started this command. Only
without that tool, the console started it when `AKKA_RUN_ID` is set in its
environment, or when the command has no shell to run the akka CLI in. The
console has already opened the run and enforced the rules for it, so in a
console run the run is open from the first step: its id is the `run`
`akka_run_context` answered. Any stop before the normal close, such as a
mode-check refusal, a missing argument, or a check that needs a tool this run
lacks, closes it with `akka_run_close`, that `run`, `outcome: failed` and the
reason. So in a console run: the feature is `akka_run_context`'s `spec` (for
`/akka:discover`, the topic is its `topic`), and the command never searches for
one; skip every step that finds, adopts, starts or links an idea, and never ask
a person a question: wherever this command would ask one, it closes the run with
`outcome: waiting` and `question` set to the question (`--outcome waiting
--question "<question>"` on the CLI); the owner answers in the console, and the
re-run reads the answer from `akka_run_context`'s `questions` (`{station, run,
question, answer}`) and does not ask it again; run the mode check with `--idea`
set to the `idea` `akka_run_context` answered, and skip it when it cannot run
here or no idea is known; open the run by calling `akka_run_start` with
`command` and `args` only, no `idea` and no `station`, and the CLI joins the
console's run; close it as usual; and skip the carry-on step, because the
console moves the idea on. A run with no shell for the akka CLI that
`akka_run_context` answers `console: false` for is not a console run and keeps
no record: open no run, ask nothing about ideas or lanes, and carry the command
out as before the idea record, skipping every step marked **Idea record**.

**Idea record: specify in a console run.** Present no clarification questions:
leave the `[NEEDS CLARIFICATION]` markers in the spec for
`/akka-specify:clarify`, and the console shows them as waits. Close the run as
usual.

The record names each station command by its `akka` plugin name, so this
plugin's commands open their runs under `/akka:` names.

## Outline

The text the user typed after `/akka-specify:specify` in the triggering message **is** the feature description. Assume you always have it available in this conversation even if `$ARGUMENTS` appears literally below. Do not ask the user to repeat it unless they provided an empty command.

Given that feature description, do this:

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

2e. **Idea record: start the idea and open the run.** In a console run, skip the idea steps here and open the run by calling `akka_run_start` with `command: /akka:specify` and `args` only; the CLI joins the console's run, and its close links the spec from the outputs. On a laptop run, Discover is optional in every mode, so a new idea may start here. `/akka:specify` always records against a new idea or the idea of the discovery topic this feature continues, never an idea found from the git branch. Below, `<NNN-name>` is FEATURE_DIR's folder name. When the feature continues a discovery topic (the person names it, or the spec rests on its findings), look for that topic's idea in `akka specify idea list --json`: the idea whose `topic` is the topic's folder name and whose `spec` is null. When that idea has `derived: true`, it has no record yet: adopt it with `akka specify ideas adopt --idea <id>`, then use it. If there is one, link it to this spec with `akka specify idea link --idea <idea> --spec <NNN-name>`. Otherwise start a new idea: ask the person how it ships, Deploy to Akka (`akka`) or Commit to internal systems (`internal`), with your suggestion, then run `akka specify idea new --spec <NNN-name> --lane <lane> "<words>"` with the feature description as its words, quoted as one argument. When the adopt, `idea link` or `idea new` fails, in Enforced mode (`akka specify mode`) stop with the CLI's message; otherwise open no run, say in one line that this run is not recorded, and continue. Then open the run against that idea: call the `akka_run_start` MCP tool with `station: specify`, `command: /akka:specify`, `idea` set to it and `args` set to the user input. Where the tool is not available, run `akka specify run start --station specify --command /akka:specify --idea <idea> --args "<the user input>" --json`, with the input quoted as one argument. It answers JSON: `recorded`, and for a recorded run its `idea` and `run.id`. Keep both: the closing steps use them. When it answers `recorded: false`, continue without a run, and say in one line that this run is not recorded, with its `reason`. A refusal by rule is an error whose JSON is `{refused, message, remedy}`, `refused` naming the rule: `paused`, `limit`, `shipped`, `dropped`, `approval`, `order`, `no-idea-enforced`, `idea-unresolved` or `console-run`. Print `message` and `remedy` verbatim and stop. Any other error, one without `refused` (such as no login), does not stop the command: continue without a run, and say in one line that this run is not recorded. Once the run is open, every way the command ends closes it. When the work fails (a build or tests fail, or a step stops the command early), call `akka_run_close` with `run`, `outcome: failed` and `error` set to what failed, in one line, then stop. Where the tool is not available, run `akka specify run close --run <id> --outcome failed --error "<what failed>"`. When the person stops the command, close the run with `outcome: stopped`. This holds in a console run too. The closing steps are for the work's normal end.

3. Load `akka_sdd_get_template` to understand required sections.

4. Follow this execution flow:

    1. Parse user description from Input
       If empty: ERROR "No feature description provided"
    2. Extract key concepts from description
       Identify: actors, actions, data, constraints
    3. For unclear aspects:
       - Make informed guesses based on context and industry standards
       - Only mark with [NEEDS CLARIFICATION: specific question] if:
         - The choice significantly impacts feature scope or user experience
         - Multiple reasonable interpretations exist with different implications
         - No reasonable default exists
       - **LIMIT: Maximum 3 [NEEDS CLARIFICATION] markers total**
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

      ## Notes

      - Items marked incomplete require spec updates before `/akka-specify:clarify` or `/akka-specify:plan`
      ```

   b. **Run Validation Check**: Review the spec against each checklist item:
      - For each item, determine if it passes or fails
      - Document specific issues found (quote relevant spec sections)

   c. **Handle Validation Results**:

      - **If all items pass**: Mark checklist complete and proceed to step 6

      - **If items fail (excluding [NEEDS CLARIFICATION])**:
        1. List the failing items and specific issues
        2. Update the spec to address each issue
        3. Re-run validation until all items pass (max 3 iterations)
        4. If still failing after 3 iterations, document remaining issues in checklist notes and warn user

      - **If [NEEDS CLARIFICATION] markers remain**:
        1. Extract all [NEEDS CLARIFICATION: ...] markers from the spec
        2. **LIMIT CHECK**: If more than 3 markers exist, keep only the 3 most critical (by scope/security/UX impact) and make informed guesses for the rest
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

7. Report completion with branch name, spec file path, checklist results, and readiness for the next phase (`/akka-specify:clarify` or `/akka-specify:plan`).

8. **Close the run.** If a run was opened, call the `akka_run_close` MCP tool with `run` set to its id and `outputs` set to SPEC_FILE and `FEATURE_DIR/checklists/requirements.md` as project-relative paths. Where the tool is not available, run `akka specify run close --run <id>` with one `--file <path>` for each output. On an error, print its message; the spec already written stands.

9. **Idea record: end waiting for the owner's approval.** When a run was opened, the spec now waits for the owner's approval before the next station runs. Say so and, when a run was opened, say how to give it: on the idea in the console's Ideas page, or `akka specify idea approve <idea> spec`, where `<idea>` is the idea `akka_run_start` named. Do not carry out `/akka-specify:plan` or any later station; name `/akka-specify:clarify` or `/akka-specify:plan` as the command for after the approval. Without a run, name the next command and stop.

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
3. **Limit clarifications**: Maximum 3 [NEEDS CLARIFICATION] markers - use only for critical decisions that:
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

- Data retention: Industry-standard practices for the domain
- Performance targets: Standard web/mobile app expectations unless specified
- Error handling: User-friendly messages with appropriate fallbacks
- Authentication method: Standard session-based or OAuth2 for web apps
- Integration patterns: Use project-appropriate patterns (REST/GraphQL for web services, function calls for libraries, CLI args for tools, etc.)

### Success Criteria Guidelines

Success criteria must be:

1. **Measurable**: Include specific metrics (time, percentage, count, rate)
2. **Technology-agnostic**: No mention of frameworks, languages, databases, or tools
3. **User-focused**: Describe outcomes from user/business perspective, not system internals
4. **Verifiable**: Can be tested/validated without knowing implementation details

**Good examples**:

- "Users can complete checkout in under 3 minutes"
- "System supports 10,000 concurrent users"
- "95% of searches return results in under 1 second"
- "Task completion rate improves by 40%"

**Bad examples** (implementation-focused):

- "API response time is under 200ms" (too technical, use "Users see results instantly")
- "Database can handle 1000 TPS" (implementation detail, use user-facing metric)
- "React components render efficiently" (framework-specific)
- "Redis cache hit rate above 80%" (technology-specific)
