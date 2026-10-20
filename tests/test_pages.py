# ========================================================================
#   About This File
# ========================================================================

# Route tests through the preview server. Each page and permalink a
# reader can land on returns 200 with its title, each asset and every
# stylesheet a page links loads from every path the browser requests it
# at, the redirects nginx sends are answered, and an unknown path is a
# 404.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re
from collections.abc import Callable
from pathlib import Path
from urllib.parse import urljoin

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

SITE              = Path(__file__).resolve().parent.parent / "public"
HOME_TITLE        = "<title>Models Gone Wild: AI Containment Registry</title>"

ASSET_BASES       = ["/", "/threat-matrix/", "/poster/sol-hugging-face/"]
ASSETS            = ["js/cases.js", "js/glossary.js", "js/vendor/html2canvas.min.js", "img/annielytics-logo.png"]

REDIRECTS         = [
    ("",                 "/tools/models-gone-wild/"),
    ("/threat-matrix",   "/tools/models-gone-wild/threat-matrix/"),
    ("/?view=matrix",    "/tools/models-gone-wild/threat-matrix/"),
    ("/?view=labs",      "/tools/models-gone-wild/lab-counts/"),
]

STYLESHEET_PAGES  = [
    ("index.html",             "/"),
    ("index.html",             "/threat-matrix/"),
    ("index.html",             "/poster/sol-hugging-face/"),
    ("methodology/index.html", "/methodology/"),
]



# ========================================================================
#   Pages
# ========================================================================

@pytest.mark.parametrize("path", ["/", "/threat-matrix/", "/lab-counts/"])
def test_home_and_views_render(fetch: Callable[[str], tuple], path: str) -> None:
    """
    Checks the home page and both view permalinks return 200 with the home title

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        path (str): The page's path under the prefix

    Returns:
        None
    """

    status, _, body = fetch(path)
    assert status == 200
    assert HOME_TITLE in body


def test_methodology_renders(fetch: Callable[[str], tuple]) -> None:
    """
    Checks the Methodology page returns 200 with its own title

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server

    Returns:
        None
    """

    title           = "<title>Methodology: Models Gone Wild</title>"
    status, _, body = fetch("/methodology/")

    assert status == 200
    assert title in body


def test_poster_permalink_renders(fetch: Callable[[str], tuple], slug: str) -> None:
    """
    Checks every case's poster permalink returns 200 with the home title

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        slug (str): One case's poster slug

    Returns:
        None
    """

    status, _, body = fetch(f"/poster/{slug}/")
    assert status == 200
    assert HOME_TITLE in body



# ========================================================================
#   Assets
# ========================================================================

@pytest.mark.parametrize("base", ASSET_BASES)
@pytest.mark.parametrize("asset", ASSETS)
def test_asset_loads(fetch: Callable[[str], tuple], base: str, asset: str) -> None:
    """
    Checks each asset loads from the home page, a view, and a poster permalink

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        base (str): The page path the browser resolves the asset against
        asset (str): The asset's relative path

    Returns:
        None
    """

    status, _, body = fetch(f"{base}{asset}")
    assert status == 200
    assert body



# ========================================================================
#   Stylesheets
# ========================================================================

def linked_stylesheets(page: str) -> list:
    """
    Reads the local stylesheet links a page carries, in link order

    Args:
        page (str): The page's path from public/

    Returns:
        list: Each link's href as written
    """

    link = re.compile(r'<link rel="stylesheet" href="(?!https?:)([^"]+)">')

    return link.findall((SITE / page).read_text())


@pytest.mark.parametrize("page, base", STYLESHEET_PAGES)
def test_stylesheets_load(fetch: Callable[[str], tuple], page: str, base: str) -> None:
    """
    Checks every stylesheet a page links exists and loads where the page is served

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        page (str): The page's path from public/
        base (str): A path the page is served at, under the prefix

    Returns:
        None
    """

    hrefs = linked_stylesheets(page)
    assert hrefs

    for href in hrefs:
        assert ((SITE / page).parent / href).resolve().is_file(), href

        status, _, body = fetch(urljoin(base, href))
        assert status == 200, href
        assert body, href


def test_pages_link_every_stylesheet_in_one_order() -> None:
    """
    Checks both pages link every file in css/ and in the same order

    Args:
        None

    Returns:
        None
    """

    home        = [Path(href).name for href in linked_stylesheets("index.html")]
    methodology = [Path(href).name for href in linked_stylesheets("methodology/index.html")]

    assert home == methodology
    assert sorted(home) == sorted(path.name for path in (SITE / "css").glob("*.css"))



# ========================================================================
#   Redirects and 404
# ========================================================================

@pytest.mark.parametrize("path, location", REDIRECTS)
def test_redirect(fetch: Callable[[str], tuple], path: str, location: str) -> None:
    """
    Checks an unslashed or old ?view= path gets a 301 to its permalink

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        path (str): The old path under the prefix
        location (str): Where the redirect should point

    Returns:
        None
    """

    status, headers, _ = fetch(path)
    assert status == 301
    assert headers["Location"] == location


@pytest.mark.parametrize("path", ["/no-such-page/", "/case/files/no-such-page"])
def test_unknown_path_is_404(fetch: Callable[[str], tuple], path: str) -> None:
    """
    Checks a path that matches no page returns 404 with the app's own 404 page

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        path (str): The unknown path, one folder deep or several

    Returns:
        None
    """

    title           = "<title>File Not Found: Models Gone Wild</title>"
    status, _, body = fetch(path)

    assert status == 404
    assert title in body
    assert '<meta name="robots" content="noindex">' in body