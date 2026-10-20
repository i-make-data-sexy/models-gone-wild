# ========================================================================
#   About This File
# ========================================================================

"""
Checks every case's poster slug in public/js/cases.js.

Each slug becomes a public URL, /poster/<slug>/, so every case needs
one, no two cases may share one, and each must be lowercase letters,
digits, and hyphens to match the nginx rewrite and posterFromUrl.
Exits 1 on any failure.

Usage:
    python3 scripts/check_slugs.py
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re
import sys

# Local
from cases import case_blocks, load_cases_js, text_field



# ========================================================================
#   Checks
# ========================================================================

def read_cases() -> list:
    """
    Pulls each case's id and slug out of the CASES array

    Args:
        None

    Returns:
        list: (id, slug) tuples in array order, with slug None when missing
    """

    return [(cid, text_field(block, "slug") or None) for cid, block in case_blocks(load_cases_js()).items()]


def main() -> int:
    """
    Prints each slug with its verdict

    Args:
        None

    Returns:
        int: 1 when any slug fails, 0 otherwise
    """

    slug_re = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    seen    = {}
    failed  = False

    for cid, slug in read_cases():
        if slug is None:
            verdict = "MISSING"
        elif not slug_re.match(slug):
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

    return 1 if failed else 0



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    sys.exit(main())