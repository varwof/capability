# Standard MCP Tool-Access Capability Reference

> scheme_id: `std/mcp-v1` · Version `1.1.0` · Vendor `std` / Product `mcp-v1`

Standard semantics for AI-agent access to Model Context Protocol servers:
only allowlisted tools may be called, per the capability parameters bound in
the AIC. Version 1.1.0 adds per-tool argument constraints (`tool_args` with
`path_prefixes`) and the fail-closed boundary rules below.

## Capability Catalog

| Capability | Summary |
|------|------|
| `tools:call` | Call allowlisted MCP tools |

## Detailed Capability Semantics

### `tools:call`
- **summary**: Invoke only the tools the principal authorized on this MCP
  server.
- **usage**: Agents that operate through an MCP server behind the gateway.
- **when_not**: Dangerous tools (`bash`, `delete`, `admin`) must be excluded
  unless explicitly granted.
- **examples**: `POST /mcp {"method":"tools/call","params":{"name":"read_file","arguments":{...}}}`
- **parameters**:
  - `tools` (array, required, allowlist). An omitted `tools` field stays
    unconstrained; an **empty declared array (`"tools":[]`) is an explicit
    deny** (deny-when-declared).
  - `tool_args` (object, optional): per-tool argument constraints keyed by
    tool name. Currently defined sub-constraint: `path_prefixes` (array of
    path prefixes) for file-path arguments.
  - `max_requests_per_minute` (integer >= 1).

## Fail-Closed Decision Rules

Enforced by the AIC gateway (gateway-core `v0.4.6` or later):

1. `tools/call` without `params.name` is **denied**.
2. A tool not present in the declared allowlist is **denied**.
3. `"tools":[]` denies every `tools/call` (explicit deny-all).
4. Path arguments are cleaned before comparison, and a prefix matches only
   at an exact path or a path-separator boundary. Lexical siblings
   (`/workspace-evil/secret`) and parent traversal (`/workspace/../etc/shadow`)
   are **denied** even when `/workspace` is allowlisted.
5. Unknown scheme/capability or any other out-of-bounds request is
   **denied** (fail-closed).

## Verification Matrix (gateway-core v0.4.6)

| Request | Decision |
|---|---|
| `read_file` with `path=/workspace/src/a.txt` | ALLOW |
| `read_file` with `path=/workspace-evil/secret` | DENY (path boundary) |
| `read_file` with `path=/workspace/../etc/shadow` | DENY (parent traversal) |
| `tools/call` missing `params.name` | DENY |
| `bash` (not allowlisted) | DENY |
| `"tools":[]`, any tool | DENY (explicit deny-all) |
| `initialize` / `ping` / `tools/list` | no `tools/call` decision |
