//! Peer-discovery defaults for every command that starts networking.
//!
//! Reth starts discv5 by default. discv5 uses the node's p2p key through k256, which depends on
//! crypto-bigint 0.5 (RUSTSEC-2026-0387, fixed only in 0.7.6, which k256 0.13 cannot use).
//! Permissioned networks connect to configured peers, so this binary turns discv5 off. discv4
//! uses libsecp256k1 and is unchanged.

use reth_ethereum::{cli::interface::Cli, node::core::args::DefaultDiscoveryArgs};
use std::ffi::OsString;

/// Parses the process command line with discv5 off by default.
pub fn parse_args() -> eyre::Result<Cli> {
    parse_args_from(std::env::args_os())
}

fn parse_args_from<I, T>(args: I) -> eyre::Result<Cli>
where
    I: IntoIterator<Item = T>,
    T: Into<OsString> + Clone,
{
    disable_discv5()?;
    // Same output and exit status as `Cli::parse_args` for `--help`, `--version` and bad input.
    Ok(Cli::try_parse_args_from(args).unwrap_or_else(|err| err.exit()))
}

/// Makes `--disable-discv5-discovery` default to set. The flag takes no value, so the command line
/// cannot turn discv5 back on.
///
/// Must run before the command line is parsed: Reth reads these defaults once, on first use.
fn disable_discv5() -> eyre::Result<()> {
    DefaultDiscoveryArgs::default()
        .with_disable_discv5_discovery(true)
        .try_init()
        .map_err(|_| eyre::eyre!("discovery defaults were set before discv5 could be disabled"))
}

#[cfg(test)]
mod tests {
    use reth_ethereum::{
        cli::interface::{Cli, Commands},
        node::core::args::DiscoveryArgs,
    };

    fn discovery(cli: Cli) -> DiscoveryArgs {
        let Commands::Node(node) = cli.command else {
            panic!("expected the node command")
        };
        node.network.discovery
    }

    fn parse(args: &[&str]) -> Cli {
        Cli::try_parse_args_from(["ops-reth-approvals", "node"].iter().chain(args))
            .expect("node arguments parse")
    }

    // One test: the defaults are process-global and can be set only once.
    #[test]
    fn node_runs_without_discv5_and_the_command_line_cannot_enable_it() {
        let default = discovery(super::parse_args_from(["ops-reth-approvals", "node"]).unwrap());
        assert!(default.disable_discv5_discovery);
        assert!(!default.disable_discovery);
        assert!(!default.disable_discv4_discovery);

        // Defaults that are already set mean something read them first; startup must refuse.
        assert!(super::disable_discv5().is_err());

        // The hidden legacy flag is a no-op upstream and must stay one.
        assert!(discovery(parse(&["--enable-discv5-discovery"])).disable_discv5_discovery);
        assert!(
            Cli::try_parse_args_from([
                "ops-reth-approvals",
                "node",
                "--disable-discv5-discovery=false"
            ])
            .is_err()
        );
        // Turning all discovery off still works alongside the new default.
        assert!(discovery(parse(&["--disable-discovery"])).disable_discovery);
    }
}
