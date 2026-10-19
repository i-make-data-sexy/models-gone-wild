# ========================================================================
#   About This File
# ========================================================================

# Route tests through the preview server. Each page and permalink a
# reader can land on returns 200 with its title, each asset loads from
# every path the browser requests it at, the redirects nginx sends are
# answered, and an unknown path is a 404.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
from collections.abc import Callable

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

HOME_TITLE        = "<title>Models Gone Wild: AI Containment Registry</title>"

ASSET_BASES       = ["/", "/threat-matrix/", "/poster/sol-hugging-face/"]
ASSETS            = ["css/styles.css", "js/cases.js", "js/glossary.js", "js/vendor/html2canvas.min.js", "img/annielytics-logo.png"]

REDIRECTS         = [
    ("",                 "/tools/models-gone-wild/"),
    ("/threat-matrix",   "/tools/models-gone-wild/threat-matrix/"),
    ("/?view=matrix",    "/tools/models-gone-wild/threat-matrix/"),
    ("/?view=labs",      "/tools/models-gone-wild/lab-counts/"),
]



# ========================================================================
#   Pages
# ========================================================================

@pytest.mark.parametrize("path", ["/", "/threat-matrix/", "/lab-counts/"])
def test_home_and_views_render(fetch: Callable, path: str) -> None:
    """
    Checks the home page and both view permalinks return 200 with the home title

    Args:
        fetch (Callable): Requests a path on the preview server
        path (str): The page's path under the prefix

    Returns:
        None
    """

    status, _, body = fetch(path)
    assert status == 200
    assert HOME_TITLE in body


def test_methodology_renders(fetch: Callable) -> None:
    """
    Checks the Methodology page returns 200 with its own title

    Args:
        fetch (Callable): Requests a path on the preview server

    Returns:
        None
    """

    title           = "<title>Methodology: Models Gone Wild</title>"
    status, _, body = fetch("/methodology/")

    assert status == 200
    assert title in body


def test_poster_permalink_renders(fetch: Callable, slug: str) -> None:
    """
    Checks every case's poster permalink returns 200 with the home title

    Args:
        fetch (Callable): Requests a path on the preview server
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
def test_asset_loads(fetch: Callable, base: str, asset: str) -> None:
    """
    Checks each asset loads from the home page, a view, and a poster permalink

    Args:
        fetch (Callable): Requests a path on the preview server
        base (str): The page path the browser resolves the asset against
        asset (str): The asset's relative path

    Returns:
        None
    """

    status, _, body = fetch(f"{base}{asset}")
    assert status == 200
    assert body



# ========================================================================
#   Redirects and 404
# ========================================================================

@pytest.mark.parametrize("path, location", REDIRECTS)
def test_redirect(fetch: Callable, path: str, location: str) -> None:
    """
    Checks an unslashed or old ?view= path gets a 301 to its permalink

    Args:
        fetch (Callable): Requests a path on the preview server
        path (str): The old path under the prefix
        location (str): Where the redirect should point

    Returns:
        None
    """

    status, headers, _ = fetch(path)
    assert status == 301
    assert headers["Location"] == location


def test_unknown_path_is_404(fetch: Callable) -> None:
    """
    Checks a path that matches no page returns 404

    Args:
        fetch (Callable): Requests a path on the preview server

    Returns:
        None
    """

    status, _, _ = fetch("/no-such-page/")
    assert status == 404