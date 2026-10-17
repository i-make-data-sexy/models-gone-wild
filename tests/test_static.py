# ========================================================================
#   About This File
# ========================================================================

# Tests that read the shipped files directly, with no server. They turn
# the copy-and-paste checks in UPDATE.md into tests, keep the two copies
# of the site header in step, and guard against a POST form or a cookie
# ever appearing, which would make the audit's CSRF finding real.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re

from pathlib import Path



# ========================================================================
#   Global Variables
# ========================================================================

REPO  = Path(__file__).resolve().parent.parent
PAGES = [REPO / "index.html", REPO / "methodology" / "index.html"]

# The files a leading-slash path would break
SLASH_FILES = PAGES + [REPO / "css" / "styles.css"]
LEADING_RE  = re.compile(r"""(href|src|action|url\()\s*=?\s*["']/[^/]""")

# Fields every case needs
REQUIRED = {
    "id", "slug", "alias", "lab", "org", "date", "disclosed", "lag", "order", "cls",
    "complexity", "harm", "charge", "wantedFor", "mo", "caution",
    "escapedFrom", "lastSeen", "disclosedBy", "outcome", "reach",
}

# Poster footer width limit in pixels
FOOTER_MAX = 392



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


def script_block() -> str:
    """
    Pulls the inline script out of index.html the way the check scripts do

    Args:
        None

    Returns:
        str: The text between the first bare <script> tag and its close
    """

    return re.search(r"<script>(.*?)</script>", read(REPO / "index.html"), re.S).group(1)


def case_blocks() -> dict:
    """
    Splits the CASES array into one text block per case

    Args:
        None

    Returns:
        dict: Each case's id mapped to the source text of its object
    """

    js = script_block()
    return {
        cid: re.search(r'\{\s*id:"' + cid + r'".*?\n  \}', js, re.S).group(0)
        for cid in re.findall(r'id:"(\w+)"', js)
    }


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

def test_script_block_balances() -> None:
    """
    Checks the inline script's braces, parentheses, and backticks pair up

    Args:
        None

    Returns:
        None
    """

    js = script_block()
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

    blocks  = case_blocks()
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
    for cid, block in case_blocks().items():
        est   = " (EST.)" if re.search(r"estimated\s*:\s*true", block) else ""
        date  = "ESCAPED · " + re.search(r'date:"([^"]*)"', block).group(1).upper() + est
        seen  = "LAST SEEN · " + re.search(r'lastSeen:"([^"]*)"', block).group(1).upper()
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