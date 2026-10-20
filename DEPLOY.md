# DEPLOY.md for Models Gone Wild

Deployment guide for a static app. There is no Flask, no gunicorn, no systemd service, no virtualenv, and no database. Nginx reads the files off disk and serves them.

Claude Code: read this entire file before taking any deployment action. Never proceed past a step marked CRITICAL without explicit confirmation from Annie. Never develop on main. Always create a branch.

## What this app is

Three HTML pages, seven stylesheets all three link in the same order, the case data in two scripts, the page's behavior in ten more, and one vendored JavaScript library.

```
index.html                    the page's markup, loading the scripts below in order
methodology/index.html        the Methodology page, explaining each filter
404.html                      the page nginx serves for any unknown path
css/variables.css             the custom properties, linked first
css/base.css                  the page shell, site header, masthead, and footer
css/registry.css              the registry panel, timeline, and case cards
css/charts.css                the tooltip, Threat Matrix, and Cases by Lab
css/poster.css                the wanted poster
css/methodology.css           the Methodology page
css/responsive.css            the breakpoints and reduced motion, linked last
js/cases.js                   the case registry, CASES
js/glossary.js                the glossary, GLOSSARY
js/labels.js                  the labels, notes, and icons the cards and posters show
js/text.js                    the glossary markup and date helpers
js/mugshot.js                 the booking photos, drawn as SVG
js/timeline.js                the filters and the timeline view
js/charts.js                  the Threat Matrix and Cases by Lab charts
js/views.js                   applying the filters, the options menu, and the tabs
js/tooltip.js                 the glossary and info-note tooltip
js/poster.js                  the poster, its permalink, Copy link, and Download poster
js/menu.js                    the mobile menu, shared with the Methodology page
js/main.js                    starts the page, and loads last
js/gtm.js                     loads Google Tag Manager, first in each page's head
js/vendor/html2canvas.min.js  powers Download poster, loaded on its first press
DEPLOY.md                     this file
.gitignore
```

All three pages load the site-wide Google Tag Manager container, GTM-5FJGP2, which AI Timeline and AI Strategy share. Its one tag fires GA4 (G-2CGX3KD64R). `js/gtm.js` reads the container ID from its own `data-gtm-id` attribute, and each page carries the `<noscript>` fallback frame right after `<body>`, hidden by `.gtm-noscript-frame` in `css/base.css`.

The case data lives in the `CASES` array in `js/cases.js`, and the glossary in `GLOSSARY` in `js/glossary.js`. Adding an escapee means appending an object to that array and pushing. There is no admin screen and no database, by design.

## App variables

```
APP_NAME=           models-gone-wild
APP_DISPLAY_NAME=   Models Gone Wild
APP_TYPE=           static
APP_PATH_SEGMENT=   tools/models-gone-wild
BASE_URL_PROD=      https://www.annielytics.com/tools/models-gone-wild/
BASE_URL_STAGING=   https://staging.annielytics.com/tools/models-gone-wild/
HAS_DATABASE=       no
PROD_PORT=          8025 (reserved, not in use)
STAGING_PORT=       8026 (reserved, not in use)
```

## About the reserved ports

A static app binds no port, so nothing listens on 8025 or 8026. Both are held in the registry in `~/.claude/skills/DEPLOY.md` so no future app claims them. They become real only if this app is ever rebuilt on Flask, which is covered in the last section.

Do not create a systemd service for this app. There is no process to supervise.

## Pre-flight checklist

Four things have to be true before a deploy:

- Every path to a local file in the three pages is relative, never starting with a slash. See the next section.
- The page opens correctly from a local web server, not just by double-clicking the file.
- `git status` is clean and the work is committed on a branch.
- For production, the branch has been checked on staging and merged to main on Annie's word, since production pulls main.

## CRITICAL: the one URL rule that still matters

The app is served at `/tools/models-gone-wild/`, not at the site root. That makes any path beginning with a slash a bug. A tag written as `src="/js/cases.js"` resolves to `annielytics.com/js/cases.js` and returns a 404, while `src="js/cases.js"` correctly resolves to `annielytics.com/tools/models-gone-wild/js/cases.js`.

None of the Python prefix machinery applies here. There is no `SCRIPT_NAME`, no `request.script_root`, no `url_for`, and no app-prefix meta tag, because there is no Flask to read them. Relative paths are the entire solution.

Run this before every deploy. It must return nothing:

```bash
grep -nE '(href|src|action|url\()\s*=?\s*["'"'"']/[^/]' index.html methodology/index.html 404.html css/*.css \
  | grep -v '404.html:.*<base href="/tools/models-gone-wild/">'
```

The one exception is the `<base href>` in `404.html`. Nginx serves that page at whatever depth the unknown URL had, so its relative paths resolve from the app folder only through the base tag.

A leading double slash is fine, since `//fonts.googleapis.com` is an absolute external URL and not a site-root path.

## Deploying to production

### Step 1. Clone the repo onto the server

CRITICAL: confirm the directory does not already exist before cloning. If it does, stop and ask Annie how to proceed. Do not overwrite.

```bash
ssh anniecushing@208.109.215.51
ls -la ~/apps/
```

```bash
cd ~/apps
git clone git@github.com:i-make-data-sexy/models-gone-wild.git models-gone-wild
```

There is no venv step, no pip install, and no logs directory, since nginx writes its own logs.

### Step 2. Update the Nginx production config

CRITICAL: view the current file first, then show Annie the proposed block and wait for her confirmation before writing anything.

```bash
sudo cat /etc/nginx/sites-available/annielytics.conf
```

Add all six blocks to `annielytics.conf`, in this order. They live with the other `/tools/` apps, after the `model-safety` blocks:

```nginx
# Send the bare path to the trailing-slash form. Without this, a request
# to /tools/models-gone-wild does not match the prefix location below and
# falls through to whatever else is configured.
location = /tools/models-gone-wild {
    return 301 /tools/models-gone-wild/;
}

# The dashboard permalinks. /threat-matrix/ and /lab-counts/ are the same
# page as the bare path, with the view read from the URL by the page's
# script. Bare forms first get their trailing slash, which keeps one
# canonical URL per view.
location ~ ^/tools/models-gone-wild/(threat-matrix|lab-counts)$ {
    return 301 /tools/models-gone-wild/$1/;
}

# Strip the view segment and match again. That serves index.html for the
# permalink itself, and it resolves the page's relative asset paths, which
# the browser requests as /threat-matrix/css/base.css and so on. `last`
# reruns location matching on the rewritten URI, so the 404, cache, and
# .git rules all still apply to it. Keep the slug list in step with
# VIEW_SLUGS in js/views.js and scripts/serve.py.
location ~ ^/tools/models-gone-wild/(?:threat-matrix|lab-counts)/ {
    rewrite ^/tools/models-gone-wild/(?:threat-matrix|lab-counts)/(.*)$ /tools/models-gone-wild/$1 last;
}

# The wanted-poster permalinks, /poster/<slug>/. Same page again, with
# the poster read from the URL by the page's script, so they get the same
# trailing-slash 301 and the same strip-and-rematch as the views. Keep the
# slug pattern in step with posterFromUrl in js/views.js and scripts/serve.py.
location ~ ^/tools/models-gone-wild/poster/([a-z0-9-]+)$ {
    return 301 /tools/models-gone-wild/poster/$1/;
}

location ~ ^/tools/models-gone-wild/poster/[a-z0-9-]+/ {
    rewrite ^/tools/models-gone-wild/poster/[a-z0-9-]+/(.*)$ /tools/models-gone-wild/$1 last;
}

# Repo files that ship with the clone but are not site content. Without
# this, DEPLOY.md is served publicly and it carries the server path and
# the host IP. Nginx picks regex locations over prefix ones, so this
# intercepts before the page block below.
#
# .py is in the list because scripts/ ships with the clone. Add the
# extension here whenever a new kind of tooling file joins the repo,
# or it will be readable on the live site.
location ~* ^/tools/models-gone-wild/.+\.(md|txt|json|ya?ml|lock|py)$ {
    include snippets/models-gone-wild-headers.conf;
    error_page 404 /tools/models-gone-wild/404.html;
    return 404;
}

# Unchanging assets cache hard: the vendored library and the images.
# The app's own scripts in js/ change with every case, so they are left
# to the page block below. Also a regex, so it beats the prefix block,
# and the filename character class cannot express ".." so it cannot be
# walked out of the directory.
location ~* ^/tools/models-gone-wild/(js/vendor|img|fonts/[\w-]+)/([\w.-]+\.(?:js|png|jpe?g|svg|webp|ico|woff2))$ {
    alias /home/anniecushing/apps/models-gone-wild/$1/$2;
    add_header Cache-Control "public, max-age=2592000, no-transform";
    include snippets/models-gone-wild-headers.conf;
}

# The page itself, its stylesheet, and the app's own scripts, which
# carry the case data, so a stale copy is a wrong copy and none of them
# may be cached.
#
# The two ifs move links shared before the permalinks, when a view was a
# ?view= parameter, to their permalink for good. An if whose only job is
# a return is the one use nginx documents as safe inside a location. The
# page's script also tidies a ?view= link on arrival, which covers a
# local preview and anything that slips past these.
location /tools/models-gone-wild/ {
    if ($arg_view = matrix) { return 301 /tools/models-gone-wild/threat-matrix/; }
    if ($arg_view = labs)   { return 301 /tools/models-gone-wild/lab-counts/; }

    alias /home/anniecushing/apps/models-gone-wild/;
    index index.html;
    error_page 404 /tools/models-gone-wild/404.html;
    add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    include snippets/models-gone-wild-headers.conf;
}
```

The trailing slashes on both the `location` and the `alias` have to match. Dropping either one produces paths that silently resolve to the wrong place.

`try_files` is deliberately absent. The `alias` plus `index` pair already serves the page, a missing file 404s on its own, and `try_files` combined with `alias` has a long-standing resolution quirk. Adding it back buys nothing.

The `error_page 404` lines in the page block and the repo-file block answer an unknown path, and a blocked repo file, with `404.html` and a 404 status rather than nginx's built-in page. The redirect to `404.html` is internal, so it lands in the page block and carries that block's headers. The page block's `Cache-Control` carries `always` so the 404 is sent no-cache too, since nginx adds a header without `always` only to 2xx and 3xx responses. `scripts/serve.py` does the same for the local preview.

The `css/` directory and the app's own scripts in `js/` need no rule of their own. The asset regex above covers `js/vendor/` and `img/` only, so a request for `css/base.css` or `js/cases.js` falls through to the page block and is served with the page's no-cache headers. That is the right outcome: the stylesheets change whenever the design does and the data scripts change with every case, and a hard-cached copy would strand readers on an old one. Do not widen the asset regex to `css` or all of `js` without also solving cache-busting.

The clone's `.git` directory and `.gitignore` need no rule here. The config already carries a `location ~ /\.git` block further down, and regex locations outrank the prefix block above.

The security headers come from `deploy/nginx/headers.conf` in the repo, copied to `/etc/nginx/snippets/models-gone-wild-headers.conf` (production) and `/etc/nginx/snippets/models-gone-wild-headers-staging.conf` (staging). Nginx drops inherited `add_header` lines in any block that sets its own, so each serving block includes the snippet itself. When the repo file changes, copy it to the staging snippet during the build and to the production snippet at ship time. `scripts/serve.py` reads the same file, so the local preview sends the same headers.

The same snippet carries the Content Security Policy, enforced on every response. It allows only the app's own files, plus Google Tag Manager and the hosts GA4 sends hits to, which are copied from AI Timeline's policy. `style-src` also names one hash, for the fixed `<style>` block html2canvas adds while it copies a poster (see `js/vendor/VENDORED.md`). A Custom HTML tag added in GTM would be refused, since the policy allows no inline script. `scripts/csp-walk/run.sh <ref>` walks every page and state under a ref's policy, a poster download included, and `tests/test_csp.py` holds the policy's shape.

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Step 3. Verify

CRITICAL: verify at the origin, not the public URL. Cloudflare serves a challenge page to scripted requests for HTML, so a public `curl` returns 403 with a Cloudflare body no matter what user-agent it sends. Static assets pass through, which makes the result look even more confusing. A public 403 on the page says nothing about whether the deploy worked.

Run this on the server, which bypasses Cloudflare by talking to nginx directly:

```bash
H="Host: www.annielytics.com"; B="https://127.0.0.1/tools/models-gone-wild"
for f in "" "methodology/" "threat-matrix/" "lab-counts/" "lab-counts/css/registry.css" "poster/sol-hugging-face/" "poster/sol-hugging-face/css/poster.css" "poster/sol-hugging-face/js/vendor/html2canvas.min.js" "poster/sol-hugging-face/DEPLOY.md" "js/vendor/html2canvas.min.js" "js/cases.js" "img/annielytics-logo.png" "DEPLOY.md" ".git/config"; do
  printf "%-28s %s\n" "/$f" "$(curl -sk -H "$H" -o /dev/null -w '%{http_code}' "$B/$f")"
done
printf "%-28s %s\n" "bare path" "$(curl -sk -H "$H" -o /dev/null -w '%{http_code}' "$B")"
printf "%-28s %s\n" "bare poster" "$(curl -sk -H "$H" -o /dev/null -w '%{http_code} %{redirect_url}' "$B/poster/sol-hugging-face")"
for q in "matrix" "labs"; do
  printf "%-28s %s\n" "?view=$q" "$(curl -sk -H "$H" -o /dev/null -w '%{http_code} %{redirect_url}' "$B/?view=$q")"
done
```

Expected results, in order. The page, the Methodology page, and both view permalinks are 200, the stylesheet requested through a permalink is 200, the poster permalink and its stylesheet and script are 200, `DEPLOY.md` requested through the poster path is 404, the three assets are 200, `DEPLOY.md` is 404, `.git/config` is 403, the bare path is 301, and the bare poster path is 301 to `/poster/sol-hugging-face/`. The two old `?view=` links are 301 to `/threat-matrix/` and `/lab-counts/`. The redirect URL prints as `https://127.0.0.1/...`, since curl builds it from the address it called; the path is what to check.

Wait a couple of seconds after `systemctl reload nginx` before running this. A reload leaves the old workers draining, so a check fired immediately can still be answered by a worker running the previous config and show a stale result.

Then open the page in a real browser, which is the only way to confirm the last mile past Cloudflare. Check that the fonts render as the typewriter and condensed faces rather than a fallback, that tapping a case opens its poster and puts `/poster/<slug>/` in the address bar, that Copy link copies that URL, and that the download button on an open poster produces a PNG.

## Updating after the first deploy

Every update goes to staging first and reaches production only on Annie's word. "Deploying the change" in `UPDATE.md` has the full commands, and the order never changes:

1. Push the branch, deploy it to staging (see "Staging" below), run the staging health check, and give Annie the staging links.
2. Stop until she says to ship it.
3. Merge the branch to `main`, push, and pull `main` on production.
4. Switch staging back to `main` (see "Staging").

The production pull, run only after step 2:

```bash
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 \
  "set -e; cd ~/apps/models-gone-wild && git fetch origin && git checkout main \
   && git pull --ff-only origin main && git log --oneline -1"
```

That is the whole deploy. There is no service to restart, because nginx reads the file fresh on every request. The no-cache headers mean a reload in the browser shows the change immediately.

## Staging

Staging is a second checkout of the repo at `~/apps/staging/models-gone-wild`, served by nginx from `/etc/nginx/sites-available/staging.annielytics.conf` under `staging.annielytics.com`. Like production, it has no service, no gunicorn, and no port. Port 8026 stays reserved and unused.

A branch goes to staging first, gets checked there, and reaches production only on Annie's word. Deploy a branch to staging:

```bash
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 \
  "set -e; cd ~/apps/staging/models-gone-wild && git fetch origin && git checkout <branch> \
   && git pull --ff-only origin <branch> && git log --oneline -1"
```

Once the change reaches production, switch staging back to `main`:

```bash
ssh -i ~/.ssh/id_ed25519_imds anniecushing@208.109.215.51 \
  "set -e; cd ~/apps/staging/models-gone-wild && git fetch origin && git checkout main \
   && git pull --ff-only origin main"
```

### The loopback exception

The staging server block sets `auth_basic` for the whole host, so every request needs the staging password. The page block and the asset block carry four extra lines that let the server itself through without it:

```nginx
satisfy any;
allow 127.0.0.1;
allow ::1;
deny all;
```

With `satisfy any`, a request passes if it comes from loopback or carries the password. Nginx takes the client address only from Cloudflare's ranges (`/etc/nginx/conf.d/cloudflare-real-ip.conf`), and UFW lets only Cloudflare reach ports 80 and 443, so no outside request can arrive as `127.0.0.1`. A browser on the public URL still gets the password prompt.

The redirect, rewrite, and repo-file blocks need no exception. A `return` or a `rewrite` runs before the access check, and each rewrite hands off to the page or asset block, which applies it. The staging config's server-wide `location ~ /\.git` and `.env` rules cover the clone, as they do in production.

Run the staging health check on the server. It needs no password:

```bash
H="Host: staging.annielytics.com"; B="https://127.0.0.1/tools/models-gone-wild"
for p in "" methodology/ threat-matrix/ lab-counts/ poster/sol-hugging-face/ DEPLOY.md .git/config no-such-page/; do
  printf "%-28s %s\n" "/$p" "$(curl -sk -H "$H" -o /dev/null -w "%{http_code}" "$B/$p")"; done
```

Healthy output is five 200s, then 404 for `DEPLOY.md`, 403 for `.git/config`, and 404 for `no-such-page/`.

### The staging blocks

These sit in `staging.annielytics.conf` after the Treks and the City blocks and before Vinspire, added 2026-10-16. They match the production blocks above line for line, apart from the staging aliases and the loopback exception.

```nginx
# ===============================================================
# Models Gone Wild Staging - static page, no gunicorn and no port
# ===============================================================
# Port 8026 is reserved for this app but unused, since nginx serves
# the checkout straight off disk. Blocks that serve a file let
# loopback through without the staging password (satisfy any), so
# the server's own health checks need no credentials. Everyone else
# still gets the password prompt.

# The bare path would fall through to location / below, so send it
# to the trailing-slash form.
location = /tools/models-gone-wild {
    return 301 /tools/models-gone-wild/;
}

# The dashboard permalinks. /threat-matrix/ and /lab-counts/ are the
# same page as the bare path; the page reads the view from the URL.
# Bare forms get their trailing slash first.
location ~ ^/tools/models-gone-wild/(threat-matrix|lab-counts)$ {
    return 301 /tools/models-gone-wild/$1/;
}

# Strip the view segment and match again. Serves index.html for the
# permalink and resolves its relative assets (threat-matrix/css/...).
# `last` reruns location matching, so the rules below still apply.
location ~ ^/tools/models-gone-wild/(?:threat-matrix|lab-counts)/ {
    rewrite ^/tools/models-gone-wild/(?:threat-matrix|lab-counts)/(.*)$ /tools/models-gone-wild/$1 last;
}

# The wanted-poster permalinks, /poster/<slug>/. Same page again; the
# page reads the poster from the URL. Bare forms get their trailing
# slash, then the segment is stripped and matched again like the views.
location ~ ^/tools/models-gone-wild/poster/([a-z0-9-]+)$ {
    return 301 /tools/models-gone-wild/poster/$1/;
}

location ~ ^/tools/models-gone-wild/poster/[a-z0-9-]+/ {
    rewrite ^/tools/models-gone-wild/poster/[a-z0-9-]+/(.*)$ /tools/models-gone-wild/$1 last;
}

# Repo files that ship with the clone but are not site content.
# DEPLOY.md in particular carries the server path and host IP.
location ~* ^/tools/models-gone-wild/.+\.(md|txt|json|ya?ml|lock|py)$ {
    include snippets/models-gone-wild-headers-staging.conf;
    error_page 404 /tools/models-gone-wild/404.html;
    return 404;
}

# Unchanging assets cache hard: the vendored library and the images.
# A regex beats the prefix block below, and the extension whitelist
# keeps it to real assets.
location ~* ^/tools/models-gone-wild/(js/vendor|img|fonts/[\w-]+)/([\w.-]+\.(?:js|png|jpe?g|svg|webp|ico|woff2))$ {
    satisfy any;
    allow 127.0.0.1;
    allow ::1;
    deny all;

    alias /home/anniecushing/apps/staging/models-gone-wild/$1/$2;
    add_header Cache-Control "public, max-age=2592000, no-transform";
    include snippets/models-gone-wild-headers-staging.conf;
}

# The page itself, its stylesheet, and the app's own scripts, which
# carry the case data, so a stale copy is a wrong copy and none of them
# may be cached.
location /tools/models-gone-wild/ {
    satisfy any;
    allow 127.0.0.1;
    allow ::1;
    deny all;

    # Old ?view= links from before the permalinks, moved for good.
    if ($arg_view = matrix) { return 301 /tools/models-gone-wild/threat-matrix/; }
    if ($arg_view = labs)   { return 301 /tools/models-gone-wild/lab-counts/; }

    alias /home/anniecushing/apps/staging/models-gone-wild/;
    index index.html;
    error_page 404 /tools/models-gone-wild/404.html;
    add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    include snippets/models-gone-wild-headers-staging.conf;
}
```

When a production block changes, make the same change here so the two stay comparable.

## Branch discipline

Before creating any new branch, the current branch has to be merged to main so the new branch starts from an up-to-date main. Skipping this strands unmerged work. A branch merges only after it has been checked on staging and Annie has signed off, since merging is what sends it to production.

```bash
# Merge the current branch, only after staging and Annie's sign-off
git checkout main
git pull origin main
git merge <current-branch> --no-edit
git push origin main

# Only now create the new branch
git checkout -b <new-branch-name>
```

If the current branch holds work Annie has not signed off on, stop and ask.

## Troubleshooting

The page 404s at the prefix but the file is on disk. Check that the `location` and `alias` trailing slashes match, then confirm nginx can traverse into `/home/anniecushing/apps/models-gone-wild/`.

Download poster shows "The image library didn't load". `js/poster.js` loads the vendored library on the first press, from `APP_BASE` plus `js/vendor/html2canvas.min.js`. Open the browser console, then request that URL directly with curl at the origin. A 404 means the file or the asset block moved.

Fonts fall back to a plain monospace face. The app serves its own fonts, with `css/fonts.css` pointing at the woff2 files in `fonts/`. Request one of those files at the origin with curl. A 404 means a file or the asset block moved. In the browser console, `[...document.fonts].map(f => f.family + ' ' + f.weight + ' ' + f.status)` lists each registered face and whether it loaded. The policy's `font-src 'self'` refuses a font from any other host, so a Google Fonts link added back would show as a violation in the console, not as a fallback alone.

Something stops working and the console names the Content Security Policy. The message names the directive and the blocked source. Run `scripts/csp-walk/run.sh` on the branch to see every refusal locally. Add a source to the policy only for a request the app needs, never `'unsafe-inline'` or `'unsafe-eval'`, then copy `deploy/nginx/headers.conf` to the snippet, reload nginx, and add a PCI row. Restoring the snippet's backup rolls the policy back with no code deploy.

GA4 Realtime shows no visit. Open GTM's Preview mode (Tag Assistant) on the page and confirm the Google Tag fires. A request the console shows as refused needs its host added to `connect-src` or `img-src`.

With GTM's Preview mode connected, the console shows one refused `data:` font under `font-src 'self'`. It is Tag Assistant's own badge font, not one of the app's, and it loads only during a Preview session, so the policy leaves it refused. The tag still fires, and a visit without Preview mode logs nothing. Google's [Tag Manager CSP guide](https://developers.google.com/tag-platform/security/guides/csp) lists the extra sources a fully clean Preview session would need.

An edit is live on disk but the browser shows the old page. Confirm the git pull actually landed, then hard-refresh. The no-cache headers should make this rare.

```bash
# Nginx logs, which are the only logs this app produces
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log

# Confirm what is actually on the server
cd ~/apps/models-gone-wild && git log --oneline -3
```

## If this ever needs Python

Two changes would justify rebuilding this on Flask. The first is wanting the shared Annielytics chrome, meaning the site header, mobile menu, and footer inherited from `base.html` rather than pasted in. The second is wanting to add cases through a form instead of editing the array, which brings in authentication and a database.

Neither is true today. If either becomes true, the general guide at `~/.claude/skills/DEPLOY.md` covers the full Flask path, and ports 8025 and 8026 are already held for it.

Worth weighing before making that jump. This page is a distressed-paper wanted-poster board with its own visual identity, so the standard black Annielytics header would fight the design rather than fit it.
