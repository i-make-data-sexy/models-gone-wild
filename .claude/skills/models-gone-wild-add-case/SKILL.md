---
name: models-gone-wild-add-case
description: Research and propose a new case (a model escape, hack, or unauthorized intrusion by an AI agent) for the Models Gone Wild registry. Annie supplies a headline and a few links; this skill runs its own searches, reconstructs the escape and disclosure timeline, scores the case against the existing ones, stages a local preview, and returns a proposal with a TL;DR, score rationale, decisions, and a to-do list with links to test. Use when Annie shares a new AI escape or hack story for Models Gone Wild, says "add a case", "new exploit", "another model got out", or pastes links about an AI agent breaching a system.
---

# Models Gone Wild: Add a Case

Turns a headline and a few links into a sourced, scored, previewable case for the registry at `~/Dropbox/Annielytics/Code/Python/Models Gone Wild`. The skill does the research, then stops for Annie's approval before anything is committed or deployed.

`UPDATE.md` in the repo is the source of truth for the case schema, the length limits, the voice rules, the checks, and the deploy. This skill is the research and proposal layer on top of it. Where the two disagree on schema or deploy, `UPDATE.md` wins; the one deliberate difference is that this skill stages an uncommitted preview before approval, so the proposal can link to something testable.

## Inputs

- A headline or one-line summary.
- One or more links. Some will be paywalled (The Information, WSJ, Bloomberg). Say which ones could not be read rather than guessing at their contents.
- Optionally, an angle Annie wants the case to carry.

## Step 1: Load the registry

1. `cd` into the repo. Confirm `git status` is clean and `main` is up to date. Branch off main (`add-<id>`). Never work on main.
2. Read `UPDATE.md` in full. It has the schema table, the `disclosedBy` test, the escape-date rule, the charge range, and the voice rules, including never praising or grading a lab.
3. Print the current cases so every score is calibrated against them:

```bash
python3 - <<'PY'
import re
js=re.search(r'<script>(.*?)</script>', open('index.html').read(), re.S).group(1)
for cid in re.findall(r'id:"(\w+)"', js):
    b=re.search(r'\{\s*id:"'+cid+r'".*?\n  \}', js, re.S).group(0)
    g=lambda k:(re.search(k+r':"?([^",]*)',b) or [0,''])[1]
    print(f"{cid:9} {g('alias'):18} {g('lab'):11} order {g('order'):2} cls {g('cls')} cx {g('complexity'):2} harm {g('harm'):2}  {g('date')} -> {g('disclosed')}")
PY
```

## Step 2: Research

Read every link Annie gave. Then search independently. A case needs, at minimum:

- The primary source, if one exists: the lab's incident report, a researcher's write-up, or a government statement. News stories are secondary.
- At least three independent outlets, including one local to the victim when the victim is a government or a company outside the US.
- The lab's own statement, quoted verbatim.

Pin down each of these, and note the source for each:

| Fact | Why it matters |
|---|---|
| Escape date | `date`. The first known escape, never the announcement. Day-precise only when a source gives the day. |
| What was escaped | `escapedFrom`. The eval, sandbox, or harness. |
| What it reached, and what it did there | `charge`, `mo`, `lastSeen`, and the harm score. |
| What it did not do | `caution`. No patient data, nothing stolen, no zero-day, and so on. |
| Technique | The complexity score. Separate what was confirmed for this target from what was shown for a related target. |
| Who made it public first, and on what date | `disclosedBy` and `disclosed`. When two parties went public the same day, find a sentence that settles the order. |
| The disclosure chain | See below. |
| Links to existing cases | Same agent swarm, same eval partner, same review. |

### The disclosure chain

Annie wants the registry to show how long labs take to report these, so every case reconstructs the chain, not just the public date:

1. Escape.
2. When the lab says it found out.
3. When the lab told the victim, and how (a call, a letter, an email to a generic inbox).
4. Any contact between the lab and the victim in between where it was not raised.
5. When it became public, and who made it public.

Compute the gaps in days. The escape-to-public gap goes in `lag`. Steps 2 and 3 go in the `notice` field (see `UPDATE.md` for its three kinds: `told` with the lab-knew-to-victim-told gap, `found` when the victim caught it and went public first, `untold` when the lab never told the victim before it went public). Leave `notice` off when the sources do not state the dates; never estimate one. Step 4, and anything the notice line cannot carry, goes in `caution` as dated facts. Don't repeat in the caution what the notice row already says. Any judgment of the delay is quoted and attributed to a named person (a minister, a regulator, the victim). The page never grades a lab in its own voice, which is a rule from `UPDATE.md`, and attributing the criticism is how a case carries the reporting-delay point without breaking it.

### Conflicts

When outlets disagree on a fact, go to the primary source and record the conflict, whichever way it resolves. A search-result snippet is not a source; confirm against the page itself. Anything that cannot be sourced is flagged in the proposal, never filled in plausibly.

## Step 3: Place it in the registry

- New case, or an update to an existing one? A case linked to an existing swarm can still be its own case if the target and the disclosure are distinct. Recommend one and say why.
- `lab` must match an existing spelling exactly.
- `alias` is the model name only. If the model is unnamed and `Unnamed agent` is already taken, propose a `scatterLabel` that tells the two apart and flag it.
- Work out the new `order` and which existing cases shift.
- Run through the claims in `scripts/check_claims.py` (both `COMPUTABLE` and `REVIEW`) and note which ones the new case touches. Any new line that compares this case to the rest needs a new entry there.

## Step 4: Score

Score against the existing cases, not in the abstract. For each of `cls`, `complexity`, and `harm`, name the nearest existing case above and below and say why this one sits between them. Complexity scores the method, never the motive. Harm scores what was reached. If a score sits on the dashed divider at 5, say which quadrant it falls in and whether that is the intent.

## Step 5: Draft and stage

Write the full case object, including `whyComplexity` and `whyHarm`, then any `GLOSSARY` terms the prose introduces. Insert it into `CASES` on the branch, renumber `order`, and add any `REVIEW` or `COMPUTABLE` entries. Do NOT commit.

### Update the footer date

The `Last updated` line at the bottom of the page is edited by hand; nothing updates it. Set it to today's date in `Month D, YYYY` form, so the preview shows it:

```bash
grep -n "Last updated" index.html
sed -i '' "s/Last updated: [A-Za-z]* [0-9]*, [0-9]*/Last updated: $(date '+%B %-d, %Y')/" index.html
grep -n "Last updated" index.html
```

Confirm the grep shows the new date, and report the old and new dates in the proposal.

Run every check from `UPDATE.md` plus:

```bash
python3 scripts/check_charges.py
python3 scripts/check_dates.py
python3 scripts/check_claims.py
python3 scripts/check_overlaps.py --shot <scratchpad>/matrix.png
```

Fix what they report.

### No overlapping pixels on the Threat Matrix

`check_overlaps.py` is a hard gate. It renders the page in headless Chrome under every Class and Lab filter combination and measures the ink of every dot, dot label, quadrant label, and axis title. A new case can crowd a row, and a label the old layout placed cleanly can end up on a neighbour's dot. The run must exit 0 before the proposal goes out.

Then open the screenshot with the Read tool and look at it. The check measures boxes; your eyes catch a label that is technically clear but reads as belonging to the wrong dot.

When it reports an overlap:

- Never change a score to make room. `complexity` and `harm` are editorial judgments, and the layout serves them, not the other way round.
- Shorten a `scatterLabel` first, since that costs nothing.
- If the layout itself cannot place the label, fix `placeLabels()` or `jitterDots()` in `index.html` (for example, add a spot to `LABEL_SPOTS`), rerun, and say in the proposal what changed.
- The checker fails on the old layout code as well as the new one, so a change to the chart can be tested against both. Self-check the prose against `~/.claude/rules/editorial/annielytics-writing-rules.md`: no em or en dashes, no comma before because or since, punctuation outside closing quotes, no red-flag words in `caution` (notable, impressive, responsible, transparent, thorough, to their credit).

Serve the preview at the real subpath, in the background:

```bash
mkdir -p /tmp/mgw/tools && ln -sfn "$PWD" /tmp/mgw/tools/models-gone-wild
(cd /tmp/mgw && python3 -m http.server 8899)
```

## Step 6: The proposal

Reply in the terminal, in this order. Keep it tight; Annie skims.

1. TL;DR. Three or four sentences. What happened, the lag, and the recommended scores.
2. Scores. A three-row table: field, score, one-line rationale naming the neighbors.
3. The disclosure chain. Dated list with day counts.
4. The case object, as it sits in `index.html`.
5. What changed around it: new glossary terms, `order` shifts, new claim entries, checks run and their results, including the overlap check's view count and where each new label landed (for example, "below-right of its dot, since the row is full").
6. Conflicts and unsourced items. What was resolved and how, and what is still thin.
7. Decisions for Annie. Numbered questions with a recommendation for each. Ask them directly; do not bury a decision in a sentence.
8. To-do. A checklist of what Annie needs to do, each with a clickable link: the preview (`http://127.0.0.1:8899/tools/models-gone-wild/`), the specific things to look at there (the card, the poster, the dot on the Threat Matrix and its tooltip), the matrix screenshot path, and the two or three source links worth spot-checking. Link the Threat Matrix directly with `?view=matrix`.
9. Sources. Every URL relied on, as markdown links.

Then STOP. Nothing is committed until Annie approves.

## After approval

Apply her edits and rerun the checks. If the deploy falls on a later day than the draft, run the footer-date step again so `Last updated` matches the day it goes live. Commit, then deploy and verify exactly as `UPDATE.md` describes. Finish with the live URL: `https://www.annielytics.com/tools/models-gone-wild/`.
