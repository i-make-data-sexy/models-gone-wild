# UPDATE.md for Models Gone Wild

How to change the app after it is live. The companion to `DEPLOY.md`, which covers the first deploy and the nginx setup. Read that one only if the server config needs to change, which a content update never does.

Claude Code: read this entire file before editing. Never develop on main. Always branch. Propose before writing when the task involves facts or editorial judgment.

## The prompts

Paste one of these into a fresh Claude Code session opened in this repo. Fill in the bracketed parts and delete the rest.

### Adding a case

The most common update. This is the one to reach for when another model escapes.

```
Add a case to Models Gone Wild, following UPDATE.md in this repo exactly.

Working dir: ~/Dropbox/Annielytics/Code/Python/Models Gone Wild

New case:
  Model or alias:  [e.g. Sol, or the model name if there is no nickname yet]
  Lab:             [e.g. OpenAI]
  Disclosed:       [e.g. August 12, 2026]
  What happened:   [paste the reporting, a link, or your own notes]

Read UPDATE.md for the field schema, the length limits, and the voice rules.
Branch off up-to-date main first. Then propose the complete filled-in case
object, including your suggested cls, complexity, and harm with the reasoning for
each, and STOP for my approval before writing anything.

Do not invent facts. Every field has to trace to what I gave you. Flag
anything you cannot source rather than filling it in plausibly.

After I approve: make the edit, run the checks in UPDATE.md, update the
"Last updated" line in the footer, commit, push, and deploy. Give me the
live URL when it is done.
```

### Changing copy

For rewording anything the reader sees, including a case's charge, the masthead, or a label.

```
Change some copy in Models Gone Wild, following UPDATE.md in this repo.

Working dir: ~/Dropbox/Annielytics/Code/Python/Models Gone Wild

Change:
  [quote the current text] -> [what it should say]

Branch off up-to-date main. Check whether the old wording appears anywhere
else, since a phrase in one place is often referenced in another, and tell me
if it does. Run the checks in UPDATE.md, commit, push, and deploy.
```

### Changing design or behavior

For layout, color, the scatter, the poster, or anything structural.

```
Make a design change to Models Gone Wild, following UPDATE.md in this repo.

Working dir: ~/Dropbox/Annielytics/Code/Python/Models Gone Wild

Change:
  [describe what should look or behave differently]

Branch off up-to-date main. Everything lives in index.html, so tell me what
you plan to touch before you touch it. Watch for the traps listed in
UPDATE.md, especially relative paths and the poster overlay's stacking order.
Run the checks, show me a local preview, and STOP for my sign-off before
deploying.
```

## The case schema

Every case is one object in the `CASES` array near the top of the script block in `index.html`. There is a comment there marking where to append.

| Field | Where it shows | Constraints |
|---|---|---|
| `id` | Internal key. Also seeds the generated mugshot, so a new id draws a different face. | Short, lowercase, unique. |
| `alias` | The card title, the large name on the poster, and the scatter dot label. | The model name and nothing else (Sol, Spark, Kimi K3), never a descriptive nickname. This is the only name the card shows; the exact version lives on the poster. Long names crowd the dot label. |
| `source` | The newspaper icon on the card, linking to the story that broke the case. | `{outlet, url}`. Leave `url` empty and the icon is not rendered at all, so a case with no source degrades cleanly. |
| `lab` | The vertical spine down the left edge of the card, and an option in the Lab dropdown. | Must match an existing lab's spelling exactly, or you get a second option for the same lab. Keep it short; the spine is the card's height. |
| `org` | The line under the alias on the POSTER only. The card does not show it. | Format is `Lab · Model`. This is where the exact version is recorded, e.g. `OpenAI · GPT-5.6`. |
| `aka` | The a.k.a. line. | Optional flavor. |
| `date` | The timeline heading and the footer's "Disclosed". | Format is `Month D, YYYY`. |
| `order` | Timeline position, sorted ascending. Array position is ignored. | Next integer in sequence. |
| `cls` | The class badge and the dot color. | `3` severe, `2` confirmed intrusion, `1` evasion only. |
| `complexity` | Scatter x-axis, how involved the escape was as a technique. | `0` to `10`. An editorial judgment of ours. Score the method, never the motive. Nothing here should imply a lab or a model meant for this to happen, which is why the field is not called intent. |
| `harm` | Scatter y-axis, how much damage the escape could do. | `0` to `10`. An editorial judgment of ours, not a figure from the reporting. |
| `whyComplexity` | The Escape complexity justification in the datapoint tooltip. | REQUIRED. One or two sentences on why that score. |
| `whyHarm` | The Harm potential justification in the datapoint tooltip. | REQUIRED. One or two sentences on why that score. The plot looks like measured data and is not, so every point has to explain itself. |
| `charge` | The one-sentence summary on the card. | One sentence, 130 to 170 characters. See the note below the table. |
| `wantedFor` | The offense line. | Separate offenses with ` · `. |
| `mo` | The modus operandi bullets. | Array of about three strings. |
| `caution` | The red caution box. | The honest caveat, including what the model did not do. |
| `escapedFrom` | The rotated ESCAPED stamp. | About 14 characters. The stamp is small. |
| `lastSeen` | The poster footer. | About 20 characters, or the footer wraps to two lines. |

### Why `charge` has a character range

Every card on the timeline is the same height, and two separate things hold that true.

The CSS floors `.card-charge` at four lines, so a charge that comes in short cannot shrink its card below the ones beside it. That end is handled and asks nothing of the writer.

The other end is not automatic. A charge past roughly 177 characters wraps onto a fifth line at desktop width, and that card then stands taller than every other card on the page. No CSS can prevent that without truncating the sentence, so it is a writing constraint rather than a styling one.

Stay between 130 and 170 characters and both ends are safe. Above 170 there is no margin left for a later reword. Below 130 the floor is carrying the card rather than the sentence, so the card shows dead space under the text.

Count every charge before committing:

```bash
python3 scripts/check_charges.py
```

`escapedFrom` and `lastSeen` are a pair. The first is the sandbox or harness the model broke out of, and the second is where it actually ended up. Together they read as a from and to. Do not put the same value in both.

### The Threat Matrix explains itself

Three things on that chart carry a definition, offered on hover, tap, or keyboard focus.

Each axis label is marked with an info icon and explains how it is scored, including the plain admission that both scores are ours rather than a published figure. Each quadrant label explains what that corner means. Each datapoint explains its own coordinates from the case's `why` field.

The axis icons are positioned by measuring the label after layout, which is why `placeAxisIcons()` runs a second time once `document.fonts` settles. Measured before Oswald arrives, the label is measured in the fallback font, which is wider, and the icon lands past the end of the label.

Clicking a datapoint still opens its wanted poster. The tooltip explains the score and the `aria-label` announces the action, so the two do not contradict each other.

## What updates itself, and what does not

Adding a case updates most of the app automatically. The Lab dropdown's options are generated from the data, the scatter plots the dot from `complexity` and `harm`, the timeline sorts by `order`, the class badge and colors follow `cls`, and the "Showing N of N files" count recalculates. That count only appears while a filter is narrowing the list, so an unfiltered page shows nothing there.

Two things are manual. The footer's `Last updated: <date>` line has to be edited by hand, and the page `<title>` only changes if the app is renamed.

The Class dropdown is hard-coded in the markup rather than generated, since the three classes are fixed. A new class would mean a new `<option>`, a new `--classN` color, and a new `CLASS_LABEL` entry.

## The glossary

Security jargon gets a dotted underline and a definition on hover, tap, or keyboard focus. The terms live in the `GLOSSARY` object in the script block, not in the case data.

Add a term by adding one line to that object. Every case, present and future, picks it up. A term is wrapped on its FIRST appearance in each passage, so a definition is offered once rather than on every repetition, and matching ignores case while preserving whatever capitalization the prose used.

Do not add a term you cannot define accurately. An invented definition is worse than no underline.

## Voice

The full rules are in `~/.claude/rules/editorial/annielytics-writing-rules.md` and they apply here. The ones this app trips over most often follow.

No em-dashes or en-dashes anywhere. No comma before "because" or "since". Oxford commas throughout. No marketese, and no editorializing about how common or how missed something is.

Punctuation goes outside a closing quote. The quote mark sits closer to the word than the comma or period does, so it is `'hyper-focused', going to` and never `'hyper-focused,' going to`. This holds for single and double quotes alike here, since nothing on the page quotes speech that carries its own punctuation.

Never praise or defend a lab. This page is written with Claude, which Anthropic makes, so any admiring line about how a lab handled its disclosure reads as a conflict of interest the moment somebody asks what wrote the copy. That applies hardest to Anthropic and is safest applied to all four. A caution that said "Notable for the sheer scale of the self-audit that uncovered it" was cut for exactly this reason, along with "no malice" in the same sentence, which defends intent rather than describing behavior.

Say what a model did and did not do. Do not grade the lab's response, its transparency, or its motives. Words to treat as red flags in a `caution`: notable, impressive, commendable, responsible, transparent, thorough, to their credit.

Suggestive rather than directive for anything diagnostic. The `caution` field in particular should say what the model did and did not do, not deliver a verdict.

The quadrant labels on the scatter each name a kind of offender rather than an outcome. That rule is recorded in a comment above them. If a label is ever reworded, keep it an actor.

Nothing on the page tells the reader to tap anything. The controls say what they produce through their own tooltips, meaning "Wanted poster" on a card and "Open X's wanted poster" on a scatter point. Keep those concrete, and do not reintroduce a prose instruction to replace them.

## Checks before committing

Run all four from the repo root. The first three take seconds.

```bash
# 1. No leading-slash paths. Must print nothing. A path starting with a
#    slash resolves to the site root and 404s under /tools/models-gone-wild/.
#    Both files, since the stylesheet carries url() references too.
grep -nE '(href|src|action|url\()\s*=?\s*["'"'"']/[^/]' index.html css/styles.css

# 2. Script block still parses structurally, and every case is well formed.
python3 - <<'PY'
import re
js=re.search(r'<script>(.*?)</script>', open('index.html').read(), re.S).group(1)
ok = js.count('{')==js.count('}') and js.count('(')==js.count(')') and js.count('`')%2==0
print("balance:", "OK" if ok else "MISMATCH")
req={'id','alias','lab','org','date','order','cls','complexity','harm',
     'charge','wantedFor','mo','caution','escapedFrom','lastSeen'}
for cid in re.findall(r'id:"(\w+)"', js):
    blk=re.search(r'\{\s*id:"'+cid+r'".*?\n  \}', js, re.S).group(0)
    missing=req-{m for m in req if re.search(m+r'\s*:', blk)}
    print(f"  {cid:8} {'OK' if not missing else 'MISSING '+', '.join(sorted(missing))}")
PY

# 3. Poster footer still fits on one line for every case.
python3 - <<'PY'
import re
js=re.search(r'<script>(.*?)</script>', open('index.html').read(), re.S).group(1)
for cid in re.findall(r'id:"(\w+)"', js):
    blk=re.search(r'\{\s*id:"'+cid+r'".*?\n  \}', js, re.S).group(0)
    d="DISCLOSED · "+re.search(r'date:"([^"]*)"',blk).group(1).upper()
    s="LAST SEEN · "+re.search(r'lastSeen:"([^"]*)"',blk).group(1).upper()
    w=(len(d)+len(s))*6.4+12
    print(f"  {w:5.0f}px  {'one line' if w<392 else 'WRAPS, shorten lastSeen'}  {cid}")
PY
```

Then look at it. Serve the repo at the real subpath so relative paths are exercised the way production exercises them, rather than opening the file directly.

```bash
mkdir -p /tmp/mgw/tools && ln -sfn "$PWD" /tmp/mgw/tools/models-gone-wild
(cd /tmp/mgw && python3 -m http.server 8899)
# then open http://127.0.0.1:8899/tools/models-gone-wild/
```

Click through both tabs, open the new case's poster, and download it. There is no JavaScript engine available in this environment, so the structural check above cannot catch a runtime error. The browser is the only real test.

## Deploying the change

```bash
git add -A
git commit -m "..."
git checkout main && git merge <branch> --no-edit && git push origin main

ssh anniecushing@208.109.215.51 "cd ~/apps/models-gone-wild && git pull origin main"
```

That is the whole deploy. There is no service to restart, since nginx reads the file off disk on every request, and the page is served with no-cache headers so a reload shows the change immediately.

Nginx only needs touching if a new kind of file is added, for example a new image directory or a stylesheet. The asset rule currently matches `js/` and `img/` only. See `DEPLOY.md` for that block.

## Verifying the deploy

Verify at the origin. Cloudflare serves a challenge page to scripted requests for HTML, so a public `curl` returns 403 no matter what user-agent it sends, while static assets pass through. A public 403 on the page proves nothing.

```bash
ssh anniecushing@208.109.215.51 '
H="Host: www.annielytics.com"; B="https://127.0.0.1/tools/models-gone-wild"
curl -sk -H "$H" -o /dev/null -w "page: %{http_code}\n" "$B/"
curl -sk -H "$H" "$B/" | grep -o "<title>[^<]*</title>"
'
```

Then open `https://www.annielytics.com/tools/models-gone-wild/` in a browser, which is the only way past Cloudflare.

## Where things live

`index.html` carries the markup and the script, including the `CASES` array. `css/styles.css` carries every style; there is no inline `<style>` block and no inline `style` attribute worth keeping. `scripts/check_charges.py` reports charge lengths against the range above.

The stylesheet is linked relatively as `css/styles.css`. A leading slash would resolve to the site root and 404, which is what check 1 guards.

## Traps

Paths to local files are relative, never starting with a slash. The app is served at `/tools/models-gone-wild/`, so a leading slash resolves to the site root and 404s. Check 1 above catches this.

The poster overlay sits at `z-index: 50` and the page shell at `1`. Giving the site header a stacking context above 50 puts the black band on top of the open poster. If a `position` is ever added to `.site-header`, keep its `z-index` below 50.

The page shell is 1200px and the content column inside it is 920px. The header spans the wider one on purpose, matching AI Timeline. Widening `.content` widens the prose and the posters too.

The scatter gridlines step by 2.5 so the dashed quadrant divider at 5 lands on a gridline. Stepping by 2 puts the divider mid-cell and the grid reads as unevenly spaced.

Nginx blocks `.md`, `.txt`, `.json`, `.yml`, and `.lock` under this path, so this file and `DEPLOY.md` are not publicly readable. Adding a data file in one of those formats means it will 404 in production even though it works locally.

After a `systemctl reload nginx`, wait a couple of seconds before checking. Old workers drain on the previous config and can answer with stale results.

`.git` is marked Dropbox-ignored on this repo. Rebuilding or re-cloning it means re-applying `xattr -w com.dropbox.ignored 1 .git`, or Dropbox will sync the git internals and eventually fork them.
