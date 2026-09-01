# varwof-capability

> ⚠️ **Preview** — Not for production use. Schemas may change before official
> release. Contributions welcome (PRs).

Capability schema data for varwof zero-trust gateways: JSON capability definitions for `std`, `varwof`, `oracle` and `x-vendor` namespaces. Consumed by the `register` module for PKCS#7-signed rules and validation.

## Structure

```
data/
  std/database-v1/v1.json         — standard database capability schema
  varwof/core/v1.json             — varwof core capabilities
  varwof/gateway/v1.json          — gateway capabilities
  varwof/constraint/v1.json       — execution constraint capabilities
  varwof/demo-mysql/v1/v1.json    — demo MySQL capabilities
  oracle/mysql/v1.json            — Oracle MySQL capabilities
  x-vendor/acme/v1.json           — example vendor capability
```

## Usage

Point `capability_schemes` (core) or the capreg directory (gateways) at the `data/` directory:

```bash
export CAPABILITY_DIR=/path/to/capability/data
```

The directory layout is `<vendor>/<product>/v*.json`; every JSON file declares `scheme_id`.

## License

Apache-2.0
