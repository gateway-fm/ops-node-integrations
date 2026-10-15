import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("build", Path(__file__).resolve().parents[1] / "node-approvals/build.py")
build = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build)


class ReleaseTests(unittest.TestCase):
    def test_bundle_excludes_private_audit_exports(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            native = root / "node-approvals"
            native.mkdir()
            for name in ["VERSION", "compatibility.json", "README.md", "OPERATIONS.md", "alerts.yml", "advisory-review.json"]:
                (native / name).write_bytes((build.HERE / name).read_bytes())
            for name in ["LICENSE", "NOTICE", "THIRD_PARTY_NOTICES.md", "SECURITY.md", build.COMPAT["protocol"]["manifest"]]:
                destination = root / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes((build.ROOT / name).read_bytes())
            (root / "security").mkdir()
            marker = b"private audit export must never be packaged"
            (root / "security/open-findings.json").write_bytes(marker)
            artifact = native / f"besu/build/libs/ops-besu-approvals-{build.VERSION}-besu-{build.COMPAT['besu']['version']}.jar"
            artifact.parent.mkdir(parents=True)
            artifact.write_bytes(b"test artifact")
            (native / "besu/build/dependency-inventory.json").write_text("[]\n")
            responses = ["", "test-commit", "test-jdk", "test-commit", ""]
            output = root / "output"
            with patch("sys.argv", ["build.py", "besu", "--output", str(output)]), \
                 patch.object(build, "ROOT", root), patch.object(build, "HERE", native), \
                 patch.object(build, "run"), patch.object(build, "output", side_effect=responses):
                build.main()
            bundle, = output.iterdir()
            self.assertFalse((bundle / "open-findings.json").exists())
            self.assertTrue((bundle / "SECURITY.md").is_file())
            notices = (bundle / "THIRD_PARTY_NOTICES.md").read_text()
            self.assertIn("copyright the Wycheproof contributors", notices)
            self.assertIn("https://github.com/gateway-fm/ops-node-integrations/blob/test-commit/"
                          "node-approvals/besu/src/test/resources/wycheproof/LICENSE", notices)
            self.assertIn("https://github.com/protocolbuffers/protobuf/blob/v36.2/LICENSE", notices)
            for path in bundle.iterdir():
                self.assertNotIn(marker, path.read_bytes())
            for line in (bundle / "SHA256SUMS").read_text().splitlines():
                digest, name = line.split("  ", 1)
                self.assertEqual(hashlib.sha256((bundle / name).read_bytes()).hexdigest(), digest)

    def test_dirty_release_fails_before_any_build(self):
        with patch("sys.argv", ["build.py", "besu", "--release"]), \
             patch.object(build, "output", return_value=" M native-source"), \
             patch.object(build, "run") as run:
            with self.assertRaisesRegex(SystemExit, "clean checkout"):
                build.main()
            run.assert_not_called()

    def test_source_change_during_release_is_rejected(self):
        for state in [("different-commit", ""), ("initial-commit", " M source")]:
            with self.subTest(state=state), patch.object(build, "output", side_effect=state):
                with self.assertRaisesRegex(SystemExit, "changed during build"):
                    build.verify_source("initial-commit", False, True)

    def test_nonrelease_records_source_changes(self):
        with patch.object(build, "output", side_effect=["different-commit", ""]):
            self.assertTrue(build.verify_source("initial-commit", False, False))

    def test_contract_pin_mismatch_fails_before_native_build(self):
        from copy import deepcopy
        compatibility = deepcopy(build.COMPAT)
        compatibility["protocol"]["sha256"] = "0" * 64
        with patch("sys.argv", ["build.py", "reth"]), \
             patch.object(build, "COMPAT", compatibility), \
             patch.object(build, "output", return_value=""), \
             patch.object(build, "run") as run:
            with self.assertRaisesRegex(SystemExit, "contract manifest differs"):
                build.main()
            run.assert_called_once_with("python3", "scripts/contract.py")


if __name__ == "__main__":
    unittest.main()
