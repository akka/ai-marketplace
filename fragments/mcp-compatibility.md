# MCP Tool Compatibility

The akka-specify plugin commands depend on MCP tools served by the Akka CLI.
The set of available tools depends on the installed CLI version.

Compatibility is checked once during `/akka.setup` (Phase 10). If tools are
missing, the user is told to upgrade the CLI and restart their AI session.

## Required tools

### SDD workflow
- `akka_sdd_init`
- `akka_sdd_constitution`
- `akka_sdd_list_specs`
- `akka_sdd_create_spec`
- `akka_sdd_get_template`

### Build & test
- `akka_maven_compile`
- `akka_maven_test`
- `akka_maven_verify`
- `akka_build_image`

### Local development
- `akka_local_start`
- `akka_local_stop`
- `akka_local_run_service`
- `akka_local_stop_service`
- `akka_local_status`
- `akka_local_logs`
- `akka_local_request`

### Platform deployment
- `akka_services_deploy`
- `akka_services_get`
- `akka_services_logs`
- `akka_push_image`
- `akka_organizations_list`
- `akka_projects_list`
- `akka_projects_create`
- `akka_hostnames_list`
- `akka_hostnames_add`
- `akka_routes_list`
- `akka_routes_create`

### Git
- `akka_git_status`
- `akka_git_create_branch`
- `akka_git_add`
- `akka_git_commit`
- `akka_git_checkout`
- `akka_git_merge`
