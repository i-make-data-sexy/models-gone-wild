# ========================================================================
#   About This File
# ========================================================================

# Browser tests in Playwright's Chromium against the preview server,
# run with -m browser. Requests to other hosts, the Google Tag Manager
# container, are answered with an empty body so the suite runs offline,
# sends no hit to Google Analytics, and runs the same way every time.
#
# The pinned footer tests check the gap above the footer is the footer's
# own top margin on every page, and that a short page pins the footer to
# the bottom of the window.
#
# The tooltip tests hold every bubble 10px inside its box, the reading
# column on the page or the open poster. The column test is the
# revert-and-fail proof for 8e726b4, which clamped the glossary bubbles
# inside the reading column. Without the clamp the bubbles spill past the
# column's edge and the test fails.



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

pytestmark    = pytest.mark.browser

DESKTOP       = {"width": 1440, "height": 900}
PHONE         = {"width": 375,  "height": 812}

TABS          = [
    ("timeline", ""),
    ("matrix",   "threat-matrix/"),
    ("labs",     "lab-counts/"),
]

FOOTER_PAGES  = [
    ("home",        ""),
    ("matrix",      "threat-matrix/"),
    ("labs",        "lab-counts/"),
    ("poster",      "poster/sol-hugging-face/"),
    ("methodology", "methodology/"),
]
FOOTER_WIDTHS = [375, 768, 1024, 1440]



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
def open_page(browser: "sync_api.Browser", base_url: str) -> Iterator[Callable[[dict], tuple]]:
    """
    Gives a helper that opens a page at a viewport and records its errors

    Args:
        browser (sync_api.Browser): The running browser
        base_url (str): The home page URL on the preview server

    Returns:
        Iterator[Callable[[dict], tuple]]: Takes a viewport dict and an optional path, and returns the loaded page and its error list
    """

    pages = []

    def load(viewport: dict, path: str = "") -> tuple:
        """
        Opens a page at one viewport size

        Args:
            viewport (dict): The width and height in pixels
            path (str): The path after the home page URL, or "" for the home page

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
        page.goto(base_url + path)
        pages.append(page)

        return page, errors

    yield load

    for page in pages:
        page.close()



# ========================================================================
#   Page Load
# ========================================================================

def test_home_loads_without_errors(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks the home page loads with no console errors and draws its cards

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport

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
def test_tab_shows_view_and_permalink(
    open_page: Callable[[dict], tuple],
    base_url:  str,
    view:      str,
    path:      str,
) -> None:
    """
    Checks each tab shows its view and puts its permalink in the address bar

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport
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


def test_poster_opens_and_escape_closes(open_page: Callable[[dict], tuple], base_url: str) -> None:
    """
    Checks a case's poster puts its permalink in the address bar and Escape restores it

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport
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

def test_class_filter_narrows_timeline(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks the Class filter narrows the timeline and shows the count line

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport

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

def test_menu_opens_and_closes_on_phone(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks the MENU label opens and closes the drawer at phone width

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport

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
def test_glossary_bubbles_stay_in_column(
    open_page: Callable[[dict], tuple],
    viewport:  dict,
) -> None:
    """
    Checks every glossary bubble in the first three cards sits 10px inside the column

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport
        viewport (dict): The width and height in pixels

    Returns:
        None
    """

    tip_gap     = 10
    tip_gaps_js = """() => {
        const tip    = document.getElementById("tip").getBoundingClientRect();
        const column = document.querySelector(".content").getBoundingClientRect();
        return {left: tip.left - column.left, right: column.right - tip.right};
    }"""

    page, _ = open_page(viewport)
    checked = 0
    outside = []

    for index in range(3):
        card = page.locator("#timeline .card").nth(index)

        for term in card.locator(".term").all():
            term.scroll_into_view_if_needed()
            page.wait_for_timeout(50)
            page.mouse.move(0, 0)
            term.hover()
            page.wait_for_selector("#tip.show")

            gaps     = page.evaluate(tip_gaps_js)
            checked += 1

            if min(gaps["left"], gaps["right"]) < tip_gap - 0.5:
                outside.append(f"{term.text_content()!r}: {gaps}")

    assert checked > 0
    assert not outside, "\n".join(outside)


@pytest.mark.parametrize("viewport", [DESKTOP, PHONE], ids=["1440", "375"])
def test_poster_bubbles_stay_in_poster(
    open_page: Callable[[dict], tuple],
    viewport:  dict,
) -> None:
    """
    Checks every bubble in an open poster sits 10px inside the poster on all four sides

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport
        viewport (dict): The width and height in pixels

    Returns:
        None
    """

    tip_gap     = 10
    tip_gaps_js = """() => {
        const tip    = document.getElementById("tip").getBoundingClientRect();
        const poster = document.querySelector("#overlay .poster").getBoundingClientRect();
        return {
            left:   tip.left - poster.left,
            right:  poster.right - tip.right,
            top:    tip.top - poster.top,
            bottom: poster.bottom - tip.bottom,
        };
    }"""

    page, _ = open_page(viewport, "poster/sol-hugging-face/")
    page.wait_for_selector("#overlay.open")
    checked = 0
    outside = []

    for trigger in page.locator("#overlay .poster [data-def], #overlay .poster [data-tip]").all():
        trigger.scroll_into_view_if_needed()
        page.wait_for_timeout(50)
        page.mouse.move(0, 0)
        trigger.hover()
        page.wait_for_selector("#tip.show")

        gaps     = page.evaluate(tip_gaps_js)
        checked += 1

        if min(gaps.values()) < tip_gap - 0.5:
            outside.append(f"{trigger.text_content()!r}: {gaps}")

    assert checked > 0
    assert not outside, "\n".join(outside)


def test_tip_text_is_left_aligned(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks the tooltip bubble computes left-aligned text

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport

    Returns:
        None
    """

    page, _ = open_page(DESKTOP)

    assert page.evaluate("getComputedStyle(document.getElementById('tip')).textAlign") == "left"



# ========================================================================
#   Pinned Footer
# ========================================================================

@pytest.mark.parametrize("width", FOOTER_WIDTHS)
@pytest.mark.parametrize("name, path", FOOTER_PAGES)
def test_gap_above_footer_is_its_margin(
    open_page: Callable[[dict], tuple],
    name:      str,
    path:      str,
    width:     int,
) -> None:
    """
    Checks the gap above the footer equals the footer's top margin, in a short window

    Args:
        open_page (Callable[[dict], tuple]): Opens a page at a viewport
        name (str): The page or view name, for the test id
        path (str): The path after the home page URL
        width (int): The window width in pixels

    Returns:
        None
    """

    gap_js = """() => {
        const foot  = document.querySelector(".site-foot");
        const shown = el => {
            const style = getComputedStyle(el);
            return el.tagName !== "SCRIPT" && !el.hidden && style.display !== "none"
                && !["absolute", "fixed"].includes(style.position)
                && el.getBoundingClientRect().height > 0;
        };
        const last  = [...document.querySelector(".page-body").children].filter(shown).pop();
        return {
            gap:    foot.getBoundingClientRect().top - last.getBoundingClientRect().bottom,
            margin: parseFloat(getComputedStyle(foot).marginTop),
        };
    }"""

    page, _ = open_page({"width": width, "height": 500}, path)

    if name == "poster":
        page.wait_for_selector("#overlay.open")

    page.evaluate("document.fonts.ready")
    measured = page.evaluate(gap_js)

    assert measured["margin"] > 0
    assert abs(measured["gap"] - measured["margin"]) < 0.5, measured


@pytest.mark.parametrize("width", [375, 1440])
@pytest.mark.parametrize("path", ["", "methodology/"], ids=["home", "methodology"])
def test_footer_pins_to_bottom_of_short_page(
    open_page: Callable[[dict], tuple],
    path:      str,
    width:     int,
) -> None:
    """
    Checks the footer ends its bottom margin above the window's edge once the page is short

    Args:
        open_page (Callable[[dict], tuple]): Opens a page at a viewport
        path (str): The path after the home page URL
        width (int): The window width in pixels

    Returns:
        None
    """

    pin_js = """() => {
        document.querySelectorAll(".content > :not(.masthead)").forEach(el => el.hidden = true);
        const foot = document.querySelector(".site-foot");
        return {
            bottom: foot.getBoundingClientRect().bottom + parseFloat(getComputedStyle(foot).marginBottom),
            inner:  innerHeight,
            scroll: document.documentElement.scrollHeight,
        };
    }"""

    page, _  = open_page({"width": width, "height": 1400}, path)
    measured = page.evaluate(pin_js)

    assert measured["scroll"] == measured["inner"], measured
    assert abs(measured["bottom"] - measured["inner"]) < 0.5, measured