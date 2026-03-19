---
description: Convert existing tasks into actionable, dependency-ordered GitHub issues for the feature based on available design artifacts.
tools: ['github/github-mcp-server/issue_write']
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Outline

1. Call the `akka_sdd_list_specs` MCP tool to find features. Verify that tasks.md exists for the target feature (has_tasks must be true). If tasks.md is missing, instruct the user to run `/akka.tasks` first. Read the tasks.md content from FEATURE_DIR. Also note which other artifacts are available (AVAILABLE_DOCS).
1. Get the Git remote by running:

> [!CAUTION]
> ONLY PROCEED TO NEXT STEPS IF THE REMOTE IS A GITHUB URL

1. For each task in the list, use the GitHub MCP server to create a new issue in the repository that is representative of the Git remote.

> [!CAUTION]
> UNDER NO CIRCUMSTANCES EVER CREATE ISSUES IN REPOSITORIES THAT DO NOT MATCH THE REMOTE URL
