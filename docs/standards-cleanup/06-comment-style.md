# Step 6: Comment Style

Branch: `standards-comment-style`

Steps F1 to F4 did this step's work, so it confirms `check_style.py` reports 0 and keeps it there. Comments and docstrings only, so no behavior changes.

## Decisions this step reads

Decision 1a (staging) and decision 26 (delete the HTML comments), recorded 2026-10-16, and decision 29 (the About section on the two pages), recorded in `docs/standards-cleanup/README.md`.

## Background

On 2026-10-16, `python3 ~/.claude/skills/annielytics-comment-style/scripts/check_style.py` reported 70 issues, and the formatting steps fix all of them:

| Category | Count | Where | Fixed in |
|---|---|---|---|
| Banners | 1 | `css/styles.css:896`, a 39-character label inside a 31-wide rule | Step F1 |
| Comment prose | 18 | 17 in `index.html`'s inline script (12 one-sentence comments ending in a period, 5 lowercase labels in the `HAIR` table), 1 in `methodology/index.html:139` | Step F2 |
| Docstrings | 51 | `scout_seen.py` 16, `check_claims.py` 12, `check_overlaps.py` 11, `check_dates.py` 8, `check_slugs.py` 4 | Step F3 |

Steps F2 and F4 deleted the 20 HTML comments under decision 26 (the 15 in `index.html` in F2, at Annie's request, and Methodology's 5 in F4), and F4 added the guard test that keeps them out. Step F7 and step 4 then wrote code under the same gate.

The checker prints at most 15 issues per category, so run it with the limit lifted to see every line (copy it to the scratchpad and change `issues[:15]` to `issues`). Nothing runs it automatically today, so a later edit could bring an issue back unseen.

## The changes

1. Read `~/.claude/skills/annielytics-comment-style/SKILL.md`, run the checker with the limit lifted, and fix any issue it finds, using the skill's scripts where they apply and by hand where they do not.
2. Add `tests/test_comment_style.py`, which runs `check_style.py` on the repo and fails on any issue. It skips with a reason when the skill is not on the machine since a fresh clone or the cloud scout may not have it.

## The sample-file review gate

- Python: `tests/test_comment_style.py` is the sample, the one Python file the step creates. Write it, show it passing and failing with one issue put back (a lowercase comment, say), and stop for approval. If step 1 finds issues to fix, the first file it fixes is that filetype's sample instead, and gets its own stop.

## Done when

`check_style.py` reports 0 with the limit lifted, the new test passes and fails with an issue put back, `grep -c '<!--' index.html methodology/index.html` prints 3 for each under decision 29a (the About banner, its note, and the page banner below it, all above the doctype, as step F4 shipped them) or 0 under 29b, and both suites pass.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py`, with the formatter re-run where a change moved a column.

## Rollback

Revert the commit.

## Paste-ready prompt: build and stage

```
Run step 6 (comment style) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/06-comment-style.md exactly. Read
docs/standards-cleanup/README.md and
~/.claude/skills/annielytics-comment-style/SKILL.md first. Use decisions 1,
26, and 29 as recorded in the README, and stop if any is blank.

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

1. Confirm step 4 is merged and live. Branch off an up-to-date main as
   standards-comment-style. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass. Run check_style.py with the 15-line limit lifted
   (a copy in the scratchpad) and show me the count by file (0 expected).
3. If it finds any issue, fix it per the skill, stopping at the first file
   of each filetype as its sample.
4. Sample-file review gate (Python): write tests/test_comment_style.py,
   show it passing and failing with one issue put back, give me a clickable
   link, a short summary, and the git diff command, and STOP until I
   approve.
5. Confirm grep -c '<!--' on both pages prints 3 each under decision 29a or
   0 under 29b. Run check_style.py (must report 0) and both suites, gating
   on each exit code.
6. Commit, push, and deploy the branch to staging with the
   README command and run the staging health check.
7. Report what you verified and how, and STOP. Do not merge to main or touch
   production until I say so.

When you stop, end your report with a lettered to-do that runs the
ship-to-production prompt at the bottom of
docs/standards-cleanup/06-comment-style.md when I reply with
its letter. Do not paste that prompt into the report.
```

## Ship-to-production prompt

Claude runs this in the same session when you reply with the ship letter at the end of the step 6 report. It needs no edits.

```
Ship step 6 (comment style) of the Models Gone Wild standards cleanup to
production, following docs/standards-cleanup/06-comment-style.md and the
rules in docs/standards-cleanup/README.md. This is my go-ahead for step 6
only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-comment-style, gating on each exit code.
2. Merge standards-comment-style to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Switch staging back to main with the README command.
5. Mark step 6 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
6. Tell me the next step is step 7, and paste its build prompt
   from the bottom of docs/standards-cleanup/07-split-css.md in full, so I can
   start the next session with it.
```
