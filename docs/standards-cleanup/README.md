# Models Gone Wild Standards Cleanup

This folder brings Models Gone Wild up to the standards AI Strategy reached in October 2026, one step per file. Each step has the background, the exact changes, the "done when" check, a rollback, and two paste-ready prompts at the bottom, one to build and stage and one to ship to production. Run one step per Claude Code session, and let each step reach production before starting the next.

The steps are the fixed list in `~/.claude/skills/app-refactor-audit/baseline.md`, in its order, with none dropped. The app has never had a cleanup, so the plan also turns every finding from a full audit into a step or a decision.

The findings came from running `~/.claude/skills/app-refactor-audit/scripts/audit_app.py` and each step's "done when" command on 2026-10-16, read only, then reading the code, the production checkout, and the live nginx config.

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
- Four check scripts (`check_charges.py`, `check_claims.py`, `check_dates.py`, and `check_slugs.py`), the two snippets in `UPDATE.md`, and the add-case skill (both copies, which `scout/SCOUT.md` follows) read the cases by matching `<script>(.*?)</script>` in `index.html`, each with its own copy of the loader. `check_quotes.py` scans the whole of `index.html`. Moving the data breaks all of them unless they move together. Step 9A.
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
- No pre-commit hook and no CI. Every check runs only when someone remembers it. Steps 1 and 8.
- Two scout branches from 2026-10-07, `update/claude` and `update/sol`, are unmerged and edit `CASES` in `index.html`. Decision 11.
- 26 local branches and 8 remote branches are already merged into `main`. Decision 10.
- Two server-wide items sit outside this app's blocks. `sites-available/` holds 53 backups (23 of `annielytics.conf` and 30 of `staging.annielytics.conf`, counted 2026-10-16), and `server_tokens off` is commented out in `nginx.conf`, so the origin names `nginx/1.18.0`. Cloudflare replaces that header, so the public never sees it. Decision 26.
- `~/.claude/rules/formatting/code-formatting.md` turns HTML comments into Jinja comments. A static page has no Jinja, so its `<!-- -->` comments must stay and ship in the page source. Decision 26.
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
| 5 | `add_type_hints.py --missing` reports zero | 5 functions in 3 files (`check_overlaps.py:218`, `check_slugs.py:42`, `serve.py:68`, `serve.py:80`, and `serve.py:96`). |
| 6 | `check_style.py` reports 0 | 75. 1 banner (CSS), 18 comment prose (17 in `index.html`, 1 in Methodology), and 56 docstring layout (scripts). |
| 7 | The screenshot diff shows no change, no CSS file more than 800 lines | `css/styles.css` is 972 lines. No screenshot harness. |
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

## The steps

| Step | File | What it fixes | Size | Status |
|---|---|---|---|---|
| 0 | [00-dropbox-ignore.md](00-dropbox-ignore.md) | `venv` and the caches would sync through Dropbox. Creates the empty `venv` so it can be marked. | Tiny | Done 2026-10-16 |
| 0B | [00b-staging.md](00b-staging.md) | No staging copy. | Small | Done 2026-10-16 (merge 4759143) |
| 1 | [01-tests.md](01-tests.md) | No test suite. Adds one, proven by reverting the tooltip clamp fix (8e726b4). | Medium | Done 2026-10-16 (merge 7eafe8d) |
| 2 | [02-security.md](02-security.md) | No security headers, duplicate `Cache-Control`, the token in the web root. | Small | Done 2026-10-16 (merge fc717de) |
| 3 | [03-requirements.md](03-requirements.md) | No pinned file for the test tools, no record of the vendored library. | Tiny | Not started |
| 4 | [04-root-files.md](04-root-files.md) | No root guard, workflow docs that skip staging, merged branches. | Small | Not started |
| 5 | [05-python-structure.md](05-python-structure.md) | 5 functions without type hints. | Tiny | Not started |
| 6 | [06-comment-style.md](06-comment-style.md) | 75 comment-style issues. | Small | Not started |
| 7 | [07-split-css.md](07-split-css.md) | 972-line stylesheet, no screenshot harness. | Medium | Not started |
| 8 | [08-design-tokens.md](08-design-tokens.md) | 90 raw values in CSS, 31 colors in `index.html`, no gate. | Medium | Not started |
| 8B | [08b-token-consolidation.md](08b-token-consolidation.md) | Near-duplicate colors and font sizes. | Medium | Skipped under decision 13a (marked 2026-10-16) |
| 9A | [09a-case-data.md](09a-case-data.md) | The case data inside the inline script, and every tool that reads it there. | Medium | Not started |
| 9B | [09b-inline-code.md](09b-inline-code.md) | The rest of both inline scripts, html2canvas in `<head>`. | Medium | Not started |
| 10A | [10a-self-host-fonts.md](10a-self-host-fonts.md) | Google Fonts, which a policy would block under Cloudflare APO. | Small | Not started |
| 10B | [10b-csp.md](10b-csp.md) | No Content Security Policy, no walk harness, no analytics tag. | Medium | Not started |
| 11 | [11-layout.md](11-layout.md) | No `<main class="page-body">`, no pinned footer. | Medium | Not started |
| 12 | [12-design-rules.md](12-design-rules.md) | Default 404 page, soft 404 posters, tooltip and footer gaps. | Medium | Not started |
| 13A | [13a-web-root.md](13a-web-root.md) | No URL list, the prefix mirrors, repo tooling in the web root. | Medium, highest SEO risk | Not started |
| 13B | [13b-canonicals.md](13b-canonicals.md) | No canonicals, the `/index.html` duplicates, no share tags. | Small, SEO risk | Not started |

Step 0B sits after step 0 because every later step deploys to it. Step 9A comes before 9B so the data move, which touches the most tooling, lands on its own. Step 10A comes before 10B because the policy would block the Google Fonts rewrite. Step 13A builds the URL list that proves 13B's changes, and splits the baseline's URL step so each half fits one session.

After step 13B, one server-wide pass remains outside this app: the nginx backups and `server_tokens`. Its prompt is in [server-wide-followup.md](server-wide-followup.md).

## Rules every step follows

- Never work on `main`. Each step gets its own branch off an up-to-date `main`.
- Run the suite before touching anything, so a later failure is known to be new: `venv/bin/python3 -m pytest`. From step 1 on, the browser tests run too: `venv/bin/python3 -m pytest -m browser`.
- Gate every deploy on the test exit code. Never put `pytest | tail` in a chain that ends in a push or deploy. Use `set -e` or `|| exit 1`.
- Keep behavior identical unless the step or a decision says otherwise.
- Put everything that can live in a function into one, in every `.py` and `.js` file a step changes or creates. A value used by only one function lives inside that function, and a value read once at startup comes from a function that remembers its result (`functools.lru_cache` in Python). The top level of a file holds only imports, the settings two or more functions share, test parametrize lists and markers (pytest reads them before any test runs), and the entry-point call. A script whose work runs loose at the top level gets a `main()` called under the entry-point guard. This holds the Functions and Global variables rules in `~/.claude/rules/formatting/code-formatting.md` strictly, and step 5 applies it to every existing script and test.
- Follow the sample-file review gate, every step, with no exceptions. The first `.py`, `.js`, `.css`, and `.html` file a step changes or creates is that filetype's sample, even when it is the only file of its type the step touches. A new file counts, test files included. Use the sample the step file names; where it names none, the first file of each type the step reaches is the sample. Finish the sample, give Annie a clickable link to it, a short summary of what changed, and the `git diff` command for it, and STOP. Change or create anything else of that filetype only after she approves it, carrying over any correction she asks for. A step file saying a filetype changes in only one file is never a reason to skip the stop.
- Deploy the branch to staging, confirm it is healthy, give the staging links, and stop. Production only on Annie's explicit word, every time.
- Once a step reaches production, switch staging back to `main`.
- New and moved code follows the house comment style and `~/.claude/rules/formatting/code-formatting.md`. Run `python3 ~/.claude/skills/annielytics-comment-style/scripts/check_style.py` before committing. From step 6 on, the expected count is 0.
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

Each step file ends with two prompts, both ready to paste with no edits:

1. Build and stage. Claude builds the step, proves it, deploys it to staging, and stops. Its report ends with the second prompt, copied out for you.
2. Ship to production. Paste it once you have checked staging. It merges to `main`, does that step's production-only work, deploys, switches staging back to `main`, marks the step done here, and names the next step.

Ship every step before starting the next since each build prompt begins by confirming the previous step is live. Step 0 has no ship prompt since it only touches your Mac.

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
