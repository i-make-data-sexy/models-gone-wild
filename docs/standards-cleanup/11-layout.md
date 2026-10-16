# Step 11: Layout and the Pinned Footer

Branch: `standards-layout`

Brings both pages to the end state of `~/.claude/rules/design/sticky-footer.md`, on the v2 header from `~/.claude/rules/design/replicate-model-picker-mobile-header.md`. AI Timeline is the reference for the end state.

## Decisions this step reads

Decision 18a (the wrapper becomes `.main-content`), recorded in `docs/standards-cleanup/README.md` on 2026-10-16.

## Background

Step 0 of the footer rule passes in part. On 2026-10-16 both pages had this shape:

```
<body>
  <div class="wrap">                 1200px shell, padding 0 30px 90px
    <header class="site-header">     v2 header, inside the wrapper
    <div class="content">            920px reading column
      <header class="masthead">
      ... the registry, or <main class="method"> on Methodology ...
      <footer class="site-foot">     "Last updated: <date>"
    </div>
  </div>
  <div class="tip">                  the shared tooltip, outside the wrapper
  <div class="overlay">              the poster overlay, outside the wrapper
</body>
```

The header sits inside the wrapper, as the v2 layout wants, and its mobile values match the rule. Four things are missing:

- The wrapper is a plain block (`.wrap{position:relative;z-index:1;max-width:1200px;margin:0 auto;padding:0 30px 90px;}`), not a window-tall flex column, so a short page cannot pin its footer. Step 12's 404 page will be the short page.
- The footer sits inside `.content`, not as a sibling of the header and the page body.
- There is no `<main class="page-body">`. The home page has no `<main>` landmark at all, and Methodology's `<main class="method">` is nested inside `.content`.
- The 90px of bottom padding on `.wrap` (`0 20px 90px` at 800px and below) is the gap below the footer.

The `.tip` and `.overlay` elements are fixed-position overlays outside the wrapper, so they take no part in the flex column.

## The changes

1. Rename `.wrap` to `.main-content` in both pages and every stylesheet (decision 18a).
2. Restructure both pages to:

   ```
   <div class="main-content">
     <header class="site-header">...</header>
     <main class="page-body">
       <div class="content"> masthead, registry or method sections </div>
     </main>
     <footer class="site-foot">Last updated: <date></footer>
   </div>
   ```

   On Methodology, `<main class="method">` becomes `<div class="method">` since a page has one `<main>`.
3. In `base.css`, make the wrapper a flex column with `min-height: 100vh`, give `.page-body` `flex: 1 0 auto`, and give `.site-foot` the 920px column (`max-width: 920px; margin-left: auto; margin-right: auto; width: 100%`) so it keeps its width now that it has left `.content`. Move the 90px bottom gap off the wrapper's padding onto the footer, in both the base rule and the 800px query.
4. Add the end state's margin strip in `base.css`, with this app's hidden markers (`[hidden]` since the page hides views and the count line with the attribute, plus `.hidden`):

   ```css
   .page-body > :nth-last-child(1 of :not(script, :empty, [hidden], .hidden)),
   .page-body > :nth-last-child(1 of :not(script, :empty, [hidden], .hidden)) > :last-child {
       margin-bottom: 0;
   }
   ```

   Then measure for the rule's four extra cases (an overlay mount, a hidden last block, an ID rule that outranks the strip, and absolutely positioned last children) and strip any that turn up.
5. Update `UPDATE.md`'s traps (the page shell, the 920px column) and `DEPLOY.md` where they name `.wrap`.
6. Add tests: both pages hold exactly one `<main class="page-body">`, the header, the page body, and the footer are siblings inside the wrapper, and there is no `.page-body-end`.

## The sample-file review gate

- HTML: `index.html` is the sample since its registry ends in views that toggle `hidden`, which the margin strip has to skip. Restructure it, run the measurements below, and stop for approval before `methodology/index.html`.
- CSS: `css/base.css` is the sample. `css/responsive.css` (the 800px query) follows.

## Done when

The rule's three proofs run with the step 7 harness:

- Gap. At 375, 768, 1024, and 1440 wide, in a short window so every page is long, `footer.getBoundingClientRect().top` minus the bottom of `main`'s last visible child with height equals the footer's top margin on every page and view, including an open poster.
- Screenshot diff against `main`. Every changed capture is shorter, never taller. You review and approve the images.
- Pinning. In a 1440 by 1400 window, the footer's bottom equals `innerHeight` (less any bottom margin the footer keeps) on Methodology, the shortest page until step 12 adds the 404.

Both suites pass, and the mobile menu still opens and closes at 375 pixels.

## Rollback

Revert the commits.

## Paste-ready prompt: build and stage

```
Run step 11 (layout and the pinned footer) of the Models Gone Wild
standards cleanup, following docs/standards-cleanup/11-layout.md exactly.
Read docs/standards-cleanup/README.md, ~/.claude/rules/design/sticky-footer.md,
and ~/.claude/rules/design/replicate-model-picker-mobile-header.md first.
Use decisions 1 and 18 as recorded in the README, and stop if either is
blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Confirm step 10B is merged and live. Branch off an up-to-date main as
   standards-layout. Never work on main.
2. Run both suites and confirm they pass. Measure the current gap above the
   footer on every page at the four widths, as the before numbers.
3. Sample-file review gate (HTML and CSS): restructure index.html and
   css/base.css as the step file shows (wrapper renamed .main-content), run the
   gap measurement, the screenshot diff, and the pinning check, and give me
   clickable links to both files, the numbers, the changed screenshots,
   and the git diff command. STOP until I approve.
4. After I approve, restructure methodology/index.html, update
   css/responsive.css's 800px query, and look for the rule's four extra
   margin cases.
5. Update UPDATE.md and DEPLOY.md, and add the layout tests.
6. Run both suites, the CSP walk, the screenshot diff, the gap and pinning
   checks, and the comment style checker (0), gating on each exit code.
7. Commit, push, and deploy the branch to staging with the
   README command and run the staging health check.
8. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh and to try the menu on my phone, and STOP. Do
   not merge to main or touch production until I say so.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/11-layout.md, copied exactly.
```

## Paste-ready prompt: ship to production

Paste this once you have approved the step 11 screenshots and checked staging. It needs no edits.

```
Ship step 11 (layout and the pinned footer) of the Models Gone Wild
standards cleanup to production, following docs/standards-cleanup/11-layout.md
and the rules in docs/standards-cleanup/README.md. This is my go-ahead for
step 11 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-layout, gating on each exit code.
2. Merge standards-layout to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Remind me to hard-refresh the home page and Methodology and to try the
   menu on my phone.
5. Switch staging back to main with the README command.
6. Mark step 11 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main. Add Models Gone Wild to
   the list of finished apps in ~/.claude/rules/design/sticky-footer.md,
   with the merge commit.
7. Tell me the next step is step 12, whose prompt is at the bottom of
   docs/standards-cleanup/12-design-rules.md.
```
