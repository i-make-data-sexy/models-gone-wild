# Step 9A: Move the Case Data Out of the Inline Script

Branch: `standards-case-data`

The first half of the baseline's inline-code step. The case data moves on its own because it is what every tool, the skill, and the scout read. Step 9B moves the rest of the code.

## Decisions this step reads

Decision 11a (you publish or close the open scout branches first), decision 14a (plain `js/cases.js` and `js/glossary.js`), and decision 15a (html2canvas moves to `js/vendor/`, and only that folder and `img/` keep the 30-day cache), recorded in `docs/standards-cleanup/README.md` on 2026-10-16. Decision 30 (the case data's layout), recorded in the README. Stop if it is blank.

## Background

On 2026-10-16, `index.html`'s one inline `<script>` ran from line 217 to 2214. The `CASES` array (21 cases) sat at lines 259 to 669, under a 40-line comment documenting the fields, and the `GLOSSARY` object (the security terms every case's prose is matched against) followed it. Both are content the add-case skill edits on every new case.

These read the cases by matching `<script>(.*?)</script>` in `index.html`, each with its own copy of the loader:

- `scripts/check_charges.py` (line 15), `check_claims.py` (line 36), `check_dates.py` (line 48), and `check_slugs.py` (line 33).
- `UPDATE.md`'s second and third checks.
- Step 3 of the add-case skill (line 27), in both copies. `scout/SCOUT.md` loads the cases "with the snippet in Step 1" of that skill.
- Step 1's `tests/test_static.py`, which carries the two `UPDATE.md` checks.

`check_quotes.py` scans the whole of `index.html` for single-quoted quotations, so it has to scan the data file too. `check_overlaps.py` symlinks the whole repo and renders the page, so it keeps working.

Two scout branches from 2026-10-07, `update/claude` and `update/sol`, edit `CASES` inside `index.html`. Merged after this step, they would put cases back in the wrong place, so decision 11 settles them first.

Nginx hard-caches everything under `js/` and `img/` for 30 days (`expires 30d`, `public, no-transform`). A data file there would reach returning readers up to a month late, and Cloudflare would cache it too.

## The changes

1. Confirm decision 11a is done. `git log --oneline origin/main..origin/update/claude -- index.html` and the same for `update/sol` print nothing, or the branches are gone. If either still carries unmerged `CASES` edits, stop.
2. Narrow the long cache, under decision 15a.
   - `git mv js/html2canvas.min.js js/vendor/html2canvas.min.js`, move `js/VENDORED.md` beside it, and update the `<script src>`, the hash test, and `DEPLOY.md`.
   - Narrow the asset rule on both servers to `^/tools/models-gone-wild/(js/vendor|img)/([\w.-]+\.(?:js|png|jpe?g|svg|webp|ico))$`, aliasing `/home/anniecushing/apps/<staging/>models-gone-wild/$1/$2`, so `js/*.js` falls through to the no-cache page block like `css/`.
3. Under decision 14a, move `CASES` and its field comment into `js/cases.js`, and `GLOSSARY` into `js/glossary.js`, as plain scripts with the same object syntax. Give each an About This File section. Under decision 30a, align the data as it moves (48 uneven runs in `CASES` and 1 in `GLOSSARY` on 2026-10-17) and update every pattern that reads the unaligned form, so the skill and the scout write aligned cases. Those patterns are in the loader in step 4, `tests/test_static.py`, `UPDATE.md`'s snippets, `check_quotes.py`'s `aka:` match, and both copies of the add-case skill. Under 30b, move the data byte for byte. Load both from `index.html` with relative `<script src>` tags before the inline script, so its top-level code sees them as before.
4. Add `scripts/cases.py` with one loader, `load_cases_js()`, that returns the case source from `js/cases.js`. Point `check_charges.py`, `check_claims.py`, `check_dates.py`, and `check_slugs.py` at it, removing their four copies. Point `check_quotes.py` at `index.html`, `js/cases.js`, and `js/glossary.js`.
5. Rewrite `UPDATE.md`'s second and third checks, "The case schema" and "Where things live", the add-case skill's loader snippet and every instruction that says the cases live in `index.html` (both copies, kept identical), and `scout/SCOUT.md` where it names `index.html`.
6. Point `tests/test_static.py` at the shared loader, and add a test that `index.html` contains no `CASES = [` or `GLOSSARY = {`.

## The sample-file review gate

- Python: `scripts/check_dates.py` is the sample since its loader also feeds the date parsing the other checks lean on. Write `scripts/cases.py`, switch `check_dates.py` to it, run it, and stop for approval before the other four scripts.
- Markdown: The repo copy of the add-case skill is the sample since it carries the most instructions about where the cases live. Update it, and stop for approval before `UPDATE.md`, `SCOUT.md`, and the home copy.
- JavaScript: `js/cases.js` is the sample. Under decision 30a, prove it with the shared loader returning the same cases from `main`'s `index.html` and from the new file. Under 30b, prove it with `diff` against the original lines.
- HTML: `index.html` only.

## Done when

The five check scripts exit 0 reading the new location, both suites pass, the screenshot diff is pixel-identical, `index.html` no longer holds the data, and `curl -skI` shows `js/cases.js` with the no-cache header and `js/vendor/html2canvas.min.js` with the 30-day one at the staging origin.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py`, with the formatter re-run where a change moved a column. Under decision 30b, `js/cases.js` and `js/glossary.js` are the one exception, and the vendored `js/vendor/html2canvas.min.js` is never checked.

## Rollback

Revert the commits. Restore the config backup on each server, run `sudo nginx -t`, reload, and add a PCI row. If production served `js/cases.js` under the old rule even once, purge it in Cloudflare (Caching, Configuration, Custom Purge, by URL).

## Paste-ready prompt: build and stage

```
Run step 9A (move the case data) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/09a-case-data.md exactly. Read
docs/standards-cleanup/README.md first. Use decisions 1, 11, 14, 15, and 30 as
recorded in the README, and stop if any is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

Hold the formatting gate. Every file you change or create ends clean on
python3 -I ~/.claude/formatting-tools/check_format.py and
python3 ~/.claude/skills/annielytics-comment-style/scripts/check_style.py,
matching AI Strategy. Run both on those files before every commit, fix
every finding, and re-run the formatter where a change moved a column.

1. Confirm step 8 (and 8B, or its skip) is merged and live. Confirm neither
   update/claude nor update/sol still carries unmerged CASES edits, and stop
   if one does. Branch off an up-to-date main as standards-case-data. Never
   work on main.
2. Run both suites and the five check scripts, and confirm they pass.
3. Confirm the formatting hook skips vendored minified files since the
   rename stages js/html2canvas.min.js and a minified library can never
   pass check_format.py. Stop if it does not. Then move html2canvas to
   js/vendor/ with git mv, and update its tag, the hash test,
   js/VENDORED.md's location, and DEPLOY.md.
4. Move CASES and GLOSSARY out of the inline script into js/cases.js and
   js/glossary.js, each with an About section, aligned under decision 30a
   or byte for byte under 30b, and load them before the inline script.
   Sample-file review gate (JavaScript): show me js/cases.js with its proof
   (the shared loader's output under 30a, a diff against the original
   lines under 30b), a clickable link, and the git diff command, and STOP
   until I approve.
5. Sample-file review gate (Python): write scripts/cases.py and switch
   scripts/check_dates.py to it. Run it and give me a clickable link, a
   short summary, and the git diff command, and STOP until I approve. Then
   switch check_charges.py, check_claims.py, check_slugs.py, and
   check_quotes.py.
6. Sample-file review gate (Markdown): update the repo copy of the add-case
   skill first, give me the link, summary, and diff command, and STOP until
   I approve. Then UPDATE.md, scout/SCOUT.md, and the home copy at
   ~/.claude/skills/models-gone-wild-add-case/SKILL.md (identical).
7. Update tests/test_static.py and add the no-data-in-index.html test.
8. Run the five check scripts, both suites, the screenshot diff
   (pixel-identical), and the comment style checker (0), gating on each
   exit code.
9. On the server: back up
   /etc/nginx/sites-available/staging.annielytics.conf, narrow this app's
   asset rule to js/vendor and img as the step file shows, show me the
   diff, and STOP until I approve. Then sudo nginx -t, reload, wait two
   seconds, and write the PCI change-log row yourself, reading it back.
10. Commit, push, deploy the branch to staging with the README command, run
    the staging health check, and show me curl -skI for js/cases.js and
    js/vendor/html2canvas.min.js at the staging origin.
11. Report what you verified and how, give me the staging links with a
    reminder to hard-refresh, open a poster, and download it, and STOP. Do
    not merge to main or touch production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/09a-case-data.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step 9A report. It needs no edits. The nginx change goes first, so the old 30-day rule never serves the data file.

```
Ship step 9A (move the case data) of the Models Gone Wild standards cleanup
to production, following docs/standards-cleanup/09a-case-data.md and the
rules in docs/standards-cleanup/README.md. This is my go-ahead for step 9A
only, including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-case-data, gating on each exit code.
2. BEFORE deploying any code: back up
   /etc/nginx/sites-available/annielytics.conf, narrow this app's asset
   rule to js/vendor and img, run sudo nginx -t, reload, wait two seconds,
   and write the PCI change-log row yourself, reading it back.
3. Merge standards-case-data to main and push, deploy main to production
   with the README command, and run the production health check.
4. Show me curl -skI for js/cases.js (no-cache) and
   js/vendor/html2canvas.min.js (30 days) at the production origin.
5. Remind me to hard-refresh, open a poster, and download it at
   https://www.annielytics.com/tools/models-gone-wild/poster/sol-hugging-face/.
6. Switch staging back to main with the README command.
7. Mark step 9A done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
8. Tell me the next step is step 9B, whose prompt is at the bottom of
   docs/standards-cleanup/09b-inline-code.md.
```
