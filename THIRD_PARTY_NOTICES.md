# Third-party notices

The project license does not replace the licenses of third-party material. Preserve applicable
copyright notices, license texts and attribution when redistributing source or build outputs.

## Source in this repository

The integration source was imported from
[Open Privacy Suite](https://github.com/gateway-fm/open-privacy-suite) under Apache-2.0.
Original authorship is preserved in Git history; [import provenance](provenance/import.json)
records the source revision and commit mapping. See [LICENSE](LICENSE) and [NOTICE](NOTICE).

The Besu test suite includes an unmodified Ed25519 fixture from C2SP Wycheproof, commit
`5722833ca004983abd1a91bcb6c24596d50ac0f9`, copyright the Wycheproof contributors, under
Apache-2.0. Its [provenance and checksum](node-approvals/besu/src/test/resources/wycheproof/README.md)
and [license](node-approvals/besu/src/test/resources/wycheproof/LICENSE) accompany the fixture.
It is test data and is not included in the plugin JAR.

## Upstream nodes and bundled libraries

These dependencies are fetched during builds rather than vendored into this repository.
Versions are pinned in the [compatibility matrix](node-approvals/compatibility.json), Gradle
build and Cargo.lock. Their licenses remain applicable to any resulting distribution.

| Component | Use | License reference |
| --- | --- | --- |
| Besu 26.8.1 | Plugin host and compile-time APIs; the plugin bundle does not include the Besu distribution | [Apache-2.0](https://github.com/besu-eth/besu/blob/26.8.1/LICENSE) |
| Reth 2.5.2, commit `5a6940e351fed80458fe6c9da8581cbe4b8bd036` | Pinned upstream source linked into the custom Reth binary | [MIT](https://github.com/paradigmxyz/reth/blob/5a6940e351fed80458fe6c9da8581cbe4b8bd036/LICENSE-MIT) OR [Apache-2.0](https://github.com/paradigmxyz/reth/blob/5a6940e351fed80458fe6c9da8581cbe4b8bd036/LICENSE-APACHE), with dependencies under their own terms |
| gRPC Java 1.79.0: grpc-stub, grpc-protobuf, grpc-protobuf-lite | Relocated into the Besu plugin JAR | [Apache-2.0](https://github.com/grpc/grpc-java/blob/v1.79.0/LICENSE) |
| Protocol Buffers Java 4.36.2 | Relocated into the Besu plugin JAR | [BSD-3-Clause](https://github.com/protocolbuffers/protobuf/blob/v36.2/LICENSE) |

Besu provides the remaining host libraries at runtime; they retain their own licenses. The
Reth dependency graph includes additional Rust and native components under separate licenses.
Build tools and test dependencies also retain their own terms.

This document identifies source attribution and major build relationships; it is not a complete
license inventory for a binary or container image. Before distributing those artifacts, review
the exact resolved dependencies (including transitive, native and operating-system components),
include all required license texts and notices, and satisfy any source-availability obligations.
See [release qualification](docs/releases.md). A lockfile or dependency list alone does not
establish license compliance.
