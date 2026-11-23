import csv
import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
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

    def test_readd_without_category_keeps_existing_category(self):
        main(["--file", self.file, "add", "W1", "Wid", "1", "1.00", "--category", "tools"])
        code, err = self.run_cli("add", "W1", "Wid", "2", "1.00")
        self.assertEqual((code, err), (0, ""))
        self.assertIn('"category": "tools"', Path(self.file).read_text())

    def test_new_item_without_category_is_general(self):
        self.assertIn('"category": "general"', Path(self.file).read_text())

    def test_readd_with_different_category_prints_error(self):
        code, err = self.run_cli("add", "A1", "Blue Widget", "1", "2.50", "--category", "heat")
        self.assertEqual(code, 1)
        self.assertIn("category", err)

    def test_add_invalid_item_prints_error(self):
        code, err = self.run_cli("add", "B1", "Bolt", "-5", "0.10")
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith("error: "), err)
        self.assertNotIn("B1", Path(self.file).read_text())

    def test_add_nan_price_prints_error(self):
        code, err = self.run_cli("add", "N1", "Thing", "1", "nan")
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith("error: Price"), err)

    def check_bad_file(self, content):
        Path(self.file).write_text(content)
        code, err = self.run_cli("list")
        self.assertEqual(code, 1)
        self.assertTrue(err.startswith(f"error: Could not load {self.file}: "), err)
        self.assertEqual(err.count("\n"), 1, "expected a one-line error, not a traceback")

    def test_invalid_saved_value_prints_error(self):
        self.check_bad_file('[{"sku": "A", "name": "x", "quantity": -1, "price": 1}]')

    def test_corrupt_json_prints_error(self):
        self.check_bad_file("{not json")

    def test_unknown_field_prints_error(self):
        self.check_bad_file('[{"sku": "A", "name": "x", "quantity": 1, "price": 1, "colour": "red"}]')


class TestCliExport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.file = str(self.dir / "inv.json")
        main(["--file", self.file, "add", "A1", "Blue Widget", "5", "2.50"])

    def tearDown(self):
        self.tmp.cleanup()

    def test_export_writes_csv_file(self):
        out = self.dir / "out.csv"
        out.write_text("old contents")
        self.assertEqual(main(["--file", self.file, "export", "--csv", str(out)]), 0)
        with open(out, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual([(r["sku"], r["quantity"]) for r in rows], [("A1", "5")])

    def test_export_to_stdout(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main(["--file", self.file, "export", "--csv", "-"])
        self.assertEqual(code, 0)
        self.assertEqual(buf.getvalue().splitlines()[1], "A1,Blue Widget,5,2.5,general")

    def test_export_to_missing_folder_prints_error(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = main(["--file", self.file, "export", "--csv", str(self.dir / "nope" / "out.csv")])
        self.assertEqual(code, 1)
        self.assertTrue(err.getvalue().startswith("error: [Errno 2] No such file or directory"), err.getvalue())
        self.assertEqual(err.getvalue().count("\n"), 1)


    def test_export_piped_into_head_exits_quietly(self):
        # 3000 rows is far more than `head -2` reads, so the pipe closes early.
        rows = [{"sku": f"S{n:04}", "name": "Bulk", "quantity": 1, "price": 1.0,
                 "category": "general"} for n in range(3000)]
        Path(self.file).write_text(json.dumps(rows))
        result = subprocess.run(
            f"{sys.executable} -m inventory.cli --file {self.file} export --csv - | head -2",
            shell=True, capture_output=True, text=True,
            cwd=Path(__file__).resolve().parent.parent,
        )
        self.assertEqual(result.stdout.splitlines()[0], "sku,name,quantity,price,category")
        self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
