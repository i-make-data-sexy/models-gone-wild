# Step 0: Dropbox Ignore

No branch. This step only sets an extended attribute on folders on your Mac. Nothing is committed and nothing reaches the server.

## Background

The repo lives in Dropbox on purpose, but Dropbox syncs every file, and when the MacBook Air and the main Mac both write to the same folder, it forks files instead of merging them. In July 2026 that forked 5,418 files in AI Timeline's `venv/` and the app stopped booting (`~/.claude/rules/coding/dropbox-sync-hygiene.md` tells the story).

The table shows where each folder stood on 2026-10-16.

| Path | `com.dropbox.ignored` |
|---|---|
| `.git` | 1 |
| `venv` | does not exist |
| `.pytest_cache` | does not exist |
| `__pycache__` (any) | does not exist |

No conflicted copies exist anywhere in the repo. This app has never had a virtualenv since nothing in it needs a package today. Step 1 needs one for pytest and Playwright, and the attribute can only be set on a folder that exists. So this step creates an empty `venv` on the same Python the rest of Annie's apps use, marks it, and leaves the installing to step 1. Step 3 then pins what step 1 installed.

A sample-file review gate does not apply. Nothing here edits a file.

## The changes

Run this from the repo root:

```
cd "/Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild"
/Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 -m venv venv
xattr -w com.dropbox.ignored 1 venv
mkdir -p .pytest_cache && xattr -w com.dropbox.ignored 1 .pytest_cache
xattr -w com.dropbox.ignored 1 .git
```

Pytest leaves `.pytest_cache` alone when it already exists, so the attribute survives the first run. `__pycache__` folders appear later, under `scripts/` and `tests/`. Step 1's build prompt marks them after its first run.

Add `.pytest_cache/` to `.gitignore` in step 1 since `venv/` and `__pycache__/` are already there.

## Done when

```
xattr -p com.dropbox.ignored .git venv .pytest_cache
```

prints `1` three times, and

```
find . -iname "*conflicted copy*" -not -path "./.git/*"
```

prints nothing.

## Rollback

`xattr -d com.dropbox.ignored venv` (or the folder in question) turns syncing back on. Deleting `venv` is harmless since nothing is installed in it yet.

## Paste-ready prompt: build

There is no ship prompt for this step since it never reaches the server.

```
Run step 0 (Dropbox ignore) of the Models Gone Wild standards cleanup,
following docs/standards-cleanup/00-dropbox-ignore.md exactly. Read
docs/standards-cleanup/README.md first.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Confirm the decisions in the README are all filled in, and stop if any
   is blank.
2. Create venv with
   /Library/Frameworks/Python.framework/Versions/3.11/bin/python3.11 -m venv venv,
   then set com.dropbox.ignored on venv, .pytest_cache (create it first),
   and .git, as the step file shows. Install nothing.
3. Run the "Done when" checks and show me the output: three 1s, and no
   conflicted copies.
4. Mark step 0 done in docs/standards-cleanup/README.md with today's date
   on a branch off an up-to-date main named standards-step-0, commit, push,
   and merge to main (it is a docs-only change, so this prompt is my
   go-ahead for that merge).
5. Tell me the next step: step 0B under decision 1a, whose prompt is at the
   bottom of docs/standards-cleanup/00b-staging.md, or step 1 under
   decision 1b, at the bottom of docs/standards-cleanup/01-tests.md.
```
