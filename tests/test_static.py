# ========================================================================
#   About This File
# ========================================================================

# Tests that read the shipped files directly, with no server. They turn
# the copy-and-paste checks in UPDATE.md into tests, keep the two copies
# of the site header in step, keep every HTML comment but the About This
# File section out of the pages, and guard against a POST form or a
# cookie ever appearing, which would make the audit's CSRF finding real.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re

from pathlib import Path

# Third party
import pytest

# Local
from conftest import cases



# ========================================================================
#   Global Variables
# ========================================================================

REPO        = Path(__file__).resolve().parent.parent
PAGES       = [REPO / "index.html", REPO / "methodology" / "index.html"]

SLASH_FILES = PAGES + [REPO / "css" / "styles.css"]
LEADING_RE  = re.compile(r"""(href|src|action|url\()\s*=?\s*["']/[^/]""")

REQUIRED    = {
    "id", "slug", "alias", "lab", "org", "date", "disclosed", "lag", "order", "cls",
    "complexity", "harm", "charge", "wantedFor", "mo", "caution",
    "escapedFrom", "lastSeen", "disclosedBy", "outcome", "reach",
}

FOOTER_MAX = 392
BALANCED   = sorted(path.name for path in (REPO / "js").glob("*.js"))



# ========================================================================
#   Helpers
# ========================================================================

def read(path: Path) -> str:
    """
    Reads a file as UTF-8 text

    Args:
        path (Path): The file to read

    Returns:
        str: The file's contents
    """

    return path.read_text(encoding="utf-8")


def site_header(path: Path) -> str:
    """
    Pulls the site header block out of a page

    Args:
        path (Path): The page to read

    Returns:
        str: The <header class="site-header"> block, tags included
    """

    return re.search(r'<header class="site-header">.*?</header>', read(path), re.S).group(0)



# ========================================================================
#   Paths
# ========================================================================

def test_no_leading_slash_paths() -> None:
    """
    Checks no page or stylesheet links a local file from the site root

    Args:
        None

    Returns:
        None
    """

    hits = [
        f"{path.relative_to(REPO)}:{number}: {line.strip()}"
        for path in SLASH_FILES
        for number, line in enumerate(read(path).splitlines(), 1)
        if LEADING_RE.search(line)
    ]
    assert not hits, "\n".join(hits)



# ========================================================================
#   Case Data
# ========================================================================

def test_index_html_holds_no_case_data() -> None:
    """
    Checks the case data stays out of index.html, in js/cases.js and js/glossary.js

    Args:
        None

    Returns:
        None
    """

    page = read(REPO / "index.html")
    assert "CASES = [" not in page
    assert "GLOSSARY = {" not in page


@pytest.mark.parametrize("name", BALANCED)
def test_scripts_balance(name: str) -> None:
    """
    Checks a script's braces, parentheses, and backticks pair up

    Args:
        name (str): The name of one of the app's files in js/

    Returns:
        None
    """

    js = read(REPO / "js" / name)
    assert js.count("{") == js.count("}")
    assert js.count("(") == js.count(")")
    assert js.count("`") % 2 == 0


def test_every_case_has_required_fields() -> None:
    """
    Checks every case carries each field the page and the poster read

    Args:
        None

    Returns:
        None
    """

    blocks  = cases.case_blocks(cases.load_cases_js())
    missing = {
        cid: sorted(field for field in REQUIRED if not re.search(field + r"\s*:", block))
        for cid, block in blocks.items()
    }
    assert blocks
    assert not {cid: fields for cid, fields in missing.items() if fields}


def test_poster_footer_fits_one_line() -> None:
    """
    Checks every case's poster footer fits on one line

    Args:
        None

    Returns:
        None
    """

    too_wide = {}

    for cid, block in cases.case_blocks(cases.load_cases_js()).items():
        est   = " (EST.)" if re.search(r"estimated\s*:\s*true", block) else ""
        date  = "ESCAPED · " + cases.text_field(block, "date").upper() + est
        seen  = "LAST SEEN · " + cases.text_field(block, "lastSeen").upper()
        width = (len(date) + len(seen)) * 6.4 + 12

        if width >= FOOTER_MAX:
            too_wide[cid] = round(width)

    assert not too_wide, f"Shorten lastSeen for {too_wide}"



# ========================================================================
#   Shared Markup
# ========================================================================

def test_site_headers_match() -> None:
    """
    Checks the Methodology page's site header matches the home page's

    Args:
        None

    Returns:
        None
    """

    home        = site_header(PAGES[0])
    methodology = site_header(PAGES[1]).replace('src="../img/', 'src="img/')
    assert home == methodology


@pytest.mark.parametrize("path", PAGES, ids=lambda path: str(path.relative_to(REPO)))
def test_only_about_comments(path: Path) -> None:
    """
    Checks a page's only HTML comments are its About This File section

    Args:
        path (Path): The page to read

    Returns:
        None
    """

    about, _, rest = read(path).partition("<html")
    assert "About This File" in about
    assert re.sub(r"<!--.*?-->", "", about, flags=re.S).split() == ["<!DOCTYPE", "html>"]
    assert "<!--" not in rest



# ========================================================================
#   CSRF Guard
# ========================================================================

def test_no_post_forms() -> None:
    """
    Checks no page carries a form that posts

    Args:
        None

    Returns:
        None
    """

    for path in PAGES:
        forms = re.findall(r"<form\b[^>]*>", read(path), re.I)
        assert not [form for form in forms if re.search(r"method\s*=\s*[\"']?post", form, re.I)]


def test_no_cookies_set() -> None:
    """
    Checks no script sets a cookie

    Args:
        None

    Returns:
        None
    """

    for path in PAGES:
        assert not re.search(r"document\.cookie\s*=(?!=)", read(path))