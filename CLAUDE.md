# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A small inventory tracker in pure Python (standard library only, Python 3.10+), used as a
sandbox for practicing with Claude Code. `EXERCISES.md` lists the practice levels the user
works through, so fix only what the user asks for and mention anything else you notice.

## Rules

- Never push directly to `main`. Do all work on a branch and push that branch.

## Commands

```bash
python3 -m unittest                                   # all tests (no pytest; don't add dependencies)
python3 -m unittest tests.test_store                  # one file
python3 -m unittest tests.test_store.TestValidation.test_item_rejects_negative_price  # one test
python3 -m inventory.cli --file examples/nba-tricky.json report   # run the CLI against sample data
```

`--file` belongs to the top-level parser, so it goes before the subcommand. Without it the CLI
reads and writes `inventory.json` in the current directory, which is git-ignored scratch data.
`examples/nba-tshirts.json` (clean) and `examples/nba-tricky.json` (edge-case inputs) are
tracked sample data; `*.csv` is git-ignored.

## Architecture

Layers depend downward only: `cli` → `report` / `export` → `store` → `models`.

- **`models.Item`** is the single place for data validation and normalization. `__post_init__`
  trims text fields, lowercases the category, and rejects empty text, control characters
  (including line breaks), spaces in the SKU, negative quantities, and prices that are negative,
  non-finite or have fractions of a cent. Input from the CLI, `add_item` and JSON loading is all
  checked there, so a saved file with one invalid entry fails to load as a whole. `Item.value` (quantity × price) is the one definition of an
  item's value; use it rather than recomputing.
- **`store.Inventory`** holds items in a dict keyed by SKU and persists them as a JSON list.
  Re-adding an existing SKU merges quantities but raises if the name, price or category differs.
  The CLI's `add --category` defaults to the existing item's category (or `general` for a new
  SKU), so re-adding stock doesn't require repeating it. `search` ignores case and accents. Removing down to 0 deletes the item.
- **Error contract:** library code raises `KeyError` (unknown SKU) or `ValueError` (bad input).
  `cli.main()` has the only error handler: it prints a one-line `error: ...` to stderr and
  returns exit code 1, also for `OSError`, and exits quietly on `BrokenPipeError`. Argparse
  usage errors exit with code 2. `_load()` wraps any load failure in a `ValueError` naming the
  file. New commands go in `cli._run()` and should not add their own try/except.
- **`report.build_report`** output is checked byte-for-byte by `tests/test_report.py`. Keep
  float summation order unchanged (subtotals in name order, the total via
  `Inventory.total_value()` in insertion order), or the last cent can change.
- **`export.write_csv`** takes an open file object (tests use `io.StringIO`). Columns come
  from the `Item` dataclass fields, so a new field becomes a new column automatically. Rows are
  sorted by SKU. Files must be opened with `newline=""` and `encoding="utf-8"`.
- **`importer.read_csv`** is the inverse: it returns `(line number, Item)` pairs and raises
  `ValueError("header: ...")` or `ValueError("line N: ...")`, which the CLI prefixes with the file
  name. Headers are case-insensitive in any order; `category` is optional and resolved through a
  `default_category(sku)` callback (the CLI passes the existing item's category, as `add` does).
  `cli import` applies all rows or none: the default adds stock via `add_item`, `--replace` makes
  the file the whole inventory. Open import files with `encoding="utf-8-sig"` to drop Excel's BOM.

## Tests

Tests use `unittest`. CLI tests call `main([...])` directly with a temporary `--file` and
capture output with `redirect_stdout` / `redirect_stderr`, asserting on the exit code and the
exact message. When adding a validation rule, also assert that the inventory or file is left
unchanged after the rejected operation.
