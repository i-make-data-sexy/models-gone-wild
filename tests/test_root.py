# ========================================================================
#   About This File
# ========================================================================

# Tests that keep the repo root to a known set of files and public/ to
# the kinds of file the site serves. Nginx serves all of public/ and
# nothing outside it, so a stray file there would be public. Also holds
# the home copy of the add-case skill to the repo's copy, which the cloud
# scout reads, so the two never drift apart.



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

REPO = Path(__file__).resolve().parent.parent



# ========================================================================
#   Root Files
# ========================================================================

def test_root_holds_only_allowed_files() -> None:
    """
    Checks every tracked file at the repo root is on the allowlist, ignoring folders

    Args:
        None

    Returns:
        None
    """

    allowed = {".gitignore", "pytest.ini", "requirements-dev.txt", "DEPLOY.md", "UPDATE.md"}

    result = subprocess.run(
        ["git", "ls-files"],
        cwd            = REPO,
        capture_output = True,
        text           = True,
        check          = True,
    )
    root_files = {path for path in result.stdout.splitlines() if "/" not in path}
    assert not root_files - allowed, f"Unexpected root files: {sorted(root_files - allowed)}"



# ========================================================================
#   Public Files
# ========================================================================

def test_public_holds_only_served_file_types() -> None:
    """
    Checks every tracked file in public/ is a page, stylesheet, script, font, or image

    Args:
        None

    Returns:
        None
    """

    served = {".html", ".css", ".js", ".woff2", ".png"}

    result = subprocess.run(
        ["git", "ls-files", "public"],
        cwd            = REPO,
        capture_output = True,
        text           = True,
        check          = True,
    )
    strays = sorted(path for path in result.stdout.splitlines() if Path(path).suffix not in served)
    assert result.stdout.strip(), "No tracked files in public/"
    assert not strays, f"Files in public/ the site does not serve: {strays}"



# ========================================================================
#   Add-Case Skill
# ========================================================================

def test_home_skill_matches_repo_skill() -> None:
    """
    Checks the home copy of the add-case skill matches the repo's, skipping when absent

    Args:
        None

    Returns:
        None
    """

    home_skill = Path.home() / ".claude" / "skills" / "models-gone-wild-add-case" / "SKILL.md"
    repo_skill = REPO / ".claude" / "skills" / "models-gone-wild-add-case" / "SKILL.md"

    if not home_skill.exists():
        pytest.skip("No home copy of the add-case skill on this machine")
    assert home_skill.read_bytes() == repo_skill.read_bytes()