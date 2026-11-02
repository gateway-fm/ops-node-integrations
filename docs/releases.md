# Build and release qualification

The commands below prepare and verify artifacts locally. They do not authorize repository,
binary or image publication. Distribution requires approval through the organisation's
release process, including security and license review. No production release is currently
approved for this repository.

1. Update VERSION, native package versions, compatibility pins, the protocol manifest hash and
   supported OPS commit together. Changes to protocol meaning require a new contract version.
2. Pass the native unit/vector suites and real-node/HTTP scenarios against every supported OPS
   revision. Resolve security and license findings through private review; follow SECURITY.md
   for vulnerability reporting. Keep private audit exports and risk-acceptance records out of
   public source, pull requests, logs and downloadable artifacts.
3. Build from a clean checkout with the pinned toolchain. `build.py --release` rejects dirty
   source. Bundles include source revision, protocol manifest, dependency inventory or lockfile,
   compatibility matrix, license, third-party notices, operator guidance and SHA256SUMS. They
   identify their target OS and architecture; deterministic ZIP ordering is not a promise of cross-platform binary
   reproducibility. The `--release` flag validates build inputs; it is not publication approval.
4. Before binary or image distribution, produce an SBOM for the exact artifacts and review all
   resolved licenses, including transitive Rust/Java libraries, linked native code and image
   packages. Include required license texts and notices and satisfy source-availability
   obligations. The source repository's THIRD_PARTY_NOTICES.md is not a complete binary license
   inventory. Record the review and any required approvals privately.
5. After distribution approval, publish the exact reviewed and tested bundles with their archive
   checksums. Do not rebuild between testing and publication. CI does not automatically upload
   bundles or raw scenario/audit evidence to this public repository.
6. Update the OPS consumer using actual immutable checksums or an image digest. Verify a clean
   checkout's demos and sender compatibility before removing its native source and build path.

A contract pin is the integration Git commit plus SHA-256 of `contract/manifest.json`; each
manifest file is independently hashed. Updating it requires review in both repositories. OPS
may vendor generated inputs for offline Go builds, but CI verifies them against this pin and
must reject unreviewed local regeneration. The protobuf retains its Go package name so sender
code does not change merely because the contract moved.
