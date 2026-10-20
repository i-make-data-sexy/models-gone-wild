# Step 13B: Canonicals, the /index.html Duplicates, and Share Tags

Branch: `standards-canonicals`

The second half of the baseline's URL step, and the last step in the plan. It changes what search engines are told about each URL, so every change is an approved difference in step 13A's URL list.

## Decisions this step reads

Decision 24b (a canonical per permalink, sent as an nginx `Link` header) and decision 25b (a meta description and share tags, with a share image you design), recorded in `docs/standards-cleanup/README.md` on 2026-10-16. Step 13A moved the pages into `public/` (decision 23a).

## Background

On 2026-10-16 no page carried a canonical tag, a meta description, or Open Graph or Twitter tags. At the production origin, the home page, `/index.html`, `threat-matrix/`, `lab-counts/`, and all 21 poster permalinks returned 200 with the same HTML, and `methodology/` and `methodology/index.html` returned the same page. Search engines see up to 25 URLs and pick canonicals themselves.

The views and posters are states of one page, drawn by the script from the address bar. Their HTML is identical, so a tag in the page cannot tell them apart. Under decision 24b, nginx sends each one its own canonical as a `Link: <url>; rel="canonical"` header. That rules out a static `<link rel="canonical">` in `index.html` since the page would then name one URL while the header named another, and search engines ignore conflicting signals.

Two nginx details shape how. A header set in a block that ends in `rewrite ... last` is dropped because the request finishes in the page block, so the value cannot be set in the rewrite blocks. And `$request_uri` keeps the original address through a rewrite, so a `map` on it can work out the canonical in the page block. Both server configs are loaded into one `http` context, so a `map` can only be defined once. It goes in its own file in `/etc/nginx/conf.d/`, which both sites see. Staging's canonicals point at `www`, which is correct since staging must never claim to be the canonical copy.

A link shared on social media shows no title card today.

## The changes

Decision 25 was amended during the build on 2026-10-20: each view gets its own share card, nginx swaps the view's values into the one `index.html`, and a generator keeps the two chart cards current. The changes below are what the step did.

1. `deploy/nginx/canonical-map.conf`, installed once as `/etc/nginx/conf.d/models-gone-wild-canonical.conf`, which both servers load. Its first two maps give each permalink its canonical from `$request_uri` and turn it into a `Link: <url>; rel="canonical"` value. Assets requested under a permalink, the 404 page, and every other address map to an empty value, and nginx sends no header with an empty value. The other maps give each view its share title, meta description, share description, URL, image, and alt text, each defaulting to the home page's tag. Named captures carry an `mgw_` prefix, since nginx makes them request variables visible to every app on the server.
2. `deploy/nginx/share.conf`, installed as `/etc/nginx/snippets/models-gone-wild-share-staging.conf` and `models-gone-wild-share.conf` and included in each server's page block. It sends the `Link` header and swaps the view's values into `index.html` with `sub_filter`. Each search string is a home page tag, so the home page passes through unchanged. A poster keeps the lineup card but names itself in `og:url`, so `og:url` and the canonical agree on every permalink.
3. An `if ($request_uri ~ ...) { return 301 ...; }` in each page block sends an `index.html` address to its folder, for the home page, Methodology, the views, and the posters. The plan's `location = .../index.html` blocks would loop, since the `index` directive's internal hop to `index.html` reruns location matching. `$request_uri` keeps the address as requested.
4. `scripts/serve.py` reads both files and mirrors the header, the swap, and the 301s. `tests/test_nginx_mirror.py`'s emulator reads the new 301 from `DEPLOY.md`'s blocks.
5. The copy, approved by Annie, follows `~/.claude/rules/editorial/annielytics-writing-rules.md` and `UPDATE.md`'s voice rules: no lab named, no counts, no grading. The three cards are `public/img/share.png` (the lineup, for the home page, Methodology, and posters), `share-threat-matrix.png`, and `share-lab-counts.png`, each 1200 by 630.
6. Both pages carry `<meta name="description">`, `og:type`, `og:title`, `og:description`, `og:url`, `og:image` with its width, height, and alt, and `twitter:card`, `twitter:title`, `twitter:description`, `twitter:image`, and `twitter:image:alt`. The image and URL values are absolute, which the leading-slash test allows since none starts with a slash. Each image URL carries `?v=` with the data version, so a redrawn card gets a new URL past the 30-day image cache. `404.html` gets none.
7. `scripts/share_cards.py` redraws the three cards from `scripts/share-cards/cards.html`, which uses the app's own fonts, tokens, cases, and mugshots. It stamps each PNG with a hash of the case fields the charts draw and sets the pages' `?v=` to match. `UPDATE.md` and the add-case skill run it after a case changes.
8. The URL list records the `Link` header, the meta description, `og:url`, and `og:image`, and checks the view and poster `index.html` forms. `tests/test_share.py` holds every rule above, including that the cards and pages carry the current data version.

## The sample-file review gate

- HTML: `public/index.html` was the sample since its share tags serve every view and poster.
- Python: `scripts/serve.py` was the sample, before the tests and the generator.
- CSS and JavaScript: `scripts/share-cards/cards.css` and `cards.js`, reviewed together.
- Config: the two nginx files are new, so there is nothing to sample. On the servers, staging goes first, during the build.

## Done when

The URL list for the branch matches `main` except for the approved changes (the four new columns, the three card images, and every `index.html` form now 301), locally and at the staging origin, and the local and staging lists match each other. Both suites, the CSP walk, and the screenshot diff (pixel-identical since nothing visible changes) pass. After the ship, the Facebook Sharing Debugger shows each card for the home page and both views.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py`, with the formatter re-run where a change moved a column.

## Rollback

Revert the commits. On each server, restore the config backup, remove the share snippet from `/etc/nginx/snippets/` and `/etc/nginx/conf.d/models-gone-wild-canonical.conf`, run `sudo nginx -t`, reload, and add a PCI row. A canonical that shipped wrong should be fixed and redeployed rather than removed, so search engines see one consistent change.

## Paste-ready prompt: build and stage

```
Run step 13B (canonicals and share tags) of the Models Gone Wild standards
cleanup, following docs/standards-cleanup/13b-canonicals.md exactly. Read
docs/standards-cleanup/README.md and
~/.claude/rules/editorial/annielytics-writing-rules.md first. Decisions 24b
and 25b apply (recorded 2026-10-16).

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

1. Confirm step 13A is merged and live. Branch off an up-to-date main as
   standards-canonicals. Never work on main.
2. Run both suites and the CSP walk, and confirm they pass. Record the URL
   list for main with scripts/url-list/run.sh main.
3. Propose the meta description and the share title and description for
   both pages, and STOP until I approve the copy. Then ask me for the share
   image, 1200 by 630, and save it as public/img/share.png.
4. Sample-file review gate (HTML): add the approved tags to
   public/index.html, run the URL list against the branch, and give me a
   clickable link, a short summary, the URL list diff, and the git diff
   command. STOP until I approve. Then public/methodology/index.html, and
   confirm public/404.html has no canonical and no share tags.
5. Write deploy/nginx/canonical-map.conf, mirror the map and the
   index.html 301s in scripts/serve.py, extend the URL list's columns, and
   add the tests.
6. Run both suites, the CSP walk, the screenshot diff (pixel-identical), and
   the comment style checker (0), gating on each exit code.
7. On the server: back up
   /etc/nginx/sites-available/staging.annielytics.conf, install the map as
   /etc/nginx/conf.d/models-gone-wild-canonical.conf, add the Link header to
   this app's staging page block and the two 301 blocks, show me the diff,
   and STOP until I approve. Then sudo nginx -t, reload, wait two seconds,
   and write the PCI change-log row yourself, reading it back. The map file
   is loaded by production too, but it only defines variables, so
   production sends nothing new until its page block uses them.
8. Commit, push, deploy the branch to staging with the README command, run
   scripts/url-list/origin.sh against staging, and diff it with production.
9. Report what you verified and how, give me the staging links, and STOP.
   Do not merge to main or touch production until I say so.

When you stop, end your report with a lettered to-do that runs the
ship-to-production prompt at the bottom of
docs/standards-cleanup/13b-canonicals.md when I reply with
its letter. Do not paste that prompt into the report.
```

## Ship-to-production prompt

Claude runs this in the same session when you reply with the ship letter, once the staging URL list checks out. It needs no edits.

```
Ship step 13B (canonicals and share tags) of the Models Gone Wild standards
cleanup to production, following docs/standards-cleanup/13b-canonicals.md
and the rules in docs/standards-cleanup/README.md. This is my go-ahead for
step 13B only, including the production nginx change.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-canonicals, gating on each exit code.
2. Merge standards-canonicals to main and push, and deploy main to
   production with the README command.
3. Back up /etc/nginx/sites-available/annielytics.conf, install
   deploy/nginx/share.conf as /etc/nginx/snippets/models-gone-wild-share.conf,
   add its include and the index.html if to this app's page block as
   DEPLOY.md shows, run sudo nginx -t, reload, and wait two seconds. Write
   the PCI change-log row yourself and read it back.
4. Run scripts/url-list/origin.sh against production, diff it with the list
   from before the change, show me every difference, and run the production
   health check.
5. Switch staging back to main with the README command.
6. Mark step 13B done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Give me the production links to spot-check, and the Facebook Sharing
   Debugger (https://developers.facebook.com/tools/debug/) to check the
   share cards for the home page, /threat-matrix/, and /lab-counts/. Then
   tell me the standards cleanup is finished, that the server-wide nginx
   follow-up in docs/standards-cleanup/server-wide-followup.md comes next,
   and paste its prompt from that file in full, so I can start the next
   session with it.
```
