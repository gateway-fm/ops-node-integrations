#!/usr/bin/env python3
"""Prepare a disposable, pinned OPS checkout for integration compatibility scenarios."""
import json
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
OPS = ROOT / ".tmp/ops"
COMPAT = json.loads((ROOT / "node-approvals/compatibility.json").read_text())


def run(*args, **kwargs):
    subprocess.run(args, check=True, cwd=OPS, **kwargs)


def main():
    actual = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=OPS, text=True).strip()
    if actual != COMPAT["ops"]["commit"]:
        raise SystemExit("OPS checkout differs from compatibility.json")
    if subprocess.check_output(["git", "status", "--porcelain"], cwd=OPS, text=True).strip():
        raise SystemExit("start compatibility tests from a clean OPS checkout")
    run("python3", str(ROOT / "scripts/contract.py"), "--ops", str(OPS))
    # Only this repository-owned, disposable fixture checkout is modified. The linked source
    # is the candidate under test, never the older native source from the OPS revision.
    if OPS.is_symlink() or OPS.resolve() != ROOT / ".tmp/ops":
        raise SystemExit("refuse an external OPS fixture checkout")
    shutil.rmtree(OPS / "node-approvals")
    (OPS / "node-approvals").symlink_to(ROOT / "node-approvals", target_is_directory=True)
    scratch = OPS / ".tmp"
    scratch.mkdir(exist_ok=True)
    if (ROOT / ".tmp/reth").exists():
        (scratch / "reth").symlink_to(ROOT / ".tmp/reth", target_is_directory=True)
    run("go", "test", "-race", "./internal/nodeapproval")
    run("go", "build", "-o", ".tmp/approval-client", "./poc/reth-signed-approvals/client")
    run("go", "test", "-c", "-o", ".tmp/server-approval.test", "./internal/server")
    run("go", "build", "-tags", "mockauth", "-o", ".tmp/ops-server", "./cmd/server")


if __name__ == "__main__":
    main()
