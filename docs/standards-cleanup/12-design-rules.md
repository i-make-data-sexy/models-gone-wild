# Step 12: Design Rules and the 404 Page

Branch: `standards-design-rules`

Applies the four design rules in `~/.claude/rules/design/` (footer icon discs, the sweep underline, the button underline fix, and tooltip containment) and gives an unknown path the app's own 404 page.

## Decisions this step reads

Decision 19a (footer icon discs drawn in inline SVG), decision 20a (prose links keep the 2026-10-14 no-underline style), and decision 21a (an unknown poster slug shows a notice and is marked noindex), recorded in `docs/standards-cleanup/README.md` on 2026-10-16.

## Background

Two problems showed at the production origin on 2026-10-16:

- An unknown path, like `/tools/models-gone-wild/no-such-page/`, returned nginx's built-in 162-byte "404 Not Found" page, with no header, no footer, and no way back.
- `/tools/models-gone-wild/poster/no-such-slug/` returned 200 with the full page. The script found no case for the slug and showed the timeline, so a mistyped or retired poster link is a soft 404 that search engines can index.

Each of the four rules stands differently here:

- Footer icon discs. The footer is one line, "Last updated: <date>", with no links, so the rule has nothing to attach to. Font Awesome is not loaded; the app draws its icons as inline SVG in a line-icon style (the filter button, the close button).
- Sweep underline. The nav menu already has it (`base.css`, the `min-width: 501px` block). Prose links lost their underline on 2026-10-14 (27ce695) by your choice: stamp red at rest, ink on hover. The back links rely on their small uppercase type.
- Button underline. The app has no `.button` class. Its buttons are `<button>` elements, except the case source link, `<a class="icon-btn">`, which never sets `text-decoration: none`. It holds only an SVG, so nothing shows, but the rule pins it.
- Tooltip containment. Already met in most respects: one bubble on `<body>`, measured and clamped with a 10px margin, flipping above or below, hiding on scroll and resize, and showing on keyboard focus. Two gaps: inside an open poster, `positionTip()` clamps to the window (`column = null`), not to the `.poster` box, so a bubble near the poster's edge can overhang it; and `.tip` never sets `text-align: left` explicitly, which the rule requires.

## The changes

1. The 404 page. Add `404.html` at the root (and to step 4's root allowlist) on the step 11 layout. It carries the site header, a masthead in the page's voice ("File not found" under the bureau line), a link back to the registry, the footer, and step 10B's tag (`js/gtm.js` first in the head with `data-gtm-id="GTM-5FJGP2"`, and the `<noscript>` frame after `<body>`). Nginx serves it at whatever depth the bad URL had, so relative paths would break; give `404.html` alone `<base href="/tools/models-gone-wild/">` and keep its paths relative to it, and add `404.html` as the one exception in the leading-slash test. On both servers, add `error_page 404 /tools/models-gone-wild/404.html;` inside this app's page block and denylist block. `scripts/serve.py` serves the same file with a 404 for any path it cannot find. Add `noindex` in a robots meta tag.
2. When `posterFromUrl()` names no case, show a "no such file" notice where the poster would open, with a link to the registry, and add `<meta name="robots" content="noindex">` to the head from the script.
3. Add a `<nav class="footer-nav">` with two icon discs, Methodology and the announcement post (`https://www.annielytics.com/blog/ai/models-gone-wild-an-app-to-track-the-model-containment-crisis/`), drawn with inline SVG in the line-icon style, following `~/.claude/rules/design/apply-footer-icon-disc-redesign.md` for the disc and the hover pill. Keep "Last updated" beneath. Propose the two icons in prose first and stop for approval.
4. Mark the sweep rule not applicable to prose links in the README (decision 20a), citing 27ce695. The nav keeps its sweep.
5. Pin `text-decoration: none` on `.icon-btn` and its `:hover`, `:focus`, `:active`, and `:visited` states, per `~/.claude/rules/design/remove-underlines-from-buttons.md`.
6. In `js/tooltip.js`, clamp to the `.poster` box when the trigger is inside an open poster, and to `.content` otherwise. Add `text-align: left` to `.tip`.
7. Tests: an unknown path through the preview server returns 404 with the app's title; an unknown poster slug shows the notice and the robots tag (browser test); a glossary bubble inside an open poster sits at least 10px inside the poster at 375 and 1440 (browser test); `.tip` computes `text-align: left`.

## The sample-file review gate

- HTML: `404.html` is new. `index.html` is the sample for the footer nav; `methodology/index.html` and `404.html` follow.
- CSS: `css/charts.css` is the sample since it holds the tooltip. `base.css` (footer discs) and `registry.css` (`.icon-btn`) follow.
- JavaScript: `js/tooltip.js` is the sample; `js/poster.js` (the unknown-slug notice) follows.

## Done when

Each rule's verifying checklist passes in a browser at desktop and 375 pixels wide (hover, keyboard focus, and the worst-case tooltip near a poster edge); at the staging origin `no-such-page/` returns 404 with the app's page and `.git/config` still returns 403; the CSP walk reports zero violations with the 404 page added to its routes; and both suites pass.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py`, with the formatter re-run where a change moved a column.

## Rollback

Revert the commits. Restore the config backup on each server, run `sudo nginx -t`, reload, and add a PCI row.

## Paste-ready prompt: build and stage

```
Run step 12 (design rules and the 404 page) of the Models Gone Wild
standards cleanup, following docs/standards-cleanup/12-design-rules.md
exactly. Read docs/standards-cleanup/README.md and the four rules it names
in ~/.claude/rules/design/ first. Use decisions 1, 19, 20, and 21 as
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

1. Confirm step 11 is merged and live. Branch off an up-to-date main as
   standards-design-rules. Never work on main.
2. Run both suites and confirm they pass.
3. Propose the two footer icons in prose and STOP
   until I approve them.
4. Sample-file review gate (CSS and JavaScript): fix the tooltip in
   js/tooltip.js and css/charts.css first. Give me clickable links, a short
   summary, the result of the in-poster tooltip test, and the git diff
   command, and STOP until I approve.
5. Sample-file review gate (HTML): add the footer nav to index.html,
   run the screenshot diff, and give me the link, the changed screenshots,
   and the diff command. STOP until I approve. Then methodology/index.html.
6. Build 404.html with its base href, the serve.py fallback, the unknown
   poster notice, the .icon-btn fix, and the README mark for decision 20a. Add the tests, and add the 404
   page to the CSP walk's routes.
7. Run both suites, the CSP walk, the screenshot diff, and the comment style
   checker (0), gating on each exit code.
8. On the server: back up
   /etc/nginx/sites-available/staging.annielytics.conf, add error_page 404
   to this app's staging page and denylist blocks, show me the diff, and
   STOP until I approve. Then sudo nginx -t, reload, wait two seconds, and
   write the PCI change-log row yourself, reading it back.
9. Commit, push, deploy the branch to staging with the README command, and
   run the staging health check (no-such-page/ must be a 404 with the app's
   page).
10. Report what you verified and how, give me the staging links including
    the 404 page and https://staging.annielytics.com/tools/models-gone-wild/poster/no-such-slug/,
    and STOP. Do not merge to main or touch production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/12-design-rules.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you have checked step 12 on staging. It needs no edits.

```
Ship step 12 (design rules and the 404 page) of the Models Gone Wild
standards cleanup to production, following
docs/standards-cleanup/12-design-rules.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 12 only,
including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-design-rules, gating on each exit code.
2. Merge standards-design-rules to main and push, and deploy main to
   production with the README command.
3. Back up /etc/nginx/sites-available/annielytics.conf, add error_page 404
   to this app's page and denylist blocks, run sudo nginx -t, reload, and
   wait two seconds. Write the PCI change-log row yourself and read it back.
4. Run the production health check. no-such-page/ must return 404 with the
   app's page, and .git/config must still return 403.
5. Give me https://www.annielytics.com/tools/models-gone-wild/no-such-page/
   and https://www.annielytics.com/tools/models-gone-wild/poster/no-such-slug/
   to check, with a reminder to hard-refresh and hover a glossary term
   inside an open poster.
6. Switch staging back to main with the README command.
7. Mark step 12 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
8. Tell me the next step is step 13A, whose prompt is at the bottom of
   docs/standards-cleanup/13a-web-root.md.
```
