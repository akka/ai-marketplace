---
description: Review implemented code for Akka SDK best practices, and optionally against spec, plan, and constitution.
handoffs:
  - label: Fix Issues
    agent: akka.implement
    prompt: Fix the issues found in review
    send: true
  - label: Track Issues
    agent: akka.issues
    prompt: Track the issues found in this review
    send: true
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Review Modes

This review supports two modes:

- **Full review** (default): Reviews the entire project against Akka SDK best
  practices. Runs the complete checklist below. Use this when no specific
  feature is mentioned, or when the user explicitly asks for a project-wide
  review.
- **Feature review**: Reviews the implementation of a specific feature against
  its spec, plan, and constitution, in addition to the best practices
  checklist. Activated when the user names a feature, or when SDD artifacts
  (spec, plan, tasks) exist and the user doesn't explicitly ask for a general
  review.

## Outline

### Steps 1-4: SDD alignment (feature review mode only)

Skip these steps entirely in full review mode.

1. **Setup**: Call `akka_sdd_list_specs` to find the target feature. Load the
   spec, plan, tasks, and checklist.

2. **Load context**: Read the constitution using `akka_sdd_constitution`.
   Understand what patterns and rules must be followed.

3. **Review implementation against spec**:
   - Are all functional requirements implemented?
   - Are all acceptance criteria met?
   - Are there deviations from the spec? If so, are they justified?

4. **Review implementation against constitution**:
   - Apply project-specific principles and rules from the constitution
   - Check that architectural decisions align with documented rationale

### Step 5: Akka SDK best practices checklist (always runs)

Load the review checklist using `akka_sdd_get_template` with template name
`review-checklist`. Walk through every check. For each check, report PASS,
WARN (acceptable deviation with reason), or FAIL (must fix). For WARN and
FAIL items, cite the specific file(s) and line(s).

### Step 6: Runtime verification (optional, either mode)

If the service is running locally (via `/akka:build`), use backoffice tools
with `local=true` to verify that the implementation behaves correctly at
runtime — not just in code:
   - `akka_backoffice_list_components` with `local=true` to confirm all
     expected components are registered
   - `akka_backoffice_list_events` to verify entities emit the expected events
     after commands (compare against spec's event definitions)
   - `akka_backoffice_get_workflow` to verify workflow steps execute in the
     expected order with correct state transitions
   - `akka_backoffice_query_view` to confirm views produce correct query results
   - `akka_backoffice_list_agent_interactions` to review agent tool calls,
     guardrails, and response quality
   - If the service serves a web UI, use `akka_browser_navigate` and
     `akka_browser_screenshot` to capture UI state for visual review

### Step 7: Report

   - **Mode**: state whether this was a full review or a feature review
   - Overall assessment: approved / approved with issues / needs rework
   - Issues found, grouped by severity (CRITICAL first, then RECOMMENDED,
     then DESIGN)
   - Checklist pass rate per section
   - If feature review: spec alignment summary (requirements met vs gaps)
   - Recommendations

## How to Work

- Use file search, grep, and read tools to gather evidence — do NOT assume
  compliance without checking code
- Check a representative sample (3-5 files per category) for pattern-based
  checks
- For one-of-a-kind checks (e.g., "does `definition()` exist"), grep the
  whole codebase
- Be specific: reference file paths and line numbers for every finding
- Every issue must cite the rule it violates (e.g., "violates A3")
- CRITICAL findings are reported as FAIL; RECOMMENDED findings are reported
  as WARN; DESIGN findings are reported as OBSERVATION
- For DESIGN checks, read the domain model, entity state shapes, event types,
  workflow steps, and component interaction patterns holistically — these
  cannot be checked mechanically
- Acknowledge good patterns and practices, not just problems

## Report Format

### Section Scores

```
Section                            | Pass/Total | Severity
A. Serialization & State           | N/3        | CRITICAL
B. Endpoints & Security            | N/2        | CRITICAL
C. Workflows                       | N/3        | CRITICAL
D. Agents                          | N/1        | CRITICAL
E. Views                           | N/3        | CRITICAL
F. Error Handling                  | N/2        | CRITICAL
G. Payload & State Size            | N/4        | CRITICAL
H. Code Quality & Safety           | N/3        | CRITICAL
I. PII & Data Sanitization         | N/4        | CRITICAL
J. Serialization Conventions       | N/4        | RECOMMENDED
K. Architecture & Conventions      | N/7        | RECOMMENDED
L. Endpoint Conventions            | N/6        | RECOMMENDED
M. Workflow & Agent Conventions    | N/9        | RECOMMENDED
N. Consumer & Idempotency          | N/9        | RECOMMENDED
O. Testing Conventions             | N/7        | RECOMMENDED
P. Error Handling Conventions      | N/3        | RECOMMENDED
Q. Design Review                   | N/13       | DESIGN
TOTAL CRITICAL                     | N/25
TOTAL RECOMMENDED                  | N/44
TOTAL DESIGN                       | N/13
```

Note: Skip sections that don't apply (e.g., no gRPC endpoints, no workflows).
Only count applicable checks in the total.

### Findings

Report CRITICAL findings first, then RECOMMENDED, then DESIGN. For each:
```
[ID] FAIL/WARN/OBSERVATION — Description
  Severity: CRITICAL / RECOMMENDED / DESIGN
  File: path/to/file.java, Line: N
  Evidence: <code snippet or grep result>
  Fix/Suggestion: <specific remediation or design alternative>
```

DESIGN items are reported as OBSERVATION with reasoning about the trade-off,
not as simple pass/fail. Explain what the current design implies for
performance or maintainability and suggest alternatives if appropriate.

### All Findings

List ALL findings, not just a top N. Group by severity: all CRITICAL (FAIL)
first, then all RECOMMENDED (WARN), then all DESIGN (OBSERVATION). Within
each severity group, order by impact.
