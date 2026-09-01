# LLM API Capability Reference

> scheme_id: `varwof/llm` · Version `1.0.0` · Vendor `varwof` / Product `llm`

Capabilities for AI agents calling LLM inference APIs through the gateway.

## Capability Catalog

| Capability | Summary |
|------|------|
| `chat` | Call a chat-completion API |

## Detailed Capability Semantics

### `chat`
- **summary**: Send chat completion requests to an LLM backend.
- **usage**: Agents that need LLM inference through the gateway.
- **when_not**: Read-only data agents that never call LLM APIs.
- **examples**: `POST /v1/chat/completions`
- **parameters**: `model` (list, allowed models), `max_tokens` (int 1..32768,
  default 2048).
