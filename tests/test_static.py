# ========================================================================
#   About This File
# ========================================================================

# Tests that read the shipped files directly, with no server. They turn
# the copy-and-paste checks in UPDATE.md into tests, keep the two copies
# of the site header in step, keep the pages' HTML comments to the About
# section and the page banner above <html>, and guard against a POST form
# or a cookie ever appearing, which would make the audit's CSRF finding
# real.



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

REPO     = Path(__file__).resolve().parent.parent
PAGES    = [REPO / "index.html", REPO / "methodology" / "index.html", REPO / "404.html"]
BALANCED = sorted(path.name for path in (REPO / "js").glob("*.js"))



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

    slash_files = PAGES + sorted((REPO / "css").glob("*.css"))
    leading_re  = re.compile(r"""(href|src|action|url\()\s*=?\s*["']/[^/]""")
    allowed     = {("404.html", '<base href="/tools/models-gone-wild/">')}

    hits = [
        f"{path.relative_to(REPO)}:{number}: {line.strip()}"
        for path in slash_files
        for number, line in enumerate(read(path).splitlines(), 1)
        if leading_re.search(line) and (str(path.relative_to(REPO)), line.strip()) not in allowed
    ]
    assert not hits, "\n".join(hits)



# ========================================================================
#   Stylesheets
# ========================================================================

def test_no_stylesheet_over_800_lines() -> None:
    """
    Checks every file in css/ stays at or under 800 lines

    Args:
        None

    Returns:
        None
    """

    limit  = 800
    sheets = sorted((REPO / "css").glob("*.css"))
    long   = [f"{path.name}: {count} lines" for path in sheets if (count := len(read(path).splitlines())) > limit]

    assert sheets
    assert not long, "\n".join(long)



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

    required = {
        "id", "slug", "alias", "lab", "org", "date", "disclosed", "lag", "order", "cls",
        "complexity", "harm", "charge", "wantedFor", "mo", "caution",
        "escapedFrom", "lastSeen", "disclosedBy", "outcome", "reach",
    }

    blocks  = cases.case_blocks(cases.load_cases_js())
    missing = {
        cid: sorted(field for field in required if not re.search(field + r"\s*:", block))
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

    footer_max = 392
    too_wide   = {}

    for cid, block in cases.case_blocks(cases.load_cases_js()).items():
        est   = " (EST.)" if re.search(r"estimated\s*:\s*true", block) else ""
        date  = "ESCAPED · " + cases.text_field(block, "date").upper() + est
        seen  = "LAST SEEN · " + cases.text_field(block, "lastSeen").upper()
        width = (len(date) + len(seen)) * 6.4 + 12

        if width >= footer_max:
            too_wide[cid] = round(width)

    assert not too_wide, f"Shorten lastSeen for {too_wide}"



# ========================================================================
#   Shared Markup
# ========================================================================

def test_site_headers_match() -> None:
    """
    Checks the Methodology and 404 pages' site headers match the home page's

    Args:
        None

    Returns:
        None
    """

    home        = site_header(PAGES[0])
    methodology = site_header(PAGES[1]).replace('src="../img/', 'src="img/')
    not_found   = site_header(PAGES[2])
    assert home == methodology == not_found


@pytest.mark.parametrize("path", PAGES, ids=lambda path: str(path.relative_to(REPO)))
def test_comments_only_above_html(path: Path) -> None:
    """
    Checks a page opens with its About banner and holds no comment inside <html>

    Args:
        path (Path): The page to read

    Returns:
        None
    """

    top, _, rest = read(path).partition("<html")
    assert "About This File" in top.split("-->", 1)[0]
    assert re.sub(r"<!--.*?-->", "", top, flags=re.S).split() == ["<!DOCTYPE", "html>"]
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