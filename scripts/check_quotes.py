#!/usr/bin/env python3
"""Lists every single-quoted span in the case copy, so a quotation never
ships in single quotes.

Somebody's words, partial or full, take double quotes. Single quotes are
only for a word or two used as a label or term. A span of three words or
more is almost always a quotation, so it fails the run. One or two words
is printed for a reader to judge, since 'hyper-focused' can be a term.
"""
import re
import sys

MAX_WORDS = 2

html = open("index.html").read()
start = html.index("const CASES = [")
cases = html[start:html.index("\n];", start)]
first_line = html.count("\n", 0, start) + 1

# An opening quote follows a space or a parenthesis and starts a word, so
# apostrophes inside words (VAHI's) never open a span. The aka field is a
# single-quoted string in the script, not a quotation, so it is skipped.
OPEN = re.compile(r"(?<=[\s(])'(?=[A-Za-z])")

failed = 0
for m in OPEN.finditer(cases):
    if cases[m.start() - 4:m.start()] == "aka:":
        continue
    end = cases.find("'", m.end())
    while end != -1 and end + 1 < len(cases) and cases[end + 1].isalpha():
        end = cases.find("'", end + 1)
    span = cases[m.start():end + 1]
    words = len(span.strip("'").split())
    line = first_line + cases.count("\n", 0, m.start())
    if words > MAX_WORDS:
        failed += 1
        print(f"  QUOTE  line {line}  {span}  ({words} words, use double quotes)")
    else:
        print(f"  READ   line {line}  {span}  (a term is fine, a quotation is not)")

print("quotes OK" if not failed else f"{failed} quotation(s) in single quotes")
sys.exit(1 if failed else 0)