#!/usr/bin/env python3
"""Reports each case's charge length against the range that keeps every
card the same height.

The CSS floors a charge at four lines, so anything short still fills its
card. The ceiling is the constraint: past about 177 characters a charge
wraps onto a fifth line at desktop width and that card grows taller than
the rest. 130 to 170 leaves margin at both ends.
"""
import re
import sys

LOW, HIGH = 130, 170

js = re.search(r"<script>(.*?)</script>", open("index.html").read(), re.S).group(1)
worst = 0
for cid in re.findall(r'id:"(\w+)"', js):
    blk = re.search(r'\{\s*id:"' + cid + r'".*?\n  \}', js, re.S).group(0)
    charge = re.search(r'charge:"([^"]*)"', blk).group(1)
    n = len(charge)
    if n > HIGH:
        note, bad = "TOO LONG, this card will grow a fifth line", 2
    elif n < LOW:
        note, bad = "short, this card will carry dead space", 1
    else:
        note, bad = "OK", 0
    worst = max(worst, bad)
    print(f"  {cid:8} {n:3} chars  {note}")

print("charges OK" if worst == 0 else "charges need attention")
sys.exit(1 if worst == 2 else 0)
