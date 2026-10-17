# Step F5: Format the Other Files and Add the Editor Settings

Branch: `standards-format-other`

The fifth formatting step. Read "Formatting comes first" in the README before anything else. It covers the file types the rule lists under "Other files", plus the editor settings that keep every column from breaking in VS Code.

## Decisions this step reads

- Decision 1a (staging) and decision 26a (keep the `scout/seen.json` seed on `main`), recorded 2026-10-16.
- Decision 27 (how a formatting step reaches production) and decision 28 (the pre-commit hook), recorded in the README. Stop if either is blank.

## Background

Counted on 2026-10-17:

| Filetype | Files | What the rule asks |
|---|---|---|
| requirements | `requirements-dev.txt` (2 pins, `pytest==9.1.1` and `playwright==1.64.0`) | The version specifiers align in one column. |
| Shell | `scripts/screenshot-diff/run.sh` and `scripts/git-hooks/pre-commit`, both added in step F1 | Continuation backslashes align in one column. Never pad an assignment since a space around `=` breaks it. |
| Editor settings | None. There is no `.vscode/` folder. | Add `.vscode/settings.json` from the rule's "Editor settings" section, which turns off soft wrap for every formatted language. |

Left alone, and why:

- `scout/seen.json`: A seed the scout overwrites with `json.dump` at the start of every run (decision 26), so any alignment would be undone the next morning.
- `deploy/nginx/headers.conf`: An nginx include. The rule has no format for nginx, and its three `add_header` lines already align.
- `.gitignore`: The rule has no format for it.
- No `.env` file is tracked, and the server copies are Annie's to edit by hand.

Aligning the pins (`pytest     ==9.1.1`) is valid for pip, which allows spaces before the operator, but step 3's `test_dev_requirements_are_pinned` matches `name==version` with no space, so it would fail. Widen its pattern to allow spaces before `==`, and keep it failing on any operator other than `==`.

The editor settings live in a `.vscode/` folder at the root. Step 4's root guard counts tracked files at the root, not folders, so it is unaffected. Nginx's denylist covers `.json`, so the settings file is never served.

## The changes

1. Align `requirements-dev.txt` per section O2 of `~/.claude/formatting-examples/06-other-formats.md`, and widen the pin test's pattern in `tests/test_dependencies.py` in the same commit.
2. Confirm both shell scripts match the rule since F1 wrote them to it, and give each an About This File comment in the comment-style format if it lacks one. Never pad an assignment.
3. Add `.vscode/settings.json` in its own commit.

## The sample-file review gate

- Python: `tests/test_dependencies.py` is the sample, the one Python file the step changes. Widen the pattern, show the test passing on the aligned file and failing on a `>=` pin, and stop for approval.
- requirements: `requirements-dev.txt` is the one file. Show it with the Python sample.
- Shell: `scripts/screenshot-diff/run.sh` is the sample, the longer of the two. Stop for approval before the hook.

## Proving it

- `pip install --dry-run -r requirements-dev.txt` in the venv resolves the same versions as on `main`, and step 3's pin test and hash test pass.
- `verify_equivalent.py sh main <files>` exits 0 and `bash -n` passes on both shell scripts, and the hook still stops a commit with a staged stray space in a gated file.
- Both suites pass with the same counts.

## Done when

Every file in the table matches the rule, the pip dry run resolves the same versions, the equivalence checks and `bash -n` pass, `.vscode/settings.json` exists, and both suites pass with the same counts.

## Rollback

Revert the merge commit.

## Paste-ready prompt: build and stage

```
Run step F5 (format the other files and add the editor settings) of the
Models Gone Wild standards cleanup, following
docs/standards-cleanup/f5-other-files.md exactly. Read
docs/standards-cleanup/README.md first, starting with "Formatting comes
first", then the "Other files" and "Editor settings" sections of
~/.claude/rules/formatting/code-formatting.md and
~/.claude/formatting-examples/06-other-formats.md. Decisions 1, 26, 27, and
28 apply; stop if 27 or 28 is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step F4 is merged and live (marked done in the README). Branch
   off an up-to-date main as standards-format-other. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Record both counts.
3. Sample-file review gate (Python and requirements): align
   requirements-dev.txt and widen the pattern in tests/test_dependencies.py
   to allow spaces before ==. Show the test passing on the aligned file and
   failing on a >= pin, and the pip dry run resolving the same versions as
   main. Give me clickable links to both files, a short summary, and the
   git diff command, then STOP until I approve.
4. Sample-file review gate (shell): bring scripts/screenshot-diff/run.sh to
   the rule, prove it with verify_equivalent.py sh and bash -n, and STOP
   until I approve. Then do scripts/git-hooks/pre-commit and show it still
   stopping a commit with a staged stray space.
5. Add .vscode/settings.json in its own commit.
6. Prove it: the equivalence checks, bash -n, the pip dry run, and both
   suites (same counts), each gated on its exit code.
7. Push, deploy the branch to staging with the README command, and run
   the staging health check. Confirm .vscode/settings.json returns 403 or
   404, never 200, at the staging origin.
8. Report what you verified and how, and STOP. Do not merge to main or
   touch production until I say so. The one exception is decision 27b:
   then run the ship prompt below yourself once every check passes.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/f5-other-files.md, copied exactly,
so I can paste it.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step F5 report. It needs no edits.

```
Ship step F5 (format the other files and add the editor settings) of the
Models Gone Wild standards cleanup to production, following
docs/standards-cleanup/f5-other-files.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step F5 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-format-other, gating on each exit code.
2. Merge standards-format-other to main and push.
3. Deploy main to production with the README command and run the production
   health check. Confirm .vscode/settings.json returns 403 or 404, never
   200, at the origin:
   curl -sk -H "Host: www.annielytics.com" -o /dev/null -w "%{http_code}\n" https://127.0.0.1/tools/models-gone-wild/.vscode/settings.json
4. Switch staging back to main with the README command.
5. Mark step F5 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
6. Tell me the next step is step F6, whose prompt is at the bottom of
   docs/standards-cleanup/f6-quotes.md.
```
