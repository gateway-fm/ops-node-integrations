#!/usr/bin/env python3
"""Validate the versioned approval protocol; no network or native toolchain required."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "contract/manifest.json"


def sha256(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify(root, manifest):
    root = root.resolve()
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise ValueError("contract must contain files")
    for name, expected in files.items():
        relative = Path(name)
        path = root / relative
        if relative.is_absolute() or ".." in relative.parts or not name:
            raise ValueError(f"unsafe contract path: {name}")
        if any((root / Path(*relative.parts[:i])).is_symlink()
               for i in range(1, len(relative.parts) + 1)):
            raise ValueError(f"contract symlink: {name}")
        if not path.is_file() or path.resolve().is_relative_to(root) is False:
            raise ValueError(f"missing contract file: {name}")
        if sha256(path) != expected:
            raise ValueError(f"contract checksum differs: {name}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ops", type=Path, help="also verify the pinned OPS sender inputs")
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text())
    verify(ROOT, manifest)
    if args.ops:
        mapping = manifest["ops_files"]
        for source, destination in mapping.items():
            path = args.ops / destination
            if not path.is_file() or sha256(path) != manifest["files"][source]:
                raise SystemExit(f"OPS contract differs: {destination}")
    print(f"approval contract {manifest['version']} verified")


if __name__ == "__main__":
    main()
