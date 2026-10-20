# Step 0B: A Staging Copy

Branch: `standards-staging`

Decision 1a (recorded 2026-10-16). Port 8026 is reserved for this staging copy in `~/.claude/skills/DEPLOY.md`. A static copy served by nginx binds no port, so 8026 stays held and unused unless the app is ever rebuilt on Flask. Do not create a systemd unit.

## Background

Every other Annielytics app deploys a branch to staging, gets checked there, and reaches production only on your word. This app has no staging copy and no staging nginx block, and its own docs deploy straight to production. The server showed four things on 2026-10-16:

- `~/apps/staging/` holds nine apps and no `models-gone-wild`.
- `/etc/nginx/sites-available/staging.annielytics.conf` has no block for this app.
- Staging's server block sets `auth_basic` for the whole host (`/etc/nginx/.htpasswd`), so a check run on the server gets a 401 without credentials.
- Nginx takes the client address only from Cloudflare's ranges (`/etc/nginx/conf.d/cloudflare-real-ip.conf`), and UFW only lets Cloudflare reach ports 80 and 443. A request from `127.0.0.1` is therefore always the server itself, which makes a loopback exception to the password safe.
- The staging config carries the `.env` deny rule. Confirm it also carries a `location ~ /\.git` rule, as production does, before relying on it.

## The changes

### On the server

1. Confirm `~/apps/staging/models-gone-wild` does not exist. If it does, stop and ask.
2. Clone: `cd ~/apps/staging && git clone git@github.com:i-make-data-sexy/models-gone-wild.git models-gone-wild`. It starts on `main`.
3. Back up the staging config: `sudo cp /etc/nginx/sites-available/staging.annielytics.conf /etc/nginx/backup/staging.annielytics.conf.bak.$(date +%Y%m%d-%H%M%S)`.
4. Add the six blocks from production's config (lines 310 to 372 of `annielytics.conf`) to the staging config, after the other `/tools/` apps, with two changes: every `alias` points at `/home/anniecushing/apps/staging/models-gone-wild/`, and each block that serves a file gets the loopback exception:

   ```nginx
   satisfy any;
   allow 127.0.0.1;
   allow ::1;
   deny all;
   ```

   With `satisfy any`, a request passes if it comes from loopback or carries the staging password, so the server's own checks need no credentials and everyone else still gets the password prompt. Blocks that only `return` a redirect need nothing since a redirect runs before the access check.
5. If the staging config has no `location ~ /\.git` rule, add `location ~ ^/tools/models-gone-wild/.*\.git { deny all; return 403; }` with the app's other blocks.
6. `sudo nginx -t`, `sudo systemctl reload nginx`, wait two seconds.
7. Write the PCI change-log row (Component "Nginx staging config", the backup file name, and the `nginx -t` result).

### In the repo

1. Add a "Staging" section to `DEPLOY.md` naming the checkout, the config file, the loopback exception, and the staging deploy command from the README.
2. Show the staging blocks in `DEPLOY.md` alongside the production ones, so the two can be compared.

A sample-file review gate does not apply. The step changes one Markdown file and one server config.

## Done when

The staging health check from the README prints five 200s, then 404 for `DEPLOY.md`, 403 for `.git/config`, and 404 for `no-such-page/`, all without a password. You then open https://staging.annielytics.com/tools/models-gone-wild/ in a browser and get the password prompt, which proves the exception reaches loopback only.

## Rollback

Restore the backup over `staging.annielytics.conf`, run `sudo nginx -t`, reload, and add a PCI row for the rollback. `rm -rf ~/apps/staging/models-gone-wild` removes the checkout. Revert the `DEPLOY.md` commit.

## Paste-ready prompt: build and stage

```
Run step 0B (staging copy) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/00b-staging.md exactly. Read
docs/standards-cleanup/README.md first. Decision 1a applies (recorded
2026-10-16). Create no systemd unit; port 8026 stays reserved and unused.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step 0 is marked done in the README. Branch off an up-to-date
   main as standards-staging. Never work on main.
2. On the server (ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51),
   confirm ~/apps/staging/models-gone-wild does not exist, then clone the
   repo there on main.
3. Back up /etc/nginx/sites-available/staging.annielytics.conf, then show
   me the six blocks you will add (aliases pointing at
   /home/anniecushing/apps/staging/models-gone-wild/, the loopback
   exception on every block that serves a file, and a scoped .git rule if
   the config lacks one). STOP until I approve them.
4. After I approve, add them, run sudo nginx -t, reload, wait two seconds,
   and write the PCI change-log row into the Google Sheet yourself, reading
   it back afterward.
5. Run the staging health check from the README and show me the output.
6. Add the Staging section to DEPLOY.md, commit, and push the branch.
7. Give me https://staging.annielytics.com/tools/models-gone-wild/ to open
   in a browser, where I should get the password prompt. Then STOP. Do not
   merge to main until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/00b-staging.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once the staging copy checks out. It needs no edits. Nothing in this step changes production; it merges the docs and records the step.

```
Ship step 0B (staging copy) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/00b-staging.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 0B only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Merge standards-staging to main and push.
2. Deploy main to production with the README command (only DEPLOY.md
   changed) and run the production health check.
3. Switch staging to main with the README command and run the staging
   health check.
4. Mark step 0B done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
5. Tell me the next step is step 1, whose prompt is at the bottom of
   docs/standards-cleanup/01-tests.md.
```
