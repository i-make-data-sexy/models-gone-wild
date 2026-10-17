# Step F6: Convert the Quotes

Branch: `standards-format-quotes`

The sixth formatting step. Read "Formatting comes first" in the README before anything else. The rule wants double quotes in Python, JavaScript, and HTML attributes, as AI Strategy now has them. This is not a whitespace change, so it has its own step and its own proof, the "Step 2: quote cleanup" section of `~/.claude/rules/formatting/code-formatting.md`.

## Decisions this step reads

- Decision 1a (staging), recorded 2026-10-16.
- Decision 27 (how a formatting step reaches production) and decision 28 (the pre-commit hook), recorded in the README. Stop if either is blank.

## Background

Counted on 2026-10-17, read only:

| Language | Single-quoted | To convert | To keep, and why |
|---|---|---|---|
| Python | 27 strings in 7 files | 0 | All 27. Each holds a double quote, mostly a pattern that matches the page's JavaScript (`id:"`, `date:"([^"]*)"`), so it would need escaping. |
| JavaScript, `index.html` outside `CASES` and `GLOSSARY` | About 330 | About 322 | About 8 that hold a double quote, mostly strings that build markup with double-quoted attributes. |
| JavaScript, `methodology/index.html` | About 9 | About 9 | None expected. |
| HTML attributes | 0 | 0 | None. |

The JavaScript counts come from a rough pattern, so the step starts by counting exactly with a tokenizer.

`CASES` and `GLOSSARY` are left exactly as they are. Step 9A moves them under decision 30, and `scripts/check_quotes.py` skips the single-quoted `aka:` field in `CASES` by matching it as written.

So this step converts JavaScript only. It confirms Python and HTML have nothing to convert and changes neither.

## The changes

1. Count every single-quoted string in the two inline scripts with a tokenizer, outside `CASES` and `GLOSSARY`, and list each one that must stay single with its reason.
2. Convert the rest to double quotes, one commit per page, the `index.html` block first. A string that holds a double quote stays single. So does any string a test or a check script matches as exact text, with its reason listed.

## The sample-file review gate

- JavaScript: The `index.html` block is the sample, holding nearly every string. Convert it and stop for approval before the Methodology block.
- HTML: The only change to either page is its script block, so `index.html` is the sample here too. Show its diff with the JavaScript sample.
- Python: No Python file changes.

## Proving it

- A token comparison of each block against `main`, treating `'x'` and `"x"` as the same string, finds no other change, and `node --check` passes on each block.
- `git diff main -- index.html` touches no line of `CASES` or `GLOSSARY`, and the five check scripts exit 0.
- Both suites pass with the same counts before every commit, `scripts/screenshot-diff/run.sh main standards-format-quotes` reports zero changed pixels, and `scripts/check_overlaps.py` reports no overlaps.
- `check_format.py` still exits 0 on both pages and both scratch blocks outside the data.

## Done when

Every JavaScript string outside `CASES` and `GLOSSARY` that can take double quotes has them, each kept single quote is on the list Annie approved, every proof above passes, and both suites pass with the same counts.

## Rollback

Revert the merge commit.

## Paste-ready prompt: build and stage

```
Run step F6 (convert the quotes) of the Models Gone Wild standards
cleanup, following docs/standards-cleanup/f6-quotes.md exactly. Read
docs/standards-cleanup/README.md first, starting with "Formatting comes
first", then the Quotes rule and the "Step 2: quote cleanup" section of
~/.claude/rules/formatting/code-formatting.md, and the quote notes in
~/.claude/formatting-tools/HANDOFF-prompt.md. Decisions 1, 27, and 28
apply; stop if 27 or 28 is blank.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

Follow the README's sample-file review gate exactly. The first .py, .js,
.css, and .html file you change or create is that filetype's sample, test
files included. Finish each sample, give me a clickable link, a short
summary, and the git diff command, and STOP until I approve it. Never skip
a stop because a filetype changes in only one file.

1. Confirm step F5 is merged and live (marked done in the README). Branch
   off an up-to-date main as standards-format-quotes. Never work on main.
2. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   and confirm both pass before any change. Record both counts. Count the
   single-quoted strings in both inline scripts with a tokenizer, outside
   CASES and GLOSSARY, and confirm the 27 Python strings each hold a double
   quote and no HTML attribute is single-quoted.
3. Sample-file review gate (JavaScript and HTML): convert the index.html
   block, leaving CASES and GLOSSARY byte for byte, and prove it with the
   token comparison, node --check, and git diff main -- index.html. Give
   me a clickable link, a short summary, the list of quotes kept with the
   reason for each, and the git diff command, then STOP until I approve.
   Carry any correction I ask for.
4. On approval, convert the methodology/index.html block in its own commit.
5. Prove it: the token comparison and node --check on both blocks, the
   five check scripts, both suites (same counts), the screenshot diff
   (zero changed pixels), check_overlaps.py, and check_format.py on both
   pages, each gated on its exit code.
6. Push, deploy the branch to staging with the README command, and run
   the staging health check.
7. Report what you verified and how, give me the staging links with a
   reminder to hard-refresh, and STOP. Do not merge to main or touch
   production until I say so. The one exception is decision 27b: then run
   the ship prompt below yourself once every check passes.

When you stop, end your report with the ship-to-production prompt from
the bottom of docs/standards-cleanup/f6-quotes.md, copied exactly, so I
can paste it.
```

## Paste-ready prompt: ship to production

Paste this once you are happy with the step F6 report. It needs no edits.

```
Ship step F6 (convert the quotes) of the Models Gone Wild standards cleanup
to production, following docs/standards-cleanup/f6-quotes.md and the rules
in docs/standards-cleanup/README.md. This is my go-ahead for step F6 only.

Repo root: /Users/anniecushing/Dropbox/Annielytics/Code/Python/Models Gone Wild

1. Run venv/bin/python3 -m pytest and venv/bin/python3 -m pytest -m browser
   on standards-format-quotes, gating on each exit code.
2. Merge standards-format-quotes to main and push.
3. Deploy main to production with the README command and run the production
   health check.
4. Remind me to hard-refresh (Command-Shift-R) the pages I check, and to
   open a poster and press Download poster.
5. Switch staging back to main with the README command.
6. Mark step F6 done in docs/standards-cleanup/README.md with today's date
   and the merge commit, commit, and push to main.
7. Give me https://www.annielytics.com/tools/models-gone-wild/ and
   https://www.annielytics.com/tools/models-gone-wild/poster/sol-hugging-face/
   to spot-check. Then tell me the next step is step F7, whose prompt is at
   the bottom of docs/standards-cleanup/f7-python-structure.md.
```
