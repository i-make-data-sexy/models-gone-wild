# ========================================================================
#   About This File
# ========================================================================

# Test that keeps every banner, comment, and docstring in the house
# format. It runs check_style.py from the annielytics-comment-style skill
# on the tracked files and fails on any issue it reports. The skill lives
# in the home folder, so a fresh clone or the cloud scout skips the test.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import subprocess
import sys

from pathlib import Path

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

REPO    = Path(__file__).resolve().parent.parent
CHECKER = Path.home() / ".claude" / "skills" / "annielytics-comment-style" / "scripts" / "check_style.py"



# ========================================================================
#   Comment Style
# ========================================================================

def test_check_style_reports_no_issues() -> None:
    """
    Checks check_style.py reports no issues in the repo, skipping when the skill is absent

    Args:
        None

    Returns:
        None
    """

    if not CHECKER.exists():
        pytest.skip("No annielytics-comment-style skill on this machine")

    result = subprocess.run(
        [sys.executable, "-I", str(CHECKER)],
        cwd            = REPO,
        capture_output = True,
        text           = True,
    )
    assert result.returncode == 0, result.stdout + result.stderr