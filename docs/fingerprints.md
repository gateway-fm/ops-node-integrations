# Approval fingerprint contract

The protocol supports two execution projections. Their domain separation and canonical byte
encoding are part of contract version 1.0.0. The executable reference vectors are in
`contract/vectors`; changing a vector requires a new manifest version and cross-language tests.

## Strict execution

The strict projection binds the observed call tree and account-state changes. Its reference
input and expected digest are `fingerprint.json`. The sender computes the fingerprint before
forwarding the transaction; the producer computes it from provisional execution and excludes
the candidate if they differ. Call ordering, normalized account values, code and storage changes
must match the canonical encoders. Unsupported execution is denied, never approximated.

The canonical encoders are `internal/nodeapproval` in the pinned OPS sender,
`node-approvals/besu/src/main/java/ops/approvals/StrictFingerprint.java` and
`node-approvals/reth/src/fingerprint.rs`. The shared input and expected bytes protect against
language-specific JSON ordering, number formatting, and empty-value differences.

## Calls V3

Calls V3 binds the call graph, input, value, code identity, storage context and success/failure.
It intentionally permits ordinary storage, return data and log changes that preserve the approved
call behavior. Contract creation and destruction require the strict projection. The normative
reference input and digest are `call-v3.json`; the corresponding signed batch is `call-batch.json`.
Receivers must reject unsupported call shapes rather than silently dropping fields.

`batch.json` and `call-batch.json` contain public synthetic Ed25519 test keys and signatures.
The key material is never an operator credential. Each implementation verifies the same signed
bytes and expiry, chain, domain, and key-id constraints described in the
[wire contract](implementation/approvals-wire-contract.md).

## Contract changes

Propose changed protobuf, semantics and vectors together in this repository. Bump
`contract/manifest.json`'s semantic version and update its SHA-256 entries. Use a new major version
for incompatible wire or fingerprint semantics. Run Java, Rust and the supported OPS sender
compatibility suites before publishing. OPS consumes a fixed repository commit and the manifest
hash; its copied protobuf and vectors are generated inputs, not a second editable contract.
Generate proposed vectors in a disposable OPS checkout and submit them here for review before
updating the OPS pin. Never regenerate and silently bless a mismatching fixture in CI.
