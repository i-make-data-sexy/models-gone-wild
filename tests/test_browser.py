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
# the bottom of the window. The not-found tests cover the 404 page's
# footer discs, the notice an unknown poster link opens, and the message
# a failed poster download shows in place of a dialog.
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
    ("404",         "no-such-page/"),
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
#   Search
# ========================================================================

def search_for(page: "sync_api.Page", query: str) -> None:
    """
    Opens the options menu if needed, types a search, and presses Enter

    Args:
        page (sync_api.Page): The loaded home page
        query (str): The text to search for

    Returns:
        None
    """

    if not page.locator("#optionsMenu[open]").count():
        page.click("#optionsMenu summary")

    page.fill("#searchInput", query)
    page.press("#searchInput", "Enter")


def test_search_narrows_and_writes_q(open_page: Callable[[dict], tuple], base_url: str) -> None:
    """
    Checks a search narrows the timeline and puts q in the address bar

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport
        base_url (str): The home page URL on the preview server

    Returns:
        None
    """

    page, errors = open_page(DESKTOP)
    cards        = page.locator("#timeline .card")
    total        = cards.count()
    search_for(page, "Hugging Face")

    shown = cards.count()
    assert 0 < shown < total
    assert page.url == base_url + "?q=Hugging+Face"
    assert page.text_content("#filterCount") == f'Showing {shown} of {total} files on record matching "Hugging Face".'
    assert page.locator("#optionsDot").is_visible()
    assert not errors


def test_search_reads_q_from_address(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks a link carrying q opens with that search applied

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport

    Returns:
        None
    """

    page, _ = open_page(DESKTOP, "?q=zero-day")
    total   = page.evaluate("CASES.length")
    shown   = page.locator("#timeline .card").count()
    assert 0 < shown < total
    assert page.input_value("#searchInput") == "zero-day"


def test_plain_search_needs_every_word(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks a plain search keeps only the cases holding every word typed

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport

    Returns:
        None
    """

    page, _ = open_page(DESKTOP)
    search_for(page, "OpenAI")
    one_word = page.locator("#timeline .card").count()

    search_for(page, "OpenAI qqqxyz")
    assert one_word > 0
    assert page.locator("#timeline .card").count() == 0
    assert page.text_content("#timeline .empty-note") == "No files match this search."


def test_advanced_switches_and_whole_word(open_page: Callable[[dict], tuple], base_url: str) -> None:
    """
    Checks Advanced opens the three switches and Match whole word narrows a search

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport
        base_url (str): The home page URL on the preview server

    Returns:
        None
    """

    page, _ = open_page(DESKTOP)
    page.click("#optionsMenu summary")
    assert not page.locator("#advancedModes").is_visible()

    page.click("label:has(#advancedToggle)")
    assert page.locator("#advancedModes").is_visible()

    search_for(page, "sol")
    partial = page.locator("#timeline .card").count()

    page.click("label:has(#matchWord)")
    whole = page.locator("#timeline .card").count()
    assert 0 < whole < partial
    assert page.url == base_url + "?q=sol&word=1"

    page.click("label:has(#advancedToggle)")
    assert not page.locator("#advancedModes").is_visible()
    assert page.url == base_url + "?q=sol"
    assert page.locator("#timeline .card").count() == partial


def test_bad_regex_shows_error_and_keeps_cases(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks a regex that fails to compile shows the error line rather than an empty registry

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport

    Returns:
        None
    """

    page, _ = open_page(DESKTOP)
    total   = page.evaluate("CASES.length")
    page.click("#optionsMenu summary")
    page.click("label:has(#advancedToggle)")
    page.click("label:has(#matchRegex)")
    search_for(page, "(unclosed")

    assert page.locator("#searchError").is_visible()
    assert page.locator("#timeline .card").count() == total


def test_search_highlights_matches_on_cards(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks a search marks the matched words in the card text and Clear all removes the marks

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport

    Returns:
        None
    """

    page, errors = open_page(DESKTOP)
    search_for(page, "hugging face")

    marks = page.locator("#timeline mark.search-hit")
    texts = {text.lower() for text in marks.all_text_contents()}
    assert texts == {"hugging", "face"}
    assert page.locator("#timeline mark.search-hit").count() == page.locator(".card-alias mark, .card-charge mark").count()

    page.click("#optionsClear")
    assert marks.count() == 0
    assert not errors


def test_clear_all_resets_search(open_page: Callable[[dict], tuple], base_url: str) -> None:
    """
    Checks Clear all empties the search and takes q out of the address bar

    Args:
        open_page (Callable[[dict], tuple]): Opens the home page at a viewport
        base_url (str): The home page URL on the preview server

    Returns:
        None
    """

    page, _ = open_page(DESKTOP)
    total   = page.evaluate("CASES.length")
    search_for(page, "Hugging Face")
    page.click("#optionsClear")

    assert page.input_value("#searchInput") == ""
    assert page.locator("#timeline .card").count() == total
    assert page.url == base_url



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
@pytest.mark.parametrize("path", ["", "methodology/", "no-such-page/"], ids=["home", "methodology", "404"])
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



# ========================================================================
#   Not Found
# ========================================================================

def test_unknown_poster_shows_notice(open_page: Callable[[dict], tuple], base_url: str) -> None:
    """
    Checks a poster link that names no case opens the notice, keeps its URL, and marks the page noindex

    Args:
        open_page (Callable[[dict], tuple]): Opens a page at a viewport
        base_url (str): The home page URL on the preview server

    Returns:
        None
    """

    page, errors = open_page(DESKTOP, "poster/no-such-slug/")
    page.wait_for_selector("#overlay.open .poster-missing")

    assert page.locator("#posterAlias").text_content() == "No File"
    assert page.locator('meta[name="robots"]').get_attribute("content") == "noindex"
    assert page.url == f"{base_url}poster/no-such-slug/"
    assert page.locator(".poster-missing .back-link").evaluate("a => a.href") == base_url
    assert not errors

    page.keyboard.press("Escape")
    page.wait_for_url(base_url)
    assert page.locator("#overlay.open").count() == 0


def test_failed_download_shows_message_in_poster(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks a Download poster press with html2canvas blocked shows a message in the poster, not a dialog

    Args:
        open_page (Callable[[dict], tuple]): Opens a page at a viewport

    Returns:
        None
    """

    library = "**/js/vendor/html2canvas.min.js"
    dialogs = []

    page, _ = open_page(DESKTOP)
    page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
    page.route(library, lambda route: route.abort())

    page.locator("#timeline [data-open]").first.click()
    page.locator("#dlBtn").click()
    page.wait_for_selector("#poster #posterMessage:not([hidden])")

    assert "didn't load" in page.locator("#posterMessage").text_content()
    assert not dialogs

    page.unroute(library)

    with page.expect_download():
        page.locator("#dlBtn").click()

    assert page.locator("#posterMessage").is_hidden()
    assert not dialogs


def test_footer_disc_opens_on_hover(open_page: Callable[[dict], tuple]) -> None:
    """
    Checks a footer disc grows into its labeled pill on hover, with no underline

    Args:
        open_page (Callable[[dict], tuple]): Opens a page at a viewport

    Returns:
        None
    """

    disc_js = """a => ({
        width:      a.getBoundingClientRect().width,
        label:      getComputedStyle(a.querySelector(".footer-label")).opacity,
        decoration: getComputedStyle(a).textDecorationLine,
    })"""

    page, _ = open_page(DESKTOP, "no-such-page/")
    disc    = page.locator(".footer-link").first
    disc.scroll_into_view_if_needed()
    rest    = disc.evaluate(disc_js)

    disc.hover()
    page.wait_for_timeout(600)
    hover   = disc.evaluate(disc_js)

    assert rest["width"] == 44 and rest["label"] == "0"
    assert hover["width"] > 100 and hover["label"] == "1"
    assert rest["decoration"] == hover["decoration"] == "none"