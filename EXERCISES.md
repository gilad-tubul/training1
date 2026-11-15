# Exercises

Do these in order. The **Try saying** lines are example prompts; use your own words too.
Tick a box when you're done.

## Level 1: Explore and ask questions
Learn: how Claude reads a codebase before changing anything.

- [ ] **1.1 Get oriented.** Try saying: *"Explain how this project is structured and what each file does."*
- [ ] **1.2 Trace a flow.** *"What happens, step by step, when I run `inventory.cli add ...`?"*
- [ ] **1.3 Run things.** *"Run the tests and tell me which ones fail and why. Don't fix anything yet."*
  Notice how Claude asks permission before running commands (you can change this with the permission-mode picker).

## Level 2: Fix bugs
Learn: letting Claude edit code, then checking its work.

- [ ] **2.1 One bug at a time.** *"Fix the failing search test."* Review the diff before accepting.
- [ ] **2.2 Let it loop.** *"Make all the tests pass."* Watch it edit → run tests → fix again.
- [ ] **2.3 Find a hidden bug.** No test covers this one: adding an item with a **negative quantity** is accepted.
  *"Are there any input-validation bugs in store.py? Add tests for them, then fix them."*
- [ ] **2.4 Review.** Run `/code-review` to get a second pass over your changes.

## Level 3: Refactor safely
Learn: changing structure without changing behavior, with tests as a safety net.

- [ ] **3.1** `inventory/report.py` works but is ugly. *"Refactor report.py for readability. The output must not change; keep test_report passing."*
- [ ] **3.2** Run `/simplify` afterward and see what else it suggests.

## Level 4: Add features (plan first)
Learn: Plan mode (Shift+Tab in the CLI, or ask Claude to plan first) for bigger changes.

- [ ] **4.1** *"Plan how to add an `export --csv out.csv` command. Show me the plan before writing code."* Push back on the plan if you'd do it differently.
- [ ] **4.2** Implement it, with tests.
- [ ] **4.3** Your own idea: price history, reorder suggestions, a `--json` output flag...

## Level 5: Teach Claude about your project
Learn: making Claude remember your conventions across sessions.

- [ ] **5.1** Run `/init` to generate a `CLAUDE.md`. Read it and edit it.
- [ ] **5.2** Add a rule, e.g. *"Always use unittest, never pytest"* or *"Use f-strings, not % formatting"*. Start a new session and check it's followed.
- [ ] **5.3** Ask Claude to create a custom slash command / skill, e.g. `/check` that runs the tests and summarizes results.
- [ ] **5.4** Ask Claude to add a hook (via `/update-config`), e.g. "run the tests every time a Python file is edited".

## Level 6: Git workflow
- [ ] **6.1** *"Commit my changes with a good message."*
- [ ] **6.2** Make a branch, add a feature, and ask Claude to summarize the diff against `main`.
- [ ] **6.3** If this is pushed to GitHub: *"Open a pull request for this branch."*

## Level 7: Bigger tools
- [ ] **7.1 Subagents.** *"Use a subagent to review report.py for edge cases while you write the CSV export."*
- [ ] **7.2 Break it on purpose.** Introduce a bug yourself, then just paste the error message to Claude.
- [ ] **7.3 Rebuild it in another language.** *"Port this project to TypeScript with the same tests."*
