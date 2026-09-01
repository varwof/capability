# Standard MCP Tool-Access Capability Reference

> scheme_id: `std/mcp-v1` · Version `1.0.0` · Vendor `std` / Product `mcp-v1`

Standard semantics for AI-agent access to Model Context Protocol servers:
only allowlisted tools may be called, per the capability parameters bound in
the AIC.

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
- **parameters**: `tools` (array, required, allowlist),
  `max_requests_per_minute` (integer >= 1).
