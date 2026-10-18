# ========================================================================
#   About This File
# ========================================================================

"""
Reports each case's charge length against the range that keeps every
card the same height.

The CSS floors a charge at four lines, so anything short still fills its
card. The ceiling is the constraint: past about 177 characters a charge
wraps onto a fifth line at desktop width and that card grows taller than
the rest. 130 to 170 leaves margin at both ends.

Exit status is 1 when a charge is too long, 0 otherwise. A short charge
is reported but never fails the run.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import sys

# Local
from cases import case_blocks, load_cases_js, text_field



# ========================================================================
#   Main
# ========================================================================

def main() -> int:
    """
    Prints each case's charge length with its verdict

    Args:
        None

    Returns:
        int: 1 when any charge is too long, 0 otherwise
    """

    low, high = 130, 170
    worst     = 0

    for cid, block in case_blocks(load_cases_js()).items():
        n = len(text_field(block, "charge"))

        if n > high:
            note, bad = "TOO LONG, this card will grow a fifth line", 2
        elif n < low:
            note, bad = "short, this card will carry dead space", 1
        else:
            note, bad = "OK", 0

        worst = max(worst, bad)
        print(f"  {cid:8} {n:3} chars  {note}")

    print("charges OK" if worst == 0 else "charges need attention")

    return 1 if worst == 2 else 0



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    sys.exit(main())