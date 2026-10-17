# Step F4: Format the HTML

Branch: `standards-format-html`

The fourth formatting step. Read "Formatting comes first" in the README before anything else. Both pages end this step reading the way AI Strategy's templates read, as far as a static page can.

## Decisions this step reads

- Decision 1a (staging), recorded 2026-10-16.
- Decision 26 (delete the HTML comments outright), recorded 2026-10-16. This step carries it out in place of step 6.
- Decision 27 (how a formatting step reaches production), decision 28 (the pre-commit hook), and decision 29 (the About section on the two pages), recorded in the README. Stop if any is blank.

## Background

Measured with `audit_format.py` and `check_format.py` on 2026-10-17, read only. The app has two pages, 2,371 lines, both served by nginx exactly as written, with no template engine. Neither passes:

| Page | Lines | HTML comments | Comments over one line | Wordy | Banner problems |
|---|---|---|---|---|---|
| `index.html` | 2,216 | 15 | 12 | 12 | 33 |
| `methodology/index.html` | 155 | 5 | 3 | 3 | 1 |

Neither has an About This File section, and both end with a newline. Most of `index.html`'s banner problems are the inline script's banners, which step F2 fixes, so rerun the audit at the start.

The rule turns HTML comments into Jinja comments so none reaches the page source. These pages have no Jinja, so decision 26 deletes all 20 instead. Two of them carry a warning that keeps a line from being "fixed" wrongly. The page's paths stay relative because it is served under `/tools/models-gone-wild/`, and `.menu-toggle` must never get a click handler because that breaks the menu on iPhone Safari. Under decision 29a, each page's About section keeps those two as one-line notes.

The markup is indented two spaces per level, and the contents of `<head>` and `<body>` start at column 0. The rule wants four spaces per level, with each tag inside another indented four from it. The inline `<script>` block keeps its lines exactly as step F2 left them since `CASES` and `GLOSSARY` sit inside it and the case loaders depend on their indentation.

The model is AI Strategy's `templates/base.html` and `templates/index.html`. This app has no base template, so `index.html`, the page that carries the shared site header, stands in for it. The rules are the HTML section of `~/.claude/rules/formatting/code-formatting.md`, and the worked example is `~/.claude/formatting-examples/05-html-jinja.html`. Annie rejected stacked attributes on 2026-10-13, so every tag stays on one line, however long, with its attributes in their original order.

## The changes

One commit per pass, all of them on the sample first.

1. Layout: Four spaces per level, with nested tags indented four from their parent. A tag split across lines is joined back onto one line. The inline `<script>` and its contents are left as they are.
2. Comments: Delete every `<!-- -->` comment outright (decision 26), printing each one removed. The `/* */` and `//` comments inside the inline script stay, as step F2 left them.
3. About This File: Under decision 29a, add a short About This File banner as an HTML comment just below `<!DOCTYPE html>`, in the comment-style banner format, saying what the page is, with the two one-line warnings above. Under decision 29b, add none.
4. The guard: Add a test to `tests/test_static.py` that fails if either page holds any HTML comment other than its About banner (or any at all under decision 29b), so a comment cannot come back.

Keep the two copies of the site header identical since `test_site_headers_match` compares them.

In the last commit, under decisions 28a and 29a, add `html` to `scripts/git-hooks/format-languages`. Under decision 29b the pages cannot pass `check_format.py`, so `html` stays off the list and each later step checks its HTML by hand.

## The sample-file review gate

- HTML: `index.html` is the sample, the page every case and the shared header live in. Apply every pass to it and stop for approval before `methodology/index.html`.
- Python: `tests/test_static.py` is the sample for the guard test. Add it, show it failing with one comment put back, and stop for approval.

## Proving it

- Serve `main` and the branch with `scripts/serve.py`, fetch every page and view, and compare the HTML once whitespace is collapsed. The only differences allowed are the 20 deleted comments and the two About banners. `verify_equivalent.py html main index.html methodology/index.html` covers the source since it ignores comments and whitespace.
- `scripts/screenshot-diff/run.sh main standards-format-html` reports zero changed pixels, and `scripts/check_overlaps.py` reports no overlaps.
- Both suites pass with the same counts plus the new guard test before every commit, and the five check scripts exit 0.
- `~/.claude/formatting-tools/check_format.py` exits 0 on both pages (under decision 29a), and both read top to bottom like AI Strategy's templates.

## Done when

`verify_equivalent.py html` passes, the page comparison shows only the deleted comments and the About banners, the screenshot diff shows no change, the guard test passes and fails with a comment put back, `check_format.py` passes on both pages (under decision 29a), and both suites pass.

## Rollback

Revert the merge commit. The pages render the same apart from the comments.

## Paste-ready prompt: build and stage

```
Run step F4 (format the HTML) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/f4-html.md exactly. Read
docs/standards-cleanup/README.md first, starting with "Formatting comes
first", then ~/.claude/rules/formatting/code-formatting.md,
~/.claude/formatting-examples/05-html-jinja.html, and
~/.claude/formatting-tools/HANDOFF-prompt.md. Open AI Strategy's
leaderboard_assistant/templates/base.html and templates/index.html as the
model. Decisions 1, 26, 27, 28, and 29 apply; stop if 27, 28, or 29 is
blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step F3 is merged and live (marked done in the README). Branch
   off an up-to-date main as standards-format-html. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Record both counts. Rerun
   audit_format.py on both pages, and save every page and view as served
   by scripts/serve.py on main.
3. Sample-file review gate (HTML): apply every pass to index.html (layout
   to four spaces with the inline script untouched, every <!-- -->
   comment deleted, and the About This File banner under decision 29),
   one commit per pass. Prove it with verify_equivalent.py html and the
   served-page comparison. Give me a clickable link, a short summary,
   every comment you deleted, and the git diff command, then STOP until I
   approve. Carry any correction I ask for.
4. On approval, do methodology/index.html the same way, keeping the two
   site headers identical.
5. Sample-file review gate (Python): add the guard test to
   tests/test_static.py, show it passing and failing with one comment put
   back, give me a clickable link, a short summary, and the git diff
   command, then STOP until I approve.
6. Under decisions 28a and 29a, add html to
   scripts/git-hooks/format-languages in the last commit.
7. Prove it: the served-page comparison, verify_equivalent.py html, the
   screenshot diff (zero changed pixels), check_overlaps.py, the five
   check scripts, both suites, and check_format.py on both pages, each
   gated on its exit code.
8. Push, deploy the branch to staging with the README command, and run
   the staging health check.
9. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh, and STOP. Do not merge to main or touch
   production until I say so. The one exception is decision 27b: then run
   the ship prompt below yourself once every check passes.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/f4-html.md, copied exactly, so I can
paste it.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step F4 report. It needs no edits.

```
Ship step F4 (format the HTML) of the Models Gone Wild standards cleanup
to production, following docs/standards-cleanup/f4-html.md and the rules
in docs/standards-cleanup/README.md. This is my go-ahead for step F4 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-format-html, gating on each exit code.
2. Merge standards-format-html to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Remind me to hard-refresh (Command-Shift-R) the pages I check, and to
   open the mobile menu on my phone.
5. Switch staging back to main with the README command.
6. Mark step F4 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Give me https://www.annielytics.com/tools/models-gone-wild/ and
   https://www.annielytics.com/tools/models-gone-wild/methodology/ to
   spot-check. Then tell me the next step is step F5, whose prompt is at
   the bottom of docs/standards-cleanup/f5-other-files.md.
```
