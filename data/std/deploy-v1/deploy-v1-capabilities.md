# Standard Deployment/Infra Capability Reference

> scheme_id: `std/deploy-v1` · Version `1.0.0` · Vendor `std` / Product `deploy-v1`

Standard semantics for AI-agent access to deployment and infrastructure
operations: apply changes only to allowlisted environments, read infra state,
read only allowlisted secrets. **Production environments are excluded unless
explicitly granted.**

## Capability Catalog

| Capability | Summary | Related |
|------|------|----------|
| `deploy:apply` | Apply deployment changes to allowlisted environments | infra:read |
| `infra:read` | Read infrastructure state | deploy:apply |
| `secret:read` | Read allowlisted secrets | deploy:apply |

## Detailed Capability Semantics

### `deploy:apply`
- **summary**: Deploy resources into environments/namespaces the principal
  authorized.
- **usage**: Agents that release, scale, or roll back workloads.
- **when_not**: Never granted with `production` in `environments` unless
  explicitly intended; namespace/resource bounds should be narrow.
- **examples**: `POST /v1/deploy/apply {"environment":"staging","namespace":"web","replicas":3}`
- **parameters**: `environments` (array, required), `namespaces` (array),
  `resources` (array), `max_replicas` (integer 1..100).

### `infra:read`
- **summary**: Query resources/namespaces in authorized environments.
- **usage**: Agents that inspect state before acting.
- **when_not**: Reads outside the authorized environments must be rejected.
- **examples**: `GET /v1/infra/read?environment=staging&resource=deployments`
- **parameters**: `environments` (array, required), `namespaces` (array),
  `resources` (array).

### `secret:read`
- **summary**: Read only the secrets the principal authorized.
- **usage**: Agents that need specific credentials.
- **when_not**: Secret name allowlist required; never grant `"*"`.
- **examples**: `GET /v1/secrets/read?secret=api-key-staging`
- **parameters**: `secrets` (array, required), `environments` (array).
