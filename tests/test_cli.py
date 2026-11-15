import io
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path

from inventory.cli import main


class TestCliErrors(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.file = str(Path(self.tmp.name) / "inv.json")
        main(["--file", self.file, "add", "A1", "Blue Widget", "5", "2.50"])

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        err = io.StringIO()
        with redirect_stderr(err):
            code = main(["--file", self.file, *args])
        return code, err.getvalue()

    def test_remove_too_many_prints_error(self):
        code, err = self.run_cli("remove", "A1", "999")
        self.assertEqual(code, 1)
        self.assertEqual(err, "error: Cannot remove 999 of A1: only 5 in stock\n")

    def test_remove_unknown_sku_prints_error(self):
        code, err = self.run_cli("remove", "ZZZ", "1")
        self.assertEqual(code, 1)
        self.assertEqual(err, "error: Unknown SKU: ZZZ\n")

    def test_failed_remove_does_not_change_file(self):
        before = Path(self.file).read_text()
        self.run_cli("remove", "A1", "999")
        self.assertEqual(Path(self.file).read_text(), before)

    def test_successful_remove_returns_zero(self):
        code, err = self.run_cli("remove", "A1", "2")
        self.assertEqual((code, err), (0, ""))

    def test_add_invalid_item_prints_error(self):
        code, err = self.run_cli("add", "B1", "Bolt", "-5", "0.10")
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith("error: "), err)
        self.assertNotIn("B1", Path(self.file).read_text())


if __name__ == "__main__":
    unittest.main()
