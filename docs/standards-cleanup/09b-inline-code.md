# Step 9B: Move the Rest of the Inline Code

Branch: `standards-inline-code`

The second half of the baseline's inline-code step. After step 9A, `index.html` still carries about 1,550 lines of inline script, and `methodology/index.html` carries 18. This step moves every line into files, keeps the execution order, and adds the guard.

## Decisions this step reads

Decision 15a (the app's scripts live in `js/`, served no-cache since step 9A) and decision 16a (html2canvas loads on the first Download poster press), recorded in `docs/standards-cleanup/README.md` on 2026-10-16. Decision 31 (this step runs right after step 9A and takes over step F2's remainder), recorded 2026-10-17.

## Background

The script's banners divide it into these sections, with line numbers in `index.html` from 2026-10-16, before step 9A moved the data:

| Lines | Sections | Target file |
|---|---|---|
| 219 to 744 | The Registry (labels, notes, and lookup tables left after 9A), Card Action Icons | `js/labels.js` |
| 745 to 845 | Glossary helpers (`gloss()`, `escAttr`, and the date helpers). The terms themselves moved to 9A's data file, which stays data only. | `js/text.js` |
| 846 to 1034 | Mugshot Generator, Shared Furniture, Skulls, Noses, Hair, The Four Faces | `js/mugshot.js` |
| 1035 to 1149 | Filter State, Build Lab Options, Render Timeline | `js/timeline.js` |
| 1150 to 1736 | Render Scatter, Dot and Label Layout, Axis Spacing Tokens, Render Lab Chart | `js/charts.js` |
| 1737 to 1878 | Apply Filters, Options Menu, View Tabs | `js/views.js` |
| 1879 to 1983 | Tooltip | `js/tooltip.js` |
| 1984 to 2176 | Modal, Copy Link, PNG Export | `js/poster.js` |
| 2177 to 2197 | Site Header Mobile Menu | `js/menu.js`, shared with Methodology |
| 2198 to 2214 | Init | `js/main.js` |

Confirm the boundaries at the start since 9A shifted them. `charts.js` lands near 590 lines; split it at "Render Lab Chart" if it runs past 600.

The Methodology page's inline script is the same menu listener as lines 2177 to 2197, so both pages load `js/menu.js` and the duplicate goes.

The files stay classic scripts, not modules, loaded in the table's order at the end of `<body>`, where the inline script sat. Top-level `const` and `function` declarations in one classic script are visible to the next, so the code runs exactly as before. Modules would change scoping and timing, which is out of scope here.

`js/vendor/html2canvas.min.js` (moved there in step 9A) loads in `<head>`, render-blocking, on every visit. It is 198 KB, and only Download poster uses it.

Step F2 formatted `index.html`'s script in place (alignment, spacing, and every comment but the section banners deleted) and left four things to this step under decision 31. They are Methodology's 18-line script, which `js/menu.js` replaces, the four-space indentation (the script is indented two spaces), an About section for each file, and `js` on the formatting hook. Step 9A did the same for `js/cases.js` and `js/glossary.js`.

Neither page has a `<style>` block, a `style=` attribute, or an `on*=` handler. The script sets 15 style properties through `element.style`, which a Content Security Policy allows. The JS template strings that build cards and posters carry no `style=` or `on*=` either.

## The changes

1. Move each section into its file, byte for byte, and replace the inline script with one relative `<script src>` per file in the table's order (`../js/menu.js` on Methodology). Then, in separate commits, re-indent each file to four spaces (decision 31), re-run `format_js.py` where that moved a column, and give each file an About This File section (step F2 gave the inline block none).
2. Drop html2canvas's `<script>` from `<head>`. In `js/poster.js`, load it on the first Download poster press by appending a `<script>` element and awaiting its `load` event, with the button showing "Rendering…" as it already does while it works.
3. Add `tests/test_inline.py`. It fails on any `<script>` without `src` (other than `type="application/json"`), any `<style>` block, any `style=` attribute, or any `on*=` attribute in `index.html` and `methodology/index.html` (and `404.html` once step 12 adds it), and on any `style=` or `on[a-z]+=` inside a template string in the app's own JS files.
4. Update `UPDATE.md` ("Changing design or behavior" says "Everything lives in index.html"; "Where things live"; the traps) and `DEPLOY.md`'s file list.
5. In the last commit, once every JavaScript file passes `check_format.py` (the vendored `js/vendor/` files are skipped), add `js` to `scripts/git-hooks/format-languages` under decision 28a.
6. Give the vendored library one `Cache-Control` header (approved 2026-10-17 at the end of step 9A). This app's asset block, `(js/vendor|img)`, sets both `expires 30d` and `add_header Cache-Control "public, no-transform"`, so the library goes out with two `Cache-Control` headers, the same duplicate step 2 removed from the page block. On each server, replace those two lines with `add_header Cache-Control "public, max-age=2592000, no-transform";`, which keeps the 30 days and the `no-transform` that stops Cloudflare or a proxy rewriting the file. Make the same change in both nginx copies in `DEPLOY.md`.

## The sample-file review gate

- JavaScript: `js/poster.js` is the sample since it carries the history, clipboard, and export code, and the new on-demand loading. Move it first, leaving the code before and after it inline in the same order, run both suites and the screenshot diff, download a poster, and stop for approval before the other files.
- HTML: `index.html` is the sample. `methodology/index.html` follows, swapping its inline script for `../js/menu.js`.

## Done when

`tests/test_inline.py` passes on both pages and fails when an inline `<script>` is added back (show both), both suites pass, the screenshot diff is pixel-identical, `scripts/check_overlaps.py` reports no overlaps, a poster downloads as a PNG locally and on staging, and `curl -skI` shows exactly one `Cache-Control` header, `public, max-age=2592000, no-transform`, on `js/vendor/html2canvas.min.js` and on `img/annielytics-logo.png` at each origin.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and has no `check_style.py` issue, with the formatter re-run where a change moved a column. Each new file is indented four spaces and has an About section, `verify_equivalent.py js` passes on each against the code it came from, and `js` is on the hook.

## Rollback

Revert the commits. Restore the config backup on each server, run `sudo nginx -t`, reload, and add a PCI row.

## Paste-ready prompt: build and stage

```
Run step 9B (move the rest of the inline code) of the Models Gone Wild
standards cleanup, following docs/standards-cleanup/09b-inline-code.md
exactly. Read docs/standards-cleanup/README.md first. Use decisions 1, 15,
and 16 as recorded in the README, and stop if any is blank. Decision 31
runs this step right after 9A and gives it step F2's remainder.

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

1. Confirm step 9A is merged and live. Branch off an up-to-date main as
   standards-inline-code. Never work on main.
2. Run both suites, the five check scripts, and check_overlaps.py, and
   confirm they pass. Confirm the section boundaries against the step
   file's table.
3. Sample-file review gate (JavaScript): move the Modal, Copy Link, and PNG
   Export sections into js/poster.js, byte for byte, with html2canvas
   loaded on the first Download poster press, then re-indent it to four
   spaces and give it an About section, each in its own commit. Prove the
   re-indent with verify_equivalent.py js and node --check. Run both
   suites and the screenshot diff, download a poster, and give me a
   clickable link, a short summary, and the git diff command. STOP until
   I approve.
4. After I approve, move the other sections into their files in order and
   replace the inline script in index.html (the HTML sample), re-indenting
   each file and giving it an About section the same way. Show me
   index.html and STOP until I approve, then swap methodology/index.html's
   inline script for ../js/menu.js.
5. Add tests/test_inline.py and show it failing on a re-added inline
   script and passing without it.
6. Update UPDATE.md and DEPLOY.md where they describe where the code lives.
7. Run both suites, the five check scripts, check_overlaps.py, the
   screenshot diff (pixel-identical), check_format.py on every JavaScript
   file (exit 0), and the comment style checker (no issue in any file you
   changed), gating on each exit code. Download a poster locally. Then
   add js to scripts/git-hooks/format-languages in the last commit.
8. On the server: back up
   /etc/nginx/sites-available/staging.annielytics.conf, give this app's
   asset block one Cache-Control header as the step file's change 6
   shows, show me the diff, and STOP until I approve. Then sudo nginx -t,
   reload, wait two seconds, and write the PCI change-log row yourself,
   reading it back.
9. Commit, push, and deploy the branch to staging with the
   README command, run the staging health check, and confirm every new JS
   file returns 200 with the no-cache header at the staging origin, and
   that js/vendor/html2canvas.min.js and img/annielytics-logo.png each
   return one Cache-Control header.
10. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh and to download a poster, and STOP. Do not
   merge to main or touch production until I say so.

When you stop, end your report with a lettered to-do that runs the
ship-to-production prompt at the bottom of
docs/standards-cleanup/09b-inline-code.md when I reply with
its letter. Do not paste that prompt into the report.
```

## Ship-to-production prompt

Claude runs this in the same session when you reply with the ship letter at the end of the step 9B report. It needs no edits.

```
Ship step 9B (move the rest of the inline code) of the Models Gone Wild
standards cleanup to production, following
docs/standards-cleanup/09b-inline-code.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 9B only,
including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-inline-code, gating on each exit code.
2. Back up /etc/nginx/sites-available/annielytics.conf, give this app's
   asset block one Cache-Control header as the step file's change 6
   shows, run sudo nginx -t, reload, wait two seconds, and write the PCI
   change-log row yourself, reading it back.
3. Merge standards-inline-code to main and push.
4. Deploy main to production with the README command, run the production
   health check, and confirm every new JS file returns 200 with the
   no-cache header at the production origin, and that
   js/vendor/html2canvas.min.js and img/annielytics-logo.png each return
   one Cache-Control header.
5. Remind me to hard-refresh, switch tabs, open the menu on my phone, and
   download a poster at https://www.annielytics.com/tools/models-gone-wild/.
6. Switch staging back to main with the README command.
7. Mark step 9B done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
8. Tell me the next step is step F3, and paste its build prompt
   from the bottom of docs/standards-cleanup/f3-python.md in full, so I can
   start the next session with it.
```
