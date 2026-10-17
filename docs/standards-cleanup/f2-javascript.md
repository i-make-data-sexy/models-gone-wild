# Step F2: Format the JavaScript

Branch: `standards-format-js`

The second formatting step. Read "Formatting comes first" in the README before anything else. The app's own JavaScript ends this step reading the way AI Strategy's scripts read.

## Decisions this step reads

- Decision 1a (staging), recorded 2026-10-16.
- Decision 27 (how a formatting step reaches production) and decision 28 (the pre-commit hook), recorded in the README. Stop if either is blank.

## Background

The app's own JavaScript lives inline until steps 9A and 9B move it into files. Measured on 2026-10-17 by lifting each `<script>` block into a scratch `.js` file and running `audit_format.py` on it, read only:

| Block | Lines | Uneven runs | Comments over one line | Wordy | Inside a block | Mixed placement | History | Banner problems |
|---|---|---|---|---|---|---|---|---|
| `index.html`, lines 218 to 2213 | 1,996 | 81 | 89 | 108 | 7 | 1 | 3 | 32 |
| `methodology/index.html`, lines 135 to 152 | 18 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |

`check_style.py` reports 18 comment-prose issues in these blocks: 17 in `index.html` (12 one-sentence comments ending in a period, and 5 lowercase labels in the `HAIR` table near line 926) and 1 in `methodology/index.html` at line 139. This step clears all 18 by deleting the comments, the `HAIR` labels included.

The one tracked `.js` file, `js/html2canvas.min.js`, is a vendored third-party library, minified and pinned by the SHA-256 test from step 3. It stays exactly as shipped and is out of scope.

The `CASES` array (lines 259 to 669) and the `GLOSSARY` object (lines 754 to 785) stay byte for byte. Four check scripts, `tests/test_static.py`, `UPDATE.md`, and the add-case skill find cases with patterns such as `id:"` and a closing brace indented two spaces, so a realigned case breaks them all. Step 9A moves both into files and settles their format under decision 30.

`audit_format.py` measures an `.html` file's comments, not its inline code, so the hook cannot see these blocks. Adding `js` to the hook's list here makes it gate the files steps 9A and 9B create from them.

The model is AI Strategy's `static/js/network.js` and `static/js/page-tools.js`. The rules are the JavaScript section of `~/.claude/rules/formatting/code-formatting.md`, and the worked example is `~/.claude/formatting-examples/04-javascript.js`.

## The changes

Work on each block as a scratch `.js` file in the session scratchpad, then put it back between its tags with nothing else on those lines changed. One commit per pass, all three passes on the sample first.

1. Alignment and spacing: Run `format_js.py`. Consecutive `const` lines align their `=`, object values align after the colon (siblings in a bracket share one column, a key that opens a nested block included), multi-line ternaries and conditions lead with their operators, and promise chains align their arrows. Banner spacing per the rule. Restore the `CASES` and `GLOSSARY` lines from `main` before writing the block back.
2. Dead code and history: Run `strip_dead_comments.py`, printing every comment removed.
3. Label comments: Delete every comment except the section banners, with a JSON list applied by `apply_comment_edits.py`, which prints each one removed. Label comments are deleted, not shortened (see "Formatting comes first" in the README). At the sample review on 2026-10-17, Annie asked for the long comments left in `index.html` to go as well. That took the `CASES` field comment, which only repeated `UPDATE.md`'s schema table, and the page's 15 HTML comments, pulled forward from step F4.

The block gets no About This File section of its own. Step F4 gives each page one, and step 9B gives each script file it creates one.

In the last commit, add `js` to `scripts/git-hooks/format-languages` (under decision 28a).

## The sample-file review gate

- JavaScript: The `index.html` block is the sample, the code with the most findings and every pattern the rule covers (declarations, nested objects, event maps, promise chains, template strings, and long comment blocks). Run all three passes on it and stop for approval before the Methodology block.
- HTML: The only change to either page is its script block, so `index.html` is the sample here too. Show its diff with the JavaScript sample.

## Proving it

- For each block, `python3 -I ~/.claude/formatting-tools/verify_equivalent.py js` passes on the scratch file against the block on `main`, and `node --check` passes on the scratch file.
- `git diff main -- index.html` touches no line of `CASES` or `GLOSSARY`, and the five check scripts exit 0.
- Both suites pass with the same counts before every commit. The browser suite opens the tabs, filters, a poster, and the glossary bubbles, so it catches a script that no longer runs.
- `scripts/screenshot-diff/run.sh main standards-format-js` reports zero changed pixels, and `scripts/check_overlaps.py` reports no overlaps.
- `check_format.py` exits 0 on each scratch file outside `CASES` and `GLOSSARY`, and `check_style.py` reports 51.

## Done when

Each block passes `verify_equivalent.py js` and `node --check`, `check_format.py` passes on both blocks apart from `CASES` and `GLOSSARY`, which are unchanged, the screenshot diff shows no change, both suites pass with the same counts, and `check_style.py` reports 51.

## Rollback

Revert the merge commit. Whitespace and comments only.

## Paste-ready prompt: build and stage

```
Run step F2 (format the JavaScript) of the Models Gone Wild standards
cleanup, following docs/standards-cleanup/f2-javascript.md exactly. Read
docs/standards-cleanup/README.md first, starting with "Formatting comes
first", then ~/.claude/rules/formatting/code-formatting.md,
~/.claude/formatting-examples/04-javascript.js, and
~/.claude/formatting-tools/HANDOFF-prompt.md. Open AI Strategy's
leaderboard_assistant/static/js/network.js and static/js/page-tools.js as
the model. Decisions 1, 27, and 28 apply; stop if 27 or 28 is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step F1 is merged and live (marked done in the README). Branch
   off an up-to-date main as standards-format-js. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Record both counts.
3. Lift the index.html script block (lines 218 to 2213) into a scratch .js
   file in the session scratchpad. Leave CASES (lines 259 to 669) and
   GLOSSARY (lines 754 to 785) byte for byte, and leave
   js/html2canvas.min.js alone.
4. Sample-file review gate (JavaScript and HTML): run the three passes on
   the index.html block (alignment and spacing, dead code and history,
   then deleting every label comment, keeping only the section banners
   and the CASES field comment), one commit per pass, writing it back
   between its tags. Prove it with verify_equivalent.py js and node
   --check on the scratch file, and git diff main -- index.html showing
   no line of CASES or GLOSSARY changed. Give me a clickable link to
   index.html, a short summary, a linked file listing the full text of
   every comment you deleted, and the git diff command, then STOP until I
   approve. Carry any correction I ask for.
5. On approval, do the methodology/index.html block the same way, then add
   js to scripts/git-hooks/format-languages in the last commit.
6. Prove it: verify_equivalent.py js and node --check on both blocks, the
   five check scripts (exit 0), both suites (same counts), the screenshot
   diff (zero changed pixels), check_overlaps.py, check_format.py on both
   scratch files outside CASES and GLOSSARY, and check_style.py (51), each
   gated on its exit code.
7. Push, deploy the branch to staging with the README command, and run
   the staging health check.
8. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh, and STOP. Do not merge to main or touch
   production until I say so. The one exception is decision 27b: then run
   the ship prompt below yourself once every check passes.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/f2-javascript.md, copied exactly, so
I can paste it.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step F2 report. It needs no edits.

```
Ship step F2 (format the JavaScript) of the Models Gone Wild standards
cleanup to production, following docs/standards-cleanup/f2-javascript.md
and the rules in docs/standards-cleanup/README.md. This is my go-ahead for
step F2 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-format-js, gating on each exit code.
2. Merge standards-format-js to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Remind me to hard-refresh (Command-Shift-R) the pages I check, and to
   open a poster and press Download poster.
5. Switch staging back to main with the README command.
6. Mark step F2 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Give me https://www.annielytics.com/tools/models-gone-wild/ and
   https://www.annielytics.com/tools/models-gone-wild/poster/sol-hugging-face/
   to spot-check. Then tell me the next step is step F3, whose prompt is at
   the bottom of docs/standards-cleanup/f3-python.md.
```
