# Models Gone Wild Standards Cleanup

This folder brings Models Gone Wild up to the standards AI Strategy reached in October 2026, one step per file. Each step has the background, the exact changes, the "done when" check, a rollback, and two prompts at the bottom: a build-and-stage prompt you paste into a fresh session, and a ship-to-production prompt Claude runs in that same session when you reply with its letter. Run one step per Claude Code session, and let each step reach production before starting the next.

The steps are the fixed list in `~/.claude/skills/app-refactor-audit/baseline.md`, in its order, with none dropped, plus formatting steps F1 to F7, which run right after step 3 (see below). Step 5 is retired into step F7. The app has never had a cleanup, so the plan also turns every finding from a full audit into a step or a decision.

The findings came from running `~/.claude/skills/app-refactor-audit/scripts/audit_app.py` and each step's "done when" command on 2026-10-16, read only, then reading the code, the production checkout, and the live nginx config.

## Formatting comes first

Reformatting every Python, HTML, CSS, and JavaScript file to match AI Strategy is one of the most important revisions in this cleanup. AI Strategy is the only app that has been fully reformatted, and every file in this app has to read the way its files do when the cleanup ends.

Annie set the order on 2026-10-17. Formatting steps F1 to F7 run next, right after step 3, before step 4 or any later step starts, and every step after them keeps the files it touches formatted. The first draft of this plan formatted only the code each step moved, so the files no step touched would have kept their old layout, and every step in between would have kept writing into unformatted files.

Annie revised the order on 2026-10-17, during step F2, under decision 31. The page is split into files right after F2, since formatting code that is about to leave the page does little good and the gate can only check JavaScript that lives in `.js` files. Step F2 formats the `index.html` script and ships, steps 9A and 9B then move the case data and the rest of both scripts into `js/`, and F3 to F7, step 4, and the rest follow.

Read these before any formatting work:

- The rules: The formatting rule at `~/.claude/rules/formatting/code-formatting.md`, with the column rules, the one-line comment rule, the file structure, and the sweep procedure, and the gate at `~/.claude/rules/formatting/format-gate.md`
- The examples: One worked file per language in `~/.claude/formatting-examples/`
- The model files: AI Strategy's own files in `~/Dropbox/Annielytics/Code/Python/AI Strategy/leaderboard_assistant/`, namely `services/filters.py` and `scripts/csp-walk/walk.py` for Python, `static/css/base.css` and `static/css/components.css` for CSS, `static/js/network.js` and `static/js/page-tools.js` for JavaScript, and `templates/base.html` and `templates/index.html` for the pages
- The tools: The formatters, the tidiness audit (`audit_format.py`), the gate (`check_format.py`), the equivalence proof (`verify_equivalent.py`), and the comment tools in `~/.claude/formatting-tools/`
- The handoff: `~/.claude/formatting-tools/HANDOFF-prompt.md`, with the rules AI Strategy's sweep settled on 2026-10-13 and its pitfalls
- The comment style: The annielytics-comment-style skill and its `check_style.py`

Every file in AI Strategy meets these standards, and every file here must meet them too:

- Values line up in columns, and a long line that keeps its column beats a short line that breaks it.
- The stylesheet has one main value column and a second one for its long property names, with media queries sharing both.
- The comments that stay are the About This File section, the section banners, and in Python the import group labels and the docstrings. Label comments above a rule or a line are deleted, not shortened, since they were notes for editing by hand. Annie set this on 2026-10-17 during step F1. Docstring explanations and each Args and Returns entry are one line. Only the About This File section runs longer.
- No comment sits inside a block (a CSS rule, an object, or a dict), apart from short group labels in `:root`.
- Every file opens with an About This File section. Python files also follow `filters.py`'s banners (Imports, Global Variables, then one per section) with no loose code.
- Python, JavaScript, and HTML attributes use double quotes.
- Every Python function carries full type hints.
- Comments carry no history, no commented-out code, and no names.

Three things set this app apart from AI Strategy. Its JavaScript is inline in the two pages until steps 9A and 9B move it into files, which run right after step F2 under decision 31. The pages are static, with no template engine, so the 20 HTML comments are deleted under decision 26 rather than turned into Jinja comments. The `CASES` and `GLOSSARY` data inside the main script stays byte for byte through F2 since the check scripts, the tests, and the add-case skill parse it as written, and step 9A settles its format under decision 30.

The steps run in the order AI Strategy's sweep ran, measured with `audit_format.py` and `check_format.py` on 2026-10-17, read only:

| Step | Covers | Before (audit on 2026-10-17) |
|---|---|---|
| F1 | 1 CSS file, `css/styles.css`, 972 lines | Not clean. No About section, 15 value columns where the rule allows 2, 135 uneven runs, 59 comments over one line, 64 wordy, 6 inside a rule, 3 history notes, 21 banner problems. No screenshot harness and no hook, so F1 adds both. |
| F2 | The inline scripts, 2,014 lines (1,996 in `index.html`, 18 in `methodology/index.html`) | Neither clean. 82 uneven runs, 90 comments over one line, 109 wordy, 7 inside a block, 1 mixed placement, 3 history notes, 32 banner problems, and 18 of `check_style.py`'s 70 issues. The one `.js` file is the vendored html2canvas, which stays as shipped. |
| F3 | 15 Python files, 2,508 lines | 7 clean (`serve.py` and six test files). The other 8 hold 25 uneven runs, 6 comments over one line, 8 wordy, 3 history notes, 8 banner problems, and 51 of `check_style.py`'s issues. 7 lack an About section and 6 end with a newline. Heaviest: `scripts/scout_seen.py`. |
| F4 | 2 pages, 2,371 lines | Neither clean. Neither has an About section, both end with a newline, and they hold 15 comments over one line, 15 wordy, and the 20 HTML comments decision 26 deletes. Step F2 deleted the 15 in `index.html` at Annie's request on 2026-10-17. Markup indented two spaces, where the rule wants four. |
| F5 | requirements, shell, editor settings | `requirements-dev.txt` (2 pins, not aligned), the 2 shell scripts F1 adds, and no `.vscode/settings.json`. |
| F6 | Quotes | 27 single-quoted Python strings, all holding a double quote, so all stay. About 330 single-quoted strings in the inline scripts outside the data, about 8 of which stay. No single-quoted HTML attributes. |
| F7 | Python structure and type hints, formerly step 5 | 1 function without a hint. 11 files keep top-level names only one function uses, `capture.py` the most with eight (remeasured 2026-10-18, after step 9A gave every script a `main()`). |

Once a language's F step ships, its files stay formatted for the rest of the cleanup. Every later step runs `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py` on each file it changes or creates, fixes every finding before it commits, and re-runs the formatter where a change moved a column (a token name longer than the value it replaced, say). A step is not done while a file it touched has a finding. Under decision 28a, the pre-commit hook from step F1 enforces the same on every commit, one language at a time as each step adds it (step 9B adds `js`).

## This app is live, static, and indexed

The app is public at https://www.annielytics.com/tools/models-gone-wild/. It is two static HTML pages, one stylesheet, one vendored library, and a logo, served by nginx straight from the git checkout at `~/apps/models-gone-wild`. There is no Flask, no gunicorn, no systemd unit, no server virtualenv, and no database. A deploy is a `git pull` on the server, and nginx serves the change on the next request.

That shapes the plan in three ways.

- Several baseline steps were written for a Flask app. Each still has its file. Where part of a step cannot apply here (a secret key, a DEBUG flag, a debug route), the step file shows the evidence and does the part that does apply.
- Every header, redirect, and 404 comes from nginx, so the security, policy, 404, and URL steps change nginx. Each of those changes gets a row in the PCI Network Security Change Log.
- There is no staging copy today. Step 0B adds one (decision 1a), and every later step deploys there before production.

Behavior stays identical unless a step says otherwise or a decision below approves an intended change.

## What the audit found

The audit script reported five findings. Each was checked against the code and against nginx on the server.

| Finding | Severity | Verdict | Step or decision |
|---|---|---|---|
| No sign of CSRF protection | HIGH | False positive. The app has no form, no POST endpoint, no session, and no cookie. Nginx serves files only. | Step 1 adds a guard test that fails if a POST form or a cookie ever appears. |
| No test suite | HIGH | Confirmed. No `tests/`, no pytest, no virtualenv. Six check scripts in `scripts/` run by hand. | Step 1, decisions 2 and 3 |
| No baseline security response headers | MEDIUM | Confirmed at the origin. No page, stylesheet, or script returns `X-Content-Type-Options`, `X-Frame-Options`, or `Referrer-Policy`. | Step 2, decisions 4 and 5 |
| No requirements.txt | LOW | Confirmed, and by design. Production installs nothing, and every script uses the standard library. The test tools step 1 adds will need a pinned file. | Step 3, decision 7 |
| No Content Security Policy | LOW | Confirmed. Nothing sets one, and both pages load Google Fonts from Google. | Steps 10A and 10B, decisions 4 and 17 |

The script also suggested an inline-code step while reporting no inline-code finding. Its inline check reads only a `templates/` folder, which a static app does not have, so it never scanned `index.html`. The hand review below covers it.

## What the review found by hand

- There is no staging copy and no staging nginx block for this app. `UPDATE.md`'s "Adding a case" and "Changing copy" prompts end in "commit, push, and deploy" to production, and the add-case skill ends in "Commit, then deploy", so content reaches the live site with no stop for your word after the build. Decisions 1 and 9.
- Staging sits behind basic auth for the whole host, so a check run on the server cannot reach a staging copy without credentials. Nginx takes the client address only from Cloudflare's ranges (`/etc/nginx/conf.d/cloudflare-real-ip.conf`), so letting loopback through without a password is safe. Step 0B.
- `index.html` carries one inline `<script>` of 1,996 lines (lines 217 to 2214), 411 of them the `CASES` array. `methodology/index.html` carries an 18-line inline script for the menu. Neither page has a `<style>` block, a `style=` attribute, or an `on*=` handler. Steps 9A and 9B.
- Four check scripts (`check_charges.py`, `check_claims.py`, `check_dates.py`, and `check_slugs.py`), the two snippets in `UPDATE.md`, and the add-case skill (one file at two paths, since the home copy is a symlink to the repo's skill folder, and `scout/SCOUT.md` follows it) read the cases by matching `<script>(.*?)</script>` in `index.html`, each with its own copy of the loader. `check_quotes.py` scans the `CASES` span of `index.html`. Moving the data breaks all of them unless they move together. Step 9A.
- Nginx caches everything under `js/` and `img/` for 30 days. Any app code or case data moved into `js/` would reach returning readers a month late. Decision 15.
- `js/html2canvas.min.js` (198 KB, version 1.4.1, the current release) loads render-blocking in `<head>` on every visit, though only the Download poster button uses it. Decision 16.
- Both pages load Oswald, Special Elite, Courier Prime, and a one-glyph Noto Emoji subset from `fonts.googleapis.com`. Under a policy without `'unsafe-inline'`, Cloudflare APO's rewrite of those links would block every face, per `~/.claude/rules/design/self-host-google-fonts.md`. Step 10A.
- The app loads no analytics tag, unlike the other public tools, which share GTM-5FJGP2. Decision 17.
- The production checkout holds a `.env` with a `CLOUDFLARE_API_TOKEN` (mode 600, written 2026-10-16) inside the folder nginx serves. A server-wide `location ~* /\.env$` rule returns 403 for it, so it is not public. No tracked file reads the variable. Decision 6.
- The page and the stylesheet each return two `Cache-Control` headers because the page block sets both `expires -1` and `add_header Cache-Control`. Step 2.
- An unknown path returns nginx's built-in 162-byte 404 page, not one in the app's design. Step 12.
- `/poster/no-such-slug/` returns 200 with the full page, so a mistyped or retired poster link is a soft 404. Decision 21.
- No page carries a canonical tag, a meta description, or Open Graph tags. The home page, both view permalinks, all 21 poster permalinks, and `/index.html` serve the same HTML with a 200. Decisions 24 and 25.
- The web root is the git checkout, so `.claude/`, `scout/`, `scripts/`, `DEPLOY.md`, and `UPDATE.md` sit in it. An extension denylist (`md|txt|json|ya?ml|lock|py`) keeps them private today, and any new kind of file would be public until someone adds its extension. Decision 23.
- Layout. The v2 header sits inside the page wrapper, which is named `.wrap` rather than `.main-content`. The footer is a one-line `.site-foot` ("Last updated") inside the 920px `.content` column. There is no `<main class="page-body">`, and the wrapper is not a flex column, so a short page cannot pin its footer. The Methodology page's `<main class="method">` sits inside `.content`. Step 11, decision 18.
- The site header is copied by hand into `methodology/index.html` ("Keep the two in step"). Nothing checks that the copies match. Step 1.
- Tooltips already follow most of the containment rule. One bubble sits on `<body>`, and `positionTip()` places it with a 10px clamp, flips it when needed, and hides it on scroll and resize. Two gaps remain. Inside an open poster the bubble clamps to the window rather than the poster box, and `.tip` never sets `text-align: left` explicitly. Step 12.
- Prose links lost their underline on 2026-10-14 (27ce695), by your choice, and change color on hover. The sweep-underline rule adds a hover underline. The nav menu already has the sweep. Decision 20.
- The footer has no links, so the footer icon discs have nothing to attach to. Decision 19.
- The `.icon-btn` anchors (a case's source link) never set `text-decoration: none`. Each holds only an SVG, so nothing shows today. Step 12.
- `index.html` holds 31 hex colors in JS constants (`DISC_FILL`, `M_INK`, `M_PAPER`, `M_WHITE`, `M_BACK`) and the two legend SVGs. Most repeat CSS tokens (`#8f1d16` is `--stamp-red`, `#5a6b2a` is `--class1`). The raw-value checker scans CSS and Python only, so it reports the HTML clean. Decision 12.
- No pre-commit hook and no CI. Every check runs only when someone remembers it. Steps 1, F1, and 8.
- Two scout branches from 2026-10-07, `update/claude` and `update/sol`, are unmerged and edit `CASES` in `index.html`. Decision 11.
- 26 local branches and 8 remote branches are already merged into `main`. Decision 10.
- Two server-wide items sit outside this app's blocks. `sites-available/` holds 53 backups (23 of `annielytics.conf` and 30 of `staging.annielytics.conf`, counted 2026-10-16), and `server_tokens off` is commented out in `nginx.conf`, so the origin names `nginx/1.18.0`. Cloudflare replaces that header, so the public never sees it. Decision 26.
- `~/.claude/rules/formatting/code-formatting.md` turns HTML comments into Jinja comments. A static page has no Jinja, so its `<!-- -->` comments must stay and ship in the page source. Decision 26, carried out in step F4.
- `scout/seen.json` on `main` is a seed the scout overwrites at the start of every run. It is 922 lines behind the live ledger on `scout-state`. Decision 26.
- The mobile menu's link text is `antiquewhite`, where the v2 header rule says white. The `nav-antiquewhite` and `menu-toggle-antiquewhite` branches show it was chosen. Decision 26.

These checked out fine, so they are not in the plan. With no Python serving pages, there is no secret key, DEBUG flag, debug route, request logging, or `str(e)` response. There are no systemd units and no server virtualenv, so nothing differs between units or interpreters. The production checkout holds no dumps, `.bak` files, or logs, and is clean on `main` at 27ce695. At the origin, `.git/config` and `.gitignore` return 403, and `DEPLOY.md`, `scout/SCOUT.md`, `scripts/serve.py`, and the skill's `SKILL.md` return 404. No shipped code hardcodes the URL prefix (the five strings in shipped files are all in comments). The mobile header matches the v2 rule's padding values and uses the single `change` listener. `.git` is Dropbox-ignored and no conflicted copies exist.

## Before numbers

| Step | "Done when" check | Before (2026-10-16) |
|---|---|---|
| 0 | `xattr -p com.dropbox.ignored .git venv` prints 1 for each | `.git` prints 1. `venv`, `.pytest_cache`, and every `__pycache__` do not exist yet. |
| 0B | Staging serves every page at 127.0.0.1 without a password | No staging checkout, no staging nginx block. |
| 1 | `venv/bin/python3 -m pytest` passes and the revert-and-fail proof works | No `tests/`, no `venv`, no pytest. Six check scripts run by hand; `check_overlaps.py` needs Chrome. |
| 2 | The three headers on every page, from nginx at 127.0.0.1 | None of the three on any page, stylesheet, or script. Two `Cache-Control` headers on the page. |
| 3 | Every line pinned with `==`, and `pip-audit` reports nothing | No requirements file of either kind. |
| 4 | A root guard test fails on any other root file | Root holds `.gitignore`, `DEPLOY.md`, `UPDATE.md`, and `index.html`. No guard. |
| 5 (now F7) | `add_type_hints.py --missing` reports zero | 2 functions in 2 files (`check_overlaps.py:218` and `check_slugs.py:42`). The other 3, in `serve.py`, were hinted with the Python sample for the stricter review gate. |
| 6 | `check_style.py` reports 0 | 70. 1 banner (CSS), 18 comment prose (17 in `index.html`, 1 in Methodology), and 51 docstring layout (scripts). `serve.py`'s 5 were fixed with the Python sample. Steps F1, F2, and F3 fix all 70. |
| 7 | The screenshot diff shows no change, no CSS file more than 800 lines | `css/styles.css` is 972 lines. No screenshot harness (step F1 adds it). |
| 8 | `check_raw_values.py` reports zero raw colors, font sizes, and line heights in every CSS file | 90 in `css/styles.css` (5 hex colors, 14 `rgb()`/`rgba()`, 52 font sizes, 19 line heights). 14 tokens, 3 never used. 31 hex colors in `index.html` outside the checker's reach. No gate. |
| 9A and 9B | A test fails on any inline style, handler, or script | 2 inline scripts (1,996 and 18 lines). No guard. |
| 10A and 10B | A browser walk of every page logs zero violations | No policy. No walk harness. Google Fonts load from Google. |
| 11 | The footer rule's gap measurement and tall-window check pass | No `<main class="page-body">`, wrapper not a flex column, footer inside `.content`. |
| 12 | Each design rule's checklist passes in a browser | Nginx's default 404. No footer links. Tooltips clamp to the window inside a poster. |
| 13A and 13B | The before-and-after URL list matches, apart from approved canonical changes | No canonical on any page. `/index.html` and `methodology/index.html` return 200. No URL list tool. The web root holds the repo's tooling, behind an extension denylist. |

## Decisions

Answer these before running the steps. Record each answer here because the step prompts read them from this section and stop if one they need is blank.

1. Staging (every step, and step 0B). a) Add a staging copy at `~/apps/staging/models-gone-wild`, with this app's blocks in `staging.annielytics.conf` behind the existing basic auth and loopback let through, so every step deploys there first (recommended since the house rule is staging before production and this app has no stop between build and live today). b) No staging. Each build stops at the local preview (`scripts/serve.py` on port 8899) and the test suite, and production waits for your word.
   Decision: a, recorded 2026-10-16. Port 8026 is reserved for the staging copy. As a static copy served by nginx it binds no port, so 8026 stays held, unused, in case the app is ever rebuilt on Flask.
2. The bug the revert-and-fail proof uses (step 1). a) 8e726b4, where glossary bubbles spilled past the left edge of the reading column until `positionTip()` clamped them. A browser test asserts every bubble sits at least 10px inside the column (recommended). b) A data invariant, such as two cases sharing a poster slug. c) Claude picks.
   Decision: a, recorded 2026-10-16.
3. The six check scripts (step 1). a) Wrap each in a test that runs it and asserts exit 0, keep them runnable alone, and run `check_overlaps.py` under `-m browser` since it needs Chrome (recommended). b) Leave them as manual commands outside the suite.
   Decision: a, recorded 2026-10-16.
4. Where the headers and the policy live (steps 2 and 10B). a) One file tracked in the repo at `deploy/nginx/headers.conf`, copied to a staging snippet and a production snippet in `/etc/nginx/snippets/` and included in each of this app's serving blocks, with `scripts/serve.py` reading the same file so the local preview sends the same headers (recommended). b) `add_header` lines written into each nginx block by hand, and a separate copy in `serve.py`.
   Decision: a, recorded 2026-10-16.
5. `X-Frame-Options` (step 2). a) `SAMEORIGIN` (recommended, unless the registry is shown in an iframe on another site). b) Omit it.
   Decision: a, recorded 2026-10-16.
6. The Cloudflare token in production's app folder (step 2). a) You delete `~/apps/models-gone-wild/.env` on the server since nothing tracked reads it and the local copy remains (recommended). b) Move it outside the served folder, to `~/.config/models-gone-wild/.env`. c) Leave it, relying on nginx's `.env` rule.
   Decision: a, recorded 2026-10-16.
7. Requirements (step 3). a) Add `requirements-dev.txt` with the test tools pinned with `==`, clean under `pip-audit`, and no `requirements.txt` since production installs nothing. Record html2canvas 1.4.1 and its SHA-256 in `js/VENDORED.md` (recommended). b) Mark step 3 not applicable.
   Decision: a, recorded 2026-10-16.
8. `DEPLOY.md` and `UPDATE.md` (step 4). a) Keep both at the root and allow them in the root guard since the house convention puts `DEPLOY.md` at the root and the skill and the scout point at `UPDATE.md` there (recommended). b) Move both to `docs/` and update every reference.
   Decision: a, recorded 2026-10-16.
9. The prompts that deploy straight to production (step 4). a) Rewrite `UPDATE.md`'s three prompts, its "Deploying the change" section, both copies of the add-case skill, and `DEPLOY.md`'s update section to branch, staging (or the local preview under 1b), and production only on your word (recommended). b) Leave them, treating your approval of a proposal as the go-ahead.
   Decision: a, recorded 2026-10-16.
10. Branches already merged into `main` (step 4). a) Delete the 26 local and 8 remote branches already merged, keeping `main`, `scout-state`, every `update/*` and `candidate/*`, and the current branch (recommended). b) Leave them.
    Decision: a, recorded 2026-10-16.
11. The open scout branches `update/claude` and `update/sol` (before step 9A). a) You publish or close each before step 9A, and its build prompt stops if either still edits `CASES` in `index.html` (recommended). b) Leave them, and rebase each by hand after step 9A moves the data.
    Decision: a, recorded 2026-10-16.
12. The 31 colors in `index.html` (step 8). a) Read them from the CSS tokens at runtime with `getComputedStyle`, so each color has one source and html2canvas still receives literal values when it draws a poster (recommended). b) Tokenize the CSS only and leave the 31.
    Decision: a, recorded 2026-10-16.
13. Token consolidation (step 8B). a) Pixel-identical tokens and the pre-commit gate only (recommended). b) Also run step 8B, which merges near-duplicate colors and snaps the 16 font sizes (e.g., 10.5px, 11px, 11.5px, and 12.5px) onto a scale, a visual change you review.
    Decision: a, recorded 2026-10-16.
14. The case data's format (step 9A). The cases and the glossary move together since the add-case skill edits both. a) Plain scripts, `js/cases.js` and `js/glossary.js`, holding `CASES` and `GLOSSARY` exactly as they are written now, so the skill and the scout keep editing the same object syntax (recommended). b) JSON in `<script type="application/json">` blocks inside `index.html`, with every key quoted. c) `data/cases.json` and `data/glossary.json` fetched at load, which also needs `.json` taken off nginx's denylist for `data/`.
    Decision: a, recorded 2026-10-16.
15. Caching the moved code (step 9A). a) Move html2canvas to `js/vendor/`, narrow the 30-day rule to `js/vendor/` and `img/`, and let the app's own scripts fall through to the no-cache page block like `css/` (recommended). b) Put the app's scripts in a new top-level folder the cache rule never matches, with no nginx change. c) Add a hand-edited `?v=` to each script tag on every change.
    Decision: a, recorded 2026-10-16.
16. Loading html2canvas (step 9B). a) Load it on the first Download poster press, saving 198 KB on every other visit (recommended). b) Add `defer`. c) Leave it in `<head>`.
    Decision: a, recorded 2026-10-16.
17. An analytics tag (step 10B). a) Leave the app untagged, so the policy stays `'self'` only. b) Add Google Tag Manager through an external loader file, as AI Timeline does, and allow it in the policy.
    Decision: b, recorded 2026-10-16. Same container as AI Timeline and AI Strategy, GTM-5FJGP2 (one tag, GA4 G-2CGX3KD64R).
18. The wrapper's name (step 11). a) Rename `.wrap` to `.main-content`, the name the layout and footer rules use (recommended). b) Keep `.wrap` with the same flex rules.
    Decision: a, recorded 2026-10-16.
19. Footer icon discs (step 12). a) Add a footer nav of discs for Methodology and the announcement post, drawn with inline SVG in the app's line-icon style rather than Font Awesome, with "Last updated" kept beneath (recommended). b) Mark the footer disc rule not applicable since the footer has no links.
    Decision: a, recorded 2026-10-16.
20. Prose link hover (step 12). a) Keep your 2026-10-14 choice (stamp red at rest, ink on hover, no underline), and mark the sweep rule not applicable to prose links. The nav keeps its sweep (recommended). b) Add the sweep underline on hover to prose links.
    Decision: a, recorded 2026-10-16.
21. An unknown poster slug (step 12). a) The page shows a "no such file" state in place of the poster and adds `<meta name="robots" content="noindex">` (recommended). b) An nginx map of valid slugs that returns a real 404, which needs an nginx change for every new case. c) Leave it.
    Decision: a, recorded 2026-10-16.
22. The URL prefix mechanism (step 13A). a) Keep relative paths served through nginx's strip-and-rematch as the one mechanism, with `APP_BASE` and `serve.py` as mirrors a test holds in agreement (recommended since no shipped code names the prefix). b) A `<base href>` in each page, retiring the rewrites that serve assets under every permalink. c) Root-relative paths.
    Decision: a, recorded 2026-10-16.
23. Repo tooling in the web root (step 13A). a) Move the served files into `public/` and point nginx's `alias` there, so the denylist is no longer the only thing between `.claude/`, `scout/`, and `scripts/` and the public (recommended). b) Keep the denylist, and add a test that lists every tracked file and fails on one whose extension nginx would serve.
    Decision: a, recorded 2026-10-16.
24. Canonicals and `/index.html` (step 13B). a) A canonical to the home page on `index.html` since every view and poster is the same document, Methodology its own, the 404 none, and a 301 from `/index.html` to the bare path (recommended). b) A canonical per permalink, sent as an nginx `Link` header from each block. c) No canonicals.
    Decision: b, recorded 2026-10-16.
25. Meta description and share tags (step 13B). a) A meta description plus Open Graph and Twitter title, description, and URL on both pages, with no share image (recommended). b) The same plus a share image you design. c) Leave them out.
    Decision: b, recorded 2026-10-16.
26. Small calls. a) Take all four as listed (recommended). Leave the server-wide nginx backups and `server_tokens` for a server-wide pass, which touches every app. Keep the HTML comments as `<!-- -->` when prompt 5 reformats the code. Keep the `scout/seen.json` seed on `main`. Keep the `antiquewhite` menu text. b) Name the ones to change.
    Decision: b, recorded 2026-10-16, with the four named the same day. Leave the nginx backups and `server_tokens` for a server-wide pass after this cleanup, whose prompt is in [server-wide-followup.md](server-wide-followup.md). Delete the 20 HTML comments outright in step 6, with no render step. Keep the `scout/seen.json` seed on `main`. Keep the `antiquewhite` menu text.
27. How a formatting step reaches production (steps F1 to F7). a) Like every other step, each ships only on your word, with its own ship prompt (recommended). b) Claude ships each verified F step itself once every proof passes, and stops on any failure or unexplained difference, the way AI Strategy's sweep ran on 2026-10-12.
    Decision: a, recorded 2026-10-17.
28. The pre-commit hook (step F1). a) Install it per `~/.claude/rules/formatting/format-gate.md`. `scripts/git-hooks/pre-commit` runs the shared gate, `~/.claude/formatting-tools/check_format.py`, on the staged files of each language listed in `scripts/git-hooks/format-languages`, each F step adds its language once every file of it is clean, and step 8 adds its raw-value check to the same hook (recommended). b) The per-step check only, with no hook.
    Decision: a, recorded 2026-10-17.
29. The About This File section on the two pages (step F4). The rule opens every file with one, but these pages have no template engine, so it can only be an HTML comment, which ships in the page source, and decision 26 deletes every HTML comment. a) Keep one short About This File banner as an HTML comment just below the doctype of each page, holding the two warnings that keep a line from being "fixed" wrongly (relative paths, no click handler on `.menu-toggle`), the only comment the guard test allows, so both pages pass the gate and `html` joins the hook (recommended). b) No About section on the two pages, so they never pass `check_format.py`, `html` stays off the hook, and each later step checks its HTML by hand.
    Decision: a, recorded 2026-10-17.
30. The case data's layout (step 9A). Decision 14a moves `CASES` and `GLOSSARY` into `js/cases.js` and `js/glossary.js` byte for byte, but the gate then checks the new files, and the data as written holds 48 uneven runs in `CASES` and 1 in `GLOSSARY`. a) Align the data as it moves, prove the shared loader returns the same cases and glossary before and after, and update every pattern that reads the unaligned form in the check scripts, the tests, `UPDATE.md`, and both copies of the add-case skill, so the skill and the scout write aligned cases from then on (recommended). b) Move the data byte for byte with only an About section added, and accept the two data files as the one known gap in the JavaScript gate.
    Decision: a, recorded 2026-10-17.
31. When the page is split (steps 9A and 9B). a) Right after step F2. F2 ships what it did to the `index.html` script, 9A moves the case data (re-indented to four spaces as it is aligned), and 9B moves the rest, taking over F2's remainder (Methodology's script, the four-space re-indent of each new file, its About section, and `js` on the hook). F3 to F7 then run, and F4 and F6 work on the files rather than inline code (recommended). b) Keep 9A and 9B after step 8.
    Decision: a, recorded 2026-10-17. Annie asked for it during step F2, since formatting inline code she wants out of the page does little good.

## The steps

| Step | File | What it fixes | Size | Status |
|---|---|---|---|---|
| 0 | [00-dropbox-ignore.md](00-dropbox-ignore.md) | `venv` and the caches would sync through Dropbox. Creates the empty `venv` so it can be marked. | Tiny | Done 2026-10-16 |
| 0B | [00b-staging.md](00b-staging.md) | No staging copy. | Small | Done 2026-10-16 (merge 4759143) |
| 1 | [01-tests.md](01-tests.md) | No test suite. Adds one, proven by reverting the tooltip clamp fix (8e726b4). | Medium | Done 2026-10-16 (merge 7eafe8d) |
| 2 | [02-security.md](02-security.md) | No security headers, duplicate `Cache-Control`, the token in the web root. | Small | Done 2026-10-16 (merge fc717de) |
| 3 | [03-requirements.md](03-requirements.md) | No pinned file for the test tools, no record of the vendored library. | Tiny | Done 2026-10-17 (merge 8243928) |
| F1 | [f1-css.md](f1-css.md) | `css/styles.css` to AI Strategy's format, the screenshot harness, and the formatting pre-commit hook. | Medium | Done 2026-10-17 (merge df0fd2d) |
| F2 | [f2-javascript.md](f2-javascript.md) | `index.html`'s inline script to AI Strategy's format and its long comments deleted, the case data left as is. Methodology's script and the `js` hook entry moved to 9B. | Medium | Done 2026-10-17 (merge db0c0a6) |
| 9A | [09a-case-data.md](09a-case-data.md) | The case data inside the inline script, and every tool that reads it there. Moved up under decision 31. | Medium | Done 2026-10-17 (merge c238686) |
| 9B | [09b-inline-code.md](09b-inline-code.md) | The rest of both inline scripts, html2canvas in `<head>`, and the new files' formatting, including `js` on the hook. Moved up under decision 31. | Medium | Done 2026-10-18 (merge 0fcab89) |
| F3 | [f3-python.md](f3-python.md) | 8 Python files to the rule's spacing, comments, and docstrings, and `check_style.py` to 0. | Small | Done 2026-10-18 (merge b2a02f5) |
| F4 | [f4-html.md](f4-html.md) | Both pages to AI Strategy's format, Methodology's 5 HTML comments deleted (`index.html`'s 15 went in F2). | Small | Done 2026-10-18 (merges fe881f3 and fe04ea2, the page banners) |
| F5 | [f5-other-files.md](f5-other-files.md) | The requirements and shell formatting, and the editor settings. | Tiny | Done 2026-10-18 (merge 16bfe73) |
| F6 | [f6-quotes.md](f6-quotes.md) | Double quotes in the app's JavaScript files. | Small | Done 2026-10-19 (merge 604f841) |
| F7 | [f7-python-structure.md](f7-python-structure.md) | `filters.py`'s layout on every Python file, 1 function without type hints. Formerly step 5. | Small | Done 2026-10-19 (merge 754cb52) |
| 4 | [04-root-files.md](04-root-files.md) | No root guard, workflow docs that skip staging, merged branches. | Small | Not started |
| 5 | Moved to [f7-python-structure.md](f7-python-structure.md) | Now step F7. | | Moved 2026-10-17 |
| 6 | [06-comment-style.md](06-comment-style.md) | 70 comment-style issues, which steps F1 to F3 fix, so this step confirms 0 and keeps it there. | Tiny | Not started |
| 7 | [07-split-css.md](07-split-css.md) | 972-line stylesheet. Reuses step F1's screenshot harness. | Medium | Not started |
| 8 | [08-design-tokens.md](08-design-tokens.md) | 90 raw values in CSS, 31 colors in `index.html`, no gate. | Medium | Not started |
| 8B | [08b-token-consolidation.md](08b-token-consolidation.md) | Near-duplicate colors and font sizes. | Medium | Skipped under decision 13a (marked 2026-10-16) |
| 10A | [10a-self-host-fonts.md](10a-self-host-fonts.md) | Google Fonts, which a policy would block under Cloudflare APO. | Small | Not started |
| 10B | [10b-csp.md](10b-csp.md) | No Content Security Policy, no walk harness, no analytics tag. | Medium | Not started |
| 11 | [11-layout.md](11-layout.md) | No `<main class="page-body">`, no pinned footer. | Medium | Not started |
| 12 | [12-design-rules.md](12-design-rules.md) | Default 404 page, soft 404 posters, tooltip and footer gaps. | Medium | Not started |
| 13A | [13a-web-root.md](13a-web-root.md) | No URL list, the prefix mirrors, repo tooling in the web root. | Medium, highest SEO risk | Not started |
| 13B | [13b-canonicals.md](13b-canonicals.md) | No canonicals, the `/index.html` duplicates, no share tags. | Small, SEO risk | Not started |

Steps F1 and F2 sit right after step 3, the last step done when Annie moved the reformat to the front. Steps 9A and 9B follow F2 under decision 31, so F3 to F7 and every later step work in formatted files, with the JavaScript already in `js/`. Step 0B sits after step 0 because every later step deploys to it. Step 9A comes before 9B so the data move, which touches the most tooling, lands on its own. Step 10A comes before 10B because the policy would block the Google Fonts rewrite. Step 13A builds the URL list that proves 13B's changes, and splits the baseline's URL step so each half fits one session.

After step 13B, one server-wide pass remains outside this app, for the nginx backups and `server_tokens`. Its prompt is in [server-wide-followup.md](server-wide-followup.md).

## Rules every step follows

- Never work on `main`. Each step gets its own branch off an up-to-date `main`.
- Run the suite with `venv/bin/python3 -m pytest` before touching anything, so a later failure is known to be new. From step 1 on, run the browser tests too, with `venv/bin/python3 -m pytest -m browser`.
- Gate every deploy on the test exit code. Never put `pytest | tail` in a chain that ends in a push or deploy. Use `set -e` or `|| exit 1`.
- Keep behavior identical unless the step or a decision says otherwise.
- Put everything that can live in a function into one, in every `.py` and `.js` file a step changes or creates. A value used by only one function lives inside that function, and a value read once at startup comes from a function that remembers its result (`functools.lru_cache` in Python). The top level of a file holds only imports, the settings two or more functions share, test parametrize lists and markers (pytest reads them before any test runs), and the entry-point call. A script whose work runs loose at the top level gets a `main()` called under the entry-point guard. This holds the Functions and Global variables rules in `~/.claude/rules/formatting/code-formatting.md` strictly, and step F7 applies it to every existing script and test.
- Follow the sample-file review gate, every step, with no exceptions. The first `.py`, `.js`, `.css`, and `.html` file a step changes or creates is that filetype's sample, even when it is the only file of its type the step touches. A new file counts, test files included. Use the sample the step file names; where it names none, the first file of each type the step reaches is the sample. Finish the sample, give Annie a clickable link to it, a short summary of what changed, and the `git diff` command for it, and STOP. Change or create anything else of that filetype only after she approves it, carrying over any correction she asks for. A step file saying a filetype changes in only one file is never a reason to skip the stop.
- Deploy the branch to staging, confirm it is healthy, give the staging links, and stop. Production only on Annie's explicit word, every time.
- Once a step reaches production, switch staging back to `main`.
- Formatting is a gate, not a nicety. Every file a step changes or creates ends clean on `python3 -I ~/.claude/formatting-tools/check_format.py` and `python3 ~/.claude/skills/annielytics-comment-style/scripts/check_style.py`, matching AI Strategy, per "Formatting comes first". Run both before committing, fix every finding, and re-run the formatter where a change moved a column. From step F3 on, the expected comment-style count is 0. The one standing exception is the vendored `js/html2canvas.min.js`, which stays as shipped.
- Every relative path stays relative. Run the leading-slash check from `UPDATE.md` before every deploy. The two exceptions are `404.html`'s `<base href>` (step 12) and the absolute canonical and share URLs (step 13B), each allowed by name in the test.
- Server `.env` changes are Annie's to make by hand. Claude gives the exact line and file and never edits a `.env` with a command.
- An nginx, firewall, or server package change gets a row in the PCI Network Security Change Log, which Claude writes into the Google Sheet itself (tab "PCI Compliance Log", read the tab first, write below the last filled row, never use the append call, read it back), as `~/.claude/CLAUDE.md` describes. Back up the config first, run `sudo nginx -t` before every reload, and wait two seconds after a reload before checking.
- Plan and code prose follows `~/.claude/rules/editorial/annielytics-writing-rules.md`.
- Exporting the prompts to an Evernote file follows `~/.claude/rules/coding/evernote-exports.md`.

## Common commands

Run the tests locally (from step 1 on):

```
venv/bin/python3 -m pytest
venv/bin/python3 -m pytest -m browser
```

Run the local preview, then open http://127.0.0.1:8899/tools/models-gone-wild/ (the script serves the repo at the real prefix and strips view and poster segments the way nginx does):

```
python3 scripts/serve.py --port 8899
```

Deploy a branch to staging (after step 0B). There is no service to restart since nginx reads files off disk:

```
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 \
  "set -e; cd ~/apps/staging/models-gone-wild && git fetch origin && git checkout <branch> \
   && git pull --ff-only origin <branch> && git log --oneline -1"
```

Deploy to production, only after Annie's go-ahead, once the branch is merged to `main` and pushed:

```
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 \
  "set -e; cd ~/apps/models-gone-wild && git fetch origin && git checkout main \
   && git pull --ff-only origin main && git log --oneline -1"
```

Then switch staging back to `main`:

```
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 \
  "set -e; cd ~/apps/staging/models-gone-wild && git fetch origin && git checkout main \
   && git pull --ff-only origin main"
```

These facts were confirmed against the server on 2026-10-16:

- Production is the checkout at `~/apps/models-gone-wild`, on `main` at 27ce695, served by the six blocks at lines 310 to 372 of `/etc/nginx/sites-available/annielytics.conf` (enabled through `sites-enabled`). The page block aliases the checkout with `expires -1` and no-cache. A regex block hard-caches `js/` and `img/` for 30 days. Another returns 404 for `md`, `txt`, `json`, `yml`, `yaml`, `lock`, and `py`.
- There is no systemd unit, no gunicorn, and no port. Ports 8025 and 8026 are only reserved in the registry.
- Staging, after step 0B, is the checkout at `~/apps/staging/models-gone-wild`, served from `/etc/nginx/sites-available/staging.annielytics.conf` under `staging.annielytics.com`.
- Cloudflare returns 403 to scripted requests for HTML, so every check talks to nginx on the server at `https://127.0.0.1` with a `Host` header.

Run the production health check:

```
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 '
H="Host: www.annielytics.com"; B="https://127.0.0.1/tools/models-gone-wild"
for p in "" methodology/ threat-matrix/ lab-counts/ poster/sol-hugging-face/ DEPLOY.md .git/config no-such-page/; do
  printf "%-28s %s\n" "/$p" "$(curl -sk -H "$H" -o /dev/null -w "%{http_code}" "$B/$p")"; done'
```

Run the staging health check (after step 0B):

```
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 '
H="Host: staging.annielytics.com"; B="https://127.0.0.1/tools/models-gone-wild"
for p in "" methodology/ threat-matrix/ lab-counts/ poster/sol-hugging-face/ DEPLOY.md .git/config no-such-page/; do
  printf "%-28s %s\n" "/$p" "$(curl -sk -H "$H" -o /dev/null -w "%{http_code}" "$B/$p")"; done'
```

Healthy output is five 200s, then 404 for `DEPLOY.md`, 403 for `.git/config`, and 404 for `no-such-page/`. A browser on the public URL is the only way past Cloudflare, so the last check of every step is yours.

## Shipping a step to production

Each step file ends with two prompts, and the only one you copy is the first:

1. Build and stage. Paste it into a fresh session. Claude builds the step, proves it, deploys it to staging, and stops. Its report ends with a lettered to-do that runs the second prompt.
2. Ship to production. Once you have checked staging, reply with that letter, and Claude runs this prompt in the same session. It merges to `main`, does that step's production-only work, deploys, switches staging back to `main`, marks the step done here, names the next step, and pastes that step's build prompt in full for your next session.

Ship every step before starting the next since each build prompt begins by confirming the previous step is live. The order is 0, 0B, 1, 2, 3, F1, F2, 9A, 9B, F3 to F7, then 4, 6, 7, 8, and 10A onward (step 5 is retired into F7, and 8B is skipped). Step 0 has no ship prompt since it only touches your Mac.

## Links to test

### Staging

These need step 0B, and sit behind the staging password.

- Home, with the timeline, filters, and a poster: https://staging.annielytics.com/tools/models-gone-wild/
- Threat Matrix: https://staging.annielytics.com/tools/models-gone-wild/threat-matrix/
- Cases by Lab: https://staging.annielytics.com/tools/models-gone-wild/lab-counts/
- A poster: https://staging.annielytics.com/tools/models-gone-wild/poster/sol-hugging-face/
- Methodology: https://staging.annielytics.com/tools/models-gone-wild/methodology/
- The 404 page: https://staging.annielytics.com/tools/models-gone-wild/no-such-page/

### Production

- Home: https://www.annielytics.com/tools/models-gone-wild/
- Threat Matrix: https://www.annielytics.com/tools/models-gone-wild/threat-matrix/
- Cases by Lab: https://www.annielytics.com/tools/models-gone-wild/lab-counts/
- A poster: https://www.annielytics.com/tools/models-gone-wild/poster/sol-hugging-face/
- Methodology: https://www.annielytics.com/tools/models-gone-wild/methodology/
- The 404 page: https://www.annielytics.com/tools/models-gone-wild/no-such-page/

### Local preview

Use these before any deploy.

- Home: http://127.0.0.1:8899/tools/models-gone-wild/
- Threat Matrix: http://127.0.0.1:8899/tools/models-gone-wild/threat-matrix/
- Methodology: http://127.0.0.1:8899/tools/models-gone-wild/methodology/
