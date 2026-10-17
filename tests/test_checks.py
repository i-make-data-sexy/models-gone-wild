# ========================================================================
#   About This File
# ========================================================================

# Runs each check script in scripts/ and expects exit 0. The scripts
# stay runnable on their own; this only puts them inside the suite.
# check_overlaps.py drives headless Chrome, so it runs under -m browser.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import subprocess

from pathlib import Path

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

REPO   = Path(__file__).resolve().parent.parent
PYTHON = REPO / "venv" / "bin" / "python3"

CHECKS = [
    "check_charges",
    "check_claims",
    "check_dates",
    "check_slugs",
    "check_quotes",
    pytest.param("check_overlaps", marks=pytest.mark.browser),
]



# ========================================================================
#   Check Scripts
# ========================================================================

@pytest.mark.parametrize("script", CHECKS)
def test_check_script_passes(script: str) -> None:
    """
    Checks one script in scripts/ exits 0, printing its output when it does not

    Args:
        script (str): The script's file name without .py

    Returns:
        None
    """

    result = subprocess.run(
        [str(PYTHON), f"scripts/{script}.py"],
        cwd            = REPO,
        capture_output = True,
        text           = True,
        timeout        = 600,
    )
    assert result.returncode == 0, result.stdout + result.stderr