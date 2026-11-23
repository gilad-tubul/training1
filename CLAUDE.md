# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A small inventory tracker in pure Python (standard library only, Python 3.10+), used as a
sandbox for practicing with Claude Code. `EXERCISES.md` lists the practice levels the user
works through. Some known issues are deliberately left open for later exercises (e.g. names with
line breaks or surrounding spaces, empty names, `Lakers`/`lakers` treated as separate categories,
accent-insensitive search), so fix only what the user asks for and mention anything else you notice.

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

- **`models.Item`** is the single place for data validation. `__post_init__` rejects negative
  quantities and negative or non-finite prices, so input from the CLI, `add_item` and JSON
  loading is all checked there. `Item.value` (quantity × price) is the one definition of an
  item's value; use it rather than recomputing.
- **`store.Inventory`** holds items in a dict keyed by SKU and persists them as a JSON list.
  Re-adding an existing SKU merges quantities but raises if the name or price differs
  (category is intentionally not compared). Removing down to 0 deletes the item.
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

## Tests

Tests use `unittest`. CLI tests call `main([...])` directly with a temporary `--file` and
capture output with `redirect_stdout` / `redirect_stderr`, asserting on the exit code and the
exact message. When adding a validation rule, also assert that the inventory or file is left
unchanged after the rejected operation.
