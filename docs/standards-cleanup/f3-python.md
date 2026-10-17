# Step F3: Format the Python

Branch: `standards-format-python`

The third formatting step. Read "Formatting comes first" in the README before anything else. This step changes whitespace, comments, and docstrings only, so every Python file reads the way AI Strategy's Python reads. The structural half of that layout (the Imports and Global Variables banners, no loose code, and type hints) is step F7 since it moves code and needs its own proof.

## Decisions this step reads

- Decision 1a (staging), recorded 2026-10-16.
- Decision 27 (how a formatting step reaches production) and decision 28 (the pre-commit hook), recorded in the README. Stop if either is blank.

## Background

Measured with `audit_format.py` and `check_format.py` on 2026-10-17, read only. There are 15 tracked Python files, 2,508 lines. Seven already pass, namely `scripts/serve.py`, brought to the rule as step 5's Python sample, and the six test files written to it in steps 1 and 3. The other eight fail:

| File | Lines | About section | Uneven runs | Comments over one line | Wordy | History | Banner problems |
|---|---|---|---|---|---|---|---|
| `scripts/scout_seen.py` | 204 | Missing | 5 | 2 | 2 | 2 | 2 |
| `scripts/check_dates.py` | 195 | Missing | 9 | 1 | 1 | 0 | 0 |
| `scripts/check_overlaps.py` | 317 | Missing | 2 | 2 | 2 | 0 | 3 |
| `scripts/check_claims.py` | 277 | Missing | 5 | 0 | 1 | 0 | 2 |
| `scripts/check_quotes.py` | 41 | Missing | 2 | 1 | 1 | 0 | 0 |
| `scripts/check_charges.py` | 31 | Missing | 2 | 0 | 0 | 0 | 0 |
| `scripts/check_slugs.py` | 68 | Missing | 0 | 0 | 0 | 0 | 1 |
| `tests/test_headers.py` | 85 | Present | 0 | 0 | 1 | 1 | 0 |

Six of the eight also end with a newline. `check_style.py` reports 51 docstring issues in five of them, nearly all a missing blank line before `Args:` or `Returns:`: `scout_seen.py` 16, `check_claims.py` 12, `check_overlaps.py` 11, `check_dates.py` 8, and `check_slugs.py` 4. After F1 and F2 these are the last 51 of its 70, so this step brings it to 0.

The scripts are standalone tools with a `main()`, not modules of an app, so the closest models are AI Strategy's `leaderboard_assistant/scripts/csp-walk/walk.py` for a script and its `services/filters.py` for the banners and docstrings. The rules are the Python section of `~/.claude/rules/formatting/code-formatting.md`, and the worked example is `~/.claude/formatting-examples/03-python.py`. The comment-style skill governs banners and docstrings.

## The changes

One commit per pass, all four passes on the sample first.

1. Alignment and spacing: Run `format_py.py`. Consecutive assignments align their `=`, keyword arguments in a multi-line call align, dict values align after the colon, siblings in a bracket share a column, `from X import` runs align their `import`, wrapped conditions lead with `and` and `or`, and trailing comments in a block share one column. Three blank lines above a section banner, two above a subsection banner, one blank line after every docstring, and no newline at the end of the file.
2. Dead code and history: Run `strip_dead_comments.py`, printing every comment removed. Step and decision numbers, dates, "moved out of", and "used to" go since git keeps that record.
3. About This File: Run `add_about_py.py`, turning each module docstring into the About This File section.
4. One-line comments and docstrings: Run the comment-style skill's `docstring_layout.py` for the blank lines, then a reviewed JSON list applied with `apply_comment_edits.py`. Every comment is one line, a short label. A docstring's explanation paragraph and each Args and Returns entry are one line. A warning that stops a line being "fixed" wrongly stays, cut to its label.

In the last commit, add `py` to `scripts/git-hooks/format-languages` (under decision 28a).

## The sample-file review gate

- Python: `scripts/scout_seen.py` is the sample, the file with the most findings (14) and the most docstring issues (16). It carries constants, a ledger it reads and writes, history notes, and long docstrings, so it exercises every pass. Run all four passes on it and stop for approval before the other seven.

## Proving it

- `python3 -I ~/.claude/formatting-tools/verify_equivalent.py py main <files>` exits 0 for the alignment, dead-code, and About passes, and `verify_equivalent.py py-comments main <files>` exits 0 for the docstring pass, so the `ast.dump` of every file is identical.
- `git ls-files '*.py' | xargs python3 -m py_compile` passes.
- Every script prints the same output and exit code before and after (`scout_seen.py` through its read-only `check` and `week` subcommands).
- Both suites pass with the same counts before every commit.
- `check_style.py` reports 0, and `~/.claude/formatting-tools/check_format.py` exits 0 on every Python file. Three files read top to bottom look like `walk.py`.

## Done when

`~/.claude/formatting-tools/check_format.py` passes on all 15 Python files, `verify_equivalent.py` passes on every file, every script's output and exit code are unchanged, `check_style.py` reports 0, and both suites pass with the same counts.

## Rollback

Revert the merge commit. The code is unchanged by construction.

## Paste-ready prompt: build and stage

```
Run step F3 (format the Python) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/f3-python.md exactly. Read
docs/standards-cleanup/README.md first, starting with "Formatting comes
first", then ~/.claude/rules/formatting/code-formatting.md,
~/.claude/formatting-examples/03-python.py,
~/.claude/skills/annielytics-comment-style/SKILL.md, and
~/.claude/formatting-tools/HANDOFF-prompt.md. Open AI Strategy's
leaderboard_assistant/scripts/csp-walk/walk.py and services/filters.py as
the model. Decisions 1, 27, and 28 apply; stop if 27 or 28 is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step F2 is merged and live (marked done in the README). Branch
   off an up-to-date main as standards-format-python. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Record both counts. Run every
   script in scripts/ and save its output and exit code in the session
   scratchpad (scout_seen.py through its read-only check and
   week --today 2026-10-17 subcommands only, which never write the ledger).
3. Sample-file review gate (Python): run all four passes on
   scripts/scout_seen.py (alignment and spacing, dead code and history,
   About This File, one-line comments and docstrings), one commit per
   pass, and prove it with verify_equivalent.py (py, and py-comments for
   the docstring pass) and a matching output and exit code. Give me a
   clickable link to it, a short summary, every comment you deleted, and
   the git diff command, then STOP until I approve. Carry any correction I
   ask for into the rest.
4. On approval, do the other seven failing Python files, one commit per
   pass, and confirm the seven clean files still pass. Add py to
   scripts/git-hooks/format-languages in the last commit.
5. Prove it: verify_equivalent.py against main on every file, py_compile
   on every file, every script's output and exit code against the saved
   ones, both suites (same counts), check_style.py (0), and
   ~/.claude/formatting-tools/check_format.py on every Python file, each
   gated on its exit code. Read three files top to bottom.
6. Push, deploy the branch to staging with the README command, and run
   the staging health check.
7. Report what you verified and how, and STOP. Do not merge to main or
   touch production until I say so. The one exception is decision 27b:
   then run the ship prompt below yourself once every check passes.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/f3-python.md, copied exactly, so I
can paste it.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step F3 report. It needs no edits.

```
Ship step F3 (format the Python) of the Models Gone Wild standards cleanup
to production, following docs/standards-cleanup/f3-python.md and the rules
in docs/standards-cleanup/README.md. This is my go-ahead for step F3 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-format-python, gating on each exit code.
2. Merge standards-format-python to main and push.
3. Deploy main to production with the README command and run the production
   health check. The Python ships no page, so this confirms only that the
   deploy left the site whole.
4. Switch staging back to main with the README command.
5. Mark step F3 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
6. Tell me the next step is step F4, whose prompt is at the bottom of
   docs/standards-cleanup/f4-html.md.
```
