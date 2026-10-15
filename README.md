# OPS node integrations

Besu and Reth producer integrations for the Open Privacy Suite V1 signed-approval protocol.
The OPS Go policy engine and approval sender remain in
[Open Privacy Suite](https://github.com/gateway-fm/open-privacy-suite).

Both integrations verify the same [versioned protocol](contract/manifest.json),
[wire semantics](docs/implementation/approvals-wire-contract.md),
[fingerprints](docs/fingerprints.md) and signed test vectors. Besu loads a plugin; Reth runs a
custom binary built against an unchanged, pinned upstream checkout. Approval checks govern
locally produced blocks; they are not consensus validation of imported blocks.

## Build and verify

Clone the repository and run the contract and tooling checks with Python 3.11 or later:

```sh
git clone https://github.com/gateway-fm/ops-node-integrations.git
cd ops-node-integrations
python3 scripts/contract.py
python3 -B -m unittest discover -s tests
python3 -B -m unittest discover -s node-approvals -p test_audit_dependencies.py
```

To build either integration, install its exact toolchain from
[compatibility.json](node-approvals/compatibility.json), then run the corresponding command:

```sh
python3 node-approvals/build.py besu
python3 node-approvals/build.py reth
```

Besu requires Temurin 25.0.4.1+1 and Gradle 9.2.1. Reth requires Rust 1.98.1, protoc, clang,
pkg-config and OpenSSL development headers. The build prepares the pinned upstream Reth source
under `.tmp/reth` and uses its own Cargo.lock. Native tests run before bundles are produced.
Bundles are written to `.tmp/approval-release/`. Follow the
[operator guide](node-approvals/OPERATIONS.md) to configure approval keys, install the Besu
plugin or run the Reth binary, and connect the OPS sender. All generated output belongs under
`.tmp/` or ignored build directories.

## Compatibility and releases

The compatibility matrix pins one exact OPS sender commit, Besu distribution, Reth commit and
protocol manifest. Integration CI checks the Go sender and both native implementations against
that combination. See [release procedure](docs/releases.md) and
[operator guidance](node-approvals/OPERATIONS.md).

No approved production release is available from this repository. Build outputs are for local
verification; binary or image distribution requires separate approval. OPS currently retains
its existing native build path. This repository supports the V1 signed-approval protocol only.

## Contributing, security and licensing

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow and DCO sign-off requirement,
and follow the [Code of Conduct](CODE_OF_CONDUCT.md). Report vulnerabilities privately as
described in [SECURITY.md](SECURITY.md).

Project code is licensed under [Apache-2.0](LICENSE). See [NOTICE](NOTICE) and
[third-party notices](THIRD_PARTY_NOTICES.md) for attribution and dependencies with their own
terms. Source provenance and preserved commit mapping are in [provenance](provenance/import.json).
