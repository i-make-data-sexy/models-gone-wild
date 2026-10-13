#!/usr/bin/env python3
"""Checks every case's poster slug in index.html.

Each slug becomes a public URL, /poster/<slug>/, so every case needs
one, no two cases may share one, and each must be lowercase letters,
digits, and hyphens to match the nginx rewrite and posterFromUrl.
Exits 1 on any failure.

Usage:
  python3 scripts/check_slugs.py
"""
import os
import re
import sys

REPO    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


# ========================================================================
#   Checks
# ========================================================================

def read_cases() -> list:
    """
    Pulls each case's id and slug out of the CASES array

    Returns:
        list: (id, slug) tuples in array order, with slug None when missing
    """

    html = open(os.path.join(REPO, "index.html"), encoding="utf-8").read()
    js   = re.search(r"<script>(.*?)</script>", html, re.S).group(1)
    out  = []
    for cid in re.findall(r'\n    id:"(\w+)"', js):
        block = re.search(r'\{\s*id:"' + cid + r'".*?\n  \}', js, re.S).group(0)
        slug  = re.search(r'slug:"([^"]*)"', block)
        out.append((cid, slug.group(1) if slug else None))
    return out


def main():
    """
    Prints each slug with its verdict and exits 1 if any fails
    """

    cases  = read_cases()
    seen   = {}
    failed = False
    for cid, slug in cases:
        if slug is None:
            verdict = "MISSING"
        elif not SLUG_RE.match(slug):
            verdict = "BAD FORMAT, use lowercase letters, digits, and hyphens"
        elif slug in seen:
            verdict = f"DUPLICATE of {seen[slug]}"
        else:
            verdict = "OK"
        if slug:
            seen.setdefault(slug, cid)
        failed = failed or verdict != "OK"
        print(f"  {cid:10} {slug or '':28} {verdict}")
    print("slugs FAILED" if failed else "slugs OK")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
