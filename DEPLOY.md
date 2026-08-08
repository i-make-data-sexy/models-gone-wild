# DEPLOY.md for Models Gone Wild

Deployment guide for a static app. There is no Flask, no gunicorn, no systemd service, no virtualenv, and no database. Nginx reads the files off disk and serves them.

Claude Code: read this entire file before taking any deployment action. Never proceed past a step marked CRITICAL without explicit confirmation from Annie. Never develop on main. Always create a branch.

## What this app is

One self-contained HTML page plus one vendored JavaScript library.

```
index.html                  the whole app: markup, CSS, data, and behavior
js/html2canvas.min.js       powers the "download poster" button
DEPLOY.md                   this file
.gitignore
```

The case data lives in a `CASES` array near the top of the script block in `index.html`. Adding an escapee means appending an object to that array and pushing. There is no admin screen and no database, by design.

## App variables

```
APP_NAME=           models-gone-wild
APP_DISPLAY_NAME=   Models Gone Wild
APP_TYPE=           static
APP_PATH_SEGMENT=   tools/models-gone-wild
BASE_URL_PROD=      https://www.annielytics.com/tools/models-gone-wild/
HAS_DATABASE=       no
PROD_PORT=          8025 (reserved, not in use)
STAGING_PORT=       8026 (reserved, not in use)
```

## About the reserved ports

A static app binds no port, so nothing listens on 8025 or 8026. Both are held in the registry in `~/.claude/skills/DEPLOY.md` so no future app claims them. They become real only if this app is ever rebuilt on Flask, which is covered in the last section.

Do not create a systemd service for this app. There is no process to supervise.

## Pre-flight checklist

Four things have to be true before a deploy:

- Every path to a local file in `index.html` is relative, never starting with a slash. See the next section.
- The page opens correctly from a local web server, not just by double-clicking the file.
- `git status` is clean and the work is committed on a branch.
- The branch has been merged to main, since the server pulls main.

## CRITICAL: the one URL rule that still matters

The app is served at `/tools/models-gone-wild/`, not at the site root. That makes any path beginning with a slash a bug. A tag written as `src="/js/html2canvas.min.js"` resolves to `annielytics.com/js/html2canvas.min.js` and returns a 404, while `src="js/html2canvas.min.js"` correctly resolves to `annielytics.com/tools/models-gone-wild/js/html2canvas.min.js`.

None of the Python prefix machinery applies here. There is no `SCRIPT_NAME`, no `request.script_root`, no `url_for`, and no app-prefix meta tag, because there is no Flask to read them. Relative paths are the entire solution.

Run this before every deploy. It must return nothing:

```bash
grep -nE '(href|src|action|url\()\s*=?\s*["'"'"']/[^/]' index.html
```

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

Add all four blocks to `annielytics.conf`, in this order. They live with the other `/tools/` apps, after the `model-safety` blocks:

```nginx
# Send the bare path to the trailing-slash form. Without this, a request
# to /tools/models-gone-wild does not match the prefix location below and
# falls through to whatever else is configured.
location = /tools/models-gone-wild {
    return 301 /tools/models-gone-wild/;
}

# Repo files that ship with the clone but are not site content. Without
# this, DEPLOY.md is served publicly and it carries the server path and
# the host IP. Nginx picks regex locations over prefix ones, so this
# intercepts before the page block below.
location ~* ^/tools/models-gone-wild/.+\.(md|txt|json|ya?ml|lock)$ {
    return 404;
}

# Unchanging assets cache hard. Also a regex, so it beats the prefix
# block below, and the filename character class cannot express ".."
# so it cannot be walked out of the directory.
location ~* ^/tools/models-gone-wild/(js|img)/([\w.-]+\.(?:js|png|jpe?g|svg|webp|ico))$ {
    alias /home/anniecushing/apps/models-gone-wild/$1/$2;
    expires 30d;
    add_header Cache-Control "public, no-transform";
}

# The page itself. It carries the case data inline, so a stale copy is a
# wrong copy and it must never be cached.
location /tools/models-gone-wild/ {
    alias /home/anniecushing/apps/models-gone-wild/;
    index index.html;
    expires -1;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

The trailing slashes on both the `location` and the `alias` have to match. Dropping either one produces paths that silently resolve to the wrong place.

`try_files` is deliberately absent. The `alias` plus `index` pair already serves the page, a missing file 404s on its own, and `try_files` combined with `alias` has a long-standing resolution quirk. Adding it back buys nothing.

The `css/` directory needs no rule of its own. The asset regex above covers `js/` and `img/` only, so a request for `css/styles.css` falls through to the page block and is served with the page's no-cache headers. That is the right outcome: the stylesheet changes whenever the design does, and a hard-cached copy would strand readers on an old one. Do not add `css` to the asset regex without also solving cache-busting.

The clone's `.git` directory and `.gitignore` need no rule here. The config already carries a `location ~ /\.git` block further down, and regex locations outrank the prefix block above.

```bash
sudo nginx -t && sudo systemctl reload nginx
```

### Step 3. Verify

CRITICAL: verify at the origin, not the public URL. Cloudflare serves a challenge page to scripted requests for HTML, so a public `curl` returns 403 with a Cloudflare body no matter what user-agent it sends. Static assets pass through, which makes the result look even more confusing. A public 403 on the page says nothing about whether the deploy worked.

Run this on the server, which bypasses Cloudflare by talking to nginx directly:

```bash
H="Host: www.annielytics.com"; B="https://127.0.0.1/tools/models-gone-wild"
for f in "" "js/html2canvas.min.js" "img/annielytics-logo.png" "DEPLOY.md" ".git/config"; do
  printf "%-28s %s\n" "/$f" "$(curl -sk -H "$H" -o /dev/null -w '%{http_code}' "$B/$f")"
done
printf "%-28s %s\n" "bare path" "$(curl -sk -H "$H" -o /dev/null -w '%{http_code}' "$B")"
```

Expected results, in order. The page is 200, both assets are 200, `DEPLOY.md` is 404, `.git/config` is 403, and the bare path is 301.

Wait a couple of seconds after `systemctl reload nginx` before running this. A reload leaves the old workers draining, so a check fired immediately can still be answered by a worker running the previous config and show a stale result.

Then open the page in a real browser, which is the only way to confirm the last mile past Cloudflare. Check that the fonts render as the typewriter and condensed faces rather than a fallback, that tapping a case opens its poster, and that the download button on an open poster produces a PNG.

## Updating after the first deploy

```bash
ssh anniecushing@208.109.215.51
cd ~/apps/models-gone-wild
git pull origin main
```

That is the whole deploy. There is no service to restart, because nginx reads the file fresh on every request. The no-cache headers mean a reload in the browser shows the change immediately.

## Branch discipline

Before creating any new branch, the current branch has to be merged to main so the new branch starts from an up-to-date main. Skipping this strands unmerged work.

```bash
# Merge the current branch, only after Annie signs off
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

The page loads but the download button does nothing. The vendored library failed to load. Open the browser console, then request the js URL directly with curl. A 404 usually means a leading slash crept back into the script tag.

Fonts fall back to a plain monospace face. The page reaches out to `fonts.googleapis.com`, so check whether a Content-Security-Policy header on `annielytics.com` is blocking it. Nothing in this app sets a CSP, so any policy comes from the server config.

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
