# Step 10B: An Enforced Content Security Policy and the Analytics Tag

Branch: `standards-csp`

## Decisions this step reads

Decision 4a (the headers live in one repo file, copied to a staging and a production snippet) and decision 17b (the app gets Google Tag Manager, as AI Timeline and AI Strategy have), recorded in `docs/standards-cleanup/README.md` on 2026-10-16.

## Background

On 2026-10-16 nothing set a Content Security Policy, at nginx or anywhere else, and the app loaded no analytics tag. Steps 9A, 9B, and 10A leave the page in this state.

- Every script is a file from this app. There is no inline script, no `eval`, and no in-browser compiling.
- Every stylesheet and font is a file from this app. Google Fonts are gone.
- The script sets styles only through `element.style` and `style.setProperty`, which a policy allows. No markup or template string carries a `style=` attribute.
- The body's paper texture is a `data:` SVG in the stylesheet, so `img-src` needs `data:`.
- html2canvas builds each downloaded poster on a canvas and hands it back as a `data:` URL, so `img-src` needs `data:` and `blob:`.

The tag is the site-wide container, GTM-5FJGP2, which AI Timeline and AI Strategy already load. On 2026-10-16 it held exactly one tag, the Google Tag firing GA4 G-2CGX3KD64R, plus built-in variables and one Custom JavaScript variable. It has no Custom HTML tag, so nothing in it injects an inline script and no nonce is needed, which a static page served by nginx could not mint per request anyway. If a Custom HTML tag is ever added in GTM, this policy will block it.

AI Timeline loads the container through an external loader, `static/js/gtm.js`, which reads the container ID from its own `data-gtm-id` attribute, so the page carries no inline snippet. This app copies that file as it is. AI Timeline's policy also found, on the day it was enforced, that GA4 with Google Signals sends each hit to `analytics.google.com`, `stats.g.doubleclick.net`, and `www.google.com` as well as `*.google-analytics.com`. The walk aborts Google's hosts and cannot see those, so the connect list below copies AI Timeline's exactly, and a test keeps it intact.

One risk needs checking rather than assuming. html2canvas clones the page into a hidden same-origin frame and, to draw `::before` and `::after` content, injects a `<style>` element into the clone. The frame inherits the page's policy, so `style-src 'self'` may refuse that `<style>`. The cards' icon buttons and the glossary terms use pseudo-elements. The walk downloads a poster with the policy on and records any violation. If one appears, stop and bring the options to Annie rather than adding `'unsafe-inline'`. A looser rule for the poster alone is not possible since one policy covers the whole response.

Cloudflare sits between nginx and every visitor and can add its own scripts (APO, email obfuscation, Rocket Loader, a beacon). The local walk cannot see those, so the last check is the browser console on production.

## The policy

```
default-src 'self'; script-src 'self' https://www.googletagmanager.com; style-src 'self'; img-src 'self' data: blob: https://*.google-analytics.com https://*.googletagmanager.com https://*.g.doubleclick.net https://*.google.com; font-src 'self'; connect-src 'self' https://www.google-analytics.com https://*.google-analytics.com https://*.analytics.google.com https://analytics.google.com https://*.google.com https://*.g.doubleclick.net https://*.googletagmanager.com; frame-src https://www.googletagmanager.com; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'self'
```

`frame-src` admits the tag's `<noscript>` fallback frame. `frame-ancestors 'self'` matches `X-Frame-Options: SAMEORIGIN` (decision 5a).

## The changes

1. Copy `~/Dropbox/Annielytics/Code/Python/AI Timeline/static/js/gtm.js` to `js/gtm.js`, rewriting only its header comment for this app. Load it as the first script in the `<head>` of `index.html` and `methodology/index.html` (step 12 builds `404.html` with it), with a relative path and `data-gtm-id="GTM-5FJGP2"`. Put the fallback right after `<body>` on each page as `<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5FJGP2" height="0" width="0" class="gtm-noscript-frame"></iframe></noscript>`, and hide `.gtm-noscript-frame` in `base.css` (`display: none; visibility: hidden;`) since an inline `style=` would break step 9B's guard.
2. Add `add_header Content-Security-Policy "<the policy>" always;` to `deploy/nginx/headers.conf`. `scripts/serve.py` already sends that file's headers, so the local preview enforces the same policy.
3. Port AI Strategy's walk (`~/Dropbox/Annielytics/Code/Python/AI Strategy/leaderboard_assistant/scripts/csp-walk/`, with `walk.py`, `run.sh`, and `routes.py`) into `scripts/csp-walk/`, using this repo's `venv` and serving each ref from a worktree under `/tmp` with that ref's `scripts/serve.py`. Like AI Strategy's, it lets GTM load so the container is checked against the policy, and aborts only the analytics beacons, after the policy has judged them, so the walk never sends a hit to GA4. The routes are the home page, `threat-matrix/`, `lab-counts/`, all 21 poster permalinks (read from `js/cases.js`), `methodology/`, and an unknown path. The states are each tab, each filter, a glossary bubble on hover, an open poster, Copy link, and Download poster with the PNG actually produced. It records every `securitypolicyviolation` event and every JavaScript error, and exits 1 on any.
4. Add `tests/test_csp.py`. The preview server sends the policy on every page, as `Content-Security-Policy` and not `-Report-Only`, with no `'unsafe-inline'` or `'unsafe-eval'`. Its `connect-src` names `analytics.google.com`, `*.google.com`, and `*.g.doubleclick.net`. Every page loads `js/gtm.js` as its first script with `data-gtm-id="GTM-5FJGP2"` and carries the `<noscript>` frame. Mark a test that runs the walk as `browser`.
5. Update `DEPLOY.md`: the "Fonts fall back" troubleshooting entry, which says nothing in this app sets a policy, and a note that the page loads GTM-5FJGP2.

## The sample-file review gate

- Python: `scripts/csp-walk/walk.py` is the sample since it carries the routes and the states. Write it with `run.sh`, run it against `main` (no policy, so zero violations by definition) and against the branch, and stop for approval before the test file.
- HTML: `index.html` is the sample for the tag and the fallback frame. `methodology/index.html` follows after approval.
- JavaScript and config: There is one new file of each, so there is nothing to sample.

## Done when

`scripts/csp-walk/run.sh standards-csp` reports zero violations and zero JavaScript errors across every route and state, with a poster downloaded. `curl -skI` at the staging origin shows `Content-Security-Policy` on every page. Both suites pass. On staging, GTM's Preview mode (Tag Assistant) shows the Google Tag firing on the home page with no blocked request, and GA4's Realtime report shows the visit. After the ship, the browser console on production shows no violation on the home page, a poster, and Methodology.

## Rollback

Restore the snippet backup on the affected host (`models-gone-wild-headers.conf` for production, `models-gone-wild-headers-staging.conf` for staging), run `sudo nginx -t`, reload, and add a PCI row. The policy lives only in nginx, so that rollback needs no code deploy. Reverting the commit removes the tag.

## Paste-ready prompt: build and stage

```
Run step 10B (Content Security Policy and the analytics tag) of the Models
Gone Wild standards cleanup, following docs/standards-cleanup/10b-csp.md
exactly. Read docs/standards-cleanup/README.md first. Decisions 4a, 5a, and
17b apply (recorded 2026-10-16).

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step 10A is merged and live. Branch off an up-to-date main as
   standards-csp. Never work on main.
2. Run both suites and confirm they pass.
3. Sample-file review gate (HTML): copy AI Timeline's static/js/gtm.js to
   js/gtm.js, load it first in index.html's head with
   data-gtm-id="GTM-5FJGP2", add the noscript frame after <body> with the
   gtm-noscript-frame class, and hide that class in css/base.css. Give me a
   clickable link to index.html, a short summary, and the git diff command,
   and STOP until I approve. Then do methodology/index.html.
4. Sample-file review gate (Python): port AI Strategy's csp-walk into
   scripts/csp-walk/ with the routes and states the step file lists,
   including a real poster download, letting GTM load and aborting only the
   analytics beacons. Run it against main, then add the policy from the
   step file to deploy/nginx/headers.conf and run it against the branch.
   Give me a clickable link to walk.py, a short summary, both reports, and
   the git diff command, and STOP until I approve.
5. If the walk records a violation from html2canvas or anything else, STOP
   and bring me the options. Do not add 'unsafe-inline' or 'unsafe-eval'.
6. Add tests/test_csp.py and update DEPLOY.md.
7. Run both suites, the walk, the screenshot diff (pixel-identical), and
   the comment style checker (0), gating on each exit code.
8. On the server: back up
   /etc/nginx/snippets/models-gone-wild-headers-staging.conf, copy the
   updated deploy/nginx/headers.conf over it, show me the diff, and STOP
   until I approve. Then sudo nginx -t, reload, wait two seconds, and write
   the PCI change-log row yourself, reading it back.
9. Commit, push, deploy the branch to staging with the README command, run
   the staging health check, and show me the policy header at the staging
   origin.
10. Report what you verified and how. Give me the staging links, and ask me
    to open the browser console on the home page and a poster, download a
    poster, and check GTM Preview mode and GA4 Realtime for the visit. Then
    STOP. Do not merge to main or touch production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/10b-csp.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once the console and Tag Assistant on staging are clean. It needs no edits.

```
Ship step 10B (Content Security Policy and the analytics tag) of the
Models Gone Wild standards cleanup to production, following
docs/standards-cleanup/10b-csp.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 10B only,
including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-csp, and scripts/csp-walk/run.sh standards-csp, gating on
   each exit code.
2. Back up /etc/nginx/snippets/models-gone-wild-headers.conf, copy
   deploy/nginx/headers.conf over it, run sudo nginx -t, reload, and wait
   two seconds, so the policy that admits GTM is live before the tag ships.
   Write the PCI change-log row yourself and read it back.
3. Merge standards-csp to main and push, and deploy main to production with
   the README command.
4. Run the production health check and show me the policy header at the
   production origin.
5. Ask me to open the browser console on
   https://www.annielytics.com/tools/models-gone-wild/, a poster, and
   Methodology, download a poster, and confirm the visit in GA4 Realtime.
   If anything was refused, help me roll back with the step file's rollback
   before anything else.
6. Switch staging back to main with the README command.
7. Mark step 10B done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
8. Tell me the next step is step 11, whose prompt is at the bottom of
   docs/standards-cleanup/11-layout.md.
```
