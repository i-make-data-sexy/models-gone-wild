# ========================================================================
#   About This File
# ========================================================================

"""
Checks every case draws its own model's mugshot.

Each case draws the face in FACES in public/js/mugshot.js keyed by its
id, or by its face field when it is a repeat offender of a model with an
earlier case. A case with neither draws the shared default face, which
would put one face on two different models, so that fails. A face shared
by cases from different labs cannot be one model, so that fails too.
Every shared face is printed for a person to confirm it is one model.
Exits 1 on any failure.

Usage:
    python3 scripts/check_mugshots.py
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re
import sys

from pathlib import Path

# Local
from cases import case_blocks, load_cases_js, text_field



# ========================================================================
#   Global Variables
# ========================================================================

MUGSHOT_JS = Path(__file__).resolve().parent.parent / "public" / "js" / "mugshot.js"



# ========================================================================
#   Checks
# ========================================================================

def face_keys() -> set:
    """
    Reads the face names defined in FACES, leaving out the default face

    Args:
        None

    Returns:
        set: Each face name in FACES other than _default
    """

    js    = MUGSHOT_JS.read_text(encoding="utf-8")
    block = re.search(r"\nconst FACES = \{\n(.*?)\n\};", js, re.S).group(1)

    return {key for key in re.findall(r"^    (\w+):\s*\{", block, re.M) if key != "_default"}


def read_cases() -> list:
    """
    Pulls each case's id, face, lab, and model line out of the CASES array

    Args:
        None

    Returns:
        list: (id, face, lab, org) tuples in array order, with face the id when unset
    """

    rows = []

    for cid, block in case_blocks(load_cases_js()).items():
        rows.append((cid, text_field(block, "face") or cid, text_field(block, "lab"), text_field(block, "org")))

    return rows


def main() -> int:
    """
    Prints each case's face with its verdict, then every shared face

    Args:
        None

    Returns:
        int: 1 when any case fails, 0 otherwise
    """

    faces  = face_keys()
    cases  = read_cases()
    shared = {}
    failed = False

    for cid, face, lab, org in cases:
        shared.setdefault(face, []).append((cid, lab, org))

    for cid, face, lab, org in cases:
        labs = {other_lab for _, other_lab, _ in shared[face]}

        if face not in faces:
            verdict = "NO FACE, draws the default; add one to FACES or name a repeat offender's face"
        elif len(labs) > 1:
            verdict = "SHARED ACROSS LABS, so not one model"
        else:
            verdict = "OK"

        failed = failed or verdict != "OK"
        print(f"  {cid:10} {face:10} {verdict}")

    for face, users in shared.items():
        if len(users) > 1:
            print(f"  repeat offender {face}: " + "; ".join(f"{cid} ({org})" for cid, _, org in users))

    print("mugshots FAILED" if failed else "mugshots OK")

    return 1 if failed else 0



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    sys.exit(main())