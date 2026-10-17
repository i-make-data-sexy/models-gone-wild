# Step 5: Python Structure and Type Hints

Branch: `standards-type-hints`

## Background

The baseline step splits any module that mixes setup, security, filters, and routes, and adds type hints to every function. This app has no application module. Its Python is eight standalone tools in `scripts/` (1,247 lines), each with one job and a `main()`, plus the test suite from step 1. None mixes setup, security, filters, and routes, so there is nothing to split. The four copies of the case loader in the check scripts are consolidated in step 9A, which has to touch them anyway.

The type-hint half applies. On 2026-10-16, this command reported five functions. The three in `scripts/serve.py` were hinted with the Python sample for the stricter review gate, so two remain:

```
python3 ~/.claude/skills/annielytics-comment-style/scripts/add_type_hints.py --missing $(git ls-files '*.py')
```

| File | Line | Function | Missing |
|---|---|---|---|
| `scripts/check_overlaps.py` | 218 | `log_message` | `*args` and the return |
| `scripts/check_slugs.py` | 42 | `main` | the return |

The tests written in steps 1 to 4 must carry hints too. Run the check on them as well.

The README's rule on functions applies too. On 2026-10-16, every Python file kept values at the top level that only one function uses, and two scripts ran their whole job there with no `main()`:

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

`scripts/serve.py` was brought down to `REPO` and `PREFIX` as the Python sample for the stricter review gate, so it needs no further change here.

## The changes

1. Run `add_type_hints.py` (without `--missing`) on every tracked `.py` file to write the hints it can prove from the docstrings.
2. Write the rest by hand, using the real types: `log_message(self, format: str, *args: object) -> None` and `check_slugs.py`'s `main` return type as its docstring states (`int` if it returns an exit status, `None` otherwise). Test functions return `None`, and fixtures name their real types (`pytest.MonkeyPatch`, Playwright's `Page`, `str`).
3. Keep each docstring's `Args` and `Returns` types in step with the hints.
4. Roll every file's top-level code into functions under the README's rule. Move each value only one function uses into that function, give `check_charges.py` and `check_quotes.py` a `main()` called under the entry-point guard, and leave only imports, shared settings, parametrize lists, markers, and the entry-point call at the top level. Prove each script unchanged by running it before and after and comparing its output and exit code, and prove the tests by the same pass count.

## The sample-file review gate

- Type hints: `scripts/check_overlaps.py` is the sample since its `log_message` takes `*args`, the least obvious type left. Hint it first and stop for approval before the rest.
- Top-level code: `scripts/check_quotes.py` is the sample since it runs its whole job loose at the top level. Roll it up and stop for approval before the rest.

## Done when

```
python3 ~/.claude/skills/annielytics-comment-style/scripts/add_type_hints.py --missing $(git ls-files '*.py')
```

reports zero, `python3 -m py_compile` passes on every tracked `.py` file, both suites pass, every script prints the same output and exit code as before, and no file keeps a top-level name the README's rule does not allow.

## Rollback

Revert the commit. Hints change no behavior.

## Paste-ready prompt: build and stage

```
Run step 5 (Python structure and type hints) of the Models Gone Wild
standards cleanup, following docs/standards-cleanup/05-python-structure.md
exactly. Read docs/standards-cleanup/README.md first. Use decision 1 as
recorded in the README, and stop if it is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step 4 is merged and live. Branch off an up-to-date main as
   standards-type-hints. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Run add_type_hints.py --missing
   on every tracked .py file and show me the count.
3. Sample-file review gate (Python): hint scripts/check_overlaps.py first, keep its
   docstrings in step, and give me a clickable link, a short summary, and
   the git diff command. STOP until I approve.
4. After I approve, hint every other tracked .py file, the tests included.
5. Roll each file's top-level code into functions under the README's rule,
   starting with scripts/check_quotes.py as the sample. Run it before and
   after, show me the matching output and exit code with a clickable link,
   a short summary, and the git diff command, and STOP until I approve.
   Then do the rest, proving each the same way.
6. Run add_type_hints.py --missing (must report zero), py_compile on every
   tracked .py file, both suites, and the comment style checker, gating on
   each exit code.
7. Commit, push, and deploy the branch to staging with the
   README command and run the staging health check.
8. Report what you verified and how, and STOP. Do not merge to main or touch
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
