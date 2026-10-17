# Step 8B: Token Consolidation (Pass B)

Branch: `standards-token-consolidation`

Skipped under decision 13a (recorded 2026-10-16), and marked skipped in the README. The file stays so the pass can run later if you change your mind. Do not run its prompts without changing decision 13 first.

This is pass B of the design-tokens skill, a deliberate visual change reviewed screenshot by screenshot. Pass A (step 8) has to be in production first, so a bug in this step cannot be mistaken for the extraction.

## Background

On 2026-10-16, `audit_tokens.py .` reported 16 distinct font sizes, among them 9px, 10px, 10.5px, 11px, 11.5px, 12px, 12.5px, 13px, 14px, 15px, 19px, 30px, 64px, and `.95em`, and 12 distinct line heights (1.5, 1, 1.7, 1.2, 1.55, .86, 1.05, 1.45, .82, 1.1, .95, and 1.65). Several sit a half pixel apart (10.5 and 11, 11.5 and 12, 12.5 and 13), which reads as drift rather than design.

The color palette is small, and `audit_tokens.py` reported no near-duplicate clusters. The one exact duplicate is `--stamp-red` and `--class3` (`#8f1d16`).

The distressed-paper design relies on small type in Courier Prime, Special Elite, and Oswald, so the scale is the app's own, not another app's.

## The changes

1. Propose a type scale for the app's three faces (the steps, which existing sizes each absorbs, and where each size is used), and a line-height set. STOP for approval before applying anything.
2. Apply the approved scale, one token at a time, rerunning the screenshot diff after each.
3. Under your call during review, make `--class3` reference `--stamp-red` (or the reverse) so the shared value has one definition.
4. Keep `check_raw_values.py` at zero throughout.

## The sample-file review gate

- CSS: `css/poster.css` is the sample since the poster carries the most sizes (its footer line has to fit on one row, which `UPDATE.md`'s third check and step 1's test guard). Apply the scale there first, show the before-and-after screenshots of a poster at 375 and 1440 pixels, and stop for approval before the other files.

## Done when

You approve every changed screenshot in `scripts/screenshot-diff/` output, every poster footer still fits on one line (step 1's test), `scripts/check_overlaps.py` still reports no overlaps at 1300 and 390 pixels wide, and both suites pass.

## Rollback

Revert the commits. Pass A's tokens remain.

## Paste-ready prompt: build and stage

```
Run step 8B (token consolidation, pass B) of the Models Gone Wild standards
cleanup, following docs/standards-cleanup/08b-token-consolidation.md
exactly. Read docs/standards-cleanup/README.md and
~/.claude/skills/design-tokens/SKILL.md first. Use decisions 1 and 13 as
recorded in the README, and stop if either is blank. Under 13a, mark step 8B
skipped in the README on a branch, merge that docs change, and stop.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step 8 is merged and live. Branch off an up-to-date main as
   standards-token-consolidation. Never work on main.
2. Run both suites and confirm they pass. Run audit_tokens.py and show me
   the font sizes and line heights in use, with counts.
3. Propose the type scale and line-height set as the step file describes,
   and STOP until I approve.
4. Sample-file review gate (CSS): apply the approved scale to
   css/poster.css first, run the screenshot diff, and give me clickable
   links to the poster screenshots at 375 and 1440, a short summary, and
   the git diff command. STOP until I approve.
5. After I approve, apply it to the other CSS files, one token at a time,
   rerunning the screenshot diff, and show me every changed screenshot.
6. Run both suites, check_overlaps.py at --width 1300 and --width 390,
   check_raw_values.py (0), and the comment style checker (0), gating on
   each exit code.
7. Commit, push, and deploy the branch to staging with the
   README command and run the staging health check.
8. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh, and STOP. Do not merge to main or touch
   production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/08b-token-consolidation.md, copied
exactly.
```

## Paste-ready prompt: ship to production

Paste this once you have approved the step 8B screenshots on staging. It needs no edits.

```
Ship step 8B (token consolidation) of the Models Gone Wild standards cleanup
to production, following docs/standards-cleanup/08b-token-consolidation.md
and the rules in docs/standards-cleanup/README.md. This is my go-ahead for
step 8B only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-token-consolidation, gating on each exit code.
2. Merge standards-token-consolidation to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Remind me to hard-refresh the production pages and open a poster.
5. Switch staging back to main with the README command.
6. Mark step 8B done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Tell me the next step is step 9A, whose prompt is at the bottom of
   docs/standards-cleanup/09a-case-data.md.
```
