# Step 6: Comment Style

Branch: `standards-comment-style`

Apply the annielytics-comment-style skill. Comments and docstrings only, so no behavior changes.

## Background

On 2026-10-16, `python3 ~/.claude/skills/annielytics-comment-style/scripts/check_style.py` reported 75 issues:

| Category | Count | Where |
|---|---|---|
| Banners | 1 | `css/styles.css:896`, a 39-character label inside a 31-wide rule |
| Comment prose | 18 | 17 in `index.html` (12 one-sentence comments ending in a period, 5 starting lowercase in the `HAIR` table near line 926), 1 in `methodology/index.html:139` |
| Docstrings | 56 | `scout_seen.py` 16, `check_claims.py` 12, `check_overlaps.py` 11, `check_dates.py` 8, `serve.py` 5, `check_slugs.py` 4. Nearly all are a missing blank line before `Args:` or `Returns:`. |
| Dashes, trailing comments, JS block comments, annotations | 0 | |

The checker prints at most 15 issues per category, so run it with the limit lifted to see every line (copy it to the scratchpad and change `issues[:15]` to `issues`). Tests added in steps 1 to 5 are in scope too.

The five lowercase comments label hair styles in a lookup table (`side part, swept across the crown`). Capitalize them; do not reword them.

## The changes

1. Read `~/.claude/skills/annielytics-comment-style/SKILL.md` and follow it.
2. Fix the banner, the comment prose, and the docstrings, using the skill's scripts where they apply (`docstring_layout.py` for the blank lines, `normalize_banners.py` for the banner) and by hand where they do not.
3. HTML comments stay `<!-- -->` since a static page has no Jinja to hide them in, unless decision 26 names them as one of the small calls to change.

## The sample-file review gate

- Python: `scripts/scout_seen.py` is the sample since it carries the most docstring issues (16).
- HTML: `index.html` is the sample since it carries 17 of the 18 prose issues. `methodology/index.html` follows.
- CSS: There is one file, so there is nothing to sample.

Fix each sample, stop for approval, then do the rest of that filetype.

## Done when

`python3 ~/.claude/skills/annielytics-comment-style/scripts/check_style.py` reports 0, and both suites pass. For the Python files, `ast.dump` of each file is identical before and after with docstrings excluded, which proves only comments moved.

## Rollback

Revert the commit.

## Paste-ready prompt: build and stage

```
Run step 6 (comment style) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/06-comment-style.md exactly. Read
docs/standards-cleanup/README.md and
~/.claude/skills/annielytics-comment-style/SKILL.md first. Stop if decision
26 in the README still says which small calls to change are to be named.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Confirm step 5 is merged and live. Branch off an up-to-date main as
   standards-comment-style. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass. Run check_style.py with the 15-line limit lifted
   (a copy in the scratchpad) and show me the full count by file.
3. Sample-file review gate (Python): fix scripts/scout_seen.py first, then
   give me a clickable link, a short summary, and the git diff command, and
   STOP until I approve. Then fix the other .py files.
4. Sample-file review gate (HTML): fix index.html's 17 comments first (keep
   them as <!-- --> and /* */, capitalize the HAIR labels without
   rewording), give me the link, summary, and diff command, and STOP until I
   approve. Then fix methodology/index.html.
5. Fix the CSS banner at css/styles.css:896.
6. Prove the Python is unchanged with an ast.dump comparison that excludes
   docstrings. Run check_style.py (must report 0) and both suites, gating on
   each exit code.
7. Commit, push, and deploy the branch to staging with the
   README command and run the staging health check.
8. Report what you verified and how, and STOP. Do not merge to main or touch
   production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/06-comment-style.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step 6 report. It needs no edits.

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
6. Tell me the next step is step 7, whose prompt is at the bottom of
   docs/standards-cleanup/07-split-css.md.
```
