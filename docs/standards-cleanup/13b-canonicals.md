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

1. Create `deploy/nginx/canonical-map.conf` in the repo, and install it on the server as `/etc/nginx/conf.d/models-gone-wild-canonical.conf`:

   ```nginx
   map $request_uri $mgw_canonical {
       default "";
       ~^/tools/models-gone-wild/(?:\?.*)?$                                   https://www.annielytics.com/tools/models-gone-wild/;
       ~^/tools/models-gone-wild/(?<view>threat-matrix|lab-counts)/(?:\?.*)?$ https://www.annielytics.com/tools/models-gone-wild/$view/;
       ~^/tools/models-gone-wild/poster/(?<slug>[a-z0-9-]+)/(?:\?.*)?$        https://www.annielytics.com/tools/models-gone-wild/poster/$slug/;
       ~^/tools/models-gone-wild/methodology/(?:\?.*)?$                       https://www.annielytics.com/tools/models-gone-wild/methodology/;
   }

   map $mgw_canonical $mgw_link {
       ""      "";
       default "<$mgw_canonical>; rel=\"canonical\"";
   }
   ```

   Assets requested under a permalink, the 404 page, and every other address map to an empty value, and nginx sends no header with an empty value. Confirm with `sudo nginx -t` that this nginx accepts the named captures; if not, use numbered ones.
2. Add `add_header Link $mgw_link always;` to this app's page block on each server. The page block also includes the headers snippet, which is fine since both `add_header` lines sit in the same block.
3. Mirror the map in `scripts/serve.py`, so the preview and the tests send the same header, and add a test that the two agree for every row of the URL list.
4. Add `location = /tools/models-gone-wild/index.html { return 301 /tools/models-gone-wild/; }` and the same for `methodology/index.html` on both servers, mirrored in `serve.py`.
5. Propose the copy for both pages' meta description and the Open Graph and Twitter title and description, written to `~/.claude/rules/editorial/annielytics-writing-rules.md`, in the page's voice, and never praising or grading a lab, per `UPDATE.md`'s voice rules. STOP for approval. Then ask Annie for the share image she designed: 1200 by 630 pixels, saved as `public/img/share.png`, under 5 MB. Nginx already serves `img/` with a 30-day cache.
6. Add to both pages `<meta name="description">`, `og:title`, `og:description`, `og:url`, `og:type` (`website`), `og:image`, `og:image:width` (1200), `og:image:height` (630), `og:image:alt`, `twitter:card` (`summary_large_image`), `twitter:title`, `twitter:description`, and `twitter:image`. The image and URL values are absolute (`https://www.annielytics.com/tools/models-gone-wild/img/share.png`), which the leading-slash test allows by name. `og:url` on `index.html` is the home page since the HTML is shared by every view and poster. `404.html` gets none.
7. Extend step 13A's URL list to record the `Link` header and the meta description, and add tests that each permalink's `Link` header names its own URL, the 404 page and every asset send none, and both `index.html` forms return 301.

## The sample-file review gate

- HTML: `public/index.html` is the sample since its share tags serve every view and poster. Add them, run the URL list, and stop for approval before `public/methodology/index.html`.
- Config: `deploy/nginx/canonical-map.conf` is new, so there is nothing to sample. On the servers, staging goes first, during the build.
- Python: `scripts/serve.py` is the only Python file this step changes.

## Done when

The URL list for the branch matches `main` except for the approved changes (the `Link` column, the meta description column, and the two `index.html` forms now 301), locally and at the staging origin. Both suites, the CSP walk, and the screenshot diff (pixel-identical since nothing visible changes) pass. After the ship, the Facebook Sharing Debugger shows the title card for the home page.

Every file the step changes or creates passes `python3 -I ~/.claude/formatting-tools/check_format.py` and `check_style.py`, with the formatter re-run where a change moved a column.

## Rollback

Revert the commit. On each server, restore the config backup, remove `/etc/nginx/conf.d/models-gone-wild-canonical.conf`, run `sudo nginx -t`, reload, and add a PCI row. A canonical that shipped wrong should be fixed and redeployed rather than removed, so search engines see one consistent change.

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

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/13b-canonicals.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once the staging URL list checks out. It needs no edits.

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
3. Back up /etc/nginx/sites-available/annielytics.conf, add the Link header
   to this app's page block and the two 301 blocks, run sudo nginx -t,
   reload, and wait two seconds. Write the PCI change-log row yourself and
   read it back.
4. Run scripts/url-list/origin.sh against production, diff it with the list
   from before the change, show me every difference, and run the production
   health check.
5. Switch staging back to main with the README command.
6. Mark step 13B done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Give me the production links to spot-check, and the Facebook Sharing
   Debugger (https://developers.facebook.com/tools/debug/) to check the
   home page's share card. Then tell me the standards cleanup is finished,
   and that prompts 5 to 7 in
   ~/.claude/skills/app-refactor-audit/prompts.md (formatting, quotes, and
   comment length) come next.
```
