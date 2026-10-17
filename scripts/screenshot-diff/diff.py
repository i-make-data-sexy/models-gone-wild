# ========================================================================
#   About This File
# ========================================================================

"""
Compares two screenshot sets pixel for pixel.

Usage: diff.py <dir a> <dir b> <diff out dir>

Reports every image whose size or pixels differ, writes a red-highlight
image for each, and exits 1 when anything differs. A size change also
reports how many pixels taller or shorter the second capture is.
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import json
import shutil
import sys

from pathlib import Path

# Third party
from PIL import Image, ImageChops



# ========================================================================
#   Arguments
# ========================================================================

def parse_args() -> tuple:
    """
    Reads the two screenshot folders and the folder for highlight images

    Args:
        None

    Returns:
        tuple: The first folder, the second folder, and the output folder, each a Path
    """

    return Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])



# ========================================================================
#   Comparing Images
# ========================================================================

def prepare_output(out: Path) -> None:
    """
    Empties the output folder, creating it when it is missing

    Args:
        out (Path): The folder for highlight images

    Returns:
        None
    """

    if out.exists():
        shutil.rmtree(out)

    out.mkdir(parents=True)


def compare_images(a: Path, b: Path, out: Path) -> tuple:
    """
    Compares every image by name and saves a red-highlight copy of each that differs

    Args:
        a (Path): The first folder
        b (Path): The second folder
        out (Path): The folder for highlight images

    Returns:
        tuple: The sorted image names, and a list of (name, reason) for each that differs
    """

    names = sorted({p.name for p in a.glob("*.png")} | {p.name for p in b.glob("*.png")})
    bad   = []

    for n in names:
        pa, pb = a / n, b / n

        if not pa.exists() or not pb.exists():
            bad.append((n, "missing on one side"))
            continue

        ia, ib = Image.open(pa).convert("RGB"), Image.open(pb).convert("RGB")

        if ia.size != ib.size:
            delta = ib.size[1] - ia.size[1]
            bad.append((n, f"size {ia.size} vs {ib.size} ({delta:+d}px tall)"))
            continue

        d   = ImageChops.difference(ia, ib)
        box = d.getbbox()

        if box:
            mask  = d.convert("L").point(lambda v: 255 if v else 0)
            count = mask.histogram()[255]
            bad.append((n, f"{count} px differ in box {box}"))

            hl = ia.copy()
            hl.paste((255, 0, 0), mask=mask)
            hl.save(out / n)

    return names, bad



# ========================================================================
#   Comparing Notes
# ========================================================================

def read_notes(folder: Path) -> dict:
    """
    Reads a folder's capture notes, or an empty dict when it has none

    Args:
        folder (Path): A screenshot folder

    Returns:
        dict: The note for each page and width
    """

    path = folder / "_notes.json"

    return json.loads(path.read_text()) if path.exists() else {}



# ========================================================================
#   The Report
# ========================================================================

def main() -> None:
    """
    Prints every difference between the two screenshot sets and exits 1 when there is one

    Args:
        None

    Returns:
        None
    """

    a, b, out  = parse_args()

    prepare_output(out)

    names, bad = compare_images(a, b, out)
    na         = read_notes(a)
    nb         = read_notes(b)
    note_diffs = [k for k in set(na) | set(nb) if na.get(k, "").split(" ")[0] != nb.get(k, "").split(" ")[0]]
    errors     = [k for k, v in {**na, **nb}.items() if v.startswith("ERROR") or "NO-ACTION" in v]

    print(f"{len(names)} images compared, {len(bad)} differ")

    for n, why in bad:
        print("  DIFF", n, why)

    for k in sorted(note_diffs):
        print("  STATUS", k, na.get(k), "|", nb.get(k))

    for k in sorted(set(errors)):
        print("  CAPTURE-PROBLEM", k, na.get(k) or nb.get(k))

    sys.exit(1 if bad or note_diffs or errors else 0)



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    main()