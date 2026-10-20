# ========================================================================
#   About This File
# ========================================================================

# Tests that read both pages and the stylesheets for the pinned footer's
# layout, with no server. The page shell holds the site header, the one
# <main class="page-body">, and the footer as siblings, and the retired
# .wrap wrapper and the .page-body-end spacer never come back. The gap
# and pinning checks need a browser and live in test_browser.py.



# ========================================================================
#   Imports
# ========================================================================

# Standard library
import re

from html.parser import HTMLParser
from pathlib     import Path

# Third party
import pytest



# ========================================================================
#   Global Variables
# ========================================================================

SITE  = Path(__file__).resolve().parent.parent / "public"
PAGES = [SITE / "index.html", SITE / "methodology" / "index.html", SITE / "404.html"]



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


class ShellParser(HTMLParser):
    """
    Records the direct children of the page shell as tag.class strings
    """

    void_tags = {"area", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "wbr"}

    def __init__(self) -> None:
        """
        Starts with no shell found and no children recorded

        Args:
            None

        Returns:
            None
        """

        super().__init__()
        self.depth    = 0
        self.shell    = None
        self.closed   = False
        self.children = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        """
        Finds the shell, then records each tag that opens directly inside it

        Args:
            tag (str): The tag name
            attrs (list): The tag's attributes as name and value pairs

        Returns:
            None
        """

        classes = dict(attrs).get("class") or ""

        if self.shell is None and "main-content" in classes.split():
            self.shell = self.depth
        elif self.shell is not None and not self.closed and self.depth == self.shell + 1:
            self.children.append(f"{tag}.{classes}")

        if tag not in self.void_tags:
            self.depth += 1

    def handle_endtag(self, tag: str) -> None:
        """
        Steps back out of a tag and notes when the shell itself closes

        Args:
            tag (str): The tag name

        Returns:
            None
        """

        if tag in self.void_tags:
            return

        self.depth -= 1

        if self.shell is not None and self.depth == self.shell:
            self.closed = True



# ========================================================================
#   Page Shell
# ========================================================================

@pytest.mark.parametrize("path", PAGES, ids=["home", "methodology", "404"])
def test_one_main_and_it_is_the_page_body(path: Path) -> None:
    """
    Checks each page holds exactly one <main>, the page body

    Args:
        path (Path): The page to read

    Returns:
        None
    """

    assert re.findall(r"<main\b[^>]*>", read(path)) == ['<main class="page-body">']


@pytest.mark.parametrize("path", PAGES, ids=["home", "methodology", "404"])
def test_shell_holds_header_body_and_footer(path: Path) -> None:
    """
    Checks the header, the page body, and the footer are the shell's only children, in that order

    Args:
        path (Path): The page to read

    Returns:
        None
    """

    parser = ShellParser()
    parser.feed(read(path))

    assert parser.shell is not None, "no .main-content wrapper"
    assert parser.children == ["header.site-header", "main.page-body", "footer.site-foot"]


def test_no_page_body_end_or_old_wrapper() -> None:
    """
    Checks no page or stylesheet names the .page-body-end spacer or the retired .wrap wrapper

    Args:
        None

    Returns:
        None
    """

    retired = re.compile(r'page-body-end|class="wrap"|\.wrap\b')
    files   = PAGES + sorted((SITE / "css").glob("*.css"))

    hits = [
        f"{path.relative_to(SITE)}:{number}: {line.strip()}"
        for path in files
        for number, line in enumerate(read(path).splitlines(), 1)
        if retired.search(line)
    ]
    assert not hits, "\n".join(hits)