#!/usr/bin/env python3
"""Build, test and bundle a supported integration. Does not publish or modify a node install."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
COMPAT = json.loads((HERE / "compatibility.json").read_text())
VERSION = (HERE / "VERSION").read_text().strip()


def run(*args, **kwargs):
    subprocess.run(args, cwd=ROOT, check=True, **kwargs)


def output(*args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()


def verify_source(initial_commit, initial_dirty, release):
    final_commit = output("git", "rev-parse", "HEAD")
    final_dirty = bool(output("git", "status", "--porcelain", "--untracked-files=all"))
    changed = final_commit != initial_commit
    if release and (initial_dirty or final_dirty or changed):
        raise SystemExit("release source changed during build")
    return initial_dirty or final_dirty or changed


def upstream_state(source):
    """HEAD and modification state of the upstream Reth checkout the add-on compiles against."""
    return (output("git", "-C", str(source), "rev-parse", "HEAD"),
            bool(output("git", "-C", str(source), "status", "--porcelain")))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", choices=["besu", "reth"])
    parser.add_argument("--output", type=Path, default=ROOT / ".tmp/approval-release")
    parser.add_argument("--release", action="store_true", help="require clean source and pinned release toolchains")
    args = parser.parse_args()
    source_dirty = bool(output("git", "status", "--porcelain", "--untracked-files=all"))
    if args.release and source_dirty:
        raise SystemExit("release builds require a clean checkout")
    initial_commit = output("git", "rev-parse", "HEAD")
    run("python3", "scripts/contract.py")
    protocol_manifest = ROOT / COMPAT["protocol"]["manifest"]
    if hashlib.sha256(protocol_manifest.read_bytes()).hexdigest() != COMPAT["protocol"]["sha256"]:
        raise SystemExit("contract manifest differs from compatibility.json")
    if args.release:
        if args.target == "besu":
            java_home = os.environ.get("JAVA_HOME")
            if not java_home or f'IMPLEMENTOR_VERSION="Temurin-{COMPAT["besu"]["java"]}"' not in (Path(java_home) / "release").read_text().splitlines():
                raise SystemExit("release JDK differs from compatibility.json")
            if f'Gradle {COMPAT["besu"]["gradle"]}' not in output("gradle", "--version").splitlines():
                raise SystemExit("release Gradle differs from compatibility.json")
        elif output("rustc", "--version").split()[1] != COMPAT["reth"]["rust"]:
            raise SystemExit("release Rust differs from compatibility.json")
    if args.target == "besu":
        run("gradle", "-p", str(HERE / "besu"), "--no-daemon", "check", "assemble", "dependencyInventory")
        artifact = HERE / f"besu/build/libs/ops-besu-approvals-{VERSION}-besu-{COMPAT['besu']['version']}.jar"
        toolchain = output("java", "--version")
        name = artifact.stem
    else:
        source = ROOT / ".tmp/reth"
        source.parent.mkdir(exist_ok=True)
        if not source.exists():
            run("git", "clone", "--depth", "1", "--branch", "v" + COMPAT["reth"]["version"],
                COMPAT["reth"]["repository"], str(source))
        head, modified = upstream_state(source)
        if head != COMPAT["reth"]["commit"]:
            raise SystemExit("Reth checkout differs from compatibility.json")
        if modified:
            raise SystemExit("Reth checkout must be unmodified")
        import tomllib
        if tomllib.loads((HERE / "reth/Cargo.toml").read_text())["package"]["version"] != VERSION:
            raise SystemExit("Cargo package version differs from VERSION")
        target = Path(os.environ.get("CARGO_TARGET_DIR", ROOT / ".tmp/approval-target")).resolve()
        env = dict(os.environ, CARGO_TARGET_DIR=str(target))
        for verb in ["test", "build"]:
            run("cargo", verb, "--release", "--locked", "--manifest-path", str(HERE / "reth/Cargo.toml"), env=env)
        # verify_source covers this repository only, and it ignores .tmp/. A checkout switch or edit
        # while Cargo ran would package a binary that no longer matches the pinned upstream.
        if upstream_state(source) != (COMPAT["reth"]["commit"], False):
            raise SystemExit("Reth checkout changed during build")
        artifact = target / "release/ops-reth-approvals"
        toolchain = output("rustc", "--version")
        name = f"ops-reth-approvals-{VERSION}-reth-{COMPAT['reth']['version']}-{platform.system().lower()}-{platform.machine()}"
    source_dirty = verify_source(initial_commit, source_dirty, args.release)
    destination = args.output.resolve() / name
    # Refuse to mix a previous bundle's files/checksums into a new one.
    destination.mkdir(parents=True, exist_ok=False)
    shutil.copy2(artifact, destination / artifact.name)
    if args.target == "besu":
        shutil.copy2(HERE / "besu/build/dependency-inventory.json", destination / "dependency-inventory.json")
    else:
        shutil.copy2(HERE / "reth/Cargo.lock", destination / "Cargo.lock")
    commit = initial_commit
    for filename in ["VERSION", "compatibility.json", "README.md", "OPERATIONS.md", "alerts.yml", "advisory-review.json"]:
        shutil.copy2(HERE / filename, destination / filename)
        if filename.endswith(".md"):
            # External repository references still work when the bundle is unpacked alone.
            content = (destination / filename).read_text()
            content = re.sub(r"\]\(\.\./([^)]*)\)",
                             lambda match: f"](https://github.com/gateway-fm/ops-node-integrations/blob/{commit}/{match[1]})",
                             content)
            (destination / filename).write_text(content)
    for filename in ["LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md", "SECURITY.md"]:
        shutil.copy2(ROOT / filename, destination / filename)
        if filename.endswith(".md"):
            # Root documentation can reference source files absent from the bundle.
            content = (destination / filename).read_text()
            content = re.sub(r"\]\((?![a-zA-Z][a-zA-Z0-9+.-]*:|#)([^)]+)\)",
                             lambda match: f"](https://github.com/gateway-fm/ops-node-integrations/blob/{commit}/{match[1]})",
                             content)
            (destination / filename).write_text(content)
    shutil.copy2(protocol_manifest, destination / "protocol-manifest.json")
    manifest = {
        "version": VERSION, "integration": args.target,
        "source_repository": "https://github.com/gateway-fm/ops-node-integrations",
        "source_commit": commit,
        "source_dirty": source_dirty,
        "release_build": args.release,
        "toolchain": toolchain, "platform": platform.system(), "architecture": platform.machine(),
        "compatibility": COMPAT,
    }
    (destination / "build.json").write_text(json.dumps(manifest, indent=2) + "\n")
    checksums = []
    for path in sorted(destination.iterdir()):
        with path.open("rb") as stream:
            checksums.append(hashlib.file_digest(stream, "sha256").hexdigest() + "  " + path.name)
    (destination / "SHA256SUMS").write_text("\n".join(checksums) + "\n")
    print(destination)


if __name__ == "__main__":
    main()
