# Step F7: Python Structure and Type Hints

Branch: `standards-python-structure`

The last formatting step, and the old step 5, retired into this one on 2026-10-17 before it ran. Read "Formatting comes first" in the README before anything else. Step F3 gave every Python file the spacing, comments, and docstrings of the rule. This step gives every file the rest of `filters.py`'s layout, which moves code, and adds a type hint to every function.

## Decisions this step reads

- Decision 1a (staging), recorded 2026-10-16.
- Decision 27 (how a formatting step reaches production) and decision 28 (the pre-commit hook), recorded in the README. Stop if either is blank.

## Background

The baseline step splits any module that mixes setup, security, filters, and routes. This app has no application module. Its Python is eight standalone tools in `scripts/`, each with one job, plus the test suite. None mixes concerns, so there is nothing to split. The four copies of the case loader in the check scripts are consolidated in step 9A, which has to touch them anyway.

The layout half applies to every file. On 2026-10-16, every Python file kept values at the top level that only one function uses, and two scripts ran their whole job there with no `main()`:

| File | Top-level names on 2026-10-16 |
|---|---|
| `scripts/check_charges.py` | 3 names and 2 loose calls, no `main()` |
| `scripts/check_quotes.py` | 7 names and 2 loose calls, no `main()` |
| `scripts/check_claims.py` | `SRC`, `MID`, `COMPUTABLE`, `REVIEW` |
| `scripts/check_dates.py` | `SRC`, `UNDATED`, `UNDATED_LAG` |
| `scripts/check_overlaps.py` | `REPO`, `CHROME`, `SUBPATH`, `HARNESS` |
| `scripts/check_slugs.py` | `REPO`, `SLUG_RE` |
| `scripts/scout_seen.py` | `REPO`, `LEDGER`, `STATUSES` |
| `tests/conftest.py` | `REPO`, `SCRIPTS`, `PYTHON`, `BROWSER`, and the two loaded scripts |
| `tests/test_browser.py`, `test_checks.py`, `test_headers.py`, `test_pages.py`, `test_static.py` | Constants, parametrize lists, and markers |

`scripts/serve.py` was brought to `REPO` and `PREFIX` as step 5's Python sample, and `tests/test_dependencies.py` (step 3) keeps only `REPO`, so neither needs a layout change. The two harness files step F1 adds were written to the rule.

The type-hint half applies too. This command reported two functions missing a hint on 2026-10-17:

```
python3 ~/.claude/skills/annielytics-comment-style/scripts/add_type_hints.py --missing $(git ls-files '*.py')
```

| File | Line | Function | Missing |
|---|---|---|---|
| `scripts/check_overlaps.py` | 218 | `log_message` | `*args` and the return |
| `scripts/check_slugs.py` | 42 | `main` | the return |

The model for the layout is AI Strategy's `services/filters.py` for the banners, with `scripts/csp-walk/walk.py` for a standalone script, per the "File structure" section of `~/.claude/rules/formatting/code-formatting.md`. Under the README's functions rule, only imports, settings two or more functions share, test parametrize lists and markers, and the entry-point call may stay at the top level.

## The changes

1. Give every Python file `filters.py`'s layout. Banners in order: About This File, Imports (grouped as standard library, third party, and local, each with a one-line label, `import` aligned in a run of `from X import` lines), Global Variables (constants aligned on `=`), then one banner per section. Move each value only one function uses into that function, and give `check_charges.py` and `check_quotes.py` a `main()` called under the entry-point guard. A wrapped signature puts one parameter per line with names and types aligned.
2. Run `add_type_hints.py` (without `--missing`) on every tracked `.py` file to write the hints it can prove from the docstrings.
3. Write the rest by hand, using the real types: `log_message(self, format: str, *args: object) -> None`, and `check_slugs.py`'s `main` return type as its docstring states (`int` if it returns an exit status, `None` otherwise). Test functions return `None`, and fixtures name their real types (`pytest.MonkeyPatch`, Playwright's `Page`, `str`). Python 3.11 runs the venv, so the `X | None` form is safe.
4. Keep each docstring's `Args` and `Returns` types in step with the hints.
5. In `scout_seen.py` and `check_overlaps.py`, build the `--help` description from `__doc__.strip().splitlines()[0]` rather than `__doc__.splitlines()[0]`, then move each About docstring's first sentence onto its own line below the opening quotes, as the other scripts have it. Step F3 left the sentence on the quote line so the help text stayed the same. Show `--help` unchanged for both scripts. In `check_overlaps.py` the sentence wraps onto a second line, so join it first or the help text keeps only its first half, which is what it prints today.

One commit per area (the check scripts, `scout_seen.py`, and the tests), with the layout and the hints as separate commits in each.

## The sample-file review gate

- Layout: `scripts/check_quotes.py` is the sample since it runs its whole job loose at the top level. Roll it up, show its output and exit code unchanged, and stop for approval before the rest.
- Type hints: `scripts/check_overlaps.py` is the sample since its `log_message` takes `*args`, the least obvious type left. Hint it and stop for approval before the rest.

## Proving it

- The hint commits: The `ast.dump` of every file, with annotations stripped, is identical before and after.
- The layout commits: These move code, so the `ast.dump` changes. Every script prints the same output and exit code before and after (`scout_seen.py` through its read-only `check` and `week --today 2026-10-17` subcommands), and both suites pass with the same counts.
- `python3 -m py_compile` passes on every file, and no file keeps a top-level name the README's functions rule does not allow.
- `~/.claude/formatting-tools/check_format.py` exits 0 on every Python file, and `check_style.py` reports 0.

## Done when

The `--missing` command above reports zero, every Python file follows `filters.py`'s layout with no top-level name the functions rule forbids, every script's output and exit code are unchanged, the annotation-stripped `ast.dump` comparison is identical for the hint commits, `check_format.py` passes on every Python file, `check_style.py` reports 0, and both suites pass with the same counts.

## Rollback

Revert the merge commit. Type hints change no behavior, so a partial revert of one file's hints is also safe.

## Paste-ready prompt: build and stage

```
Run step F7 (Python structure and type hints) of the Models Gone Wild
standards cleanup, following docs/standards-cleanup/f7-python-structure.md
exactly. Read docs/standards-cleanup/README.md first, starting with
"Formatting comes first" and the functions rule, then the "File
structure" section of ~/.claude/rules/formatting/code-formatting.md,
~/.claude/skills/annielytics-comment-style/SKILL.md, and
~/.claude/formatting-tools/HANDOFF-prompt.md. Open AI Strategy's
leaderboard_assistant/services/filters.py and scripts/csp-walk/walk.py as
the model. Decisions 1, 27, and 28 apply; stop if 27 or 28 is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step F6 is merged and live (marked done in the README). Branch
   off an up-to-date main as standards-python-structure. Never work on
   main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Record both counts. Run the
   add_type_hints.py --missing command from the step file and record the
   total (2 on 2026-10-17). Save an ast.dump of every tracked .py file with
   annotations stripped, and every script's output and exit code
   (scout_seen.py through its read-only check and week --today 2026-10-17
   subcommands only), both in the session scratchpad.
3. Sample-file review gate (layout): roll scripts/check_quotes.py into
   filters.py's layout with a main() under the entry-point guard. Show its
   output and exit code matching the saved ones, a clickable link, a short
   summary, and the git diff command, then STOP until I approve.
4. Sample-file review gate (type hints): hint scripts/check_overlaps.py,
   keeping its docstrings in step, and give me a clickable link, a short
   summary, and the git diff command, then STOP until I approve.
5. After I approve both, do every other Python file, a commit per area
   (the check scripts, scout_seen.py, and the tests), with the layout and
   the hints as separate commits.
6. Prove it: the annotation-stripped ast.dump for the hint commits, every
   script's output and exit code against the saved ones, py_compile on
   every file, both suites (same counts), the --missing check (zero),
   check_style.py (0), and ~/.claude/formatting-tools/check_format.py on
   every Python file, each gated on its exit code.
7. Push, deploy the branch to staging with the README command, and run
   the staging health check.
8. Report what you verified and how, and STOP. Do not merge to main or
   touch production until I say so. The one exception is decision 27b:
   then run the ship prompt below yourself once every check passes.

When you stop, end your report with a lettered to-do that runs the
ship-to-production prompt at the bottom of
docs/standards-cleanup/f7-python-structure.md when I reply with
its letter. Do not paste that prompt into the report.
```

## Ship-to-production prompt

Claude runs this in the same session when you reply with the ship letter at the end of the step F7 report. It needs no edits.

```
Ship step F7 (Python structure and type hints) of the Models Gone Wild
standards cleanup to production, following
docs/standards-cleanup/f7-python-structure.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step F7 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-python-structure, gating on each exit code.
2. Merge standards-python-structure to main and push.
3. Deploy main to production with the README command and run the production
   health check. The Python ships no page, so this confirms only that the
   deploy left the site whole.
4. Switch staging back to main with the README command.
5. Mark step F7 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
6. Tell me the formatting steps are finished and the next step is step 4,
   and paste its build prompt from the bottom of
   docs/standards-cleanup/04-root-files.md in full, so I can start the
   next session with it.
```
