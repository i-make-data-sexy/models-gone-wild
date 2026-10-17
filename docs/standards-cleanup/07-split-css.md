# Step 7: Split the Stylesheet by Concern

Branch: `standards-split-css`

A pure reorganization. Every rule moves byte for byte, the cascade order is preserved, and a visitor sees no pixel change. The pattern is `~/.claude/rules/archived/css-modular-split.md`.

## Background

`css/styles.css` is 972 lines, over the 800-line limit. It was lifted out of an inline `<style>` block (90d2b19), which is why every rule is still indented two spaces. Prompt 5's formatting sweep fixes the indentation later; this step moves rules without reformatting them.

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

Confirm the line numbers at the start since step 6 may have shifted them. The media queries at lines 114, 415, 418, 431, and 684 stay with their sections.

Every file stays under `css/`, which nginx serves through the page block with no-cache headers, so no nginx rule changes. Seven no-cache requests replace one; Cloudflare serves them over HTTP/2.

Both pages keep loading every file, in the same order. Trimming what Methodology loads would change its cascade, so it is not part of this step.

## The changes

1. Split with a script that maps line ranges to files and asserts every line lands in exactly one file, as the pattern rule shows. Keep the script in the session scratchpad, not the repo.
2. Rewrite the header comment that moves to `variables.css` so it names the seven files and why they load in order.
3. In `index.html`, replace `<link rel="stylesheet" href="css/styles.css">` with seven relative links in the table's order. In `methodology/index.html`, the same with `../css/`.
4. Delete `css/styles.css`. First grep the repo for every other reference (`UPDATE.md`'s leading-slash check, `DEPLOY.md`'s verify list, the step 1 tests, `scripts/check_overlaps.py`) and update each.
5. Add a test that every stylesheet each page links exists, returns 200 through the preview server at the root and under a permalink, and that no CSS file is more than 800 lines.

## The screenshot harness

There is no harness yet. ML Model Picker's is the reference for apps with no database. It lives at `~/Dropbox/Annielytics/Code/Python/ML Model Picker/scripts/screenshot-diff/` and holds `run.sh`, `capture.py`, and `diff.py`. Port it into `scripts/screenshot-diff/` with these changes:

- Use this repo's `venv` for Playwright rather than borrowing another app's.
- Check out each ref into its own git worktree under `/tmp`, outside Dropbox, and serve it with that worktree's `scripts/serve.py` on a free port.
- Capture the home page, `threat-matrix/`, `lab-counts/`, `poster/sol-hugging-face/` with the poster open, and `methodology/`, at 375, 768, 1024, and 1440 pixels wide.
- Wait for `document.fonts.ready` before each capture since the Threat Matrix measures its labels in Oswald and lays out differently in a fallback face.
- `run.sh main main` must come back clean first, which proves the harness is stable.

Steps 8, 9A, 9B, 10A, 11, 12, and 13 reuse it.

## The sample-file review gate

- CSS: There is one source file, so the split is the sample. Run it, run the screenshot diff, and show `registry.css` (the largest piece), the coverage check, and the diff result. Stop for approval before touching anything else.
- HTML: `index.html` is the sample for the link change. `methodology/index.html` follows after approval.

## Done when

`scripts/screenshot-diff/run.sh main standards-split-css` reports zero changed pixels at every width, no file in `css/` is more than 800 lines, and both suites pass.

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

1. Confirm step 6 is merged and live. Branch off an up-to-date main as
   standards-split-css. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass.
3. Port ML Model Picker's screenshot-diff harness into
   scripts/screenshot-diff/ as the step file describes, and show me that
   run.sh main main comes back clean BEFORE editing any CSS.
4. Confirm the section line numbers in css/styles.css against the step
   file's table.
5. Sample-file review gate (CSS): split styles.css into the seven files with
   the coverage-checked script, link them from index.html (the HTML sample),
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
