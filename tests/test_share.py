# ========================================================================
#   About This File
# ========================================================================

# Canonical and share tag tests. Every row of the URL list gets a Link
# header naming its own permalink, or none, by the rule DEPLOY.md states;
# each view gets its own share card; the home and Methodology pages pass
# through the swap unchanged; every index.html address 301s to its
# folder; and the share cards were drawn from the current case data.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re
import struct
import subprocess

from collections.abc import Callable
from pathlib          import Path

# Third party
import pytest

# Local
from conftest import load_script, serve



# ========================================================================
#   Global Variables
# ========================================================================

REPO        = Path(__file__).resolve().parent.parent
SITE        = REPO / "public"
WWW         = "https://www.annielytics.com/tools/models-gone-wild"
share_cards = load_script("share_cards")

VIEWS = [
    ("threat-matrix", "Threat Matrix: Models Gone Wild", "share-threat-matrix.png"),
    ("lab-counts",    "Cases by Lab: Models Gone Wild",  "share-lab-counts.png"),
]

INDEX_REDIRECTS = [
    ("/index.html",                          "/tools/models-gone-wild/"),
    ("/methodology/index.html",              "/tools/models-gone-wild/methodology/"),
    ("/threat-matrix/index.html",            "/tools/models-gone-wild/threat-matrix/"),
    ("/poster/sol-hugging-face/index.html",  "/tools/models-gone-wild/poster/sol-hugging-face/"),
]

PAIRED_TAGS = [
    ("og:title",       "twitter:title"),
    ("og:description", "twitter:description"),
    ("og:image",       "twitter:image"),
    ("og:image:alt",   "twitter:image:alt"),
]



# ========================================================================
#   Helpers
# ========================================================================

def meta(body: str, name: str) -> str | None:
    """
    Reads one meta tag's content from a page, by its property or name

    Args:
        body (str): The page's HTML
        name (str): The property or name, such as "og:url" or "description"

    Returns:
        str | None: The tag's content, or None when the page has no such tag
    """

    found = re.search(rf'<meta (?:property|name)="{re.escape(name)}" content="([^"]*)">', body)

    return found.group(1) if found else None


def expected_link(path: str) -> str | None:
    """
    Works out the Link header a URL list row should carry, by the rule DEPLOY.md states

    Args:
        path (str): The full request path, query string included

    Returns:
        str | None: The canonical Link value, or None when the row should carry none
    """

    bare      = path.split("?", 1)[0]
    permalink = re.fullmatch(r"/tools/models-gone-wild(/(?:threat-matrix/|lab-counts/|methodology/|poster/[a-z0-9-]+/)?)", bare)

    return f'<{WWW}{permalink.group(1)}>; rel="canonical"' if permalink else None



# ========================================================================
#   Canonical Link
# ========================================================================

def test_every_url_list_row_carries_its_own_canonical(fetch: Callable[[str], tuple]) -> None:
    """
    Checks each URL list row's Link names its own permalink, and an asset, redirect, or 404 sends none

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server

    Returns:
        None
    """

    listed = subprocess.run(["bash", str(REPO / "scripts" / "url-list" / "urls.sh")], capture_output=True, text=True, check=True)
    paths  = listed.stdout.split()
    wrong  = []

    for path in paths:
        _, headers, _ = fetch(path[len(serve.PREFIX):])

        if headers.get("Link") != expected_link(path):
            wrong.append(f"{path}: {headers.get('Link')}")

    assert len(paths) > 100
    assert not wrong, "\n".join(wrong)


def test_poster_link_names_the_poster(fetch: Callable[[str], tuple], slug: str) -> None:
    """
    Checks every case's poster permalink names itself as canonical

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        slug (str): One case's poster slug

    Returns:
        None
    """

    _, headers, body = fetch(f"/poster/{slug}/")

    assert headers["Link"] == f'<{WWW}/poster/{slug}/>; rel="canonical"'
    assert meta(body, "og:url") == f"{WWW}/poster/{slug}/"


@pytest.mark.parametrize("path, location", INDEX_REDIRECTS)
def test_index_html_redirects_to_its_folder(fetch: Callable[[str], tuple], path: str, location: str) -> None:
    """
    Checks an index.html address gets a 301 to its folder, with no Link

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        path (str): The index.html path under the prefix
        location (str): Where the redirect should point

    Returns:
        None
    """

    status, headers, _ = fetch(path)

    assert (status, headers["Location"]) == (301, location)
    assert "Link" not in headers



# ========================================================================
#   Share Tags
# ========================================================================

@pytest.mark.parametrize("view, title, image", VIEWS)
def test_view_gets_its_own_card(fetch: Callable[[str], tuple], view: str, title: str, image: str) -> None:
    """
    Checks a view's page carries its own title, descriptions, URL, and card

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        view (str): The view's permalink slug
        title (str): The view's share title
        image (str): The view's card file name

    Returns:
        None
    """

    home             = (SITE / "index.html").read_text(encoding="utf-8")
    _, _, body       = fetch(f"/{view}/")
    image_url        = meta(body, "og:image") or ""

    assert meta(body, "og:title") == title
    assert meta(body, "og:url") == f"{WWW}/{view}/"
    assert image_url.startswith(f"{WWW}/img/{image}?v=")
    assert (SITE / "img" / image).is_file()

    for name in ("description", "og:description", "og:image:alt"):
        assert meta(body, name) not in (None, meta(home, name))


@pytest.mark.parametrize("path, page", [("/", "index.html"), ("/methodology/", "methodology/index.html")])
def test_page_passes_through_unchanged(fetch: Callable[[str], tuple], path: str, page: str) -> None:
    """
    Checks the home and Methodology pages are served exactly as they sit on disk

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        path (str): The page's path under the prefix
        page (str): The page's file under public/

    Returns:
        None
    """

    _, _, body = fetch(path)
    assert body == (SITE / page).read_text(encoding="utf-8")


def test_every_swap_finds_a_home_page_tag() -> None:
    """
    Checks each search string in the share snippet appears in index.html, so no swap silently stops

    Args:
        None

    Returns:
        None
    """

    home     = (SITE / "index.html").read_text(encoding="utf-8")
    _, swaps = serve.read_share()

    assert len(swaps) == 6
    assert all(search in home for search, _ in swaps), [search for search, _ in swaps if search not in home]


@pytest.mark.parametrize("path", ["/", "/threat-matrix/", "/lab-counts/", "/methodology/"])
def test_twitter_tags_mirror_open_graph(fetch: Callable[[str], tuple], path: str) -> None:
    """
    Checks each Twitter tag repeats its Open Graph twin on every page and view

    Args:
        fetch (Callable[[str], tuple]): Requests a path on the preview server
        path (str): The page's path under the prefix

    Returns:
        None
    """

    _, _, body = fetch(path)

    for og, twitter in PAIRED_TAGS:
        assert meta(body, og) is not None
        assert meta(body, og) == meta(body, twitter), og


def test_404_page_has_no_canonical_or_share_tags() -> None:
    """
    Checks the 404 page names no canonical and carries no description or share tags

    Args:
        None

    Returns:
        None
    """

    page = (SITE / "404.html").read_text(encoding="utf-8")

    assert not re.search(r'rel="canonical"|property="og:|name="twitter:|name="description"', page)


@pytest.mark.parametrize("snippet", ["models-gone-wild-share.conf", "models-gone-wild-share-staging.conf"])
def test_deploy_page_blocks_include_the_share_snippet(snippet: str) -> None:
    """
    Checks each server's page block in DEPLOY.md includes its share snippet

    Args:
        snippet (str): The snippet's file name under /etc/nginx/snippets/

    Returns:
        None
    """

    deploy = (REPO / "DEPLOY.md").read_text(encoding="utf-8")
    assert deploy.count(f"include snippets/{snippet};") == 1



# ========================================================================
#   Share Cards
# ========================================================================

@pytest.mark.parametrize("card", ["share.png", "share-threat-matrix.png", "share-lab-counts.png"])
def test_card_was_drawn_from_the_current_cases(card: str) -> None:
    """
    Checks each card carries the current data version, so a new or rescored case fails until the cards are redrawn

    Args:
        card (str): The card's file name in public/img/

    Returns:
        None
    """

    path = SITE / "img" / card
    data = path.read_bytes()

    assert share_cards.png_version(path) == share_cards.card_data_version(), "Run venv/bin/python3 scripts/share_cards.py"
    assert struct.unpack(">II", data[16:24]) == (1200, 630)
    assert len(data) < 5 * 1024 * 1024


@pytest.mark.parametrize("page", ["index.html", "methodology/index.html"])
def test_page_names_the_current_card_version(page: str) -> None:
    """
    Checks every share image URL in a page carries the current data version

    Args:
        page (str): The page's file under public/

    Returns:
        None
    """

    text     = (SITE / page).read_text(encoding="utf-8")
    versions = re.findall(r"img/share[\w-]*\.png\?v=(\w+)", text)

    assert len(versions) == 2
    assert set(versions) == {share_cards.card_data_version()}, "Run venv/bin/python3 scripts/share_cards.py"