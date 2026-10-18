# ========================================================================
#   About This File
# ========================================================================

# Tests that hold the app's two dependency records true. Every line of
# requirements-dev.txt is an exact pin, and the vendored html2canvas file
# still matches the SHA-256 recorded in js/vendor/VENDORED.md.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import hashlib
import re

from pathlib import Path



# ========================================================================
#   Global Variables
# ========================================================================

REPO = Path(__file__).resolve().parent.parent



# ========================================================================
#   Dev Requirements
# ========================================================================

def test_dev_requirements_are_pinned() -> None:
    """
    Checks every line of requirements-dev.txt is a name==version pin

    Args:
        None

    Returns:
        None
    """

    pin_re = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*==[A-Za-z0-9.+!-]+$")
    text   = (REPO / "requirements-dev.txt").read_text(encoding="utf-8")
    lines  = [line.strip() for line in text.splitlines()]
    pins   = [line for line in lines if line and not line.startswith("#")]
    assert pins
    assert not [line for line in pins if not pin_re.match(line)]



# ========================================================================
#   Vendored Library
# ========================================================================

def test_html2canvas_matches_recorded_hash() -> None:
    """
    Checks js/vendor/html2canvas.min.js still hashes to the SHA-256 in VENDORED.md

    Args:
        None

    Returns:
        None
    """

    record   = (REPO / "js" / "vendor" / "VENDORED.md").read_text(encoding="utf-8")
    recorded = re.search(r"SHA-256: `([0-9a-f]{64})`", record).group(1)
    actual   = hashlib.sha256((REPO / "js" / "vendor" / "html2canvas.min.js").read_bytes()).hexdigest()
    assert actual == recorded