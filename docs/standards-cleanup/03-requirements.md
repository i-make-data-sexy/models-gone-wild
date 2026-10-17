# Step 3: Requirements

Branch: `standards-requirements`

## Decisions this step reads

Decision 7a (a pinned `requirements-dev.txt`, no `requirements.txt`, and a record of html2canvas), recorded in `docs/standards-cleanup/README.md` on 2026-10-16.

## Background

On 2026-10-16 the app had no requirements file of either kind, and the audit reported "No requirements.txt" at LOW. That is by design rather than an oversight:

- Production installs nothing. Nginx serves files off disk.
- Every script in `scripts/` imports the standard library only (`argparse`, `datetime`, `functools`, `html`, `http.server`, `json`, `os`, `re`, `shutil`, `subprocess`, `sys`, `tempfile`, `threading`, `urllib.parse`). `check_overlaps.py` drives Chrome through a subprocess rather than a library.
- The one third-party dependency is the vendored `js/html2canvas.min.js`, version 1.4.1 from 2022, which is the latest release. Its SHA-256 on 2026-10-16 was `e87e550794322e574a1fda0c1549a3c70dae5a93d9113417a429016838eab8cb`. `pip-audit` cannot see a JavaScript file.

Step 1 added `requirements-dev.txt` with `pytest` and `playwright`. This step makes the baseline's check true of it.

## The changes

Under decision 7a, the step makes six changes.

1. Confirm every line of `requirements-dev.txt` is pinned with `==`, and that it lists exactly what the suite imports (`pytest`, `playwright`), not their transitive dependencies.
2. Run `pip-audit` against it with a throwaway install (`venv/bin/python3 -m pip install pip-audit`, then `venv/bin/python3 -m pip_audit -r requirements-dev.txt`). Bump only what it flags, to the release it names. Do not add `pip-audit` to the file; it is a tool you run, not one the suite needs.
3. Rebuild the venv from the file to prove it is complete: `rm -rf venv`, recreate it on `/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11`, re-apply `com.dropbox.ignored` to `venv` at once (recreating the folder drops the attribute), install `-r requirements-dev.txt`, run `playwright install chromium`, and run both suites.
4. Write `js/VENDORED.md` naming html2canvas, its version, where it came from (`https://html2canvas.hertzen.com`), its license (MIT), its SHA-256, and the one place the app uses it. `.md` is on nginx's denylist, so it stays private.
5. Add a test that hashes `js/html2canvas.min.js` and compares it with the SHA-256 in `js/VENDORED.md`, so a changed library cannot pass unnoticed.
6. Add a test that every line of `requirements-dev.txt` is a `name==version` pin.

No `requirements.txt` is added. A file listing nothing would suggest production installs something.

## The sample-file review gate

Each filetype changes in one file, so there is nothing to sample.

## Done when

Every line of `requirements-dev.txt` is pinned with `==`, `pip-audit -r requirements-dev.txt` reports no known vulnerabilities, both suites pass on the rebuilt venv, and `xattr -p com.dropbox.ignored venv` prints 1.

## Rollback

Revert the commits. Rebuild the venv from the previous `requirements-dev.txt` if a bump caused trouble.

## Paste-ready prompt: build and stage

```
Run step 3 (requirements) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/03-requirements.md exactly. Read
docs/standards-cleanup/README.md first. Use decisions 1 and 7 as recorded in
the README, and stop if either is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step 2 is merged and live. Branch off an up-to-date main as
   standards-requirements. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change.
3. Check the pins in requirements-dev.txt, run pip-audit against it, and
   bump only what it flags. Show me the pip-audit output.
4. Rebuild venv from the file on Python 3.11 from
   /Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11,
   re-apply com.dropbox.ignored to venv immediately, install, install
   Chromium for Playwright, and run both suites, gating on each exit code.
5. Write js/VENDORED.md and the two tests the step file lists.
6. Run the comment style checker (no higher than main), commit, push, and
   deploy the branch to staging with the README command and
   run the staging health check.
7. Report what you verified and how, and STOP. Do not merge to main or touch
   production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/03-requirements.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step 3 report. It needs no edits.

```
Ship step 3 (requirements) of the Models Gone Wild standards cleanup to
production, following docs/standards-cleanup/03-requirements.md and the
rules in docs/standards-cleanup/README.md. This is my go-ahead for step 3
only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-requirements, gating on each exit code.
2. Merge standards-requirements to main and push.
3. Deploy main to production with the README command and run the production
   health check. Confirm js/VENDORED.md returns 404 at the origin:
   curl -sk -H "Host: www.annielytics.com" -o /dev/null -w "%{http_code}\n" https://127.0.0.1/tools/models-gone-wild/js/VENDORED.md
4. Switch staging back to main with the README command.
5. Mark step 3 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
6. Tell me the next step is step 4, whose prompt is at the bottom of
   docs/standards-cleanup/04-root-files.md.
```
