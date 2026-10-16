# Step 10B: An Enforced Content Security Policy

Branch: `standards-csp`

## Decisions this step reads

Decision 1 (staging), decision 4 (where the headers live), and decision 17 (an analytics tag), from `docs/standards-cleanup/README.md`.

## Background

On 2026-10-16 nothing set a Content Security Policy, at nginx or anywhere else. Steps 9A, 9B, and 10A leave the page in this state:

- Every script is a file from this app. There is no inline script, no `eval`, and no in-browser compiling.
- Every stylesheet and font is a file from this app. Google Fonts are gone.
- The script sets styles only through `element.style` and `style.setProperty`, which a policy allows. No markup or template string carries a `style=` attribute.
- The body's paper texture is a `data:` SVG in the stylesheet, so `img-src` needs `data:`.
- html2canvas builds each downloaded poster on a canvas and hands it back as a `data:` URL, so `img-src` needs `data:` and `blob:`.
- The app loads no analytics tag (decision 17), so no nonce is needed, which a static page served by nginx could not mint per request anyway.

One risk needs checking rather than assuming. html2canvas clones the page into a hidden same-origin frame and, to draw `::before` and `::after` content, injects a `<style>` element into the clone. The frame inherits the page's policy, so `style-src 'self'` may refuse that `<style>`. The cards' icon buttons and the glossary terms use pseudo-elements. The walk below downloads a poster with the policy on and records any violation; if one appears, stop and bring the options to Annie rather than adding `'unsafe-inline'`. A looser rule for the poster alone is not possible since one policy covers the whole response.

Cloudflare sits between nginx and every visitor and can add its own scripts (APO, email obfuscation, Rocket Loader, a beacon). The local walk cannot see those, so the last check is the browser console on production.

## The policy

Under decision 17a, the policy reads as follows:

```
default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data: blob:; font-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'none'; frame-ancestors 'self'
```

Under decision 17b, add `https://www.googletagmanager.com` to `script-src`, the GA4 collection hosts to `connect-src` and `img-src`, add an external `js/gtm.js` loader as AI Timeline does, and load it from both pages. `frame-ancestors 'self'` matches `X-Frame-Options: SAMEORIGIN`; under decision 5b, use `frame-ancestors *` and say why in a comment.

## The changes

1. Under decision 4a, add `add_header Content-Security-Policy "<the policy>" always;` to `deploy/nginx/headers.conf`. `scripts/serve.py` already sends that file's headers, so the local preview enforces the same policy. Under 4b, add the line to each of this app's three serving blocks by hand and to `serve.py`.
2. Port AI Strategy's walk (`~/Dropbox/Annielytics/Code/Python/AI Strategy/leaderboard_assistant/scripts/csp-walk/`, with `walk.py`, `run.sh`, and `routes.py`) into `scripts/csp-walk/`, using this repo's `venv` and serving each ref from a worktree under `/tmp` with that ref's `scripts/serve.py`. The routes are the home page, `threat-matrix/`, `lab-counts/`, all 21 poster permalinks (read from the case data), `methodology/`, and an unknown path. The states are each tab, each filter, a glossary bubble on hover, an open poster, Copy link, and Download poster with the PNG actually produced. It records every `securitypolicyviolation` event and every JavaScript error, and exits 1 on any.
3. Add `tests/test_csp.py`: the preview server sends the policy on every page, it is `Content-Security-Policy` and not `-Report-Only`, and it holds no `'unsafe-inline'` or `'unsafe-eval'`. Mark a test that runs the walk as `browser`.
4. Update the "Fonts fall back" entry in `DEPLOY.md`'s troubleshooting, which says nothing in this app sets a policy.

## The sample-file review gate

- Python: `scripts/csp-walk/walk.py` is the sample since it carries the routes and the states. Write it with `run.sh`, run it against `main` (no policy, so zero violations by definition) and against the branch, and stop for approval before the test file.
- Config: There is one snippet, so there is nothing to sample.

## Done when

`scripts/csp-walk/run.sh standards-csp` reports zero violations and zero JavaScript errors across every route and state, with a poster downloaded; `curl -skI` at the staging origin shows `Content-Security-Policy` on every page; both suites pass; and after the ship, the browser console on production shows no violation on the home page, a poster, and Methodology.

## Rollback

Restore the snippet backup on the affected host (`models-gone-wild-headers.conf` for production, `models-gone-wild-headers-staging.conf` for staging), run `sudo nginx -t`, reload, and add a PCI row. The policy lives only in nginx, so the rollback needs no code deploy.

## Paste-ready prompt: build and stage

```
Run step 10B (Content Security Policy) of the Models Gone Wild standards
cleanup, following docs/standards-cleanup/10b-csp.md exactly. Read
docs/standards-cleanup/README.md first. Use decisions 1, 4, 5, and 17 as
recorded in the README, and stop if any is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Confirm step 10A is merged and live. Branch off an up-to-date main as
   standards-csp. Never work on main.
2. Run both suites and confirm they pass.
3. Sample-file review gate (Python): port AI Strategy's csp-walk into
   scripts/csp-walk/ with the routes and states the step file lists,
   including a real poster download. Run it against main, then add the
   policy to deploy/nginx/headers.conf (decision 4a) and run it against the
   branch. Give me a clickable link to walk.py, a short summary, both
   reports, and the git diff command, and STOP until I approve.
4. If the walk records a violation from html2canvas or anything else, STOP
   and bring me the options. Do not add 'unsafe-inline' or 'unsafe-eval'.
5. Add tests/test_csp.py and update DEPLOY.md's troubleshooting entry.
6. Run both suites, the walk, the screenshot diff (pixel-identical), and
   the comment style checker (0), gating on each exit code.
7. Under decision 1a, on the server: back up
   /etc/nginx/snippets/models-gone-wild-headers-staging.conf, copy the
   updated deploy/nginx/headers.conf over it, show me the diff, and STOP
   until I approve. Then sudo nginx -t, reload, wait two seconds, and write
   the PCI change-log row yourself, reading it back.
8. Commit, push, deploy the branch to staging with the README command, run
   the staging health check, and show me the policy header at the staging
   origin.
9. Report what you verified and how, give me the staging links and ask me
   to open the browser console on the home page and a poster and download
   it, and STOP. Do not merge to main or touch production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/10b-csp.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once the console on staging is clean. It needs no edits.

```
Ship step 10B (Content Security Policy) of the Models Gone Wild standards
cleanup to production, following docs/standards-cleanup/10b-csp.md and the
rules in docs/standards-cleanup/README.md. This is my go-ahead for step 10B
only, including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-csp, and scripts/csp-walk/run.sh standards-csp, gating on
   each exit code.
2. Merge standards-csp to main and push, and deploy main to production with
   the README command.
3. Back up /etc/nginx/snippets/models-gone-wild-headers.conf, copy
   deploy/nginx/headers.conf over it, run sudo nginx -t, reload, and wait
   two seconds. Write the PCI change-log row yourself and read it back.
4. Run the production health check and show me the policy header at the
   production origin.
5. Ask me to open the browser console on
   https://www.annielytics.com/tools/models-gone-wild/, a poster, and
   Methodology, download a poster, and tell you whether anything was
   refused. If anything was, help me roll back with the step file's
   rollback before anything else.
6. Under decision 1a, switch staging back to main with the README command.
7. Mark step 10B done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
8. Tell me the next step is step 11, whose prompt is at the bottom of
   docs/standards-cleanup/11-layout.md.
```
