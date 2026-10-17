# ========================================================================
#   About This File
# ========================================================================

# Browser tests in Playwright's Chromium against the preview server,
# run with -m browser. Requests to other hosts, the Google Fonts
# stylesheets, are answered with an empty stylesheet so the suite runs
# offline and the same way every time.
#
# The last test is the revert-and-fail proof for 8e726b4, which clamped
# the glossary bubbles inside the reading column. Without the clamp the
# bubbles spill past the column's edge and the test fails.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
from collections.abc import Callable, Iterator

# Third party
import pytest

sync_api = pytest.importorskip("playwright.sync_api")



# ========================================================================
#   Global Variables
# ========================================================================

pytestmark = pytest.mark.browser

DESKTOP = {"width": 1440, "height": 900}
PHONE   = {"width": 375,  "height": 812}

# Bubble clearance from the column edge
TIP_GAP = 10

# Each tab and its permalink
TABS = [
    ("timeline", ""),
    ("matrix",   "threat-matrix/"),
    ("labs",     "lab-counts/"),
]

# Bubble gaps to each column edge
TIP_GAPS_JS = """() => {
    const tip    = document.getElementById("tip").getBoundingClientRect();
    const column = document.querySelector(".content").getBoundingClientRect();
    return {left: tip.left - column.left, right: column.right - tip.right};
}"""



# ========================================================================
#   Fixtures
# ========================================================================

@pytest.fixture(scope="session")
def browser() -> Iterator["sync_api.Browser"]:
    """
    Launches one headless Chromium for the whole session

    Args:
        None

    Returns:
        Iterator[sync_api.Browser]: The running browser
    """

    with sync_api.sync_playwright() as playwright:
        chromium = playwright.chromium.launch()
        yield chromium
        chromium.close()


@pytest.fixture
def open_page(browser: "sync_api.Browser", base_url: str) -> Iterator[Callable]:
    """
    Gives a helper that opens the home page at a viewport and records its errors

    Args:
        browser (sync_api.Browser): The running browser
        base_url (str): The home page URL on the preview server

    Returns:
        Iterator[Callable]: Takes a viewport dict and returns the loaded page and its error list
    """

    pages = []

    def load(viewport: dict) -> tuple:
        """
        Opens the home page at one viewport size

        Args:
            viewport (dict): The width and height in pixels

        Returns:
            tuple: The page, and a list that collects console errors and page errors
        """

        page   = browser.new_page(viewport=viewport)
        errors = []
        page.on("console",   lambda message: message.type == "error" and errors.append(message.text))
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.route(
            lambda url: not url.startswith(base_url),
            lambda route: route.fulfill(status=200, body="", content_type="text/css"),
        )
        page.goto(base_url)
        pages.append(page)
        return page, errors

    yield load
    for page in pages:
        page.close()



# ========================================================================
#   Page Load
# ========================================================================

def test_home_loads_without_errors(open_page: Callable) -> None:
    """
    Checks the home page loads with no console errors and draws its cards

    Args:
        open_page (Callable): Opens the home page at a viewport

    Returns:
        None
    """

    page, errors = open_page(DESKTOP)
    assert page.locator("#timeline .card").count() > 0
    assert not errors



# ========================================================================
#   Tabs and Permalinks
# ========================================================================

@pytest.mark.parametrize("view, path", TABS)
def test_tab_shows_view_and_permalink(open_page: Callable, base_url: str, view: str, path: str) -> None:
    """
    Checks each tab shows its view and puts its permalink in the address bar

    Args:
        open_page (Callable): Opens the home page at a viewport
        base_url (str): The home page URL on the preview server
        view (str): The view's name, as used in its tab and panel ids
        path (str): The permalink path the view should show

    Returns:
        None
    """

    page, _ = open_page(DESKTOP)
    if view == "timeline":
        page.click("#tab-matrix")
    page.click(f"#tab-{view}")
    assert page.locator(f"#view-{view}").is_visible()
    assert page.get_attribute(f"#tab-{view}", "aria-selected") == "true"
    assert page.url == base_url + path


def test_poster_opens_and_escape_closes(open_page: Callable, base_url: str) -> None:
    """
    Checks a case's poster puts its permalink in the address bar and Escape restores it

    Args:
        open_page (Callable): Opens the home page at a viewport
        base_url (str): The home page URL on the preview server

    Returns:
        None
    """

    page, _ = open_page(DESKTOP)
    button  = page.locator("#timeline [data-open]").first
    slug    = page.evaluate("id => CASES.find(c => c.id === id).slug", button.get_attribute("data-open"))
    button.click()
    assert page.locator("#overlay.open").count() == 1
    assert page.url == f"{base_url}poster/{slug}/"

    page.keyboard.press("Escape")
    page.wait_for_url(base_url)
    assert page.locator("#overlay.open").count() == 0



# ========================================================================
#   Filters
# ========================================================================

def test_class_filter_narrows_timeline(open_page: Callable) -> None:
    """
    Checks the Class filter narrows the timeline and shows the count line

    Args:
        open_page (Callable): Opens the home page at a viewport

    Returns:
        None
    """

    page, _ = open_page(DESKTOP)
    cards   = page.locator("#timeline .card")
    total   = cards.count()
    page.click("#optionsMenu summary")
    page.select_option("#classFilter", "3")

    shown = cards.count()
    assert 0 < shown < total
    assert page.locator("#filterCount").is_visible()
    assert page.text_content("#filterCount") == f"Showing {shown} of {total} files on record."



# ========================================================================
#   Mobile Menu
# ========================================================================

def test_menu_opens_and_closes_on_phone(open_page: Callable) -> None:
    """
    Checks the MENU label opens and closes the drawer at phone width

    Args:
        open_page (Callable): Opens the home page at a viewport

    Returns:
        None
    """

    page, _ = open_page(PHONE)
    drawer  = page.locator(".nav-primary .menu")
    assert not drawer.is_visible()

    page.click(".menu-toggle")
    assert drawer.is_visible()
    assert page.get_attribute(".menu-toggle", "aria-expanded") == "true"

    page.click(".menu-toggle")
    assert not drawer.is_visible()



# ========================================================================
#   Tooltip Clamp
# ========================================================================

@pytest.mark.parametrize("viewport", [DESKTOP, PHONE], ids=["1440", "375"])
def test_glossary_bubbles_stay_in_column(open_page: Callable, viewport: dict) -> None:
    """
    Checks every glossary bubble in the first three cards sits 10px inside the column

    Args:
        open_page (Callable): Opens the home page at a viewport
        viewport (dict): The width and height in pixels

    Returns:
        None
    """

    page, _ = open_page(viewport)
    checked = 0
    outside = []
    for index in range(3):
        card = page.locator("#timeline .card").nth(index)
        for term in card.locator(".term").all():

            # Settle the scroll before hovering
            term.scroll_into_view_if_needed()
            page.wait_for_timeout(50)
            page.mouse.move(0, 0)
            term.hover()
            page.wait_for_selector("#tip.show")

            gaps     = page.evaluate(TIP_GAPS_JS)
            checked += 1
            if min(gaps["left"], gaps["right"]) < TIP_GAP - 0.5:
                outside.append(f"{term.text_content()!r}: {gaps}")
    assert checked > 0
    assert not outside, "\n".join(outside)