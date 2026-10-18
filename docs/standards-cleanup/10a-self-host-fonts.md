# Step 10A: Serve the Fonts From the App

Branch: `standards-self-host-fonts`

Added to the baseline because step 10B's policy cannot work without it. The pattern is `~/.claude/rules/design/self-host-google-fonts.md`, and ML Model Picker's commit eddf4b8 is the reference.

## Decisions this step reads

Decision 15a (the 30-day cache has covered only `js/vendor/` and `img/` since step 9A), recorded in `docs/standards-cleanup/README.md` on 2026-10-16. This step adds `fonts/` to that rule.

## Background

Both pages load two Google Fonts stylesheets with their two preconnects (lines 7 to 15 of `index.html` and 7 to 9 of `methodology/index.html` on 2026-10-16):

- Oswald 400, 500, 600, and 700, Special Elite, and Courier Prime 400 and 700.
- Noto Emoji 600, subset with `text=` to the one 🤘 glyph in the masthead (`index.html` only).

Cloudflare APO rewrites every Google Fonts `<link>` under `www.annielytics.com/tools/` into an inline `<style>` of `@font-face` rules. A policy without `'unsafe-inline'` in `style-src` blocks that `<style>`, and every face falls back. The fonts rule lists this app as "no policy, fonts loaded, apply this before adding a policy", which is exactly where step 10B is.

The Threat Matrix measures its labels in Oswald before laying them out, and a poster renders in Special Elite and Courier Prime, so a fallback face moves labels and changes downloaded posters.

Fonts never change, so they want a long cache. A `fonts/` folder would fall through to the page block, which sends `no-store`, and every visit would download them again. So the asset rule gains `fonts` and `woff2`. Nginx 1.18 has no `woff2` entry in `mime.types` and serves the files as `application/octet-stream`, which browsers load anyway, even under an enforced policy, as the fonts rule records. No MIME change is needed.

## The changes

1. For each Google Fonts link, fetch its CSS with a Chrome user agent so Google returns woff2:

   ```
   curl -s -A "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36" "<the link's href>"
   ```

2. Download every distinct `fonts.gstatic.com` file with `curl` (not Python's urllib, which has no CA certificates on your Mac) into `fonts/<family>/<subset>.woff2`, for example `fonts/oswald/latin.woff2`. Keep the Noto Emoji file as `fonts/noto-emoji/horns.woff2` since it holds one glyph.
3. Write `css/fonts.css` with Google's `@font-face` rules unchanged except in two ways. Each `url()` becomes relative (`../fonts/<family>/<subset>.woff2`), and the subset comments are capitalized (`/* Latin */`). Open it with a banner and a comment naming where and when the rules came from.
4. In both pages, replace the Google Fonts links and both preconnects with one relative link to `css/fonts.css` (`../css/fonts.css` on Methodology), at the position of the first Google link, so the cascade is unchanged.
5. Extend the asset rule on both servers to `^/tools/models-gone-wild/(js/vendor|img|fonts/[\w-]+)/([\w.-]+\.(?:js|png|jpe?g|svg|webp|ico|woff2))$`, with the same `alias .../$1/$2` and 30-day cache. The family folder gets its own `[\w-]+` group, which cannot express `..`, and the filename class stays as it was. Confirm by requesting `fonts/../DEPLOY.md` and getting a 404.
6. Add two tests: no tracked page, stylesheet, or script mentions `fonts.googleapis.com` or `fonts.gstatic.com`, and every `url()` in `css/fonts.css` names a file that exists.

## The sample-file review gate

- HTML: `index.html` is the sample since it carries both Google links including the emoji subset. Swap its links, run the screenshot diff, and stop for approval before `methodology/index.html`.
- CSS: `css/fonts.css` is the sample, the one CSS file the step creates. Write it to the formatting rule, show it with the screenshot diff, and stop for approval.

## Done when

The screenshot diff against `main` is pixel-identical (the files are byte for byte what Google serves), both suites pass, `check_overlaps.py` reports no overlaps, and in a browser on staging the console's `[...document.fonts].map(f => f.family + ' ' + f.weight + ' ' + f.status)` lists Oswald, Special Elite, Courier Prime, and Noto Emoji, with the weights the page uses `loaded`. Do not use `document.fonts.check()`, which returns true when no face is registered at all.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py`, with the formatter re-run where a change moved a column.

## Rollback

Revert the commit, which restores the Google links. Restore the config backup on each server, run `sudo nginx -t`, reload, and add a PCI row.

## Paste-ready prompt: build and stage

```
Run step 10A (serve the fonts from the app) of the Models Gone Wild
standards cleanup, following docs/standards-cleanup/10a-self-host-fonts.md
exactly. Read docs/standards-cleanup/README.md and
~/.claude/rules/design/self-host-google-fonts.md first. Use decisions 1 and
15 as recorded in the README, and stop if either is blank.

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

1. Confirm step 8 is merged and live. Branch off an up-to-date main as
   standards-self-host-fonts. Never work on main.
2. Run both suites and confirm they pass.
3. Fetch each Google Fonts stylesheet with the Chrome user agent, download
   every woff2 with curl into fonts/, and write css/fonts.css with relative
   url()s.
4. Sample-file review gate (HTML): swap index.html's Google links and
   preconnects for one css/fonts.css link at the same position, run the
   screenshot diff, and give me a clickable link, a short summary, the diff
   result, and the git diff command. STOP until I approve. Then do
   methodology/index.html with ../css/fonts.css.
5. Add the two tests. Run both suites, check_overlaps.py, the screenshot
   diff (pixel-identical), and the comment style checker (0), gating on
   each exit code.
6. On the server: back up
   /etc/nginx/sites-available/staging.annielytics.conf, extend this app's
   asset rule to fonts and woff2 as the step file shows, show me the diff,
   and STOP until I approve. Then sudo nginx -t, reload, wait two seconds,
   and write the PCI change-log row yourself, reading it back.
7. Commit, push, deploy the branch to staging with the README command, run
   the staging health check, show me curl -skI for one woff2 file (30-day
   cache) and the 404 for fonts/../DEPLOY.md at the staging origin.
8. Report what you verified and how, give me the staging links and the
   document.fonts console line to run, and STOP. Do not merge to main or
   touch production until I say so.

When you stop, end your report with a lettered to-do that runs the
ship-to-production prompt at the bottom of
docs/standards-cleanup/10a-self-host-fonts.md when I reply with
its letter. Do not paste that prompt into the report.
```

## Ship-to-production prompt

Claude runs this in the same session when you reply with the ship letter, once the fonts check out on staging. It needs no edits.

```
Ship step 10A (serve the fonts from the app) of the Models Gone Wild
standards cleanup to production, following
docs/standards-cleanup/10a-self-host-fonts.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 10A only,
including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-self-host-fonts, gating on each exit code.
2. Back up /etc/nginx/sites-available/annielytics.conf, extend this app's
   asset rule to fonts and woff2, run sudo nginx -t, reload, wait two
   seconds, and write the PCI change-log row yourself, reading it back.
3. Merge standards-self-host-fonts to main and push, deploy main to
   production with the README command, and run the production health check.
4. Show me curl -skI for one woff2 file and the 404 for fonts/../DEPLOY.md
   at the production origin.
5. Give me the document.fonts console line to run on
   https://www.annielytics.com/tools/models-gone-wild/ after a hard refresh.
6. Switch staging back to main with the README command.
7. Mark step 10A done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main. Update the Models Gone
   Wild row in ~/.claude/rules/design/self-host-google-fonts.md's table to
   say it is fixed in production, with the merge commit.
8. Tell me the next step is step 10B, and paste its build prompt
   from the bottom of docs/standards-cleanup/10b-csp.md in full, so I can
   start the next session with it.
```
