# Signed approval integrations

See the [repository guide](../README.md) for builds and compatibility,
[wire contract](../docs/implementation/approvals-wire-contract.md) for the shared protocol,
[security policy](../SECURITY.md) for private vulnerability reporting and
[release procedure](../docs/releases.md) for artifact qualification.

The Besu plugin verifies Ed25519 signatures with Bouncy Castle supplied by the pinned host;
it does not bundle another cryptographic provider. Reth runs against the unchanged upstream
revision in compatibility.json. Both enforce approvals on locally produced candidates, not
on imported blocks. Restrict node RPC, Engine API and delivery ports accordingly.

Supported transaction envelopes are replay-protected legacy and EIP-1559. Calls V3 binds the
call graph, inputs, value, code, storage context and success/failure while allowing ordinary
storage/output/log differences. Contract lifecycle operations use strict fingerprints.
EIP-2930/4844/7702, durable recovery, revocation and automatic transaction reconciliation are
outside this version. See [operations](OPERATIONS.md) before enabling it.
