# Step 5: Python Structure and Type Hints

Branch: `standards-type-hints`

## Background

The baseline step splits any module that mixes setup, security, filters, and routes, and adds type hints to every function. This app has no application module. Its Python is eight standalone tools in `scripts/` (1,247 lines), each with one job and a `main()`, plus the test suite from step 1. None mixes setup, security, filters, and routes, so there is nothing to split. The four copies of the case loader in the check scripts are consolidated in step 9A, which has to touch them anyway.

The type-hint half applies. On 2026-10-16, this command reported five functions:

```
python3 ~/.claude/skills/annielytics-comment-style/scripts/add_type_hints.py --missing $(git ls-files '*.py')
```

| File | Line | Function | Missing |
|---|---|---|---|
| `scripts/check_overlaps.py` | 218 | `log_message` | `*args` and the return |
| `scripts/check_slugs.py` | 42 | `main` | the return |
| `scripts/serve.py` | 68 | `do_GET` | the return |
| `scripts/serve.py` | 80 | `redirect` | the return |
| `scripts/serve.py` | 96 | `main` | the return |

The tests written in steps 1 to 4 must carry hints too. Run the check on them as well.

## The changes

1. Run `add_type_hints.py` (without `--missing`) on every tracked `.py` file to write the hints it can prove from the docstrings.
2. Write the rest by hand, using the real types: `log_message(self, format: str, *args: object) -> None`, `do_GET(self) -> None`, `redirect(self, location: str) -> None`, and the two `main` functions' return types as their docstrings state (`int` where they return an exit status, `None` otherwise). Test functions return `None`, and fixtures name their real types (`pytest.MonkeyPatch`, Playwright's `Page`, `str`).
3. Keep each docstring's `Args` and `Returns` types in step with the hints.

## File structure

`scripts/serve.py`, the sample, and every script this step edits, follow the "File structure" section of `~/.claude/rules/formatting/code-formatting.md`, laid out like AI Strategy's `leaderboard_assistant/services/filters.py` for a module and its `app.py` for an app factory. Read both before writing anything.

- Banners, in order: About This File (the module docstring), Imports (standard library, third party, and local, each with a one-line label, `import` aligned in a run of `from X import` lines), Global Variables (constants, aligned on `=`), then one banner per section, with three blank lines above each.
- No loose code. Every statement sits in a named function, apart from the imports, the constants, and the one call that builds the module's object (`app = create_app()` in an app factory). A long function becomes one helper per part, never banners inside one body.
- Comments are one-line labels of 50 characters or fewer, docstring explanations are one line, and each function has a blank line after its docstring.
- Run `python3 -I ~/.claude/formatting-tools/format_py.py` and `python3 -I ~/.claude/formatting-tools/audit_format.py` on each of these files, and show the sample only once the audit reports nothing.
- Each script keeps its `main()` under the entry-point guard. Any statement still loose at the top level moves into the function that uses it.

## The sample-file review gate

`scripts/serve.py` is the Python sample since it holds three of the five and the handler methods whose types are least obvious. Hint it and bring it to the layout above first, and stop for approval before the rest.

## Done when

```
python3 ~/.claude/skills/annielytics-comment-style/scripts/add_type_hints.py --missing $(git ls-files '*.py')
```

reports zero, `python3 -m py_compile` passes on every tracked `.py` file, `audit_format.py` reports nothing on every script this step edited, and both suites pass.

## Rollback

Revert the commit. Hints change no behavior.

## Paste-ready prompt: build and stage

```
Run step 5 (Python structure and type hints) of the Models Gone Wild
standards cleanup, following docs/standards-cleanup/05-python-structure.md
exactly. Read docs/standards-cleanup/README.md first. Use decision 1 as
recorded in the README, and stop if it is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Confirm step 4 is merged and live. Branch off an up-to-date main as
   standards-type-hints. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Run add_type_hints.py --missing
   on every tracked .py file and show me the count.
3. Sample-file review gate (Python): hint scripts/serve.py first, keep its
   docstrings in step, and lay it out per the step file's File structure
   section, like AI Strategy's leaderboard_assistant/services/filters.py
   (read it first), with format_py.py and audit_format.py clean. Give me a
   clickable link, a short summary, and the git diff command. STOP until I
   approve.
4. After I approve, hint every other tracked .py file, the tests included,
   and bring every script you edit to the same layout.
5. Run add_type_hints.py --missing (must report zero), py_compile on every
   tracked .py file, both suites, and the comment style checker, gating on
   each exit code.
6. Commit, push, and deploy the branch to staging with the
   README command and run the staging health check.
7. Report what you verified and how, and STOP. Do not merge to main or touch
   production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/05-python-structure.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step 5 report. It needs no edits.

```
Ship step 5 (Python structure and type hints) of the Models Gone Wild
standards cleanup to production, following
docs/standards-cleanup/05-python-structure.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 5 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-type-hints, gating on each exit code.
2. Merge standards-type-hints to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Switch staging back to main with the README command.
5. Mark step 5 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
6. Tell me the next step is step 6, whose prompt is at the bottom of
   docs/standards-cleanup/06-comment-style.md.
```
