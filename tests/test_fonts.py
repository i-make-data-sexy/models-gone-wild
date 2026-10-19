# ========================================================================
#   About This File
# ========================================================================

# Tests that keep the fonts served from the app. No page, stylesheet, or
# script nginx serves may name a Google Fonts host, since Cloudflare's APO
# would rewrite the link into an inline <style> a policy blocks, and every
# url() in css/fonts.css must name a file in fonts/.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re
import subprocess

from pathlib import Path

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

REPO   = Path(__file__).resolve().parent.parent
SERVED = subprocess.run(
    ["git", "ls-files", "*.html", "css/*.css", "js/*.js"],
    cwd            = REPO,
    capture_output = True,
    text           = True,
    check          = True,
).stdout.split()



# ========================================================================
#   Google Fonts Hosts
# ========================================================================

@pytest.mark.parametrize("name", SERVED)
def test_no_google_fonts_hosts(name: str) -> None:
    """
    Checks a served page, stylesheet, or script names neither Google Fonts host

    Args:
        name (str): The file's path from the repo root

    Returns:
        None
    """

    text = (REPO / name).read_text(encoding="utf-8")
    assert "fonts.googleapis.com" not in text
    assert "fonts.gstatic.com" not in text



# ========================================================================
#   Font Files
# ========================================================================

def test_every_font_url_names_a_file() -> None:
    """
    Checks every url() in css/fonts.css names a file that exists

    Args:
        None

    Returns:
        None
    """

    sheet = REPO / "css" / "fonts.css"
    urls  = re.findall(r"url\(([^)]+)\)", sheet.read_text(encoding="utf-8"))
    assert urls
    assert not [url for url in urls if not (sheet.parent / url).resolve().is_file()]