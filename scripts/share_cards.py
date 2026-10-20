# ========================================================================
#   About This File
# ========================================================================

"""
Redraws the three share cards from the live case data.

Opens scripts/share-cards/cards.html in Chrome, screenshots each 1200 by
630 card into public/img/, and stamps each PNG with the data version, a
short hash of what the chart cards draw. The same version goes on every
share image URL in both pages, as ?v=, so a redrawn card gets a new URL
past the 30-day image cache. tests/test_share.py fails when the cases
change and the cards were not redrawn.

Usage:
    venv/bin/python3 scripts/share_cards.py
"""



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import hashlib
import json
import re
import struct
import zlib

from pathlib import Path

# Third party
from playwright.sync_api import sync_playwright

# Local
from cases import case_blocks, load_cases_js, number_field, text_field



# ========================================================================
#   Global Variables
# ========================================================================

REPO  = Path(__file__).resolve().parent.parent
CARDS = {
    "lineup":        REPO / "public" / "img" / "share.png",
    "threat-matrix": REPO / "public" / "img" / "share-threat-matrix.png",
    "lab-counts":    REPO / "public" / "img" / "share-lab-counts.png",
}
KEY   = b"mgw-data"



# ========================================================================
#   Data Version
# ========================================================================

def card_data_version() -> str:
    """
    Hashes the case fields the chart cards draw

    Args:
        None

    Returns:
        str: The first eight hex digits of the hash
    """

    rows = []

    for cid, block in case_blocks(load_cases_js()).items():
        kind = re.search(r'disclosedBy:\s*\{[^}]*kind:\s*"(\w+)"', block).group(1)
        rows.append([cid, text_field(block, "lab"), number_field(block, "order"),
                     number_field(block, "complexity"), number_field(block, "harm"), kind])

    return hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()[:8]



# ========================================================================
#   PNG Stamp
# ========================================================================

def stamp_png(path: Path, version: str) -> None:
    """
    Writes the data version into a PNG as a text chunk, just before its end

    Args:
        path (Path): The PNG to stamp
        version (str): The data version

    Returns:
        None
    """

    data  = path.read_bytes()
    body  = KEY + b"\x00" + version.encode()
    chunk = struct.pack(">I", len(body)) + b"tEXt" + body + struct.pack(">I", zlib.crc32(b"tEXt" + body))
    end   = data.rindex(b"IEND") - 4

    path.write_bytes(data[:end] + chunk + data[end:])


def png_version(path: Path) -> str | None:
    """
    Reads the data version stamp_png wrote into a PNG

    Args:
        path (Path): The PNG to read

    Returns:
        str | None: The version, or None when the PNG carries no stamp
    """

    found = re.search(rb"tEXt" + KEY + rb"\x00(\w+)", path.read_bytes())

    return found.group(1).decode() if found else None



# ========================================================================
#   Drawing
# ========================================================================

def draw_cards() -> None:
    """
    Screenshots each card in cards.html into its PNG in public/img/

    Args:
        None

    Returns:
        None
    """

    page_file = REPO / "scripts" / "share-cards" / "cards.html"

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--allow-file-access-from-files"])
        page    = browser.new_page(viewport={"width": 1200, "height": 2000})
        errors  = []

        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(page_file.as_uri())
        page.wait_for_selector("body[data-ready='true']")

        for card, path in CARDS.items():
            page.locator(f"#{card}").screenshot(path=str(path))

        browser.close()

    if errors:
        raise SystemExit("cards.html raised: " + "; ".join(errors))


def update_pages(version: str) -> None:
    """
    Sets the ?v= on every share image URL in both pages to the data version

    Args:
        version (str): The data version

    Returns:
        None
    """

    pages = [REPO / "public" / "index.html", REPO / "public" / "methodology" / "index.html"]

    for page in pages:
        text = page.read_text(encoding="utf-8")
        page.write_text(re.sub(r"(img/share[\w-]*\.png\?v=)\w+", rf"\g<1>{version}", text), encoding="utf-8")



# ========================================================================
#   Command Line
# ========================================================================

def main() -> None:
    """
    Redraws the cards, stamps them, and points both pages at the new version

    Args:
        None

    Returns:
        None
    """

    version = card_data_version()

    draw_cards()

    for path in CARDS.values():
        stamp_png(path, version)

    update_pages(version)
    print(f"Drew {len(CARDS)} share cards at version {version}")



# ========================================================================
#   Entry Point
# ========================================================================

if __name__ == "__main__":
    main()