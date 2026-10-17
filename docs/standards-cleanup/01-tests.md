# Step 1: A Test Suite

Branch: `standards-tests`

Every later step leans on this suite to prove it changed nothing, so it comes first. The pattern is `~/.claude/rules/coding/add-smoke-tests.md`, adapted to a static page. There is no Flask test client, so the route tests run against `scripts/serve.py`, which already serves the repo at the real prefix and answers the same redirects nginx does.

## Decisions this step reads

Decision 2a (the tooltip clamp fix, 8e726b4, is the revert-and-fail bug) and decision 3a (the check scripts run inside the suite), recorded in `docs/standards-cleanup/README.md` on 2026-10-16.

## Background

On 2026-10-16 the app had no `tests/`, no pytest, and no virtualenv. Six check scripts in `scripts/` run by hand, and all six pass on `main`:

| Script | What it checks | Needs |
|---|---|---|
| `check_charges.py` | Charge lengths against the range in `UPDATE.md` | Standard library |
| `check_claims.py` | Copy elsewhere on the page that a case has made untrue | Standard library |
| `check_dates.py` | Lag and timeline order against the dates | Standard library |
| `check_slugs.py` | Poster slugs present, well formed, and unique | Standard library |
| `check_quotes.py` | A quotation in single quotes | Standard library |
| `check_overlaps.py` | Anything drawn on top of something else on the Threat Matrix, under every filter combination | Headless Chrome |

`UPDATE.md` also carries three snippets (leading-slash paths, case completeness, and the poster footer width) that exist only as copy-and-paste commands.

The audit's HIGH CSRF finding is a false positive. There is no form, no POST endpoint, no session, and no cookie. A guard test keeps it that way.

The site header is copied by hand from `index.html` into `methodology/index.html`, with a comment asking that the two stay in step. Nothing checks it.

Two traps are specific to this app:

- The repo root is the web root, so any file at the root is served unless nginx's denylist names its extension. The denylist covers `md`, `txt`, `json`, `yml`, `yaml`, `lock`, and `py`, but not `ini` or `toml`. A root `pytest.ini` would be public. So the suite registers its `browser` marker and the default deselection in `tests/conftest.py` with `pytest_configure` and `pytest_collection_modifyitems`, and no config file goes at the root. Step 13A moves this into a `pytest.ini` once it moves the web root (decision 23a).
- Gitignored files never reach the server, so `venv/` and `.pytest_cache/` stay local.

## The changes

1. `requirements-dev.txt` at the root (the `.txt` denylist covers it) with `pytest` and `playwright`, each pinned with `==` to the version installed. Install into the `venv` from step 0, then `venv/bin/python3 -m playwright install chromium`. Step 3 audits these pins.
2. `.gitignore` gains `.pytest_cache/`.
3. `tests/conftest.py`:
   - Registers the `browser` marker and skips browser tests unless `-m browser` is given.
   - A session fixture that starts `PreviewHandler` from `scripts/serve.py` in a `ThreadingHTTPServer` on port 0 in a background thread, and yields `http://127.0.0.1:<port>/tools/models-gone-wild/`.
   - A fixture that loads the case slugs with the same regex `check_slugs.py` uses, so every poster permalink is tested.
4. `tests/test_pages.py`, through the preview server:
   - The home page, `methodology/`, `threat-matrix/`, `lab-counts/`, and all 21 `poster/<slug>/` permalinks return 200 with the page's `<title>`.
   - `css/styles.css`, `js/html2canvas.min.js`, and `img/annielytics-logo.png` return 200 at the root and under `threat-matrix/` and one poster permalink, as the browser requests them there.
   - The bare prefix and `threat-matrix` without its slash return 301 to the slash form, and `?view=matrix` and `?view=labs` return 301 to their permalinks.
   - An unknown path returns 404.
5. `tests/test_static.py`, reading the files directly:
   - The leading-slash check from `UPDATE.md`, across `index.html`, `methodology/index.html`, and `css/styles.css`.
   - Every case carries the required fields, from `UPDATE.md`'s second snippet.
   - Every poster footer fits on one line, from `UPDATE.md`'s third snippet.
   - The `<header class="site-header">` block in both pages is identical apart from the `../` on the logo path.
   - No page contains a `<form` with `method="post"`, and no script sets `document.cookie`. The CSRF guard.
6. `tests/test_checks.py`, under decision 3a. One test per check script that runs it with `venv/bin/python3` from the repo root and asserts exit 0, printing its output on failure. `check_overlaps.py` carries the `browser` marker.
7. `tests/test_browser.py`, marked `browser`, with Playwright's Chromium against the preview server:
   - The home page loads with no console errors.
   - Each tab shows its view and puts its permalink in the address bar.
   - Opening a case's poster puts `/poster/<slug>/` in the address bar, and Escape closes it and restores the address.
   - The Class filter narrows the timeline and shows the count line.
   - At 375 pixels wide, the MENU label opens and closes the drawer.
   - The revert-and-fail test, under decision 2a. Hover every glossary term in the first three cards at 1440 and 375 pixels wide, and assert each bubble sits at least 10px inside `.content` on both sides.
8. After the first run, set `com.dropbox.ignored` on every new `__pycache__` folder:

   ```
   find . -name __pycache__ -type d -not -path './venv/*' -not -path './.git/*' -exec xattr -w com.dropbox.ignored 1 {} \;
   ```

Every test gets a docstring in the house format, per the annielytics-comment-style skill.

## The revert-and-fail proof

Prove the suite catches the decision 2a bug. 8e726b4 added the horizontal clamp in `positionTip()` (the `minX` and `maxX` lines and the two `if` statements that apply them). Delete those lines in the working tree, run `venv/bin/python3 -m pytest -m browser tests/test_browser.py`, show the failure, then restore them with `git checkout index.html` and show the pass. Paste both outcomes into the report. A test that passes on both is worse than none.

## The sample-file review gate

The step adds several Python test files. `tests/test_pages.py` is the sample since it exercises the preview server fixture every other file leans on. Write it with `conftest.py` first, run it, and stop for Annie's approval before writing the rest.

## Done when

`venv/bin/python3 -m pytest` and `venv/bin/python3 -m pytest -m browser` both pass, and the revert-and-fail proof shows a failure on the reverted code and a pass on the restored code.

## Rollback

Revert the commits. The suite adds files and changes no shipped file, so nothing a visitor sees moves.

## Paste-ready prompt: build and stage

```
Run step 1 (tests) of the Models Gone Wild standards cleanup, following
docs/standards-cleanup/01-tests.md exactly. Read
docs/standards-cleanup/README.md and ~/.claude/rules/coding/add-smoke-tests.md
first. Use decisions 1, 2, and 3 as recorded in the README, and stop if any
is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm steps 0 and 0B are marked done in the README. Branch off an up-to-date main as standards-tests. Never work on
   main.
2. Run the six check scripts in scripts/ and confirm each exits 0 before
   any change.
3. Create requirements-dev.txt with pytest and playwright pinned to what you
   install into venv, run venv/bin/python3 -m playwright install chromium,
   and add .pytest_cache/ to .gitignore. Put no pytest.ini at the root.
4. Sample-file review gate (Python): write tests/conftest.py and
   tests/test_pages.py first, run them, then give me clickable links to both,
   a short summary, the pass count, and the git diff command, and STOP until
   I approve. Carry any correction into the rest.
5. After I approve, write tests/test_static.py, tests/test_checks.py
   and tests/test_browser.py as the step file lists.
6. Do the revert-and-fail proof on 8e726b4's tooltip clamp and paste both
   outcomes.
7. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser,
   gating on each exit code, then run
   python3 ~/.claude/skills/annielytics-comment-style/scripts/check_style.py
   and confirm the count is no higher than on main (75). Mark every new
   __pycache__ folder Dropbox-ignored.
8. Commit, push, and deploy the branch to staging with the
   README command and run the staging health check. Report what you verified and how, and STOP. Do not merge to main
   or touch production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/01-tests.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step 1 report. It needs no edits.

```
Ship step 1 (tests) of the Models Gone Wild standards cleanup to
production, following docs/standards-cleanup/01-tests.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 1 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-tests, gating on each exit code.
2. Merge standards-tests to main and push.
3. Deploy main to production with the README command and run the
   production health check. Confirm tests/conftest.py and
   requirements-dev.txt return 404 at the origin:
   curl -sk -H "Host: www.annielytics.com" -o /dev/null -w "%{http_code}\n" https://127.0.0.1/tools/models-gone-wild/tests/conftest.py
   curl -sk -H "Host: www.annielytics.com" -o /dev/null -w "%{http_code}\n" https://127.0.0.1/tools/models-gone-wild/requirements-dev.txt
4. Switch staging back to main with the README command.
5. Mark step 1 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
6. Tell me the next step is step 2, whose prompt is at the bottom of
   docs/standards-cleanup/02-security.md.
```
