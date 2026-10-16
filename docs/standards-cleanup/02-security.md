# Step 2: Security Fixes

Branch: `standards-security`

Each fix is independent, so commit them separately. Nothing here changes what a visitor sees.

## Decisions this step reads

Decision 4a (one repo file, copied to a staging and a production snippet), decision 5a (`X-Frame-Options: SAMEORIGIN`), and decision 6a (you delete the server's `.env`), recorded in `docs/standards-cleanup/README.md` on 2026-10-16.

## What the baseline asks, and what applies here

The baseline step sets response headers, runs production without DEBUG, loads the secret key from the environment, and removes any public debug route. This app is served by nginx straight from disk, with no Python process, so three of those cannot apply:

- DEBUG: There is no Flask app to run in debug mode.
- A secret key: There is no session and no cookie.
- A debug route: There are no routes. The nearest risk is repo files in the web root, and at the origin on 2026-10-16 `.git/config` and `.gitignore` returned 403 and `DEPLOY.md`, `scout/SCOUT.md`, `scripts/serve.py`, and the skill's `SKILL.md` returned 404. Decision 23 (step 13A) handles the denylist itself.

The headers do apply, and they come from nginx.

## Fix 2a: Security response headers from nginx

At the origin on 2026-10-16, no page, stylesheet, or script returned `X-Content-Type-Options`, `X-Frame-Options`, or `Referrer-Policy`.

Nginx drops every inherited `add_header` in a block that sets its own, and this app's page and asset blocks each set `Cache-Control`. So a server-level header would never reach these responses. The headers have to be in each serving block.

Under decision 4a, Claude makes three changes.

1. Create `deploy/nginx/headers.conf` in the repo:

   ```nginx
   add_header X-Content-Type-Options "nosniff" always;
   add_header Referrer-Policy "strict-origin-when-cross-origin" always;
   add_header X-Frame-Options "SAMEORIGIN" always;
   ```

   `X-Frame-Options` stays, under decision 5a. `always` sends the header on a 404 too. The file sits in the web root and nginx's denylist does not cover `.conf`, so it is publicly readable. That is harmless since every value in it is sent on every response anyway, and decision 23a moves it out of the web root in step 13A.
2. On the server, copy it to two snippets, one per host, so a staging build never changes production: `/etc/nginx/snippets/models-gone-wild-headers-staging.conf`, included by this app's asset, page, and denylist blocks in `staging.annielytics.conf` during the build, and `/etc/nginx/snippets/models-gone-wild-headers.conf`, included by the same three blocks in `annielytics.conf` at ship time. Every later step that changes the headers copies the repo file to the staging snippet when it builds and to the production snippet when it ships.
3. In `scripts/serve.py`, read `deploy/nginx/headers.conf`, parse each `add_header Name "value"` line, and send those headers on every response, so the local preview and the tests see exactly what nginx sends.

Tests check that the home page, `methodology/`, a poster permalink, `css/styles.css`, `js/html2canvas.min.js`, and an unknown path each return the three headers through the preview server.

## Fix 2b: One Cache-Control header

The page block sets both `expires -1` and `add_header Cache-Control "no-cache, no-store, must-revalidate"`, so the page and the stylesheet each return two `Cache-Control` headers (`no-cache`, then the full one). Remove `expires -1` from the page block on both servers, keeping the `add_header` line, so each response carries one. Show the block in `DEPLOY.md` to match.

## Fix 2c: The Cloudflare token in the web root

Production's checkout holds `~/apps/models-gone-wild/.env` (mode 600, written 2026-10-16) with a `CLOUDFLARE_API_TOKEN`. The server-wide `location ~* /\.env$` rule returns 403 for it, so it is not public, but it sits in the folder nginx serves, and no tracked file reads the variable. Server `.env` changes are yours, so Claude gives you the command and does not run it. Under decision 6a, you run this on the server:

```
rm ~/apps/models-gone-wild/.env
```

The copy on your Mac stays.

Then Claude confirms `git -C ~/apps/models-gone-wild status --porcelain --ignored` no longer lists `.env`.

## The sample-file review gate

Each filetype changes in one file (`serve.py`, `headers.conf`, `DEPLOY.md`), so there is nothing to sample within the repo. The two nginx configs follow the same order: staging during the build, production only at ship time.

## Done when

Run this against nginx on the server:

```
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 '
for H in "Host: staging.annielytics.com" "Host: www.annielytics.com"; do echo "$H"
for p in "" methodology/ poster/sol-hugging-face/ css/styles.css js/html2canvas.min.js no-such-page/; do
  printf "  %-26s %s\n" "/$p" "$(curl -skI -H "$H" https://127.0.0.1/tools/models-gone-wild/$p | grep -ciE "^(x-content-type-options|referrer-policy|x-frame-options):")"; done; done'
```

prints 3 for every path on both hosts, and `curl -skI` on the home page shows one `Cache-Control` line. The staging half runs in the build, and the production half at ship time.

## Rollback

Each fix is its own commit, so `git revert <sha>` undoes one. On the server, restore the config backup taken before the edit, run `sudo nginx -t`, reload, and add a PCI row for the rollback.

## Paste-ready prompt: build and stage

```
Run step 2 (security fixes) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/02-security.md exactly. Read
docs/standards-cleanup/README.md first. Use decisions 1, 4, 5, and 6 as
recorded in the README, and stop if any is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Confirm step 1 is merged and live. Branch off an up-to-date main as
   standards-security. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change.
3. Fix 2a: create deploy/nginx/headers.conf with all three headers and
   teach scripts/serve.py to send them. Add the header tests. Commit.
4. Fix 2b: update the page block shown in DEPLOY.md to drop expires -1.
   Commit.
5. On the server: back up
   /etc/nginx/sites-available/staging.annielytics.conf, copy the snippet to
   /etc/nginx/snippets/models-gone-wild-headers-staging.conf, include it in
   this app's staging asset, page, and denylist blocks, and drop expires -1
   from the staging page block. Show me the diff of the config and STOP until I approve. Then run
   sudo nginx -t, reload, wait two seconds, and write the PCI change-log
   row into the Google Sheet yourself, reading it back.
6. Fix 2c: give me the rm command from the step file and wait for me to
   run it. Do not touch the .env yourself. Then confirm it is gone from git
   status --ignored.
7. Run both suites and the comment style checker, gating on each exit code,
   push, deploy the branch to staging with the README command, and run the
   "Done when" check for the staging host.
8. Report what you verified and how, give me the staging links from the
   README, and STOP. Do not merge to main or change production nginx until
   I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/02-security.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step 2 report. It needs no edits.

```
Ship step 2 (security fixes) of the Models Gone Wild standards cleanup to
production, following docs/standards-cleanup/02-security.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 2 only,
including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-security, gating on each exit code.
2. Merge standards-security to main and push, then deploy main to
   production with the README command.
3. On the server, back up /etc/nginx/sites-available/annielytics.conf, copy
   deploy/nginx/headers.conf to /etc/nginx/snippets/models-gone-wild-headers.conf,
   include it in this app's asset, page, and denylist blocks
   (lines 310 to 372 on 2026-10-16), and drop expires -1 from the page
   block. Run sudo nginx -t, reload, and wait two seconds.
4. Write the PCI change-log row into the Google Sheet yourself and read it
   back.
5. Run the "Done when" check for www.annielytics.com and the production
   health check.
6. Switch staging back to main with the README command.
7. Mark step 2 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
8. Give me https://www.annielytics.com/tools/models-gone-wild/ to
   spot-check in a browser. Then tell me the next step is step 3, whose
   prompt is at the bottom of docs/standards-cleanup/03-requirements.md.
```
