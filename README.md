# Claude Code Practice Project

A tiny inventory tracker (pure Python, no dependencies) built to practice working with Claude Code.
It has **planted bugs**, **messy code**, and **missing features** for you to fix by talking to Claude.

## Quick start

```bash
python3 -m unittest                      # run tests
python3 -m inventory.cli add A1 "Blue Widget" 10 2.50 --category widgets
python3 -m inventory.cli list
python3 -m inventory.cli report
```

### Sample data

- `examples/nba-tshirts.json`: 24 NBA player T-shirts, clean data.
- `examples/nba-tricky.json`: the same plus 10 tricky but valid entries (accents, emoji, quotes
  and commas, a spreadsheet formula, a very long name, a zero quantity, a zero price, a huge
  quantity). Good for testing the report, search and the CSV export.

Inputs the app rejects or cleans up are covered by `tests/test_store.py` (`TestTrickyInputs`):
line breaks or control characters, empty names, spaces in a SKU and sub-cent prices are
rejected; surrounding spaces are trimmed and categories are lowercased.

To start from one:

```bash
cp examples/nba-tshirts.json inventory.json
python3 -m inventory.cli report
python3 -m inventory.cli export --csv out.csv   # or --csv - to print it
```

Then open `EXERCISES.md` and work through the levels. Each level teaches a different Claude Code skill.

Tip: commit after each exercise (or ask Claude to) so you can always `git diff` / `git reset` back.
