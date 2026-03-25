---
description: Review implemented code against the spec, plan, and constitution.
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

## Outline

1. **Setup**: Call `akka_sdd_list_specs` to find the target feature. Load the spec, plan, tasks, and checklist.

2. **Load context**: Read the constitution using `akka_sdd_constitution`. Understand what patterns and rules must be followed.

3. **Review implementation against spec**:
   - Are all functional requirements implemented?
   - Are all acceptance criteria met?
   - Are there deviations from the spec? If so, are they justified?

4. **Review implementation against constitution**:
   - Event sourcing: Are events designed as facts? Are handlers pure?
   - Effects API: Are command handlers returning Effects? No side effects?
   - ComponentClient: Used for all cross-component calls?
   - ACLs: Defined on all endpoints?
   - Serialization: `@TypeName` on all state/event classes?
   - Testing: Unit and integration tests present?

5. **Code quality review**:
   - No business logic in endpoints
   - No blocking I/O in handlers
   - No shared mutable state
   - Error handling uses `effects().error()`, not exceptions
   - No fat events (events contain only changed data)

6. **Checklist verification**: Walk through the checklist and mark items as passed or failed.

7. **Report**:
   - Overall assessment: approved / approved with issues / needs rework
   - Issues found (categorized by severity)
   - Checklist completion percentage
   - Recommendations

## Key Rules

- Be specific: reference file paths and line numbers
- Every issue must cite the rule it violates
- Distinguish between must-fix (errors) and should-fix (warnings)
- Acknowledge good patterns and practices, not just problems
