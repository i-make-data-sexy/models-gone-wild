# Step 13A: The URL List and the Web Root

Branch: `standards-web-root`

The first half of the baseline's URL step, which goes last because it can break a ranked URL with no error to show for it. This half builds the before-and-after URL list and settles what the web root holds. Step 13B does the canonicals.

## Decisions this step reads

Decision 1 (staging), decision 22 (the prefix mechanism), and decision 23 (repo tooling in the web root), from `docs/standards-cleanup/README.md`.

## Background

The app handled its URLs this way on 2026-10-16:

- Pages and assets use relative paths. The view and poster permalinks (`threat-matrix/`, `lab-counts/`, `poster/<slug>/`) are the same `index.html`. Nginx serves them by stripping the segment and matching again (`rewrite ... last`), which also serves every asset under every permalink (`threat-matrix/css/...`, `poster/<slug>/js/...`).
- The script derives `APP_BASE` from the address bar, so it works under any prefix.
- `scripts/serve.py` reimplements nginx's redirects and strip-and-rematch for the local preview, and `scripts/check_overlaps.py` names the prefix once (`SUBPATH`).
- No shipped page, stylesheet, or script hardcodes the prefix. The five strings in shipped files are all comments.

So the prefix is handled by one mechanism (relative paths through nginx's rewrites), mirrored by two tools. Decision 22 keeps it (22a), replaces the asset rewrites with a `<base href>` in each page (22b), or switches to root-relative paths (22c).

The web root is the git checkout. Besides the site, it holds `.claude/`, `scout/`, `scripts/`, `tests/`, `deploy/`, `docs/`, `DEPLOY.md`, `UPDATE.md`, `requirements-dev.txt`, and the git hook. An extension denylist keeps most of them private, but `deploy/nginx/headers.conf` (step 2) and `scripts/git-hooks/pre-commit` (step 8) are served today, harmlessly, and any new kind of file would be public until someone extends the denylist.

## The URL list

Add `scripts/url-list/run.sh <ref>`, which serves the ref from a worktree under `/tmp` with its own `scripts/serve.py` and writes, for every URL below, the status, the `Location` header, the canonical tag, and the robots meta, to `/tmp/mgw-url-list/<ref>.tsv`:

- The home page, `/index.html`, `threat-matrix/`, `lab-counts/`, all 21 poster permalinks, `methodology/`, `methodology/index.html`, and the 404 page.
- The bare prefix, `threat-matrix` and a poster without their slashes, and `?view=matrix` and `?view=labs`.
- Each stylesheet, script, font, and image, at the root and under one view and one poster permalink.
- `DEPLOY.md`, `UPDATE.md`, `scripts/serve.py`, `deploy/nginx/headers.conf`, `scripts/git-hooks/pre-commit`, `.claude/skills/models-gone-wild-add-case/SKILL.md`, and `.git/config`.

Add `scripts/url-list/origin.sh <host>`, which runs the same list on the server against nginx at `https://127.0.0.1` with the given `Host` header, so staging and production can be compared with the local run. `diff` of two lists is the proof.

## The changes

1. Build the URL list and record `main` locally and on production before anything else.
2. Under decision 23a, `git mv` the site into `public/`: `index.html`, `404.html`, `methodology/`, `css/`, `js/`, `img/`, and `fonts/`. Point `scripts/serve.py`, `scripts/check_overlaps.py`, `scripts/cases.py`, the tests, and the screenshot and CSP harnesses at `public/`. Update `UPDATE.md`, `DEPLOY.md`, both copies of the add-case skill (its footer-date `sed` edits `public/index.html`), and `scout/SCOUT.md`. Move the pytest marker config from `tests/conftest.py` into a root `pytest.ini`, now that the root is private, and update the root allowlist (`index.html` and `404.html` leave it; `pytest.ini` joins). On both servers, change every `alias` to `/home/anniecushing/apps/<staging/>models-gone-wild/public/...`, and delete the denylist block since nothing outside `public/` can be reached. Keep the server-wide `.git` and `.env` rules as they are.
3. Under decision 23b, add a block returning 404 for `^/tools/models-gone-wild/(scripts|scout|tests|deploy|docs|\.claude)/`, add `conf` and `ini` to the denylist, and add `tests/test_served.py`, which lists every tracked file and fails on one nginx would serve that is not a page, stylesheet, script, font, or image.
4. Apply decision 22. Under 22a, add a test that `serve.py`'s redirects and strip-and-rematch agree with the nginx blocks shown in `DEPLOY.md`. Under 22b or 22c, change the paths and the nginx blocks together, and expect the asset-under-permalink rows to change in the URL list.

## The sample-file review gate

- Python: `scripts/serve.py` is the sample since every other tool and test serves through it. Point it at `public/` (23a), run the URL list against the branch, and stop for approval before the other scripts and tests.
- Markdown: `UPDATE.md` is the sample, then the skill copies, `DEPLOY.md`, and `SCOUT.md`.
- HTML: Under 22a and 23a the pages move without edits, so there is nothing to sample. Under 22b or 22c, `index.html` is the sample.

## Done when

The URL list for the branch matches `main` row for row, locally and at the staging origin, except that the private files now return 404 instead of 403 or the denylist's 404 (23a), and the asset-under-permalink rows under 22b or 22c. Every remaining difference is shown and approved. Both suites, the CSP walk, the five check scripts, and `check_overlaps.py` pass, and the screenshot diff is pixel-identical.

## Rollback

Revert the commit and restore the config backup on each server, run `sudo nginx -t`, reload, and add a PCI row. Under 23a the code and the config must roll back together, in one command, as they shipped.

## Paste-ready prompt: build and stage

```
Run step 13A (the URL list and the web root) of the Models Gone Wild
standards cleanup, following docs/standards-cleanup/13a-web-root.md
exactly. Read docs/standards-cleanup/README.md first. Use decisions 1, 22,
and 23 as recorded in the README, and stop if any is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Confirm step 12 is merged and live. Branch off an up-to-date main as
   standards-web-root. Never work on main.
2. Run both suites, the CSP walk, and the five check scripts, and confirm
   they pass.
3. Build scripts/url-list/run.sh and origin.sh. Record main locally and at
   the production origin (Host: www.annielytics.com), and show me both
   lists.
4. Sample-file review gate (Python): under decision 23a, git mv the site
   into public/ and point scripts/serve.py at it. Run the URL list against
   the branch and diff it with main. Give me a clickable link to serve.py,
   a short summary, the diff, and the git diff command, and STOP until I
   approve. Under 23b, do the served-files test and the nginx additions
   instead.
5. After I approve, update the other tools, the tests, the harnesses, and
   the root allowlist, then the docs (UPDATE.md first as the Markdown
   sample, STOP for approval, then both skill copies, DEPLOY.md, and
   SCOUT.md). Apply decision 22.
6. Run both suites, the CSP walk, the five check scripts,
   check_overlaps.py, the screenshot diff (pixel-identical), and the
   comment style checker (0), gating on each exit code.
7. Under decision 1a, on the server: back up
   /etc/nginx/sites-available/staging.annielytics.conf and write the new
   staging blocks to a scratch file. Show me the diff and STOP until I
   approve. Then, in ONE ssh command, deploy the branch to staging, copy the
   new blocks in, run sudo nginx -t, and reload, so the staging page is
   never without a matching config. Wait two seconds, and write the PCI
   change-log row yourself, reading it back.
8. Run origin.sh against staging and diff it with the production list from
   step 3. Show me every difference.
9. Report what you verified and how, give me the staging links, and STOP.
   Do not merge to main or touch production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/13a-web-root.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once the staging URL list checks out. It needs no edits.

```
Ship step 13A (the URL list and the web root) of the Models Gone Wild
standards cleanup to production, following
docs/standards-cleanup/13a-web-root.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 13A only,
including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-web-root, gating on each exit code.
2. Merge standards-web-root to main and push.
3. Back up /etc/nginx/sites-available/annielytics.conf, and write the new
   production blocks to a scratch file on the server. Show me the diff and
   wait for my OK.
4. In ONE ssh command, pull main in ~/apps/models-gone-wild, copy the new
   blocks in, run sudo nginx -t, and reload. If nginx -t fails, restore the
   backup and git reset to the previous commit in the same command. Wait
   two seconds.
5. Write the PCI change-log row yourself and read it back.
6. Run origin.sh against production and diff it with the list from before
   the change. Show me every difference, and run the production health
   check.
7. Under decision 1a, switch staging back to main with the README command.
8. Mark step 13A done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
9. Give me the production links to spot-check with a hard refresh. Then
   tell me the next step is step 13B, whose prompt is at the bottom of
   docs/standards-cleanup/13b-canonicals.md.
```
