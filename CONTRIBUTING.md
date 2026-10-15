# Contributing

## Contribution terms

Contributions use the [Apache License, Version 2.0](LICENSE). By adding a sign-off, you certify
the [Developer Certificate of Origin 1.1](https://developercertificate.org/), including your
right to submit the contribution under that license. This follows the contribution model of
[Open Privacy Suite](https://github.com/gateway-fm/open-privacy-suite/blob/main/CONTRIBUTING.md).

Sign off each commit with `git commit -s`. The sign-off records your name and email in the
public Git history; use an appropriate public identity. A DCO sign-off is separate from a
cryptographic commit signature. The `DCO sign-off check` workflow checks every non-merge,
human-authored commit in a pull request; GitHub bot accounts and merge commits are exempt.
Do not sign off work you do not have the right to contribute.

## Development and review

Keep changes focused and open a pull request against `main`. Explain the problem, resulting
behavior and validation. Follow the [Code of Conduct](CODE_OF_CONDUCT.md).

Start with the Python checks in [README.md](README.md). For native changes, run the matching
`python3 node-approvals/build.py besu` or `python3 node-approvals/build.py reth` command using
the pinned toolchain. These commands run native tests before producing local bundles.
Update tests when behavior changes. Compatibility CI also exercises the pinned OPS sender
and real-node scenarios.

Protocol changes must keep the manifest, compatibility matrix, generated inputs and shared
test vectors consistent. Follow [release qualification](docs/releases.md) for contract
versioning and validation in both repositories. Do not edit generated files without updating
their source and checking the result.

Keep third-party licenses and attribution intact. Identify copied or substantially
AI-assisted contributions in the pull request and explain their provenance and validation;
review their licensing before submission.

## Public content and disclosure

Do not commit secrets, private audit reports, internal ticket exports, local agent state,
temporary investigation reports or generated credentials. Maintained public documentation
should explain supported behavior, configuration and contracts using synthetic examples.

Do not report security issues in public pull requests or issues; follow [SECURITY.md](SECURITY.md).
Keep internal security triage and risk-acceptance records in the approved private system.
Previously public source does not authorize a new repository or artifact publication;
obtain the required organisational approvals before publishing.
