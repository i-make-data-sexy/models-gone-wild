# Step 8: Design Tokens (Pass A) and the Pre-Commit Gate

Branch: `standards-design-tokens`

This is pass A of the design-tokens skill. Every literal becomes a token holding the exact same value, so nothing moves by a pixel. Consolidating near-duplicates is pass B, step 8B, which is skipped under decision 13a.

## Decisions this step reads

Decision 12a (the script reads its colors from the CSS tokens) and decision 13a (no consolidation pass), recorded in `docs/standards-cleanup/README.md` on 2026-10-16.

## Background

On 2026-10-16, before the split in step 7, this command reported 90 raw values outside a token definition:

```
python3 ~/.claude/skills/design-tokens/scripts/check_raw_values.py --checks color,rgb,font-size,line-height css/styles.css
```

The checker prints only the first 40, so lift the `findings[:40]` limit in a scratchpad copy to see them all. The 90 are 5 hex colors (`#4ea3e0`, `#f4ecd8`, `#c9c2b0`, `#e6ddc6`, `#211e18`), 14 `rgb()`/`rgba()` colors, 52 font sizes, and 19 line heights. The default `--checks color` alone reports only the 5 hex colors, so always pass all four. Mapped onto step 7's files, the 90 fall in `poster.css` (28), `registry.css` (22), `charts.css` (18), `base.css` (13), `methodology.css` (7), and `responsive.css` (2).

`audit_tokens.py .` reported 14 tokens, 155 `var()` uses, and 3 tokens never used: `--stamp-red-bright`, `--amber`, and `--options-knob-fill`. The first two are unused. The third is not, which a grep found on 2026-10-19. `registry.css` sets it on the options button twice, once for the closed menu (`--paper-deep`) and once for the open menu (`--stamp-red`), and `.line-icon-knob` reads it to fill the three knob circles in `index.html`. The audit misses that read because it is written with a fallback, `var(--options-knob-fill,var(--paper))`. `--stamp-red` and `--class3` hold the same value (`#8f1d16`). They name different roles (the stamp color and the severe class), so both stay in pass A.

The checker scans CSS and Python only, so it reports both HTML pages and the JavaScript clean. `index.html` held 31 hex colors it cannot see on 2026-10-16. Steps 9A and 9B, which run before this step under decision 31, move the script's into `js/labels.js`, `js/mugshot.js`, and `js/charts.js`, so find each one again at the start:

- JS constants: `DISC_FILL` (`#5a6b2a`, `#8f1d16`), and the mugshot palette `M_INK`, `M_PAPER`, `M_WHITE`, and `M_BACK` (`#1c1a15`, `#efe7d2`, `#fbf7ec`, `#cfc4a6`).
- Template strings that draw SVG with `#3a362c` and `#4a4438` (6 each).
- The two legends in the markup, which fill their swatches with `#5a6b2a` and `#8f1d16` (comments say to keep them in step with `DISC_FILL` by hand).

Most of these repeat a CSS token. `#1c1a15` is `--ink`, `#3a362c` is `--ink-soft`, `#4a4438` is `--rule`, `#e6ddc6` is `--paper`, `#5a6b2a` is `--class1`, and `#8f1d16` is `--stamp-red`.

Under decision 28a, step F1 installed `scripts/git-hooks/pre-commit` with the formatting gate and set `core.hooksPath`. (Under 28b there is no hook, and this step installs one.) The hook has no extension, so nginx serves it from the web root. Its contents are a shell script calling the checkers, which is harmless, and decision 23a takes it out of the web root in step 13A.

## The changes

1. Read `~/.claude/skills/design-tokens/SKILL.md` and follow pass A.
2. In the seven CSS files from step 7, give every raw color, `rgb()`/`rgba()` value, font size, and line height a token in `variables.css` holding the exact literal, named for its role, and replace each use with `var()`. Keep values identical, including spelling (`.95em` stays `.95em`).
3. Remove `--stamp-red-bright` and `--amber` after grepping both pages, every CSS file, and `js/` to confirm nothing reads them. Keep `--options-knob-fill`, the options button's state token.
4. Under decision 12a, the 31 colors in `index.html` and the `js/` files move onto the tokens.
   - At startup, read each color the script draws with from the CSS custom properties with `getComputedStyle(document.documentElement).getPropertyValue(...)`, trimmed, and assign them to the existing constants (`DISC_FILL`, `M_INK`, and the rest). The SVG the script builds keeps receiving literal colors, which matters because html2canvas renders a poster's SVG as an image and would not apply a stylesheet to it.
   - Replace the two legends' `fill="#..."` attributes with classes the stylesheet colors from the tokens (the legends are never captured by html2canvas), and drop the "keep in step with `DISC_FILL`" comments since both now read one source.
   - Add a test that fails on any hex color in `index.html`, `methodology/index.html`, or the app's own `js/` files (not `js/vendor/`).
5. Add the gate to the hook: read `scripts/git-hooks/pre-commit` first, then append a call to `python3 ~/.claude/skills/design-tokens/scripts/check_raw_values.py --staged --checks color,rgb,font-size,line-height` that exits non-zero on a finding, keeping the formatting gate above it. Confirm `core.hooksPath` is `scripts/git-hooks`, and note in `UPDATE.md` that a fresh clone needs `git config core.hooksPath scripts/git-hooks`.
6. Run the screenshot diff, and open a poster and press Download poster to confirm the PNG still renders (step 1's browser suite covers opening; the download is a manual check).

## The sample-file review gate

- CSS: `css/poster.css` is the sample since it carries the most raw values of the seven (28 of 90). Tokenize it, run the screenshot diff, and stop for approval before the other six.
- JavaScript: The first `js/` file with colors is the sample. Stop for approval before the others.
- HTML: `index.html` (the two legends) is the only page with colors, so there is nothing further to sample.

## Done when

```
python3 ~/.claude/skills/design-tokens/scripts/check_raw_values.py --checks color,rgb,font-size,line-height css/*.css
```

reports zero, the screenshot diff is pixel-identical at every width, the hook blocks a test commit that adds a raw hex to a CSS file (show it, then discard the commit), and both suites pass.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py`, with the formatter re-run where a change moved a column.

## Rollback

Revert the commits, which takes the raw-value call back out of the hook and leaves the formatting gate. `git config --unset core.hooksPath` turns the whole hook off.

## Paste-ready prompt: build and stage

```
Run step 8 (design tokens, pass A) of the Models Gone Wild standards
cleanup, following docs/standards-cleanup/08-design-tokens.md exactly. Read
docs/standards-cleanup/README.md and ~/.claude/skills/design-tokens/SKILL.md
first. Use decisions 1 and 12 as recorded in the README, and stop if either
is blank.

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

1. Confirm step 7 is merged and live. Branch off an up-to-date main as
   standards-design-tokens. Never work on main.
2. Run both suites and confirm they pass. Run check_raw_values.py with
   --checks color,rgb,font-size,line-height on css/*.css and audit_tokens.py
   on the repo, and show me the counts per file.
3. Sample-file review gate (CSS): tokenize css/poster.css first, values
   unchanged, and run scripts/screenshot-diff/run.sh main
   standards-design-tokens. Give me a clickable link, a short summary, the
   diff result, and the git diff command, and STOP until I approve.
4. After I approve, tokenize the other six CSS files and remove the two
   unused tokens, keeping --options-knob-fill.
5. Read the script's colors from the tokens at startup,
   move the legend fills to classes, and add the no-hex test for both pages.
6. Append the raw-value check to scripts/git-hooks/pre-commit (step F1's
   hook, read it first), confirm core.hooksPath, note the
   command in UPDATE.md, and show me the hook blocking a raw hex.
7. Run the screenshot diff (pixel-identical), both suites, the comment
   style checker (0), and check_raw_values.py (0), gating on each exit
   code. Download one poster locally and confirm the PNG looks right.
8. Commit, push, and deploy the branch to staging with the
   README command and run the staging health check.
9. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh and to download one poster, and STOP. Do not
   merge to main or touch production until I say so.

When you stop, end your report with a lettered to-do that runs the
ship-to-production prompt at the bottom of
docs/standards-cleanup/08-design-tokens.md when I reply with
its letter. Do not paste that prompt into the report.
```

## Ship-to-production prompt

Claude runs this in the same session when you reply with the ship letter at the end of the step 8 report. It needs no edits.

```
Ship step 8 (design tokens, pass A) of the Models Gone Wild standards
cleanup to production, following docs/standards-cleanup/08-design-tokens.md
and the rules in docs/standards-cleanup/README.md. This is my go-ahead for
step 8 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-design-tokens, gating on each exit code.
2. Merge standards-design-tokens to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Remind me to hard-refresh and to download one poster from
   https://www.annielytics.com/tools/models-gone-wild/poster/sol-hugging-face/.
5. Switch staging back to main with the README command.
6. Mark step 8 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Tell me the next step is step 10A (step 8B is skipped under decision
   13a), and paste its build prompt from the bottom of
   docs/standards-cleanup/10a-self-host-fonts.md in full, so I can start
   the next session with it.
```
