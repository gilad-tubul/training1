# Claude Code Practice Project

A tiny inventory tracker (pure Python, no dependencies) built to practice working with Claude Code.
It has **planted bugs**, **messy code**, and **missing features** for you to fix by talking to Claude.

## Quick start

```bash
python3 -m unittest                      # run tests (3 fail on purpose)
python3 -m inventory.cli add A1 "Blue Widget" 10 2.50 --category widgets
python3 -m inventory.cli list
python3 -m inventory.cli report
```

Then open `EXERCISES.md` and work through the levels. Each level teaches a different Claude Code skill.

Tip: commit after each exercise (or ask Claude to) so you can always `git diff` / `git reset` back.
