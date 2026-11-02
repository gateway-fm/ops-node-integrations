import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULE = Path(__file__).resolve().parents[1] / "scripts/contract.py"
spec = importlib.util.spec_from_file_location("contract", MODULE)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)

class ContractTests(unittest.TestCase):
    def test_modified_vector_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "vector.json").write_text("original")
            manifest = {"files": {"vector.json": contract.sha256(root / "vector.json")}}
            contract.verify(root, manifest)
            (root / "vector.json").write_text("modified")
            with self.assertRaisesRegex(ValueError, "checksum"):
                contract.verify(root, manifest)

    def test_traversal_and_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / "alias").symlink_to("/etc/hosts")
            for name in ["../outside", "/etc/hosts", "alias"]:
                with self.subTest(name=name), self.assertRaises(ValueError):
                    contract.verify(root, {"files": {name: "0" * 64}})

    def test_missing_manifest_files_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                contract.verify(Path(d), {"files": {}})

if __name__ == "__main__":
    unittest.main()
