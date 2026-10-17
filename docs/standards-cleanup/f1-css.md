# Step F1: Format the CSS

Branch: `standards-format-css`

The first formatting step, run right after step 3 since Annie moved the reformat to the front on 2026-10-17. Read "Formatting comes first" in the README before anything else. The one stylesheet ends this step reading the way AI Strategy's stylesheets read, and the step adds the screenshot harness and the formatting pre-commit hook, which every later formatting step leans on.

## Decisions this step reads

- Decision 1a (staging), recorded 2026-10-16.
- Decision 27 (how a formatting step reaches production) and decision 28 (the pre-commit hook), recorded in the README. Stop if either is blank.

## Background

Measured with `audit_format.py` and `check_format.py` on 2026-10-17, read only. The app has one tracked CSS file, `css/styles.css`, 972 lines, and it fails the rule:

| Finding | Count |
|---|---|
| About This File section | Missing |
| Value columns | 15, where the rule allows 2 |
| Uneven runs | 135 |
| Comments over one line | 59 |
| Wordy comments | 64 |
| Comments inside a rule | 6 |
| History notes | 3 |
| Banner problems | 21 |
| Ends with a newline | Yes |

`check_style.py` also reports one banner issue here, at line 896, a 39-character label inside a 31-wide rule. This step fixes it.

No formatter that would fight the format is configured. There is no Prettier, Black, flake8, CI workflow, or `pyproject.toml`, and `core.hooksPath` is unset, so nothing needs removing first.

There is no screenshot harness. Step 7 planned to port ML Model Picker's, but the baseline's "done when" for F1, F2, F4, and F6 is a screenshot diff showing no change, so the port moves here and step 7 reuses it.

The model is AI Strategy's `static/css/base.css` and `static/css/components.css` in `~/Dropbox/Annielytics/Code/Python/AI Strategy/leaderboard_assistant/`. The rules are the CSS section of `~/.claude/rules/formatting/code-formatting.md`, and the worked example is `~/.claude/formatting-examples/02-css.css`.

## The changes

1. Per decision 28a, add the pre-commit hook described in `~/.claude/rules/formatting/format-gate.md`. `scripts/git-hooks/pre-commit` runs `python3 -I ~/.claude/formatting-tools/check_format.py --staged`, which checks the staged files of each language listed in `scripts/git-hooks/format-languages`, and skips with a printed note when the gate is not on the machine. The list starts empty, and each F step adds its language in its last commit, once every file of it is clean. Make the hook executable and set `git config core.hooksPath scripts/git-hooks` on this clone. Under decision 28b, skip this change and the language-list commits.
2. Port ML Model Picker's harness from `~/Dropbox/Annielytics/Code/Python/ML Model Picker/scripts/screenshot-diff/` (`run.sh`, `capture.py`, and `diff.py`) into `scripts/screenshot-diff/`. Its two Python files fail the rule today, so write the port to the rule, with AI Strategy's format-clean harness in `leaderboard_assistant/scripts/screenshot-diff/` as the layout model.
   - Use this repo's `venv` for Playwright rather than borrowing another app's.
   - Check out each ref into its own git worktree under `/tmp`, outside Dropbox, and serve it with that worktree's `scripts/serve.py` on a free port.
   - Capture the home page, `threat-matrix/`, `lab-counts/`, `poster/sol-hugging-face/` with the poster open, and `methodology/`, at 375, 768, 1024, and 1440 pixels wide.
   - Wait for `document.fonts.ready` before each capture since the Threat Matrix measures its labels in Oswald and lays out differently in a fallback face.
   - `run.sh main main` must come back clean first, which proves the harness is stable.
3. Format `css/styles.css`, one commit per pass, in the order the rule gives.
   - Alignment and spacing: Run `format_css.py`. Every rule's values start in the file's main column, set by the longest property name of 20 characters or fewer, and a rule holding a longer name moves all its values to the second column. Media queries share the columns. It also sets the banner spacing, one blank line between rules, and none before a closing brace.
   - Dead code and history: Run `strip_dead_comments.py` and delete commented-out rules, NEW and OLD markers, dates, and step numbers. Print every comment removed.
   - About This File: Run `add_about.py` with a short description of what the stylesheet styles.
   - One-line comments: List every comment over one line with `audit_comments.py`, write a reviewed JSON list of one-line labels (AI Strategy's lists in `~/.claude/formatting-tools/edits/` show the voice), and apply it with `apply_comment_edits.py`, which refuses any edit that changes a declaration. No comment sits beside a declaration or inside a rule. Fix the line 896 banner in this pass.
4. In the last commit, add `css` to `scripts/git-hooks/format-languages`, so the hook gates every CSS file from then on.

The hook, its language list, and `run.sh` sit in the web root, and nginx's denylist (`md|txt|json|ya?ml|lock|py`) does not cover a file with no extension or a `.sh` file, so all three are public until step 13A moves the site into `public/` (decision 23a). Each holds only a call to a shared checker or the harness steps, which is harmless, the same reasoning step 8 gave for its gate.

## The sample-file review gate

- Python: `scripts/screenshot-diff/capture.py` is the sample since it carries the pages, the widths, the poster state, and the font wait. Write it to the rule, prove it with `run.sh main main`, and stop for approval before `diff.py`.
- CSS: `css/styles.css` is the sample and the only CSS file. Run all four passes on it, prove it with `verify_equivalent.py` and the screenshot diff, and stop for approval before the language-list commit.

## Proving it

- `python3 -I ~/.claude/formatting-tools/verify_equivalent.py css main css/styles.css` exits 0, so the file is identical once whitespace and comments are stripped.
- `scripts/screenshot-diff/run.sh main standards-format-css` reports zero changed pixels at every width.
- Both suites pass with the same counts before every commit, and `scripts/check_overlaps.py` reports no overlaps.
- `~/.claude/formatting-tools/check_format.py` exits 0 on `css/styles.css` and on every file the step adds, and the stylesheet read top to bottom in an editor looks like AI Strategy's.
- `check_style.py` reports 69, one fewer than `main`.

## Done when

`~/.claude/formatting-tools/check_format.py` passes on `css/styles.css` and on every file the step adds, `verify_equivalent.py css` passes against `main`, the screenshot diff shows no change, both suites pass with the same counts, and (under decision 28a) a staged stray space in the stylesheet stops a commit.

## Rollback

Revert the merge commit. The stylesheet change is whitespace and comments only, and the harness and the hook change no page. `git config --unset core.hooksPath` turns the hook off.

## Paste-ready prompt: build and stage

```
Run step F1 (format the CSS) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/f1-css.md exactly. Read
docs/standards-cleanup/README.md first, starting with "Formatting comes
first", then ~/.claude/rules/formatting/code-formatting.md,
~/.claude/rules/formatting/format-gate.md,
~/.claude/formatting-examples/02-css.css, and
~/.claude/formatting-tools/HANDOFF-prompt.md. Open AI Strategy's
leaderboard_assistant/static/css/base.css and static/css/components.css as
the model. Decisions 1, 27, and 28 apply; stop if 27 or 28 is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step 3 is merged and live (marked done in the README). Branch
   off an up-to-date main as standards-format-css. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Record both counts.
3. Under decision 28a, add scripts/git-hooks/pre-commit and an empty
   scripts/git-hooks/format-languages per format-gate.md, make the hook
   executable, and set core.hooksPath on this clone. One commit.
4. Sample-file review gate (Python): port ML Model Picker's harness into
   scripts/screenshot-diff/ as the step file describes, writing
   capture.py to the formatting rule first, with AI Strategy's
   leaderboard_assistant/scripts/screenshot-diff/ as the layout model.
   Show me run.sh main main coming back clean, a clickable link to
   capture.py, a short summary, and the git diff command, then STOP until
   I approve. Then write diff.py the same way.
5. Sample-file review gate (CSS): run all four passes on css/styles.css
   (alignment and spacing, dead code and history, About This File,
   one-line comments), one commit per pass, fixing the line 896 banner.
   Prove it with verify_equivalent.py css against main and
   scripts/screenshot-diff/run.sh main standards-format-css. Give me a
   clickable link, a short summary, every comment you deleted, and the git
   diff command, then STOP until I approve. Carry any correction I ask for.
6. On approval, add css to scripts/git-hooks/format-languages in the last
   commit, and show a staged stray space in css/styles.css stopping a
   commit, then restore the file.
7. Prove it: verify_equivalent.py css against main, the screenshot diff
   (zero changed pixels), both suites (same counts), check_overlaps.py,
   ~/.claude/formatting-tools/check_format.py on css/styles.css and every
   new file, and check_style.py (69), each gated on its exit code. Read the
   stylesheet top to bottom.
8. Push, deploy the branch to staging with the README command, and run
   the staging health check.
9. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh, and STOP. Do not merge to main or touch
   production until I say so. The one exception is decision 27b: then run
   the ship prompt below yourself once every check passes.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/f1-css.md, copied exactly, so I can
paste it.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step F1 report. It needs no edits.

```
Ship step F1 (format the CSS) of the Models Gone Wild standards cleanup to
production, following docs/standards-cleanup/f1-css.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step F1 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-format-css, gating on each exit code.
2. Merge standards-format-css to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Remind me to hard-refresh (Command-Shift-R) the pages I check.
5. Switch staging back to main with the README command.
6. Mark step F1 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Give me https://www.annielytics.com/tools/models-gone-wild/ and
   https://www.annielytics.com/tools/models-gone-wild/threat-matrix/ to
   spot-check. Then tell me the next step is step F2, whose prompt is at
   the bottom of docs/standards-cleanup/f2-javascript.md.
```
