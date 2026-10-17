# Step 7: Split the Stylesheet by Concern

Branch: `standards-split-css`

A pure reorganization. Every rule moves byte for byte, the cascade order is preserved, and a visitor sees no pixel change. The pattern is `~/.claude/rules/archived/css-modular-split.md`.

## Background

`css/styles.css` is 972 lines, over the 800-line limit. Step F1 brought it to the formatting rule. This step moves every rule byte for byte, then gives each new file an About This File section and re-runs `format_css.py` on it since each file's value columns are set by its own longest property names.

The stylesheet's banners on 2026-10-16 are below, with the target file for each. The ranges are contiguous, so linking the files in this order reproduces the original cascade exactly:

| Lines | Sections | Target file |
|---|---|---|
| 1 to 26 | File header comment, `:root` | `variables.css` |
| 27 to 200 | Reset, body and paper texture, page shell, Site Header, Masthead | `base.css` |
| 201 to 598 | Registry Panel, Options Menu, Timeline, Card, Lab Spine, Card Actions, Glossary Terms | `registry.css` |
| 599 to 742 | Tooltip, Scatter (the Threat Matrix), Cases by Lab | `charts.css` |
| 743 to 855 | Modal / Poster | `poster.css` |
| 856 to 895 | Methodology Page | `methodology.css` |
| 896 to 972 | Site Header Responsive, the 1023px and 800px queries, reduced motion | `responsive.css` |

Step F1 shifted these line numbers, so find each range by its banner at the start. The media queries (at lines 114, 415, 418, 431, and 684 on 2026-10-16) stay with their sections.

Every file stays under `css/`, which nginx serves through the page block with no-cache headers, so no nginx rule changes. Seven no-cache requests replace one; Cloudflare serves them over HTTP/2.

Both pages keep loading every file, in the same order. Trimming what Methodology loads would change its cascade, so it is not part of this step.

## The changes

1. Split with a script that maps line ranges to files and asserts every line lands in exactly one file, as the pattern rule shows. Keep the script in the session scratchpad, not the repo.
2. Give each new file an About This File section with `add_about.py` and re-run `format_css.py` on it. Prove the move with the split script, which checks that the seven files, joined in link order with whitespace and comments stripped, match `css/styles.css` on `main` stripped the same way.
3. Rewrite the header comment that moves to `variables.css` so it names the seven files and why they load in order.
4. In `index.html`, replace `<link rel="stylesheet" href="css/styles.css">` with seven relative links in the table's order. In `methodology/index.html`, the same with `../css/`.
5. Delete `css/styles.css`. First grep the repo for every other reference (`UPDATE.md`'s leading-slash check, `DEPLOY.md`'s verify list, the step 1 tests, `scripts/check_overlaps.py`) and update each.
6. Add a test that every stylesheet each page links exists, returns 200 through the preview server at the root and under a permalink, and that no CSS file is more than 800 lines.

## The screenshot harness

Step F1 built it in `scripts/screenshot-diff/`. Confirm `run.sh main main` comes back clean before editing any CSS. Steps 8, 9A, 9B, 10A, 11, 12, and 13 reuse it.

## The sample-file review gate

- CSS: There is one source file, so the split is the sample. Run it, run the screenshot diff, and show `registry.css` (the largest piece), the coverage check, and the diff result. Stop for approval before touching anything else.
- HTML: `index.html` is the sample for the link change. `methodology/index.html` follows after approval.

## Done when

`scripts/screenshot-diff/run.sh main standards-split-css` reports zero changed pixels at every width, no file in `css/` is more than 800 lines, and both suites pass.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py`, with the formatter re-run where a change moved a column.

## Rollback

Revert the commit. `styles.css` returns and both pages link it again.

## Paste-ready prompt: build and stage

```
Run step 7 (split the stylesheet) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/07-split-css.md exactly. Read
docs/standards-cleanup/README.md and
~/.claude/rules/archived/css-modular-split.md first. Use decision 1 as
recorded in the README, and stop if it is blank.

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

1. Confirm step 6 is merged and live. Branch off an up-to-date main as
   standards-split-css. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass.
3. Run step F1's scripts/screenshot-diff/run.sh main main and show me it
   comes back clean BEFORE editing any CSS.
4. Find each section range in css/styles.css by its banner since step F1
   moved the line numbers, and show me the ranges against the step file's
   table.
5. Sample-file review gate (CSS): split styles.css into the seven files with
   the coverage-checked script, give each its About section and re-run
   format_css.py on it, link them from index.html (the HTML sample),
   and run run.sh main standards-split-css. Give me clickable links to
   css/registry.css and index.html, the coverage result, the diff result,
   and the git diff command, and STOP until I approve.
6. After I approve, link the seven files from methodology/index.html with
   ../css/, delete css/styles.css, update every reference to it, and add the
   stylesheet and 800-line tests.
7. Run run.sh main standards-split-css again (pixel-identical at every
   width), both suites, and the comment style checker (0), gating on each
   exit code.
8. Commit, push, and deploy the branch to staging with the
   README command, run the staging health check, and confirm
   threat-matrix/css/registry.css returns 200 at the staging origin.
9. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh (Command-Shift-R), and STOP. Do not merge to
   main or touch production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/07-split-css.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step 7 report. It needs no edits.

```
Ship step 7 (split the stylesheet) of the Models Gone Wild standards
cleanup to production, following docs/standards-cleanup/07-split-css.md and
the rules in docs/standards-cleanup/README.md. This is my go-ahead for step
7 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-split-css, gating on each exit code.
2. Merge standards-split-css to main and push.
3. Deploy main to production with the README command, run the production
   health check, and confirm css/variables.css and
   threat-matrix/css/registry.css return 200 at the origin.
4. Remind me to hard-refresh (Command-Shift-R) the production pages.
5. Switch staging back to main with the README command.
6. Mark step 7 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Give me https://www.annielytics.com/tools/models-gone-wild/ and
   https://www.annielytics.com/tools/models-gone-wild/methodology/ to
   spot-check. Then tell me the next step is step 8, whose prompt is at the
   bottom of docs/standards-cleanup/08-design-tokens.md.
```
