# Step 13B: Canonicals, the /index.html Duplicate, and Share Tags

Branch: `standards-canonicals`

The second half of the baseline's URL step, and the last step in the plan. It changes what search engines are told about each URL, so every change is an approved difference in step 13A's URL list.

## Decisions this step reads

Decision 1 (staging), decision 23 (where the pages live after 13A), decision 24 (canonicals and `/index.html`), and decision 25 (meta description and share tags), from `docs/standards-cleanup/README.md`.

## Background

On 2026-10-16 no page carried a canonical tag, a meta description, or Open Graph or Twitter tags. At the production origin, the home page, `/index.html`, `threat-matrix/`, `lab-counts/`, and all 21 poster permalinks returned 200 with the same HTML, and `methodology/` and `methodology/index.html` returned the same page. Search engines see up to 25 URLs for one document and pick a canonical themselves.

The views and posters are states of one page, drawn by the script from the address bar. Their HTML is identical, so a static tag in the page cannot tell them apart. Only a response header set per nginx block can (decision 24b), and nginx drops headers set in a block that ends in `rewrite ... last`, so 24b has to carry the value through a variable set in the rewrite block and sent from the page block.

A link shared on social media shows no title card today since there are no share tags.

## The changes

1. Under decision 24a:
   - `index.html` gains `<link rel="canonical" href="https://www.annielytics.com/tools/models-gone-wild/">`, an absolute URL, which the leading-slash test allows since it starts with `https:`.
   - `methodology/index.html` gains its own: `https://www.annielytics.com/tools/models-gone-wild/methodology/`.
   - `404.html` has none.
   - Nginx gains `location = /tools/models-gone-wild/index.html { return 301 /tools/models-gone-wild/; }` and the same for `methodology/index.html`, mirrored in `scripts/serve.py`.
2. Under decision 24b, set a `$mgw_canonical` variable in each view and poster rewrite block, send it from the page block as `add_header Link "<$mgw_canonical>; rel=\"canonical\"" always;`, and give Methodology a static tag. The 301s for the `index.html` forms are the same as 24a. Under 24c, add only the 301s.
3. Under decision 25a, propose the copy for both pages' meta description and the Open Graph and Twitter title and description (written to `~/.claude/rules/editorial/annielytics-writing-rules.md`, in the page's voice, and never praising or grading a lab, per `UPDATE.md`'s voice rules), and STOP for approval. Then add `og:title`, `og:description`, `og:url`, `og:type` (`website`), `twitter:card` (`summary`), `twitter:title`, and `twitter:description` to both pages. Under 25b, also wait for your share image and add `og:image` and `twitter:image`, with `twitter:card` set to `summary_large_image`. Under 25c, skip this.
4. Extend step 13A's URL list to record the `Link` header (24b) and the meta description, and add tests: each page's canonical is the expected absolute URL, the 404 page has none, and the `index.html` forms return 301.

## The sample-file review gate

- HTML: `index.html` is the sample since it carries the canonical every view and poster resolves to. `methodology/index.html` and `404.html` follow.
- Python: `scripts/serve.py` only.

## Done when

The URL list for the branch matches `main` except for the approved changes (the canonical column, the meta description column, and the two `index.html` forms now 301), locally and at the staging origin. Both suites, the CSP walk, and the screenshot diff (pixel-identical since nothing visible changes) pass.

## Rollback

Revert the commit. Restore the config backup on each server, run `sudo nginx -t`, reload, and add a PCI row. A canonical that shipped wrong should be fixed and redeployed rather than removed, so search engines see one consistent change.

## Paste-ready prompt: build and stage

```
Run step 13B (canonicals and share tags) of the Models Gone Wild standards
cleanup, following docs/standards-cleanup/13b-canonicals.md exactly. Read
docs/standards-cleanup/README.md and
~/.claude/rules/editorial/annielytics-writing-rules.md first. Use decisions
1, 23, 24, and 25 as recorded in the README, and stop if any is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Confirm step 13A is merged and live. Branch off an up-to-date main as
   standards-canonicals. Never work on main.
2. Run both suites and the CSP walk, and confirm they pass. Record the URL
   list for main with scripts/url-list/run.sh main.
3. Under decision 25a or 25b, propose the meta description and the share
   title and description for both pages, and STOP until I approve the copy.
4. Sample-file review gate (HTML): add the canonical (decision 24) and the
   approved tags to index.html (public/index.html under decision 23a), run
   the URL list against the branch, and give me a clickable link, a short
   summary, the URL list diff, and the git diff command. STOP until I
   approve. Then methodology/index.html, and confirm 404.html has no
   canonical.
5. Add the index.html 301s to scripts/serve.py, extend the URL list's
   columns, and add the tests.
6. Run both suites, the CSP walk, the screenshot diff (pixel-identical), and
   the comment style checker (0), gating on each exit code.
7. Under decision 1a, on the server: back up
   /etc/nginx/sites-available/staging.annielytics.conf, add the two 301
   blocks (and the 24b Link header if chosen), show me the diff, and STOP
   until I approve. Then sudo nginx -t, reload, wait two seconds, and write
   the PCI change-log row yourself, reading it back.
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
3. Back up /etc/nginx/sites-available/annielytics.conf, add the two 301
   blocks (and the 24b Link header if chosen), run sudo nginx -t, reload,
   and wait two seconds. Write the PCI change-log row yourself and read it
   back.
4. Run scripts/url-list/origin.sh against production, diff it with the list
   from before the change, show me every difference, and run the production
   health check.
5. Under decision 1a, switch staging back to main with the README command.
6. Mark step 13B done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Give me the production links to spot-check, and the Facebook Sharing
   Debugger (https://developers.facebook.com/tools/debug/) to check the
   home page's share card. Then tell me the standards cleanup is finished,
   and that prompts 5 to 7 in
   ~/.claude/skills/app-refactor-audit/prompts.md (formatting, quotes, and
   comment length) come next.
```
