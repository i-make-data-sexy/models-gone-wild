# Step 4: Root Files, Workflow Docs, and Merged Branches

Branch: `standards-root-files`

## Decisions this step reads

Decision 8a (`DEPLOY.md` and `UPDATE.md` stay at the root), decision 9a (rewrite the prompts that deploy straight to production), and decision 10a (delete merged branches), recorded in `docs/standards-cleanup/README.md` on 2026-10-16.

## Background

On 2026-10-16 the root held four tracked files (`.gitignore`, `DEPLOY.md`, `UPDATE.md`, and `index.html`). After steps 1 and 3 it also holds `requirements-dev.txt`. There is no guard, so nothing stops a stray file landing there, and in this app a root file is a public file unless nginx's denylist names its extension.

The baseline keeps `app.py`, `wsgi.py`, config, the requirements files, `pytest.ini`, `.env.example`, and dotfiles at the root. This app differs in four ways:

- There is no `app.py`, `wsgi.py`, or config file.
- `index.html` has to sit at the root while the root is the web root since the page block aliases the checkout. Decision 23a moves it in step 13A.
- There is no `pytest.ini` since a root `.ini` would be public (step 1).
- There is no `.env.example`. No tracked file reads an environment variable, and a tracked `.env.example` would be served since the server-wide rule only blocks names ending in `.env`. The local `.env` (the Cloudflare token) is gitignored and stays.

Three more items land here because they are hygiene rather than code:

- `UPDATE.md`'s "Adding a case" and "Changing copy" prompts end with "commit, push, and deploy", its "Deploying the change" section merges to `main` and pulls on production in one block, the add-case skill (`.claude/skills/models-gone-wild-add-case/SKILL.md` and `~/.claude/skills/models-gone-wild-add-case/SKILL.md`, identical on 2026-10-16) ends with "Commit, then deploy", and `DEPLOY.md`'s "Updating after the first deploy" shows the production pull alone. None of them stops at staging for your word.
- `scout/SCOUT.md`'s publishing prompt ("review the diff with me, then merge to main and deploy") is one you paste yourself, so it is already your word, but it names no staging leg.
- 26 local branches and 8 remote branches (`add-anthropic-forms`, `add-anthropic-undated`, `add-case-scout`, `add-methodology-page`, `axis-margin-tokens`, `cases-by-lab-chart`, `mockup-kind-filter`, `view-permalinks`) are already merged into `main`.

## The changes

1. `tests/test_root.py`: lists the tracked files at the root with `git ls-files` and fails on any not in the allowlist. The allowlist is `.gitignore`, `index.html`, `requirements-dev.txt`, `DEPLOY.md`, and `UPDATE.md`. Tracked folders are not counted.
2. Under decision 9a, rewrite the deploy flow in five files.
   - `UPDATE.md`: the three prompts and "Deploying the change", so each ends by deploying the branch to staging, giving the links, and stopping. Production then runs only on your word, with the commands from the README.
   - `.claude/skills/models-gone-wild-add-case/SKILL.md` and `~/.claude/skills/models-gone-wild-add-case/SKILL.md`: the closing deploy step, the same way. Keep the two copies byte-identical since the cloud scout reads the repo copy.
   - `DEPLOY.md`: "Updating after the first deploy" and "Branch discipline", to name the staging leg.
   - `scout/SCOUT.md`: the publishing prompt, to name the staging leg.
3. `tests/test_root.py` also asserts the repo's skill copy matches `~/.claude/skills/models-gone-wild-add-case/SKILL.md` when the home copy exists, and skips otherwise (the cloud has no home copy).
4. Under decision 10a, delete the merged branches, keeping `main`, `scout-state`, every `update/*` and `candidate/*`, and the current branch. List them first with `git branch --merged main` and `git branch -r --merged origin/main`, show the list, and delete only after approval: `git branch -d <name>` locally (never `-D`), and `git push origin --delete <name>` for the remote ones.

## The sample-file review gate

- Markdown: `UPDATE.md` is the sample since it holds four of the deploy instructions. Rewrite it first and stop for approval before the skill copies, `DEPLOY.md`, and `SCOUT.md`.
- Python: There is one new test file, so there is nothing to sample.

## Done when

`tests/test_root.py` passes, and fails when a scratch file is added at the root (`touch notes.txt && git add -N notes.txt`, run it, then `git rm --cached notes.txt && rm notes.txt`). Show both outcomes.

## Rollback

Revert the commits. A deleted branch whose commits are all on `main` loses nothing; `git reflog` holds the local tips if a name is wanted back.

## Paste-ready prompt: build and stage

```
Run step 4 (root files, workflow docs, merged branches) of the Models Gone
Wild standards cleanup, following docs/standards-cleanup/04-root-files.md
exactly. Read docs/standards-cleanup/README.md first. Use decisions 1, 8, 9,
and 10 as recorded in the README, and stop if any is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step 3 is merged and live. Branch off an up-to-date main as
   standards-root-files. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change.
3. Write tests/test_root.py with the allowlist from the step file, and show me
   the guard failing on a scratch root file and passing without it.
4. Sample-file review gate (Markdown): rewrite UPDATE.md's
   three prompts and its "Deploying the change" section first. Give me a
   clickable link, a short summary, and the git diff command, and STOP
   until I approve. Then do both copies of the add-case skill (identical),
   DEPLOY.md, and scout/SCOUT.md the same way.
5. List the merged local and remote branches you would
   delete, and STOP until I approve the list. Then delete them with git
   branch -d and git push origin --delete.
6. Run both suites and the comment style checker, gating on each exit code,
   commit, push, and deploy the branch to staging with the
   README command and run the staging health check.
7. Report what you verified and how, and STOP. Do not merge to main or touch
   production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/04-root-files.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step 4 report. It needs no edits.

```
Ship step 4 (root files, workflow docs, merged branches) of the Models Gone
Wild standards cleanup to production, following
docs/standards-cleanup/04-root-files.md and the rules in
docs/standards-cleanup/README.md. This is my go-ahead for step 4 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-root-files, gating on each exit code.
2. Merge standards-root-files to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Switch staging back to main with the README command.
5. Mark step 4 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
6. Tell me the next step is step 5, whose prompt is at the bottom of
   docs/standards-cleanup/05-python-structure.md.
```
